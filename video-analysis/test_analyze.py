import unittest
from pathlib import Path
import importlib.util

MODULE = Path(__file__).with_name("analyze.py")
spec = importlib.util.spec_from_file_location("foil_lab_video", MODULE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

VIDEO = {
    "id": "test-foil", "title": "Foil test", "url": "https://www.youtube.com/watch?v=123ABC",
    "publisher": "Test studio"
}

class VideoAnalysisTests(unittest.TestCase):
    def test_srt_french_extracts_technical_candidates_without_scores(self):
        srt = ("1\n00:00:05,000 --> 00:00:07,000\n"
               "Le décollage est rapide dans ces conditions.\n\n"
               "2\n00:00:10,000 --> 00:00:12,500\n"
               "Le carving reste fluide.\n")
        r = module.extract(VIDEO, srt, "fr", "test.srt")
        self.assertEqual(len(r["candidates"]), 2)
        self.assertIn("takeoff", r["candidates"][0]["categories"])
        self.assertIn("carving", r["candidates"][1]["categories"])
        self.assertEqual(r["candidates"][0]["at_s"], 5.0)
        self.assertIn("t=5s", r["candidates"][0]["link"])
        self.assertIsNone(r["performance_scores"])
        self.assertFalse(r["video_fully_watched"])

    def test_vtt_german_and_html_markup(self):
        vtt = ("WEBVTT\n\n00:00:01.500 --> 00:00:03.000 align:start\n"
               "<c>Sehr kontrollierbar in den Kurven.</c>\n\n"
               "00:00:04.000 --> 00:00:06.000\nDas Gleitverhalten ist gut.\n")
        r = module.extract(VIDEO, vtt, "de", "test.vtt")
        self.assertEqual(len(r["candidates"]), 2)
        self.assertIn("control", r["candidates"][0]["categories"])
        self.assertIn("carving", r["candidates"][0]["categories"])
        self.assertIn("glide", r["candidates"][1]["categories"])

    def test_no_guess_from_subtitle_without_technical_passage(self):
        srt = "1\n00:00:00,000 --> 00:00:02,000\nBonjour et bienvenue.\n"
        r = module.extract(VIDEO, srt, "fr", "test.srt")
        self.assertEqual(r["candidates"], [])
        self.assertEqual(r["transcript_cues"], 1)

    def test_invalid_transcript_rejected(self):
        with self.assertRaises(ValueError):
            module.extract(VIDEO, "No timestamps", "fr", "bad.vtt")

    def test_non_youtube_link_not_given_fake_timestamps(self):
        self.assertEqual(module.timed_link("https://gleiten.tv/video/example", 12),
                         "https://gleiten.tv/video/example")

if __name__ == "__main__":
    unittest.main()
