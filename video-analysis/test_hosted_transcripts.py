import importlib.util
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).parent))
spec=importlib.util.spec_from_file_location("hosted_transcripts",Path(__file__).with_name("hosted_transcripts.py"))
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)

class HostedTranscriptTests(unittest.TestCase):
    def test_no_key_means_no_paid_calls(self):
        def not_called(*args):
            self.fail("Must not fetch")
        result=mod.run_pilot(None,True,3,not_called)
        self.assertEqual(result["videos_attempted"],0)
        self.assertEqual(result["status"],"not_configured_missing_TRANSCRIPT_API_KEY")

    def test_authorization_required_even_with_key(self):
        result=mod.run_pilot("test-key",False,3,lambda *args:self.fail("Must not fetch"))
        self.assertEqual(result["status"],"skipped_billable_requests_not_authorized")
        self.assertEqual(result["videos_attempted"],0)

    def test_valid_timestamped_provider_segments(self):
        def fetch(url,headers):
            self.assertTrue(url.startswith(mod.ENDPOINT))
            self.assertIn("video_url=",url)
            self.assertEqual(headers["Authorization"],"Bearer fake-secret")
            return {"language":"fr","transcript":[
                {"start":14.2,"duration":3.2,"text":"  Le décollage est bien progressif. "},
                {"start":20.0,"duration":2.3,"text":"Le pumping me semble facile"},
                {"start":23.0,"duration":1.1,"text":"Mais pas rapide."}]}
        result=mod.run_pilot("fake-secret",True,1,fetch)
        self.assertEqual(result["transcripts_obtained"],1)
        self.assertEqual(result["videos_attempted"],1)
        claim=result["results"][0]
        self.assertEqual(claim["transcript_segments"],3)
        self.assertEqual(claim["technical_keyword_hits"],2)
        self.assertEqual(len(claim["candidates"]),2)
        self.assertIn("t=14s",claim["candidates"][0]["link"])
        self.assertIsNone(claim["candidates"][0]["performance_claim"])
        self.assertEqual(result["scores_updated"],0)

    def test_plain_text_without_timestamps_is_rejected(self):
        with self.assertRaisesRegex(ValueError,"no_timed_segments"):
            mod.normalize_segments({"transcript":"Text with no times"})

    def test_no_leak_of_secret_in_report(self):
        result=mod.run_pilot("confidential-secret",True,1,
            lambda url,headers:{"transcript":[{"start":1,"duration":1,"text":"Easy glide."}]})
        import json
        self.assertNotIn("confidential-secret",json.dumps(result))

    def test_invalid_timestamp_not_accepted(self):
        with self.assertRaisesRegex(ValueError,"no_valid_timed_segments"):
            mod.normalize_segments({"transcript":[{"start":-1,"duration":5,"text":"Glide"}]})

    def test_reject_non_youtube_host(self):
        with self.assertRaises(ValueError):
            mod.fetch_transcript({"url":"https://example.com/test"},"secret",lambda *a:None)
if __name__=="__main__":unittest.main()
