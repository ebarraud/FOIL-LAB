#!/usr/bin/env python3
"""Conservative, auditable caption availability probe and importer.

Uses yt-dlp as an OPTIONAL external executable; never downloads audiovisual
streams. Probe only checks captions; fetch requests only VTT subtitles.
No video is ever considered reviewed as a consequence of running this tool.
"""
from __future__ import annotations
import argparse
import json
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

SUPPORTED_HOSTS = {"www.youtube.com", "youtube.com", "m.youtube.com",
                   "youtu.be", "gleiten.tv", "www.gleiten.tv"}
INDEX_PATHS = {"/foil/test/wingfoil/foil/", "/foil/test/wingfoil/",
               "/foil/test/", "/foil/test/wingfoil/alle/"}
ALLOWED_LANGS = ("de", "en", "fr")
MAX_VIDEOS = 20


def eligible(video: dict) -> tuple[bool, str]:
    url = video.get("url", "")
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in SUPPORTED_HOSTS:
        return False, "unsupported_or_non_https_host"
    if not parsed.path or parsed.path in INDEX_PATHS or (
        parsed.hostname and "gleiten.tv" in parsed.hostname
        and not re.match(r"^/video/\d+", parsed.path)
        and not re.match(r"^/index.php/video/action/view/v/\d+", parsed.path)
    ):
        return False, "index_not_individual_video"
    if parsed.hostname in {"youtube.com", "www.youtube.com", "m.youtube.com"} and parsed.path == "/watch" and "v=" not in parsed.query:
        return False, "missing_youtube_video_id"
    return True, "ok"


def command(video: dict, mode: str, directory: Path, language: str) -> list[str]:
    args = [
        "yt-dlp", "--no-playlist", "--no-warnings",
        "--ignore-config", "--skip-download", "--socket-timeout", "15",
        "--retries", "1", "--extractor-retries", "1",
        "--no-progress", "--no-write-info-json", "--no-write-thumbnail",
    ]
    if mode == "probe":
        args.append("--list-subs")
    else:
        # No audiovisual media is requested. Do not generate translated
        # subtitles automatically: language is the known original language.
        args.extend(["--write-subs", "--write-auto-subs",
                     "--sub-langs", language, "--sub-format", "vtt",
                     "--paths", str(directory),
                     "--output", "%(id)s.%(ext)s"])
    return args + [video["url"]]


def invoke(cmd: list[str], *, timeout_s: int = 75):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_s,
                          check=False)


def run_video(video: dict, mode: str, runner=invoke) -> dict:
    base = {
        "id": video["id"], "url": video["url"], "publisher": video.get("publisher"),
        "mode": mode, "video_fully_watched": False,
        "performance_scores": None, "transcript_analyzed": False,
    }
    ok, why = eligible(video)
    if not ok:
        return {**base, "status": "skipped", "reason": why}
    if mode == "fetch" and video.get("language") not in ALLOWED_LANGS:
        return {**base, "status": "skipped", "reason": "language_not_whitelisted"}
    with tempfile.TemporaryDirectory(prefix="foil-lab-captions-") as folder:
        workdir = Path(folder)
        try:
            p = runner(command(video, mode, workdir, video.get("language", "de")))
        except FileNotFoundError:
            return {**base, "status": "failed", "reason": "yt_dlp_not_installed"}
        except subprocess.TimeoutExpired:
            return {**base, "status": "failed", "reason": "network_timeout"}
        except OSError:
            return {**base, "status": "failed", "reason": "tool_execution_failed"}
        # Do not publish full console output or caption text in the report.
        if p.returncode != 0:
            err = (p.stderr or "").lower()
            if "403" in err or "forbidden" in err:
                reason = "access_denied"
            elif "429" in err or "too many" in err:
                reason = "rate_limited"
            elif "unsupported url" in err or "unsupported url" in (p.stdout or "").lower():
                reason = "extractor_not_supported"
            else:
                reason = "extractor_or_network_error"
            return {**base, "status": "failed", "reason": reason, "exit_code": p.returncode}
        if mode == "probe":
            output = (p.stdout or "").lower()
            # Listing subtitles is not the same as obtaining a transcript.
            found = bool(re.search(r"available subtitles|available automatic captions|available automatic subtitles|subtitles for", output))
            return {**base, "status": "probed", "caption_listing_indicated": found,
                    "reason": "check_list_subs_output_for_details_if_needed"}
        paths = list(workdir.glob("*.vtt"))
        if not paths:
            return {**base, "status": "no_vtt", "reason": "no_matching_caption_downloaded"}
        # Process captions in memory only; never persist the full third-party text.
        try:
            from analyze import parse_cues, COMPILED
            results = []
            for path in paths:
                cues = parse_cues(path.read_text(encoding="utf-8-sig"))
                counts = {key: sum(bool(pattern.search(cue["text"])) for cue in cues)
                          for key, pattern in COMPILED.items()}
                results.append({"track": path.name, "cues": len(cues),
                                "technical_keyword_candidate_counts": counts})
            return {**base, "status": "captions_processed_locally",
                    "transcript_analyzed": False, "keyword_candidates_extracted": True, "tracks": results,
                    "note": "Keyword candidates only, not performance assertions"}
        except (OSError, UnicodeDecodeError, ValueError) as exc:
            return {**base, "status": "failed", "reason": type(exc).__name__}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default="video-analysis/manifest.json")
    parser.add_argument("--mode", choices=["probe", "fetch"], default="probe")
    parser.add_argument("--limit", type=int, default=4)
    parser.add_argument("--publisher", choices=["all", "YouTube", "Gleiten.TV"], default="all")
    parser.add_argument("--output", default="video-analysis/reports/latest.json")
    parser.add_argument("--accept-platform-terms", action="store_true",
                        help="Acknowledge that you have checked permissions, licenses and platform terms")
    args = parser.parse_args(argv)
    if args.limit < 1 or args.limit > MAX_VIDEOS:
        parser.error(f"--limit must be between 1 and {MAX_VIDEOS}")
    if args.mode == "fetch" and not args.accept_platform_terms:
        parser.error("fetch needs --accept-platform-terms after reviewing rights")
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    items = [v for v in manifest["videos"]
             if args.publisher == "all" or v.get("publisher") == args.publisher][:args.limit]
    result = {
        "schema_version": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "mode": args.mode,
        "attempted": len(items),
        "full_videos_watched": 0,
        "records": [run_video(video, args.mode) for video in items],
    }
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for row in result["records"]:
        print(f"{row['id']}: {row['status']} ({row.get('reason', 'ok')})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
