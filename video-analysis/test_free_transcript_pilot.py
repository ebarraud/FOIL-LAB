import importlib.util
import json
import math
import pathlib
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location(
    "free_trial", pathlib.Path(__file__).with_name("free_transcript_pilot.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def payload(*texts):
    return {"language": "fr", "transcript": [
        {"start": index * 3, "duration": 2, "text": text}
        for index, text in enumerate(texts)]}


class Trial(unittest.TestCase):
    def test_valid_segments_only(self):
        out = mod.parse({"transcript": [
            {"start": 1.2, "duration": 2, "text": " Gute Gleitphase "},
            {"start": -1, "duration": 1, "text": "no"},
            {"start": 3, "duration": 2, "text": "turns"}]})
        self.assertEqual(len(out), 2)
        self.assertEqual(out[0]["text"], "Gute Gleitphase")

    def test_no_fake_transcript(self):
        with self.assertRaises(ValueError):
            mod.parse({"transcript": []})

    def test_mock_success(self):
        result = mod.run(lambda video: payload("Le glide et le pumping"), 1)
        self.assertEqual(result["transcripts_obtained"], 1)
        self.assertEqual(result["notes_updated"], 0)
        self.assertEqual(result["results"][0]["candidate_passages"][0]["status"],
                         "keyword_candidate_not_validated")

    def test_provider_failure_is_reported(self):
        def blocked(_):
            raise TimeoutError("private response must not leak")
        result = mod.run(blocked, 1)
        self.assertEqual(result["transcripts_obtained"], 0)
        self.assertEqual(result["results"][0]["failure_type"], "TimeoutError")
        self.assertNotIn("private response", json.dumps(result))

    def test_all_hits_including_late_segments_retained(self):
        source = payload(*(["glisse stabilité"] * 25 + ["conclusion sans mot technique", "carving final"]))
        result = mod.summarize(mod.PILOT[0], source)
        candidates = result["candidate_passages"]
        self.assertEqual(result["technical_keyword_segments"], 26)
        self.assertEqual(result["candidate_count"], 26)
        self.assertEqual(result["candidates_omitted"], 0)
        self.assertEqual(candidates[-1]["segment_index"], 26)
        self.assertEqual(candidates[-1]["at_s"], 78)
        self.assertEqual(candidates[-1]["to_s"], 80)
        self.assertEqual(result["keyword_category_matches"], 51)
        self.assertEqual(result["keyword_category_segment_counts"]["control"], 25)
        self.assertIsNone(candidates[-1]["claim"])
        self.assertEqual(result["performance_scores_generated"], 0)

    def test_context_preserves_negation_and_multiple_sizes_as_references(self):
        source = payload("Le 650", "la glisse", "n'est pas meilleure que le 950", "plus loin")
        result = mod.summarize(mod.PILOT[0], source, context_seconds=3)
        candidate = result["candidate_passages"][0]
        self.assertEqual(candidate["context"]["segment_indices"], [0, 1, 2])
        self.assertEqual(candidate["context"]["at_s"], 0)
        self.assertEqual(candidate["context"]["to_s"], 8)
        self.assertEqual(candidate["size_hints_in_segment"], [])
        self.assertEqual(candidate["size_hints_in_context"], [650, 950])
        self.assertIsNone(candidate["size_tested"])
        self.assertIsNone(candidate["polarity"])
        # The surrounding speech stays in the cache; report has references only.
        self.assertNotIn("text", candidate["context"])
        self.assertEqual(len(result["size_mentions"]), 2)
        self.assertEqual(result["size_attribution"], "unvalidated_numeric_hints_only")

    def test_numeric_hint_does_not_match_part_of_larger_number(self):
        self.assertEqual(mod.mentioned_sizes("1650 6500 650.5 650,5 x650", [650]), [])
        self.assertEqual(mod.mentioned_sizes("650/750", [650, 750]), [650, 750])

    def test_numeric_hint_accepts_sentence_punctuation_and_german_size_suffix(self):
        self.assertEqual(mod.mentioned_sizes("C'est le 650.", [650]), [650])
        self.assertEqual(mod.mentioned_sizes("Der 825er", [825]), [825])
        self.assertEqual(mod.mentioned_sizes("1,650 et 825erweiterung", [650, 825]), [])

    def test_title_sizes_are_not_assigned_when_absent_from_speech(self):
        result = mod.summarize(mod.PILOT[0], payload("Bonne glisse"))
        self.assertEqual(result["declared_size_hints"], [650, 750, 950])
        self.assertEqual(result["size_mentions"], [])
        self.assertEqual(result["candidate_passages"][0]["size_hints_in_context"], [])
        self.assertIsNone(result["candidate_passages"][0]["size_tested"])

    def test_invalid_nonfinite_times_and_overflow_are_rejected(self):
        source = payload("glide")
        for start, duration in [(math.nan, 2), (math.inf, 2), (1, math.inf),
                                (1, math.nan), (True, 1), (1, False), (10**400, 1), (1e308, 1e308)]:
            source["transcript"].append({"start": start, "duration": duration, "text": "invalid"})
        self.assertEqual(len(mod.parse(source)), 1)
        result = mod.summarize(mod.PILOT[0], source)
        json.dumps(result, allow_nan=False)

    def test_cache_roundtrip_preserves_hash_and_is_offline(self):
        source = {"language": "fr", "transcript": [
            {"start": 1.2, "duration": 3.4, "text": " Le 750 a de la glisse "},
            {"start": 8.7, "duration": 2.1, "text": "mais pas dans ce cas"}]}
        with tempfile.TemporaryDirectory() as directory:
            result = mod.run(lambda video: source, 1, cache_dir=directory)
            self.assertEqual(result["results"][0]["local_cache_status"], "written")
            cached = mod.read_local(directory, mod.PILOT[0])
            self.assertEqual(mod.parse(cached), mod.parse(source))
            offline = mod.run(lambda video: self.fail("network is forbidden"), 1,
                              input_dir=directory)
            self.assertEqual(offline["access_method"], "local_cached_transcript_no_network")
            self.assertEqual(offline["results"][0]["transcript_sha256"],
                             result["results"][0]["transcript_sha256"])
            self.assertEqual(offline["results"][0]["candidate_passages"],
                             result["results"][0]["candidate_passages"])

    def test_missing_offline_file_does_not_fallback_online(self):
        with tempfile.TemporaryDirectory() as directory:
            result = mod.run(lambda video: self.fail("network is forbidden"), 1,
                             input_dir=directory)
        self.assertEqual(result["transcripts_obtained"], 0)
        self.assertEqual(result["results"][0]["failure_type"], "FileNotFoundError")

    def test_corrupt_or_mismatched_cache_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            mod.write_cache(directory, mod.PILOT[0], payload("glisse"))
            path = pathlib.Path(directory) / (mod.PILOT[0][0] + ".json")
            cached = json.loads(path.read_text(encoding="utf-8"))
            cached["segments"][0]["text"] = "tampered"
            path.write_text(json.dumps(cached), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "hash_mismatch"):
                mod.read_local(directory, mod.PILOT[0])
            cached["video_id"] = "another-video"
            path.write_text(json.dumps(cached), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "video_id_mismatch"):
                mod.read_local(directory, mod.PILOT[0])

    def test_cache_write_failure_does_not_erase_acquisition(self):
        with patch.object(mod, "write_cache", side_effect=PermissionError("private path")):
            result = mod.run(lambda video: payload("glide"), 1, cache_dir="unused")
        self.assertEqual(result["transcripts_obtained"], 1)
        self.assertEqual(result["results"][0]["local_cache_status"], "write_failed")
        self.assertNotIn("private path", json.dumps(result))

    def test_excerpt_is_bounded_and_marked(self):
        result = mod.summarize(mod.PILOT[0], payload("glide " * 100))
        candidate = result["candidate_passages"][0]
        self.assertEqual(len(candidate["short_excerpt"]), 130)
        self.assertTrue(candidate["excerpt_truncated"])
        self.assertNotIn("segments", result)

    def test_invalid_context_rejected(self):
        for value in (-1, math.nan, math.inf, True):
            with self.assertRaisesRegex(ValueError, "invalid_context_seconds"):
                mod.run(lambda video: self.fail("must not fetch"), 1, context_seconds=value)


if __name__ == "__main__":
    unittest.main()
