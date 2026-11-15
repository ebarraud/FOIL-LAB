import importlib.util
import json
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location("enrich_metadata",Path(__file__).with_name("enrich_metadata.py"))
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class MetadataEnrichmentTests(unittest.TestCase):
    def test_duration(self):
        self.assertEqual(mod.duration_seconds("PT13M22S"),802)
        self.assertEqual(mod.duration_seconds("PT58S"),58)
        self.assertEqual(mod.duration_seconds("P1DT2H3M4S"),93784)
        self.assertIsNone(mod.duration_seconds("bad"))
    def test_keyless_is_marked(self):
        rows=[dict(id="youtube-test",title="Wingfoil front foil review",provider="youtube",category="foil")]
        report=mod.enrich(rows,None)
        self.assertEqual(report["videos_list_api_calls"],0)
        self.assertEqual(report["full_video_transcripts_obtained"],0)
        self.assertEqual(report["videos"][0]["metadata_enrichment"],"not_requested")
    def test_caption_flag_not_transcript(self):
        sample={"items":[{"id":"abc123","snippet":{"title":"Wingfoil foil test",
          "description":"In this wingfoil review we compare foils","channelId":"c1"},
          "contentDetails":{"duration":"PT8M12S","caption":"true"},
          "status":{"privacyStatus":"public"}}]}
        calls=[]
        def fetch(url):
            calls.append(url)
            self.assertIn("/videos?",url)
            return json.dumps(sample)
        v={"id":"youtube-abc123","title":"Wingfoil foil test","provider":"youtube",
           "screening_status":"priority_metadata_candidate"}
        report=mod.enrich([v],"fake-key",fetch)
        self.assertEqual(len(calls),1)
        self.assertEqual(report["details_api_confirmed"],1)
        self.assertEqual(report["videos"][0]["video_duration_s"],492)
        self.assertEqual(report["videos"][0]["captions_metadata_flag"],"true")
        self.assertFalse(report["videos"][0]["transcript_acquired"])
        self.assertEqual(report["videos"][0]["technical_claims_from_video"],[])
        self.assertEqual(report["videos"][0]["editorial_screening"],"priority_review_metadata")
    def test_pocket_rocket_is_flagged(self):
        sample={"items":[{"id":"a","snippet":{"title":"Ozone Pocket Rocket V2 Parawing Test","description":"Parawing test"},
                          "contentDetails":{"duration":"PT12M2S","caption":"false"}}]}
        report=mod.enrich([{"id":"youtube-a","provider":"youtube","title":"Ozone Pocket Rocket V2 Parawing Test"}],
                            "key",lambda _:json.dumps(sample))
        self.assertEqual(report["screening_counts"]["potentially_out_of_scope"],1)
    def test_short_not_excluded_without_review(self):
        sample={"items":[{"id":"a","snippet":{"title":"Foil board review","description":""},
                          "contentDetails":{"duration":"PT42S"}}]}
        v={"id":"youtube-a","provider":"youtube","title":"Foil board review","screening_status":"priority_metadata_candidate"}
        report=mod.enrich([v],"key",lambda _:json.dumps(sample))
        self.assertEqual(report["videos"][0]["editorial_screening"],"short_format_requires_review")
        self.assertEqual(len(report["videos"]),1)
    def test_batch_limit(self):
        with self.assertRaises(ValueError):mod.video_details("key",["x"]*51)
if __name__=="__main__":unittest.main()
