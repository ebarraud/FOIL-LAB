#!/usr/bin/env python3
"""FOIL LAB — local subtitle analysis. Standard library only.

This is a candidate extractor, not a machine learning evaluator. No scores or
performance claims are generated automatically. Requires an explicitly provided
local .srt or .vtt subtitle file; does not download videos or subtitles.
"""
from __future__ import annotations
import argparse
import hashlib
import html
import json
import re
from pathlib import Path
from urllib.parse import urlparse, parse_qs

TIME = re.compile(r"^(\d{1,2}:)?\d{2}:\d{2}[.,]\d{3}$")
CUE = re.compile(r"^\s*((?:\d{1,2}:)?\d{2}:\d{2}[.,]\d{3})\s*-->\s*((?:\d{1,2}:)?\d{2}:\d{2}[.,]\d{3})")
TAG = re.compile(r"<[^>]*>")
CATEGORIES = {
    "takeoff": [
        r"d[eé]coll", r"take.?off", r"lift.?off", r"low.?end", r"fr[uü]h", r"abheb", r"starten", r"angleit", r"anpump", r"aufsteigen"
    ],
    "glide": [
        r"gliss", r"gleit", r"glide", r"efficien", r"drag", r"speed", r"vitesse", r"tr[aä]gheit", r"reibung", r"pump"
    ],
    "carving": [
        r"carv", r"turn", r"virage", r"kurven", r"wende", r"maniab", r"radien", r"drehen", r"surf"
    ],
    "control": [
        r"contr[oô]l", r"control", r"stabil", r"balance", r"pitch", r"tangage", r"stall", r"str[oö]mung", r"kontroll", r"ruhig", r"chop", r"clapot"
    ],
}
COMPILED = {key: re.compile("|".join(patterns), re.IGNORECASE) for key, patterns in CATEGORIES.items()}

def seconds(stamp: str) -> float:
    parts = stamp.replace(",", ".").split(":")
    if len(parts) == 2:
        return int(parts[0]) * 60 + float(parts[1])
    if len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
    raise ValueError("Invalid timestamp")

def parse_cues(content: str) -> list[dict]:
    """Parse SRT/WebVTT, ignoring cue headers, VTT settings, duplicates."""
    content = content.lstrip("\ufeff")
    cues = []
    for block in re.split(r"\n\s*\n", content.replace("\r\n", "\n")):
        lines = block.splitlines()
        match = next((CUE.match(line) for line in lines if CUE.match(line)), None)
        if not match:
            continue
        line_idx = next(i for i, line in enumerate(lines) if CUE.match(line))
        text = " ".join(TAG.sub("", html.unescape(line)).strip() for line in lines[line_idx + 1:])
        text = re.sub(r"\s+", " ", text).strip()
        if not text:
            continue
        start = round(seconds(match.group(1)), 3)
        end = round(seconds(match.group(2)), 3)
        if end < start:
            continue
        if cues and start == cues[-1]["start_s"] and text == cues[-1]["text"]:
            continue
        cues.append({"start_s": start, "end_s": end, "text": text})
    return cues

def timed_link(url: str, offset: int) -> str:
    parsed = urlparse(url)
    if parsed.hostname in {"youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be"}:
        sep = "&" if parsed.query else "?"
        return url + sep + "t=" + str(offset) + "s"
    return url

def extract(video: dict, subtitle: str, language: str, filename: str) -> dict:
    cues = parse_cues(subtitle)
    if not cues:
        raise ValueError("No valid timed subtitle cues found")
    candidates = []
    for cue in cues:
        matched = [name for name, regex in COMPILED.items() if regex.search(cue["text"])]
        if not matched:
            continue
        # Preserve a short exact excerpt and an anchor. It is NOT a conclusion.
        offset = int(cue["start_s"])
        candidates.append({
            "at_s": cue["start_s"],
            "to_s": cue["end_s"],
            "link": timed_link(video["url"], offset),
            "categories": matched,
            "excerpt": cue["text"][:280],
            "status": "keyword_candidate_needs_human_validation",
            "polarity": None,
            "claim": None,
            "size_tested": None,
            "test_conditions": None,
            "confidence": "unassessed"
        })
    return {
        "schema_version": 1,
        "video_id": video["id"],
        "title": video["title"],
        "url": video["url"],
        "publisher": video["publisher"],
        "language": language,
        "subtitle_origin": filename,
        "transcript_sha256": hashlib.sha256(subtitle.encode("utf-8")).hexdigest(),
        "transcript_cues": len(cues),
        "video_fully_watched": False,
        "status": "transcript_keyword_candidates",
        "size_and_year_verified": False,
        "performance_scores": None,
        "candidates": candidates
    }

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default="video-analysis/manifest.json")
    parser.add_argument("--id", required=True, help="Existing manifest video ID")
    parser.add_argument("--subtitles", required=True, type=Path, help="Locally supplied .srt or .vtt")
    parser.add_argument("--language", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    video = next((v for v in manifest["videos"] if v["id"] == args.id), None)
    if video is None:
        parser.error("Video ID not found in manifest")
    if args.subtitles.suffix.lower() not in {".vtt", ".srt"}:
        parser.error("Only .vtt and .srt subtitles are supported")
    subtitle = args.subtitles.read_text(encoding="utf-8-sig")
    result = extract(video, subtitle, args.language, args.subtitles.name)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(result['candidates'])} candidate passages, {result['transcript_cues']} cues; no performance notes assigned")

if __name__ == "__main__":
    main()
