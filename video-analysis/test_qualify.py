import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("qualify", Path(__file__).with_name("qualify.py"))
q = importlib.util.module_from_spec(spec)
spec.loader.exec_module(q)

def video(title, kind="foil", identifier="a", date="2026-06-15"):
    return {"id": identifier, "title": title, "category": kind, "published_on": date,
            "url": "https://www.youtube.com/watch?v=" + identifier}

class QualifyTests(unittest.TestCase):
    def test_priority_candidate_does_not_assert_review(self):
        d=q.qualify([video("New wingfoil foil test review 2026")])
        self.assertEqual(d["priority_metadata_candidates"],1)
        self.assertEqual(d["video_contents_analyzed"],0)
        self.assertFalse(d["videos"][0]["content_verified"])

    def test_tutorial_not_priority(self):
        d=q.qualify([video("How to learn wingfoil foil test tutorial")])
        self.assertEqual(d["priority_metadata_candidates"],0)

    def test_discipline_ambiguous(self):
        d=q.qualify([video("Kitefoil board test")])
        self.assertEqual(d["priority_metadata_candidates"],0)

    def test_translation_is_only_potential_duplicate(self):
        a=video("Duotone Skybrid D/LAB 80 wingboard test 2026", "board", "a")
        b=video("Duotone Skybrid D/LAB 80 wingboard test 2026 English translation", "board", "b")
        d=q.qualify([a,b])
        self.assertEqual(d["possible_duplicate_groups"],1)
        self.assertFalse(d["possible_duplicate_details"][0]["confirmed_same_test"])
        self.assertEqual(len(d["videos"]),2)

    def test_no_silent_culling(self):
        d=q.qualify([video("Unboxing a wingfoil board", "board"),
                     video("Foil test review", "foil", "b")])
        self.assertEqual(len(d["videos"]),2)
        self.assertEqual(d["needs_manual_scope_review"],1)
        self.assertEqual(d["priority_metadata_candidates"],1)

if __name__=="__main__":
    unittest.main()
