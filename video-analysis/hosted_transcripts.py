#!/usr/bin/env python3
"""Optional, explicitly authorized hosted transcript pilot for FOIL LAB.

Requires TRANSCRIPT_API_KEY for https://transcriptapi.com/api/v2/youtube/transcript.
A YouTube Data API key is NOT a transcript key. This program NEVER guesses a
transcript or labels keyword matches as technical conclusions. By default it
does not call a paid endpoint; --allow-billable-requests is required.

The provider response is processed in memory and discarded. Only brief candidate
excerpts, segment counts, provenance and source URLs enter output JSON.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen

from analyze import COMPILED, timed_link

ENDPOINT="https://transcriptapi.com/api/v2/youtube/transcript"
ALLOW_HOSTS={"www.youtube.com","youtube.com","m.youtube.com","youtu.be"}
PILOT=(
 {"id":"youtube-DMlWjjIcwss","url":"https://www.youtube.com/watch?v=DMlWjjIcwss","title":"AFS Silk V2 650 / 750 / 950","publisher":"Pimpyourride","language":"fr"},
 {"id":"youtube-aiWA2W7hKos","url":"https://www.youtube.com/watch?v=aiWA2W7hKos","title":"Duotone Glide 3.0 D/LAB 825","publisher":"Gleiten.TV","language":"de"},
 {"id":"youtube-zesN5IeyRQM","url":"https://www.youtube.com/watch?v=zesN5IeyRQM","title":"KT Halo 670 / 800","publisher":"Gleiten.TV","language":"de"},
)
MAX_REQUESTS=3
MAX_EXCERPTS=24

def valid_url(url):
    p=urlparse(url)
    return p.scheme=="https" and p.hostname in ALLOW_HOSTS

def fetch_transcript(video, key, fetch=None):
    """Fetch timed chunks from the documented, fixed-domain REST API."""
    if not valid_url(video["url"]):
        raise ValueError("unsupported_video_host")
    if fetch is None:
        def fetch(url,headers):
            req=Request(url,headers=headers)
            with urlopen(req,timeout=35) as response:
                return json.loads(response.read(3_000_000).decode("utf-8"))
    url=ENDPOINT+"?"+urlencode({"video_url":video["url"],"language":video.get("language","de,en,fr")})
    return fetch(url,{"Authorization":"Bearer "+key,"Accept":"application/json"})

def normalize_segments(payload):
    """Only real timed segments are accepted; never invent timestamps."""
    if not isinstance(payload,dict):
        raise ValueError("invalid_provider_response")
    segments=payload.get("transcript")
    if not isinstance(segments,list):
        raise ValueError("no_timed_segments")
    normalized=[]
    for row in segments:
        if not isinstance(row,dict):
            continue
        start=row.get("start");duration=row.get("duration")
        text=row.get("text")
        if isinstance(start,bool) or isinstance(duration,bool):
            continue
        if not isinstance(start,(int,float)) or not isinstance(duration,(int,float)):
            continue
        if start<0 or duration<0 or start>86400 or duration>7200:
            continue
        if not isinstance(text,str) or not text.strip():
            continue
        normalized.append({"start_s":round(float(start),2),"end_s":round(float(start+duration),2),
                           "text":" ".join(text.split())})
    normalized.sort(key=lambda v:v["start_s"])
    if not normalized:
        raise ValueError("no_valid_timed_segments")
    return normalized

def analyze_payload(video,payload):
    segments=normalize_segments(payload)
    candidates=[]
    for cue in segments:
        categories=[name for name,regex in COMPILED.items() if regex.search(cue["text"])]
        if not categories:
            continue
        if len(candidates)<MAX_EXCERPTS:
            candidates.append({"at_s":cue["start_s"],"to_s":cue["end_s"],
                "link":timed_link(video["url"],int(cue["start_s"])),
                "categories":categories,"excerpt":cue["text"][:180],
                "status":"keyword_candidate_needs_human_validation",
                "size_tested":None,"performance_claim":None,
                "confidence":"unassessed"})
    digest=hashlib.sha256(json.dumps(segments,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
    return {"id":video["id"],"title":video["title"],"url":video["url"],
            "publisher":video["publisher"],"reported_language":payload.get("language"),
            "transcript_provenance":"transcriptapi_com_hosted_provider",
            "transcript_sha256":digest,"transcript_segments":len(segments),
            "technical_keyword_hits":sum(bool(any(r.search(c["text"]) for r in COMPILED.values())) for c in segments),
            "excerpts_retained":len(candidates),"candidates":candidates,
            "status":"timed_transcript_retrieved_keyword_analysis_only",
            "video_fully_watched":False,"validated_performance_scores":0,
            "performance_scores":None}

def run_pilot(key,authorized,max_requests, fetch=None):
    summary={"schema_version":1,"provider":"TranscriptAPI.com",
      "endpoint":"official_hosted_api","paid_requests_authorized":bool(authorized),
      "provider_api_key_configured":bool(key),"videos_attempted":0,
      "transcripts_obtained":0,"videos_fully_watched":0,"scores_updated":0,
      "results":[]}
    if not key:
        summary["status"]="not_configured_missing_TRANSCRIPT_API_KEY"
        return summary
    if not authorized:
        summary["status"]="skipped_billable_requests_not_authorized"
        return summary
    summary["status"]="attempted"
    for video in PILOT[:max_requests]:
        summary["videos_attempted"]+=1
        try:
            payload=fetch_transcript(video,key,fetch)
            result=analyze_payload(video,payload)
            summary["transcripts_obtained"]+=1
        except HTTPError as error:
            result={"id":video["id"],"status":"provider_http_error","http_status":error.code}
        except (URLError,TimeoutError,OSError):
            result={"id":video["id"],"status":"provider_network_error"}
        except ValueError as error:
            result={"id":video["id"],"status":"invalid_or_missing_timed_transcript","reason":str(error)}
        summary["results"].append(result)
    return summary

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output",type=Path,default=Path("video-index/hosted-transcript-pilot.json"))
    p.add_argument("--max-requests",type=int,default=1)
    p.add_argument("--allow-billable-requests",action="store_true")
    args=p.parse_args(argv)
    if not 1<=args.max_requests<=MAX_REQUESTS:
        p.error("Pilot maximum: 3 requests; intentionally capped")
    result=run_pilot(os.getenv("TRANSCRIPT_API_KEY"),args.allow_billable_requests,args.max_requests)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("HOSTED_TRANSCRIPT_PILOT "+json.dumps(
        {"status":result["status"],"videos_attempted":result["videos_attempted"],
         "transcripts_obtained":result["transcripts_obtained"],"scores_updated":0},ensure_ascii=False))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
