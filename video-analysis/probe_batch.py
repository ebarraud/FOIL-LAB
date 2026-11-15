#!/usr/bin/env python3
"""Small, metadata-grounded pilot of caption availability on actual test videos."""
from __future__ import annotations
import argparse
import json
from collections import Counter
from pathlib import Path
from acquire import run_video

def choose(videos: list[dict], limit: int) -> list[dict]:
    chosen=[]
    # Prioritize actual API caption=true metadata over arbitrary search order.
    # This is only a signal that captions might exist, NOT permission to read them.
    videos=sorted(videos,key=lambda v: (
        v.get("captions_metadata_flag") != "true",
        v.get("editorial_screening") != "priority_review_metadata",
        v.get("screening_status") != "priority_metadata_candidate"))
    for v in videos:
        if v.get("screening_status") != "priority_metadata_candidate":
            continue
        if v.get("provider") != "youtube" or v.get("category") not in {"foil","board"}:
            continue
        if not v.get("url") or not v.get("published_on"):
            continue
        chosen.append({"id":v["id"],"url":v["url"],"title":v["title"],
                       "publisher":v.get("publisher","YouTube"),
                       "language":"de",
                       "captions_metadata_flag":v.get("captions_metadata_flag"),
                       "video_duration_s":v.get("video_duration_s")})
        if len(chosen)>=limit:
            break
    return chosen

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--limit",type=int,default=4)
    args=p.parse_args()
    if not 1<=args.limit<=5:
        p.error("Probe limited to 1-5 videos")
    data=json.loads(args.input.read_text(encoding="utf-8"))
    videos=choose(data.get("videos",[]),args.limit)
    records=[]
    for video in videos:
        result=run_video(video,"probe")
        records.append({"id":video["id"],"title":video["title"],"url":video["url"],
                        "captions_metadata_flag":video.get("captions_metadata_flag"),
                        "probe_status":result["status"],
                        "reason":result.get("reason"),
                        "caption_listing_indicated":result.get("caption_listing_indicated",False),
                        "subtitle_transcript_obtained":False,
                        "video_fully_reviewed":False})
        print("CAPTION_PROBE "+json.dumps(records[-1],ensure_ascii=False))
    counts=Counter(item["probe_status"] for item in records)
    report={"schema_version":1,"videos_checked":len(records),
            "status_counts":dict(counts),"transcripts_obtained":0,"full_videos_analyzed":0,
            "note":"Availability probe only; it never downloads or interprets transcripts.",
            "records":records}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("CAPTION_PROBE_COUNTS "+json.dumps({"checked":len(records),**counts}))

if __name__=="__main__":
    main()
