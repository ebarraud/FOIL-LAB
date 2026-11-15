import json
import tempfile
import unittest
from pathlib import Path
from dashboard import build

class DashboardTests(unittest.TestCase):
    def test_discovery_does_not_erase_collected_or_claim_analysis(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            for p in ('data/research','video-index','research'): (root/p).mkdir(parents=True,exist_ok=True)
            (root/'data/research/progress.json').write_text(json.dumps({'videos':[{'video_id':'aaaaaaaaaaa','title':'Existing','collection':'timed_transcript_received','analysis':'queued','integration':'pending','claims':0}]}))
            (root/'video-index/youtube.json').write_text(json.dumps({'videos':[{'url':'https://www.youtube.com/watch?v=aaaaaaaaaaa','title':'Duplicate'},{'url':'https://www.youtube.com/watch?v=bbbbbbbbbbb','title':'New'}]}))
            d=build(root)
            self.assertEqual(len(d['videos']),2)
            self.assertEqual(d['videos'][0]['collection'],'timed_transcript_received')
            self.assertEqual(d['videos'][1]['analysis'],'needs_qualification')
            self.assertEqual(d['videos'][1]['claims'],0)

if __name__=='__main__':unittest.main()
