import importlib.util
from pathlib import Path
from datetime import date
import unittest
spec=importlib.util.spec_from_file_location("discover_written",Path(__file__).with_name("discover_written.py"))
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
class WrittenDiscoveryTests(unittest.TestCase):
 def test_scope(self):
  self.assertEqual(mod.kind("SLINGSHOT PROJECT DRAG BOARD REVIEW"),"board")
  self.assertEqual(mod.kind("GAASTRA FOIL MOVE 800/1000 REVIEW"),"foil")
  self.assertIsNone(mod.kind("Débuter en pumpfoil — tuto dockstart"))
  self.assertIsNone(mod.kind("AFS interview sur les nouveautés"))
 def test_rss_parser_and_publication_window(self):
  rss="""<rss><channel><item><title>AFS Silk V2 Foil Review</title><link>https://www.pimpyourride.fr/afs-silk-v2-foil-review/</link><pubDate>Wed, 14 Oct 2026 08:00:00 GMT</pubDate></item></channel></rss>"""
  rows=mod.items_from_rss(rss);self.assertEqual(rows[0]["published_on"],"2026-10-14")
  self.assertTrue(mod.year_ok(date(2026,10,14),date(2026,11,15)))
  self.assertFalse(mod.year_ok(date(2022,1,1),date(2026,11,15)))
 def test_local_mock_never_generates_claims(self):
  rss="""<rss><channel><item><title>Gaastra Foil Move Review</title><link>https://www.pimpyourride.fr/test-gaastra-move-foil/</link><pubDate>Fri, 24 Jul 2026 08:00:00 GMT</pubDate></item></channel></rss>"""
  d=mod.collect(fetch=lambda _:rss,today=date(2026,11,15))
  self.assertEqual(d["article_leads"],1)
  self.assertEqual(d["technical_assertions_created"],0)
  self.assertEqual(d["articles"][0]["date_verified_from"],"publisher_rss")
 def test_blocked_source_preserves_errors(self):
  def fail(_):raise OSError("blocked")
  d=mod.collect(fetch=fail)
  self.assertEqual(d["article_leads"],0)
  self.assertTrue(all(x["access"]=="blocked" for x in d["source_status"]))
if __name__=="__main__":unittest.main()
