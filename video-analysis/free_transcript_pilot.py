#!/usr/bin/env python3
"""Free, anonymous pilot for timestamped YouTube captions; standard library only.

The report retains every keyword candidate and bounded excerpts, never scores.
Full speech is written only with --cache-dir, for local contextual review. Use
--input-dir to reprocess supplied payloads/cache files without any network call.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import re
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ENDPOINT = "https://api.freetranscriptapi.com/v1/transcript"
PILOT = [
    ("DMlWjjIcwss", "AFS Silk V2 650/750/950", "fr"),
    ("aiWA2W7hKos", "Duotone Glide 3.0 D/LAB 825", "de"),
    ("zesN5IeyRQM", "KT Halo 670/800", "de"),
]
# These are search hints from the pilot titles, not verified tested sizes.
SIZE_HINTS = {"DMlWjjIcwss": [650, 750, 950], "aiWA2W7hKos": [825],
              "zesN5IeyRQM": [670, 800]}
# Keep the v1 vocabulary to allow honest comparison with earlier runs.
PATTERNS = {
    "takeoff": re.compile(r"d[eé]coll|take.?off|lift.?off|fr[uü]h|angleit|abheb", re.I),
    "glide": re.compile(r"gliss|gleit|glide|efficien|drag|pump|vitesse|speed", re.I),
    "carving": re.compile(r"carv|virage|turn|kurven|surf|maniab", re.I),
    "control": re.compile(r"stabil|contr[oô]l|control|pitch|tangage|kontroll|clapot|chop", re.I),
}
EXCERPT_LIMIT = 130
CACHE_FORMAT = "foil_lab_timed_segments_v1"


def finite_number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


def parse(payload):
    """Normalize provider data or our local cache; never manufacture speech."""
    if not isinstance(payload, dict):
        raise ValueError("invalid_payload")
    cached = payload.get("format") == CACHE_FORMAT
    segments = payload.get("segments") if cached else payload.get("transcript")
    if not isinstance(segments, list):
        raise ValueError("no_segment_array")
    found = []
    for item in segments:
        if not isinstance(item, dict):
            continue
        start = item.get("at_s" if cached else "start")
        end_or_duration = item.get("to_s" if cached else "duration")
        txt = item.get("text")
        if not finite_number(start) or start < 0:
            continue
        if not finite_number(end_or_duration) or end_or_duration < 0:
            continue
        end = end_or_duration if cached else start + end_or_duration
        if not finite_number(end) or end < start:
            continue
        if not isinstance(txt, str) or not txt.strip():
            continue
        found.append({"at_s": float(start), "to_s": float(end),
                      "text": " ".join(txt.split())})
    if not found:
        raise ValueError("no_timed_speech")
    return sorted(found, key=lambda x: x["at_s"])


def transcript_digest(segments):
    # Same normalization and serialization as schema v1, for historical audits.
    return hashlib.sha256(json.dumps(segments, sort_keys=True,
                                    ensure_ascii=False).encode()).hexdigest()


def timed_link(video_id, at_s):
    return f"https://www.youtube.com/watch?v={video_id}&t={int(at_s)}s"


def mentioned_sizes(text, hints):
    # ASR may confuse numbers, units and names; every match remains unvalidated.
    # A numeric hint is not evidence that its surrounding claim applies to it.
    return [size for size in hints
            if re.search(r"(?<![\w.,])" + str(size) + r"(?:er)?(?!\w|[.,]\d)", text)]


def summarize(video, payload, context_seconds=8):
    if not finite_number(context_seconds) or context_seconds < 0:
        raise ValueError("invalid_context_seconds")
    segments = parse(payload)
    hints = SIZE_HINTS.get(video[0], [])
    sizes_by_segment = [mentioned_sizes(item["text"], hints) for item in segments]
    leads = []
    category_counts = {key: 0 for key in PATTERNS}
    size_mentions = []
    for index, item in enumerate(segments):
        if sizes_by_segment[index]:
            size_mentions.append({
                "segment_index": index, "at_s": item["at_s"], "to_s": item["to_s"],
                "numeric_size_hints": sizes_by_segment[index],
                "short_excerpt": item["text"][:EXCERPT_LIMIT],
                "excerpt_truncated": len(item["text"]) > EXCERPT_LIMIT,
                "link": timed_link(video[0], item["at_s"]),
                "status": "numeric_size_candidate_not_validated",
            })
        categories = [key for key, rx in PATTERNS.items() if rx.search(item["text"])]
        if not categories:
            continue
        for category in categories:
            category_counts[category] += 1
        context_indices = [i for i, other in enumerate(segments)
                           if other["to_s"] >= item["at_s"] - context_seconds
                           and other["at_s"] <= item["to_s"] + context_seconds]
        context_start = min(segments[i]["at_s"] for i in context_indices)
        context_end = max(segments[i]["to_s"] for i in context_indices)
        leads.append({
            "candidate_id": f"{video[0]}:segment:{index}",
            "segment_index": index, "at_s": item["at_s"], "to_s": item["to_s"],
            "categories": categories, "short_excerpt": item["text"][:EXCERPT_LIMIT],
            "excerpt_truncated": len(item["text"]) > EXCERPT_LIMIT,
            "link": timed_link(video[0], item["at_s"]),
            # Context text stays in the local transcript, not the public report.
            "context": {"at_s": context_start, "to_s": context_end,
                        "segment_indices": context_indices,
                        "link": timed_link(video[0], context_start)},
            "size_hints_in_segment": sizes_by_segment[index],
            "size_hints_in_context": sorted({size for i in context_indices
                                             for size in sizes_by_segment[i]}),
            "size_tested": None, "claim": None, "polarity": None,
            "status": "keyword_candidate_not_validated",
        })
    return {
        "video_id": video[0], "title": video[1], "language": payload.get("language"),
        "status": "timed_transcript_received", "segment_count": len(segments),
        "technical_keyword_segments": len(leads),
        "keyword_category_segment_counts": category_counts,
        "keyword_category_matches": sum(category_counts.values()),
        "candidate_count": len(leads), "candidates_omitted": 0,
        "candidate_selection": "all_keyword_matching_segments_chronological",
        "context_seconds": context_seconds,
        "transcript_sha256": transcript_digest(segments),
        "declared_size_hints": hints, "size_mentions": size_mentions,
        "size_attribution": "unvalidated_numeric_hints_only",
        "candidate_passages": leads, "video_fully_watched": False,
        "performance_scores_generated": 0,
    }


def default_fetch(video):
    url = ENDPOINT + "?" + urllib.parse.urlencode({"video_url": video[0], "lang": video[2]})
    req = urllib.request.Request(url, headers={"User-Agent": "FOIL-LAB-Research/1.0",
                                              "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=35) as response:
        return json.loads(response.read(2_000_000).decode("utf-8"))


def read_local(input_dir, video):
    """Read only the requested video; failures never fall back to the network."""
    payload = json.loads((Path(input_dir) / (video[0] + ".json")).read_text(encoding="utf-8-sig"))
    if isinstance(payload, dict) and payload.get("video_id", video[0]) != video[0]:
        raise ValueError("cached_video_id_mismatch")
    if isinstance(payload, dict) and payload.get("format") == CACHE_FORMAT:
        if payload.get("transcript_sha256") != transcript_digest(parse(payload)):
            raise ValueError("cached_transcript_hash_mismatch")
    return payload


def write_cache(cache_dir, video, payload):
    segments = parse(payload)
    cached = {"format": CACHE_FORMAT, "video_id": video[0], "title": video[1],
              "language": payload.get("language"),
              "cache_written_at_utc": datetime.now(timezone.utc).isoformat(),
              "transcript_sha256": transcript_digest(segments), "segments": segments}
    path = Path(cache_dir) / (video[0] + ".json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(cached, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
                    encoding="utf-8")


def run(fetch=default_fetch, limit=3, *, input_dir=None, cache_dir=None, context_seconds=8):
    if limit not in (1, 2, 3):
        raise ValueError("invalid_pilot_limit")
    if not finite_number(context_seconds) or context_seconds < 0:
        raise ValueError("invalid_context_seconds")
    output = {
        "schema_version": 2,
        "access_method": ("local_cached_transcript_no_network" if input_dir is not None
                          else "unauthenticated_no_key_no_credits"),
        "provider": "FreeTranscriptAPI.com", "attempted": 0, "transcripts_obtained": 0,
        "videos_watched": 0, "notes_updated": 0, "results": [],
        "counting_note": ("technical_keyword_segments counts matching subtitle segments, "
                          "not word occurrences or validated claims; category counts overlap"),
    }
    for video in PILOT[:limit]:
        output["attempted"] += 1
        try:
            payload = read_local(input_dir, video) if input_dir is not None else fetch(video)
            result = summarize(video, payload, context_seconds)
            output["transcripts_obtained"] += 1
            if cache_dir is not None:
                try:
                    write_cache(cache_dir, video, payload)
                    result["local_cache_status"] = "written"
                except OSError as exc:
                    # Acquisition succeeded even if persistence did not.
                    result["local_cache_status"] = "write_failed"
                    result["cache_failure_type"] = type(exc).__name__
        except Exception as exc:
            # Exception class only: no tokens, paths or transcript response exposed.
            result = {"video_id": video[0], "title": video[1], "status": "unavailable_or_blocked",
                      "failure_type": type(exc).__name__}
        output["results"].append(result)
    output["technical_keyword_segments"] = sum(r.get("technical_keyword_segments", 0)
                                              for r in output["results"])
    output["candidate_count"] = sum(r.get("candidate_count", 0) for r in output["results"])
    output["candidates_omitted"] = 0
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("video-index/free-transcript-pilot.json"))
    parser.add_argument("--limit", type=int, choices=(1, 2, 3), default=3)
    parser.add_argument("--input-dir", type=Path,
                        help="Offline: directory containing VIDEO_ID.json provider payloads or caches")
    parser.add_argument("--cache-dir", type=Path,
                        help="Opt-in LOCAL full transcripts; do not commit or publish without permission")
    parser.add_argument("--context-seconds", type=float, default=8,
                        help="Context before/after each hit, references only in report (default: 8)")
    args = parser.parse_args()
    if not finite_number(args.context_seconds) or args.context_seconds < 0:
        parser.error("--context-seconds must be finite and non-negative")
    result = run(limit=args.limit, input_dir=args.input_dir, cache_dir=args.cache_dir,
                 context_seconds=args.context_seconds)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
                           encoding="utf-8")
    print("FREE_TRANSCRIPT_RESULT " + json.dumps({
        "attempted": result["attempted"], "transcripts_obtained": result["transcripts_obtained"],
        "candidate_count": result["candidate_count"], "candidates_omitted": result["candidates_omitted"],
        "outcomes": [{"video_id": r["video_id"], "status": r["status"],
                      "segment_count": r.get("segment_count"),
                      "technical_keyword_segments": r.get("technical_keyword_segments"),
                      "failure_type": r.get("failure_type")} for r in result["results"]]}))


if __name__ == "__main__":
    main()
