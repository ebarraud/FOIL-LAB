import json,tempfile,unittest
from pathlib import Path
from apply_reference_decisions import apply
from dashboard import build

class ReferenceDecisionsTests(unittest.TestCase):
    def test_idempotent_queue_and_explicit_metadata_limits(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            (root/'data/research').mkdir(parents=True)
            (root/'video-index').mkdir()
            videos=[{'video_id':v,'title':v,'analysis':'needs_qualification','collection':'new','integration':'pending'} for v in ('-htD7qNM7_k','qkxFEAlF1p0','WCiwij40Qr0')]
            (root/'data/research/progress.json').write_text(json.dumps({'videos':videos}))
            batch=root/'video-index/batch-103.json';batch.write_text(json.dumps({'results':[]}))
            first=apply(root);apply(root)
            self.assertEqual(len(json.loads(batch.read_text())['results']),1)
            self.assertEqual(len(first['decisions']),3)
            self.assertTrue(all(not d['content_verified'] and not d['transcript_analyzed'] for d in first['decisions']))
            rows={r['video_id']:r for r in build(root)['videos']}
            self.assertEqual(rows['qkxFEAlF1p0']['analysis'],'excluded_metadata')
            self.assertEqual(rows['WCiwij40Qr0']['analysis'],'related_reference')
            self.assertEqual(rows['WCiwij40Qr0']['related_source_id'],'lrW4o4H05tI')
            self.assertEqual(rows['-htD7qNM7_k']['analysis'],'awaiting_transcript')
            self.assertNotEqual(rows['qkxFEAlF1p0']['analysis'],'interpreted')

if __name__=='__main__':unittest.main()
