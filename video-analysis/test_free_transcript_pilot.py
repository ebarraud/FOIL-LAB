import importlib.util
import pathlib
import unittest
spec=importlib.util.spec_from_file_location("free_trial",pathlib.Path(__file__).with_name("free_transcript_pilot.py"))
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
class Trial(unittest.TestCase):
 def test_valid_segments_only(self):
  out=mod.parse({"transcript":[{"start":1.2,"duration":2,"text":" Gute Gleitphase "},{"start":-1,"duration":1,"text":"no"},{"start":3,"duration":2,"text":"turns"}]})
  self.assertEqual(len(out),2)
  self.assertEqual(out[0]["text"],"Gute Gleitphase")
 def test_no_fake_transcript(self):
  with self.assertRaises(ValueError):mod.parse({"transcript":[]})
 def test_mock_success(self):
  result=mod.run(lambda video:{"language":"de","transcript":[{"start":12,"duration":4,"text":"Der Start ist leicht und die Glide gut"}]},1)
  self.assertEqual(result["transcripts_obtained"],1)
  self.assertEqual(result["notes_updated"],0)
  self.assertEqual(result["results"][0]["candidate_passages"][0]["status"],"keyword_candidate_not_validated")
 def test_provider_failure_is_reported(self):
  def blocked(_):raise TimeoutError()
  result=mod.run(blocked,1)
  self.assertEqual(result["transcripts_obtained"],0)
  self.assertEqual(result["results"][0]["failure_type"],"TimeoutError")
if __name__=="__main__":unittest.main()
