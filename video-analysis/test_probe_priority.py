import importlib.util
import unittest
from pathlib import Path

spec=importlib.util.spec_from_file_location("probe_batch",Path(__file__).with_name("probe_batch.py"))
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def entry(identifier,flag):
    return {"id":identifier,"url":"https://www.youtube.com/watch?v="+identifier.removeprefix("youtube-"),
      "title":"Foil wingfoil test","publisher":"reviewer","provider":"youtube","category":"foil",
      "published_on":"2026-05-14","screening_status":"priority_metadata_candidate",
      "captions_metadata_flag":flag,"editorial_screening":"priority_review_metadata"}

class ProbePriorityTests(unittest.TestCase):
    def test_caption_true_goes_first(self):
        videos=[entry("youtube-a","false"),entry("youtube-b","true"),entry("youtube-c","false")]
        picked=m.choose(videos,2)
        self.assertEqual([v["id"] for v in picked],["youtube-b","youtube-a"])
        self.assertEqual(picked[0]["captions_metadata_flag"],"true")
    def test_scope_filter_preserved(self):
        rows=[entry("youtube-a","true"),entry("youtube-b","true")]
        rows[0]["screening_status"]="needs_manual_scope_review"
        self.assertEqual([v["id"] for v in m.choose(rows,3)],["youtube-b"])
if __name__=="__main__":unittest.main()
