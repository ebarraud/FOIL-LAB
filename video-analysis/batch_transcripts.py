"""Sequential free transcript collection with atomic checkpoints and local cache."""
import argparse
import json
import re
import time
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from free_transcript_pilot import default_fetch, summarize, write_cache, read_local
from dashboard import build

def queue(data):
    found = {}
    for row in data.get('videos', []):
        url = urlparse(row.get('url', ''))
        vid = parse_qs(url.query).get('v', [''])[0]
        if url.hostname not in ('youtube.com', 'www.youtube.com') or not re.fullmatch(r'[A-Za-z0-9_-]{11}', vid):
            continue
        found.setdefault(vid, (vid, row.get('title', vid), row.get('language') or ''))
    return list(found.values())

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--cache-dir', type=Path, required=True)
    ap.add_argument('--limit', type=int, default=200)
    args = ap.parse_args()
    if not 1 <= args.limit <= 200: ap.error('limit must be 1–200')
    videos = queue(json.loads(args.input.read_text(encoding='utf-8')))[:args.limit]
    previous = json.loads(args.output.read_text(encoding='utf-8')) if args.output.exists() else {}
    results = {r['video_id']:r for r in previous.get('results', [])}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    for video in videos:
        if video[0] in results: continue
        try:
            cached = args.cache_dir / (video[0]+'.json')
            payload = read_local(args.cache_dir, video) if cached.exists() else default_fetch(video)
            result = summarize(video, payload)
            write_cache(args.cache_dir, video, payload)
        except Exception as exc:
            result = {'video_id':video[0], 'title':video[1], 'status':'unavailable_or_blocked', 'failure_type':type(exc).__name__}
        results[video[0]] = result
        selected = [results[v[0]] for v in videos if v[0] in results]
        report = {'schema_version':1, 'inventory_count':len(videos), 'processed':len(selected), 'transcripts_obtained':sum(r['status']=='timed_transcript_received' for r in selected), 'performance_scores_generated':0, 'semantic_claims_validated':0, 'results':selected}
        temporary = args.output.with_suffix('.tmp')
        temporary.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        temporary.replace(args.output)
        build()
        print(json.dumps({k:v for k,v in report.items() if k!='results'}), flush=True)
        time.sleep(1)

if __name__ == '__main__': main()
