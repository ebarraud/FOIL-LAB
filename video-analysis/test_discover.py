import importlib.util
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).parent
spec = importlib.util.spec_from_file_location("discovery", HERE / "discover.py")
discovery = importlib.util.module_from_spec(spec)
spec.loader.exec_module(discovery)


class DiscoveryTests(unittest.TestCase):
    def test_date_window(self):
        self.assertEqual(discovery.parse_date("14.11.2024"), discovery.START)
        self.assertEqual(discovery.parse_date("14.11.2026"), discovery.END)
        self.assertIsNone(discovery.parse_date("no date"))

    def test_video_ids_and_index_rejection(self):
        self.assertEqual(discovery.video_key("https://gleiten.tv/video/4935-a-test", "gleiten.tv"), "gleiten-4935")
        self.assertEqual(discovery.video_key("https://gleiten.tv/index.php/video/action/view/v/4935/", "gleiten.tv"), "gleiten-4935")
        self.assertIsNone(discovery.video_key("https://gleiten.tv/foil/test/wingfoil/foil/alle/", "gleiten.tv"))

    def test_review_classification(self):
        self.assertEqual(discovery.classify("2026 KT Solus Foil Test"), "foil")
        self.assertEqual(discovery.classify("KT Drifter Wingboard Test"), "board")
        self.assertIsNone(discovery.classify("How to wingfoil beginner tutorial"))
        self.assertIsNone(discovery.classify("Promo: new wingfoil board launch"))

    def test_gleiten_list_pagination_without_video_claim(self):
        p1 = """<html><a href='/video/4935-kt-foil-test'>KT Foil Test</a>21.10.2026
        <a href='/foil/test/wingfoil/foil/alle/page/2/'>Ältere →</a></html>"""
        p2 = """<html><a href='/video/4000-something'>Something</a>01.02.2025</html>"""
        def fetch(url):
            return p2 if "/page/2/" in url else p1
        records, stats = discovery.discover_gleiten("foil", 4, fetch=fetch)
        self.assertTrue(any(r["id"] == "gleiten-4935" for r in records))
        self.assertTrue(all(r["fully_watched"] is False for r in records))
        self.assertEqual(stats["pages_requested"], 2)

    def test_filters_old_video(self):
        page = """<html><a href='/video/3000-old-foil-test'>Old Foil Test</a>01.02.2024</html>"""
        items, _ = discovery.discover_gleiten("foil", 1, fetch=lambda url: page)
        self.assertEqual(items, [])


if __name__ == "__main__":
    unittest.main()
