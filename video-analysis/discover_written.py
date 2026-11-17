#!/usr/bin/env python3
"""Weekly discovery of public wingfoil written review leads.

Fetches publisher RSS when available. Falls back to publicly accessible
article index HTML. Stores metadata and source links only, never copies
full articles, extracts invented opinions, or modifies model scores.
"""
from __future__ import annotations
import argparse
from datetime import datetime, date, timezone
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser
import json
import re
from pathlib import Path
from urllib.parse import urljoin,urlparse
from urllib.request import Request,urlopen
from urllib.error import URLError, HTTPError
import xml.etree.ElementTree as ET

SOURCES=[
 {"name":"Pimpyourride", "url":"https://www.pimpyourride.fr/category/glisse-windsurf/wingfoil/review-test-materiel-wingfoil/", "feed":"https://www.pimpyourride.fr/category/glisse-windsurf/wingfoil/review-test-materiel-wingfoil/feed/"},
 {"name":"Pimpyourride latest", "url":"https://www.pimpyourride.fr/", "feed":"https://www.pimpyourride.fr/feed/"},
 {"name":"Tonic Mag foils","url":"https://www.tonicmag.com/reviews/hydrofoils/","feed":None,"category":"foil","path_prefix":"/reviews/hydrofoils/"},
 {"name":"Tonic Mag boards","url":"https://www.tonicmag.com/reviews/boards/","feed":None,"category":"board","path_prefix":"/reviews/boards/"},
 {"name":"Foiling Magazine","url":"https://www.thefoilingmagazine.com/test-center/","feed":None,"category":"needs_scope_review","path_prefix":"/test-center/"},
 {"name":"Wingpassion","url":"https://wingpassion.de/feed/","feed":"https://wingpassion.de/feed/"},
 {"name":"MACkite","url":"https://www.mackiteboarding.com/news/","feed":None,"path_prefix":"/news/"},
]
REVIEW=re.compile(r"\b(test|review|essai|praxistest|versus|comparatif)\b",re.I)
FOIL=re.compile(r"\b(foil|hydrofoil|front.?wing|kitefoil|wingfoil)\b",re.I)
BOARD=re.compile(r"\b(board|wingboard|mid.?length|planche|wingfoil)\b",re.I)
EXCLUDE=re.compile(r"\b(tuto|tutorial|comment|interview|itw|parawing\b.*\b(wing|review)|wing review|wing test|foil assist|webinar|annonce|coulisses|news|interview)\b",re.I)
MONTHS={"janvier":1,"février":2,"mars":3,"avril":4,"mai":5,"juin":6,"juillet":7,"août":8,"septembre":9,"octobre":10,"novembre":11,"décembre":12}
def get(url):
    req=Request(url,headers={"User-Agent":"FOIL-LAB-public-review-index/1.0","Accept":"text/html,application/rss+xml,application/xml"})
    with urlopen(req,timeout=16) as resp:
        return resp.read(1_400_000).decode("utf-8",errors="replace")
def kind(title):
    if not REVIEW.search(title) or EXCLUDE.search(title):return None
    if BOARD.search(title) and re.search(r"\b(board|wingboard|mid.?length|planche)\b",title,re.I):return "board"
    if FOIL.search(title):return "foil"
    return None
def year_ok(when,now):
    if when is None:return True
    try: earliest=now.replace(year=now.year-2)
    except ValueError: earliest=now.replace(year=now.year-2,day=28)
    return earliest<=when<=now
def items_from_rss(xml):
    root=ET.fromstring(xml)
    items=[]
    for item in root.findall(".//item"):
        title=item.findtext("title") or ""
        url=item.findtext("link") or ""
        when=None
        raw=item.findtext("pubDate") or ""
        if raw:
            try:when=parsedate_to_datetime(raw).date()
            except (TypeError,ValueError):pass
        items.append({"title":title.strip(),"url":url.strip(),"published_on":when.isoformat() if when else None})
    return items
class AnchorReader(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links=[];self.active=None
    def handle_starttag(self,tag,attrs):
        if tag=="a":
            attrs=dict(attrs)
            self.active={"url":attrs.get("href",""),"title":""}
    def handle_data(self,data):
        if self.active:self.active["title"]+=data
    def handle_endtag(self,tag):
        if tag=="a" and self.active:
            self.active["title"]=" ".join(self.active["title"].split())
            self.links.append(self.active)
            self.active=None
def items_from_html(page,base):
    parser=AnchorReader();parser.feed(page)
    return [{"title":item["title"],"url":urljoin(base,item["url"]),"published_on":None}
            for item in parser.links if item["url"]]
def collect(fetch=get,today=None):
    today=today or date.today()
    leads={};status=[]
    for source in SOURCES:
        entries=[];way=None;errors=[]
        for url,source_type in ((source["feed"],"rss"),(source["url"],"html_fallback")):
            if not url:continue
            try:
                data=fetch(url)
                entries=items_from_rss(data) if source_type=="rss" else items_from_html(data,url)
                way=source_type
                if entries:break
            except (OSError,ValueError,ET.ParseError) as ex:
                errors.append({"endpoint":source_type,"error":type(ex).__name__})
        for e in entries:
            category=kind(e["title"])
            u=urlparse(e["url"])
            host=(u.hostname or '').removeprefix('www.')
            expected=(urlparse(source['url']).hostname or '').removeprefix('www.')
            prefix=source.get('path_prefix')
            if re.search(r'/(?:page|issue|test-type)/',u.path) or not re.search(r'[A-Za-zÀ-ÿ]',e['title']):continue
            if prefix and u.path.startswith(prefix) and u.path.rstrip('/')!=prefix.rstrip('/') and e['title'] and not EXCLUDE.search(e['title']):category=category or source.get('category')
            if not category or u.scheme!="https" or host!=expected or (prefix and not u.path.startswith(prefix)):
                continue
            try:when=date.fromisoformat(e["published_on"]) if e["published_on"] else None
            except ValueError:when=None
            if not year_ok(when,today):continue
            url=e["url"].split("#",1)[0].split("?",1)[0]
            if url.rstrip("/") in ("https://www.pimpyourride.fr","https://www.pimpyourride.fr/category/glisse-windsurf/wingfoil/review-test-materiel-wingfoil"):
                continue
            leads.setdefault(url,{"title":e["title"],"url":url,"category":category,
                "published_on":when.isoformat() if when else None,
                "date_verified_from":"publisher_rss" if when and way=="rss" else "not_verified",
                "publisher":source["name"],"status":"article_lead_requires_source_review",
                "technical_claims":[],"video_transcript_acquired":False})
        status.append({"source":source["name"],"access":way or "blocked","items_on_index":len(entries),
                       "errors":errors})
    return {"schema_version":1,"generated_at":datetime.now(timezone.utc).isoformat(),
            "source_window_months":24,"article_leads":len(leads),
            "technical_assertions_created":0,"video_transcripts_obtained":0,
            "coverage_limit":"Publisher RSS / HTML index; not exhaustive. No automatic technical verdict.",
            "source_status":status,"articles":sorted(leads.values(),key=lambda r:r["title"])}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path,default=Path("video-index/written-review-leads.json"))
    args=p.parse_args()
    result=collect();args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("WRITTEN_REVIEW_DISCOVERY "+json.dumps({"article_leads":result["article_leads"],
         "source_status":result["source_status"],"technical_assertions_created":0},ensure_ascii=False))
    for item in result["articles"][:12]:
        print("ARTICLE_LEAD "+json.dumps({"title":item["title"],"url":item["url"]},ensure_ascii=False))
if __name__=="__main__":main()
