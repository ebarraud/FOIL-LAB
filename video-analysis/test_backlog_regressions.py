import json,os,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError
import batch_transcripts
from dashboard import build
class BacklogRegressionTests(unittest.TestCase):
 def test_batch_stops_after_first_rate_limit(self):
  previous=Path.cwd()
  with tempfile.TemporaryDirectory() as tmp:
   try:
    os.chdir(tmp)
    Path('input.json').write_text(json.dumps({'videos':[{'url':'https://www.youtube.com/watch?v='+v,'title':v} for v in ['aaaaaaaaaaa','bbbbbbbbbbb']]}))
    with patch.object(sys,'argv',['batch','--input','input.json','--output','report.json','--cache-dir','cache']),patch.object(batch_transcripts,'default_fetch',side_effect=HTTPError('https://example.com',429,'limited',{'Retry-After':'2678'},None)) as fetch,patch.object(batch_transcripts,'build'),patch.object(batch_transcripts.time,'sleep'):
     batch_transcripts.main()
    self.assertEqual(fetch.call_count,1)
    self.assertEqual(json.loads(Path('report.json').read_text())['processed'],1)
    self.assertIn('retry_not_before_utc',json.loads(Path('research/BATCH_STATUS.json').read_text()))
   finally:os.chdir(previous)
 def test_dashboard_preserves_publisher_and_rejects_wake_as_wing(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp)
   def save(name,data):
    p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data),encoding='utf8')
   save('data/research/progress.json',{'videos':[{'video_id':'aaaaaaaaaaa','publisher':'Test publisher','discovered_on':'2026-11-01'}]})
   save('video-index/batch-103.json',{'results':[{'video_id':'aaaaaaaaaaa','title':'Wake foil','status':'timed_transcript_received'}]})
   save('data/research/transcript_reviews.json',{'reviews':[{'video_id':'aaaaaaaaaaa','claims':[],'scope':'wake_only_not_wing_test'}]})
   build(root)
   v=json.loads((root/'data/research/progress.json').read_text(encoding='utf8'))['videos'][0]
   self.assertEqual(v['publisher'],'Test publisher')
   self.assertEqual(v['discovered_on'],'2026-11-01')
   self.assertEqual(v['review_kind'],'out_of_scope')
