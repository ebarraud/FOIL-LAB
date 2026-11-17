#!/usr/bin/env python3
"""Review-prioritization of discovered wingfoil test metadata.

This is a conservative *metadata* screening, not analysis of video contents.
Distinguishes review candidates from false positives and duplicate translations.
"""
from __future__ import annotations
import argparse
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

BLOCK = re.compile(
    r"\b(tutorial|how to|learn|beginner tips|beginner guide|school|cours|"
    r"astuce|tuto|unboxing|first look|preview|trailer|teaser|"
    r"launch|announcement|news|webinar|event|interview|vlog|"
    r"how does|setup guide|assemble|montage|instruction|"
    r"wing test|wing review|wing harness|kitefoil only|efoil|e-foil)\b", re.I)
REVIEW = re.compile(
    r"\b(test|tests|tested|testing|review|reviews|essai|essais|"
    r"vergleich|praxistest|fahrbericht|erfahrungsbericht|"
    r"on the water review|gear review|recensione|prova|reseña|resena)\b", re.I)
BOARD = re.compile(
    r"\b(board|boards|wingboard|foilboard|wingfoilboard|mid.?length|"
    r"skybrid|sky.?style|drifter|rocket|downwind board|"
    r"foil board|wing foil board|planche|boards)\b", re.I)
FOIL = re.compile(
    r"\b(front wing|frontwing|foil|foils|hydrofoil|"
    r"glide 3\.0|sonar|enduro|silk|high aspect foil|"
    r"foil wing|fl[uü]gel)\b", re.I)
WINGFOIL = re.compile(r"wingfoil|wing.foil|wingboard|wing.?surfen|wing.surf|winging", re.I)
OTHER = re.compile(
    r"\b(kitefoil|kite foil|pumpfoil|pump foil|surf foil|wakefoil|"
    r"efoil|e.?foil|sup foil|windfoil|wind foil)\b", re.I)
TRANSLATION = re.compile(
    r"\b(english (?:translated|translation|version)|"
    r"german (?:translated|translation|version)|"
    r"french (?:translated|translation|version)|"
    r"version (?:fran[cç]aise|anglaise|allemande)|"
    r"traduction (?:fran[cç]aise|anglaise)|"
    r"deutsche version|english subtitles)\b",
    re.I,
)

def fold(value):
    normalized = unicodedata.normalize("NFKD", value)
    return "".join(ch for ch in normalized if not unicodedata.combining(ch)).lower()

def dedup_key(video: dict) -> str:
    title = fold(video.get("title", ""))
    title = TRANSLATION.sub(" ", title)
    # Preserve year and construction: different generations are not translation duplicates.
    title = re.sub(r"\b(test|tests|tested|testing|review|reviews|essai|essais|"
                   r"wingfoil|wing board|wingboard|foil|hydrofoil|"
                   r"by|the|a|der|die|das|von|mit|in|english|"
                   r"german|french)\b", " ", title)
    title = re.sub(r"[^a-z0-9]+", " ", title).strip()
    # Require at least two informative words to avoid grouping unrelated models.
    pieces = [p for p in title.split() if len(p) > 1]
    return f"{video.get('category','other')}|{' '.join(pieces)}" if len(pieces) >= 2 else f"unique|{video.get('id')}"

def assess(video: dict) -> dict:
    title = video.get("title", "")
    category = video.get("category")
    reasons = []
    if BLOCK.search(title):
        reasons.append("non_test_or_tutorial_signal")
    if OTHER.search(title) and not WINGFOIL.search(title):
        reasons.append("other_foil_discipline_not_wingfoil_confirmed")
    if not REVIEW.search(title):
        reasons.append("no_explicit_test_or_review_signal")
    if category not in {"foil", "board"}:
        reasons.append("not_board_or_foil")
    if category == "board" and not BOARD.search(title):
        reasons.append("board_not_explicitly_named")
    if category == "foil" and not FOIL.search(title):
        reasons.append("foil_not_explicitly_named")
    if not video.get("published_on"):
        reasons.append("publication_date_missing")
    if not video.get("url"):
        reasons.append("exact_video_url_missing")
    if reasons:
        state = "needs_manual_scope_review"
    else:
        state = "priority_metadata_candidate"
    return {
        **video, "screening_status": state,
        "screening_reasons": reasons,
        "metadata_only": True,
        "transcript_evidence": False,
        "performance_scores": None,
        "content_verified": False,
        "independent_test_confirmed": False,
        "duplicate_group": None,
        "duplicate_status": "unverified",
    }

def qualify(records: list[dict]) -> dict:
    assessed = [assess(item) for item in records]
    # Exact URLs are definitive duplicates. Title-based grouping is only a
    # POTENTIAL translation/repost group; never silently drop observations.
    groups: dict[str, list[dict]] = defaultdict(list)
    for entry in assessed:
        groups[dedup_key(entry)].append(entry)
    possible_groups = []
    for key, rows in groups.items():
        if len(rows) < 2 or key.startswith("unique|"):
            continue
        for row in rows:
            row["duplicate_group"] = key
            row["duplicate_status"] = "possible_same_test_manual_check"
        possible_groups.append({
            "group_key": key, "video_ids": [x.get("id") for x in rows],
            "reason": "similar_model_names_may_include_translations_or_reposts",
            "confirmed_same_test": False
        })
    counts = Counter(x["screening_status"] for x in assessed)
    return {
        "schema_version": 1, "source_items": len(records),
        "priority_metadata_candidates": counts["priority_metadata_candidate"],
        "needs_manual_scope_review": counts["needs_manual_scope_review"],
        "possible_duplicate_groups": len(possible_groups),
        "video_contents_analyzed": 0, "transcripts_obtained": 0,
        "performance_ratings_generated": 0,
        "notes": "Conservative metadata screening: a 'priority' candidate is NOT a verified wingfoil equipment test; possible duplicates are NOT confirmed.",
        "possible_duplicate_details": possible_groups,
        "videos": assessed,
    }

def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    p.add_argument("--print-sample", type=int, default=12)
    args = p.parse_args(argv)
    raw = json.loads(args.input.read_text(encoding="utf-8"))
    data = qualify(raw.get("videos", []))
    data["window_start"] = raw.get("window_start")
    data["window_end"] = raw.get("window_end")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("QUALIFICATION_COUNTS " + json.dumps({
        k: data[k] for k in ("source_items", "priority_metadata_candidates",
          "needs_manual_scope_review", "possible_duplicate_groups",
          "transcripts_obtained", "video_contents_analyzed")
    }))
    for row in [x for x in data["videos"] if x["screening_status"] == "priority_metadata_candidate"][:max(0, args.print_sample)]:
        # Print concrete candidates so the pilot can be audited without
        # downloading the full JSON artifact.
        print("CANDIDATE " + json.dumps({
            "title": row.get("title"), "category": row.get("category"),
            "published_on": row.get("published_on"), "url": row.get("url"),
            "possible_duplicate": row["duplicate_status"] != "unverified",
        }, ensure_ascii=False))

if __name__ == "__main__":
    main()
