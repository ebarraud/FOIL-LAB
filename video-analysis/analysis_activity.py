"""Record real assistant work sessions; active markers expire automatically."""
import argparse
from datetime import datetime,timezone,timedelta
from pathlib import Path
import json
from dashboard import build

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('video_id')
    p.add_argument('status',choices=['in_progress','paused','completed'])
    p.add_argument('--step',required=True)
    a=p.parse_args()
    path=Path('data/research/analysis_activity.json')
    d=json.loads(path.read_text(encoding='utf-8')) if path.exists() else {'tasks':[]}
    now=datetime.now(timezone.utc)
    previous=next((t for t in d['tasks'] if t['video_id']==a.video_id),{})
    task={'video_id':a.video_id,'status':a.status,'step':a.step,
          'started_at_utc':previous.get('started_at_utc',now.isoformat()),
          'updated_at_utc':now.isoformat(),'expires_at_utc':(now+timedelta(minutes=20)).isoformat()}
    d['tasks']=[t for t in d['tasks'] if t['video_id']!=a.video_id]+[task]
    path.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    build()

if __name__=='__main__':main()
