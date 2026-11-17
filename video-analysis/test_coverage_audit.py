import json,os,tempfile,unittest,contextlib,io
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError
import discover,discover_written,qualify,probe_batch,enrich_metadata,free_transcript_pilot
class CoverageAuditTests(unittest.TestCase):
 def test_generations_and_constructions_not_grouped(self):
  base={'category':'board','id':'a'}
  self.assertNotEqual(qualify.dedup_key(dict(base,title='Duotone Skybrid SLS80 test2025')),qualify.dedup_key(dict(base,title='Duotone Skybrid D/LAB80 test2026')))
 def test_italian_review_not_silently_lost(self):
  r=qualify.assess(dict(id='a',title='Recensione tavola wingfoil board',category='board',published_on='2026-11-15',url='https://example.com'))
  self.assertNotIn('no_explicit_test_or_review_signal',r['screening_reasons'])
 def test_probe_does_not_invent_german_language(self):
  row=dict(id='a',title='Foil test',url='https://www.youtube.com/watch?v=aaaaaaaaaaa',provider='youtube',category='foil',published_on='2026-11-15',screening_status='priority_metadata_candidate')
  self.assertEqual(probe_batch.choose([row],1)[0]['language'],'auto')
 def test_details_stops_on_429_and_counts_actual_calls(self):
  def limited(_):raise HTTPError('https://example.com',429,'limited',{},None)
  report=enrich_metadata.enrich([{'id':'youtube-'+str(i).zfill(11),'provider':'youtube'} for i in range(75)],'test',fetch=limited)
  self.assertEqual(report['videos_list_api_calls'],1);self.assertEqual(report['errors'][0]['http_status'],429)
 def test_discovery_stops_and_remembers_cooldown(self):
  old=Path.cwd()
  with tempfile.TemporaryDirectory() as folder:
   try:
    os.chdir(folder)
    with patch.dict(os.environ,{'YOUTUBE_API_KEY':'test'}),patch.object(discover,'youtube_search',return_value=([],[{'http_status':429,'retry_after':'1200'}])) as search,contextlib.redirect_stdout(io.StringIO()):
     discover.main(['--sources','youtube','--output','out.json']);self.assertEqual(search.call_count,1)
     discover.main(['--sources','youtube','--output','out.json']);self.assertEqual(search.call_count,1)
    d=json.loads(Path('out.json').read_text());self.assertEqual(d['report']['youtube']['status'],'cooldown_active')
   finally:os.chdir(old)
 def test_free_pilot_stops_after_provider_failure(self):
  calls=[]
  def fail(v):calls.append(v);raise HTTPError('https://example.com',503,'down',{},None)
  d=free_transcript_pilot.run(fetch=fail);self.assertEqual(len(calls),1);self.assertIn('retry_not_before_utc',d)
 def test_written_other_publisher_without_review_word_and_no_pagination(self):
  sources=[{'name':'Tonic','url':'https://www.tonicmag.com/reviews/hydrofoils/','feed':None,'category':'foil','path_prefix':'/reviews/hydrofoils/'}]
  page='<a href="/reviews/hydrofoils/f-one-test-2026/">F-One Model</a><a href="/reviews/hydrofoils/page/2/">2</a><a href="https://evil.example/reviews/hydrofoils/test/">Foil test</a>'
  with patch.object(discover_written,'SOURCES',sources):d=discover_written.collect(fetch=lambda _:page)
  self.assertEqual(d['article_leads'],1);self.assertEqual(d['articles'][0]['publisher'],'Tonic');self.assertEqual(d['technical_assertions_created'],0)
