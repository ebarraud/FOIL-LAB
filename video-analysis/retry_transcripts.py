"""Resume failed acquisition slowly; stop on provider throttling or outage."""
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError
from free_transcript_pilot import default_fetch, summarize, write_cache, parse, transcript_digest

def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    temporary.replace(path)

def main():
    source = Path('video-index/batch-103.json')
    data = json.loads(source.read_text(encoding='utf-8'))
    history_path = Path('video-index/retry-history.json')
    history = json.loads(history_path.read_text(encoding='utf-8')) if history_path.exists() else {'attempts':[]}
    # Only explicit language evidence from the original pilot, no title guessing.
    languages = {'aiWA2W7hKos':'de', 'zesN5IeyRQM':'de', 'DMlWjjIcwss':'fr'}
    pending = [r for r in data['results'] if r['video_id'] in languages and r.get('language') != languages[r['video_id']]]
    pending += [r for r in data['results'] if r['status']!='timed_transcript_received' and r not in pending]
    stopped = None
    for old in pending:
        vid = old['video_id']
        language = languages.get(vid, '')
        attempt = {'video_id':vid, 'requested_language':language or 'auto', 'at_utc':datetime.now(timezone.utc).isoformat()}
        try:
            payload = default_fetch((vid, old['title'], language))
            result = summarize((vid, old['title'], language), payload)
            write_cache(Path('.transcript-cache')/(language or 'auto'), (vid,old['title'],language), payload)
            result['requested_language'] = language or 'auto'
            result['previous_language'] = old.get('language')
            data['results'][data['results'].index(old)] = result
            attempt.update(status='timed_transcript_received', returned_language=payload.get('language'))
        except HTTPError as exc:
            attempt.update(status='http_error', http_status=exc.code, retry_after=exc.headers.get('Retry-After'))
            old['last_retry'] = attempt.copy()
            if exc.code in (401,403,429) or exc.code>=500:
                stopped = 'provider_access_or_rate_limit' if exc.code<500 else 'provider_outage'
        except Exception as exc:
            attempt.update(status='error', failure_type=type(exc).__name__)
        history['attempts'].append(attempt)
        history['stopped_reason'] = stopped
        save(history_path,history)
        save(source,data)
        public = {k:v for k,v in data.items() if k!='results'}
        public['transcripts_obtained'] = sum(r['status']=='timed_transcript_received' for r in data['results'])
        public['updated_at_utc'] = attempt['at_utc']
        public['retry_status'] = stopped or 'in_progress'
        public['retry_history'] = history
        public['results'] = [{k:r.get(k) for k in ('video_id','title','status','language','segment_count','failure_type','last_retry','requested_language')} for r in data['results']]
        save(Path('research/BATCH_STATUS.json'),public)
        print(json.dumps(attempt),flush=True)
        if stopped: break
        time.sleep(5)

if __name__=='__main__': main()
