import unittest
from datetime import datetime,timezone,timedelta
from collection_policy import next_allowed,stop_status
class CollectionPolicyTests(unittest.TestCase):
 def test_delta_date_and_missing_header(self):
  t=datetime(2026,11,16,19,tzinfo=timezone.utc)
  self.assertEqual(next_allowed('2678',t),t+timedelta(seconds=2678))
  self.assertEqual(next_allowed('Mon, 16 Nov 2026 20:00:00 GMT',t),t+timedelta(hours=1))
  self.assertEqual(next_allowed(None,t),t+timedelta(hours=1))
 def test_hard_stops(self):
  for code in (401,403,429,500,503):self.assertTrue(stop_status(code))
  self.assertFalse(stop_status(404))
