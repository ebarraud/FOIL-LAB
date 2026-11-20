import json, re, subprocess, sys, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / 'data/research'


class RideFeelTest(unittest.TestCase):
    def test_annotations_reference_existing_claims_and_grid(self):
        ann = json.loads((D / 'ride_feel_annotations.json').read_text(encoding='utf-8'))
        reviews = {r['video_id']: r for r in json.loads((D / 'transcript_reviews.json').read_text(encoding='utf-8'))['reviews']}
        codes = set(ann['grid']['foil']) | set(ann['grid']['board'])
        for a in ann['annotations']:
            self.assertIn(a['video_id'], reviews)
            self.assertLess(a['claim_index'], len(reviews[a['video_id']]['claims']))
            self.assertTrue(a['criteria'])
            for c in a['criteria']:
                self.assertIn(c['c'], codes)
                self.assertIn(c['pol'], '+-~')
                self.assertIn(c['int'], (1, 2))

    def test_summary_is_reproducible(self):
        before = (D / 'ride_feel_summary.json').read_text(encoding='utf-8')
        subprocess.run([sys.executable, str(ROOT / 'video-analysis/ride_feel_report.py')], check=True, capture_output=True)
        self.assertEqual(before, (D / 'ride_feel_summary.json').read_text(encoding='utf-8'))
        s = json.loads(before)
        for fam in s['families'].values():
            for c in fam['criteria'].values():
                if c['statut'] == 'concordant':
                    self.assertGreaterEqual(c['sources'], 2)


if __name__ == '__main__':
    unittest.main()
