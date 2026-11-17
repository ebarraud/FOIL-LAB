#!/usr/bin/env python3
"""YouTube public video metadata audit (NO transcript access).

Uses videos.list in batches of <=50 with the same GitHub Actions YouTube API key.
Public video descriptions/durations and contentDetails.caption are discovery
signals only: neither captions nor full audiovisual contents are retrieved.
"""
from __future__ import annotations
import argparse
import json
import os
import re
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path
from urllib.error import HTTPError

LENGTH = re.compile(r"^P(?:(\d+)D)?(?:T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?)?$")
NEGATIVE = re.compile(r"\b(parawing only|parawing test|only parawing|pocket rocket|"
                      r"wing review|wing test|wing only|kitefoil only|"
                      r"how to|tutorial|unboxing|trailer|podcast|"
                      r"montage|how to wingfoil|lesson)\b", re.I)
DESCRIPTION_HINT = re.compile(r"\b(foil|wingfoil|wingboard|midlength|hydrofoil|"
                              r"front wing|test|review|essai|praxistest|vergleich)\b",re.I)

def duration_seconds(raw: str) -> int | None:
    match=LENGTH.fullmatch(raw)
    if not match:
        return None
    d,h,m,s=(int(value or 0) for value in match.groups())
    return d*86400+h*3600+m*60+s

def video_details(key:str, ids:list[str], fetch=None):
    """One lightweight YouTube videos.list request for up to 50 video IDs."""
    if len(ids)>50:
        raise ValueError("Maximum 50 video IDs per request")
    if not ids:
        return []
    params={"part":"snippet,contentDetails,status","id":",".join(ids),"key":key}
    url="https://www.googleapis.com/youtube/v3/videos?"+urllib.parse.urlencode(params)
    if fetch is None:
        def fetch(u):
            request=urllib.request.Request(u,headers={"User-Agent":"FOIL-LAB-Research/1"})
            with urllib.request.urlopen(request,timeout=25) as response:
                return response.read(3_000_000).decode("utf-8")
    response=json.loads(fetch(url))
    if not isinstance(response,dict) or not isinstance(response.get("items"),list):
        raise ValueError("Invalid YouTube videos.list response")
    return response["items"]

def enrich(rows:list[dict], key:str|None, fetch=None):
    records=[dict(row) for row in rows]
    ids=[row["id"].removeprefix("youtube-") for row in records
         if row.get("provider")=="youtube" and row.get("id","").startswith("youtube-")]
    lookup={}
    errors=[]
    calls=0
    if key:
        for start in range(0,len(ids),50):
            batch=ids[start:start+50]
            try:
                calls+=1
                for entry in video_details(key,batch,fetch):
                    lookup[entry.get("id")]=entry
            except Exception as error:
                errors.append({"batch":start//50+1,"error":type(error).__name__,"http_status":getattr(error,"code",None)})
                if isinstance(error,HTTPError) and (error.code in (401,403,429) or error.code>=500):break
    for row in records:
        original_id=row.get("id","").removeprefix("youtube-")
        info=lookup.get(original_id)
        row["metadata_enrichment"]="not_requested" if not key else ("api_confirmed" if info else "unavailable_or_failed")
        row["source_video_description_status"]="not_obtained"
        row["captions_metadata_flag"]=None
        row["video_duration_s"]=None
        row["evidence_type"]="metadata_only_no_transcript"
        row["technical_claims_from_video"]=[]
        row["transcript_acquired"]=False
        row["video_fully_watched"]=False
        if not info:
            row["editorial_screening"]="needs_metadata_or_manual_review"
            continue
        snippet=info.get("snippet") or {}
        details=info.get("contentDetails") or {}
        status=info.get("status") or {}
        description=snippet.get("description","")
        row["video_duration_s"]=duration_seconds(details.get("duration",""))
        # Note: YouTube contentDetails.caption is NOT an authorized transcript download.
        caption=details.get("caption")
        row["captions_metadata_flag"]=caption if isinstance(caption,str) else None
        row["youtube_public_status"]=status.get("privacyStatus")
        row["source_video_description_status"]="available_as_public_metadata" if description else "empty"
        row["description_length"]=len(description)
        row["video_details_title"]=snippet.get("title")
        row["channel_id"]=snippet.get("channelId")
        row["publisher"]=snippet.get("channelTitle") or row.get("publisher")
        row["description_scope_hint"]=bool(DESCRIPTION_HINT.search(description[:1500]))
        title=row.get("title","")
        if NEGATIVE.search(title) or NEGATIVE.search(description[:250]):
            row["editorial_screening"]="potentially_out_of_scope"
        elif row["video_duration_s"] is not None and row["video_duration_s"]<120:
            row["editorial_screening"]="short_format_requires_review"
        elif row.get("screening_status")=="priority_metadata_candidate":
            row["editorial_screening"]="priority_review_metadata"
        else:
            row["editorial_screening"]="needs_manual_scope_review"
    counter=Counter(x["editorial_screening"] for x in records)
    caption_info=Counter(x["captions_metadata_flag"] for x in records)
    return {
        "schema_version":1, "source_items":len(records),
        "videos_list_api_calls":calls,
        "details_api_confirmed":sum(x["metadata_enrichment"]=="api_confirmed" for x in records),
        "screening_counts":dict(counter),
        "captions_metadata_flags":{str(k):v for k,v in caption_info.items()},
        "errors":errors, "full_video_transcripts_obtained":0,
        "audio_or_video_downloaded":False,
        "performance_scores_generated":0,
        "warning":"YouTube contentDetails.caption is only a public metadata flag. A true value neither proves retrievable subtitles nor grants transcript access.",
        "videos":records
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    raw=json.loads(args.input.read_text(encoding="utf-8"))
    key=os.getenv('YOUTUBE_API_KEY')
    gate=Path('data/research/youtube_discovery_status.json')
    cooldown=json.loads(gate.read_text(encoding='utf-8')).get('retry_not_before_utc') if gate.exists() else None
    from datetime import datetime,timezone
    active=bool(cooldown and datetime.now(timezone.utc)<datetime.fromisoformat(cooldown))
    result=enrich(raw.get('videos',[]),None if active else key)
    if active:result.update(stopped_reason='youtube_cooldown_active',retry_not_before_utc=cooldown)
    result["window_start"]=raw.get("window_start")
    result["window_end"]=raw.get("window_end")
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("YOUTUBE_DETAILS "+json.dumps({name:result[name] for name in (
        "source_items","videos_list_api_calls","details_api_confirmed",
        "screening_counts","captions_metadata_flags","errors",
        "full_video_transcripts_obtained")},ensure_ascii=False))
    for row in [r for r in result["videos"] if r.get("editorial_screening")=="potentially_out_of_scope"][:15]:
        print("OUT_OF_SCOPE_CANDIDATE "+json.dumps({"title":row.get("title"),"url":row.get("url")},ensure_ascii=False))

if __name__=="__main__":
    main()
