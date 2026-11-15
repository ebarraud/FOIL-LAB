#!/usr/bin/env python3
"""Free, anonymous, bounded pilot for genuine timestamped YouTube captions.

Uses only unauthenticated public REST endpoint of FreeTranscriptAPI.
No API keys, account credits, payments, video or audio downloads. Third-party
availability and access permissions may change. No full transcripts are
committed or logged. Outputs short keyword excerpt leads only.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

ENDPOINT="https://api.freetranscriptapi.com/v1/transcript"
PILOT=[
 ("DMlWjjIcwss","AFS Silk V2 650/750/950","fr"),
 ("aiWA2W7hKos","Duotone Glide 3.0 D/LAB 825","de"),
 ("zesN5IeyRQM","KT Halo 670/800","de"),
]
PATTERNS={
 "takeoff":re.compile(r"d[eé]coll|take.?off|lift.?off|fr[uü]h|angleit|abheb",re.I),
 "glide":re.compile(r"gliss|gleit|glide|efficien|drag|pump|vitesse|speed",re.I),
 "carving":re.compile(r"carv|virage|turn|kurven|surf|maniab",re.I),
 "control":re.compile(r"stabil|contr[oô]l|control|pitch|tangage|kontroll|clapot|chop",re.I),
}
def parse(payload):
    if not isinstance(payload,dict):raise ValueError("invalid_payload")
    segments=payload.get("transcript")
    if not isinstance(segments,list):raise ValueError("no_segment_array")
    found=[]
    for item in segments:
        if not isinstance(item,dict):continue
        start=item.get("start");duration=item.get("duration");txt=item.get("text")
        if isinstance(start,bool) or not isinstance(start,(int,float)) or start<0:continue
        if isinstance(duration,bool) or not isinstance(duration,(int,float)) or duration<0:continue
        if not isinstance(txt,str) or not txt.strip():continue
        found.append({"at_s":float(start),"to_s":float(start+duration),
                      "text":" ".join(txt.split())})
    if not found:raise ValueError("no_timed_speech")
    return sorted(found,key=lambda x:x["at_s"])
def summarize(video,payload):
    segments=parse(payload)
    leads=[]
    hits=0
    for item in segments:
        categories=[key for key,rx in PATTERNS.items() if rx.search(item["text"])]
        if not categories:continue
        hits+=1
        if len(leads)<18:
            leads.append({"at_s":item["at_s"],"categories":categories,
                          "short_excerpt":item["text"][:130],
                          "link":"https://www.youtube.com/watch?v="+video[0]+"&t="+str(int(item["at_s"]))+"s",
                          "status":"keyword_candidate_not_validated"})
    digest=hashlib.sha256(json.dumps(segments,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    return {"video_id":video[0],"title":video[1],"language":payload.get("language"),
      "status":"timed_transcript_received","segment_count":len(segments),
      "technical_keyword_segments":hits,"transcript_sha256":digest,
      "candidate_passages":leads,"video_fully_watched":False,
      "performance_scores_generated":0}
def default_fetch(video):
    url=ENDPOINT+"?"+urllib.parse.urlencode({"video_url":video[0],"lang":video[2]})
    req=urllib.request.Request(url,headers={"User-Agent":"FOIL-LAB-Research/1.0","Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=35) as response:
        return json.loads(response.read(2_000_000).decode("utf-8"))
def run(fetch=default_fetch,limit=3):
    output={"schema_version":1,"access_method":"unauthenticated_no_key_no_credits",
     "provider":"FreeTranscriptAPI.com","attempted":0,"transcripts_obtained":0,
     "videos_watched":0,"notes_updated":0,"results":[]}
    for video in PILOT[:limit]:
        output["attempted"]+=1
        try:
            payload=fetch(video)
            result=summarize(video,payload)
            output["transcripts_obtained"]+=1
        except Exception as exc:
            # Log exception class only. No API token or transcript response exposed.
            result={"video_id":video[0],"title":video[1],"status":"unavailable_or_blocked",
                    "failure_type":type(exc).__name__}
        output["results"].append(result)
    return output
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,default=Path("video-index/free-transcript-pilot.json"))
    parser.add_argument("--limit",type=int,choices=(1,2,3),default=3)
    args=parser.parse_args()
    result=run(limit=args.limit)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("FREE_TRANSCRIPT_RESULT "+json.dumps({
      "attempted":result["attempted"],"transcripts_obtained":result["transcripts_obtained"],
      "outcomes":[{"video_id":r["video_id"],"status":r["status"],
                   "segment_count":r.get("segment_count"),
                   "technical_keyword_segments":r.get("technical_keyword_segments"),
                   "failure_type":r.get("failure_type")} for r in result["results"]]}))
if __name__=="__main__":main()
