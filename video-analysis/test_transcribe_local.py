import importlib.util
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest

spec=importlib.util.spec_from_file_location("local_asr",Path(__file__).with_name("transcribe_local.py"))
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class Engine:
    def transcribe(self,path,**options):
        self.options=options
        return iter([SimpleNamespace(start=2.1,end=5.4,text="  Der Start ist leicht "),
                     SimpleNamespace(start=5.5,end=8.2,text="  The glide is excellent.")]),None

class LocalAsrTests(unittest.TestCase):
    def test_srt_output(self):
        result,count=m.render_srt([SimpleNamespace(start=1,end=3,text="Bonjour!")])
        self.assertIn("00:00:01,000 --> 00:00:03,000",result)
        self.assertEqual(count,1)
    def test_sample_pipeline_injection(self):
        engine=Engine()
        srt,count=m.transcribe(Path("/tmp/not-a-real-file"),language="de",
                                model_size="tiny",engine=engine)
        self.assertEqual(count,2)
        self.assertIn("Der Start ist leicht",srt)
        self.assertEqual(engine.options["language"],"de")
    def test_invalid_segments_not_invented(self):
        rows=[SimpleNamespace(start=0,end=1,text=""),
              SimpleNamespace(start=6,end=5,text="reverse"),
              SimpleNamespace(start=8,end=9,text="Good carving.")]
        text,count=m.render_srt(rows)
        self.assertEqual(count,1)
        self.assertNotIn("reverse",text)
    def test_negative_timestamp_not_accepted(self):
        with self.assertRaises(ValueError):
            m.fmt_srt(-1)
    def test_no_audio_no_transcript(self):
        with self.assertRaises(ValueError):
            m.render_srt([])
if __name__=="__main__":unittest.main()
