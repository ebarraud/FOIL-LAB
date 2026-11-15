import importlib.util
import unittest
from pathlib import Path

spec=importlib.util.spec_from_file_location("video_analyze", Path(__file__).with_name("analyze.py"))
a=importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)

class CopiedYouTubeTranscriptTests(unittest.TestCase):
    def test_timestamp_and_inline_text(self):
        cues,fmt=a.parse_transcript("0:15 On décolle tôt\n0:22 Le pumping est facile\n1:04 Bonne glisse")
        self.assertEqual(fmt,"youtube_timestamped_copy")
        self.assertEqual(len(cues),3)
        self.assertEqual(cues[0]["start_s"],15)
        self.assertEqual(cues[0]["end_s"],22)
        self.assertEqual(cues[2]["end_s"],64)

    def test_two_line_timestamp_format(self):
        cues,fmt=a.parse_transcript("0:01\nDer Start ist einfach\n0:06\nKurven werden ruhig")
        self.assertEqual(len(cues),2)
        self.assertEqual(cues[0]["text"],"Der Start ist einfach")
        self.assertEqual(cues[0]["end_s"],6)

    def test_explicit_hours_and_multiline_content(self):
        cues,_=a.parse_transcript("00:01:01\nExcellent glide\nwhen pumping\n00:01:08\nGood control")
        self.assertEqual(cues[0]["start_s"],61)
        self.assertIn("when pumping",cues[0]["text"])

    def test_rejects_unaligned_text(self):
        with self.assertRaises(ValueError):
            a.parse_transcript("glide control carving with no time codes")

    def test_preserves_normal_vtt(self):
        cues,fmt=a.parse_transcript("WEBVTT\n\n00:01.000 --> 00:02.000\nBonne glisse")
        self.assertEqual(fmt,"srt_or_webvtt")
        self.assertEqual(cues[0]["start_s"],1)

    def test_extract_remains_unscored_and_sourced(self):
        video={"id":"youtube-sample","url":"https://www.youtube.com/watch?v=abc123",
               "title":"Test foil","publisher":"Tester"}
        result=a.extract(video,"0:01 Bonne glisse\n0:05 Super carving","fr","copied.txt")
        self.assertEqual(result["transcript_format"],"youtube_timestamped_copy")
        self.assertEqual(result["transcript_cues"],2)
        self.assertIsNone(result["performance_scores"])
        self.assertFalse(result["video_fully_watched"])
        self.assertTrue(result["candidates"][0]["link"].endswith("t=1s"))

if __name__=="__main__":
    unittest.main()
