#!/usr/bin/env python3
"""Discovery index: wingfoil front-foil and board reviews published in last 24 months.

Discovers Gleiten.TV category listings; optionally YouTube Data API when
YOUTUBE_API_KEY is provided. Produces metadata/evidence leads, NEVER claims
to have watched videos or to have obtained their transcripts.
"""
from __future__ import annotations
import argparse
import json
import os
import re
import time
import urllib.parse
import urllib.request
from datetime import date, datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

END = date.today()
try:
    START = END.replace(year=END.year - 2)
except ValueError:
    START = END.replace(year=END.year - 2, day=28)
GTV = {
    "foil": "https://gleiten.tv/foil/test/wingfoil/foil/alle/",
    "board": "https://gleiten.tv/foil/test/wingfoil/wingboard/alle/",
}
SEARCH_QUERIES = [
    "wingfoil front foil test review 2025",
    "wingfoil foil test review 2026",
    "wing foil Flügel Test 2025",
    "wing foil Flügel Test 2026",
    "wingfoil board test review 2025",
    "wingfoil board test review 2026",
    "wingfoil board Test 2025 deutsch",
    "wingfoil board Test 2026 deutsch",
    "Gleiten TV wingfoil foil test",
    "Gleiten TV wingboard test",
    "Nature Kite wingfoil test board foil",
    "Kiteworldshop wingfoil board foil review",
    "wingfoil essai aile avant comparatif",
    "wingfoil test planche avis",
    "wingfoil foil Test Erfahrungen",
    "wingboard Test Vergleich",
    "wingfoil foil recensione prova",
    "wingfoil tavola recensione test",
]
VIDEO_ID = re.compile(r"/video/(\d+)(?:[-/]|$)|/index\.php/video/action/view/v/(\d+)")
DAY = re.compile(r"\b([0-3]?\d)\.([01]?\d)\.(20\d\d)\b")
REVIEW = re.compile(r"\b(test|tested|review|essai|comparatif|vergleich|recensione|prova)\b", re.I)
GENERIC = re.compile(r"\b(tutorial|how to|learn to|intro|teaser|preview|event|interview|vlog|trailer|news|unboxing)\b", re.I)
FOIL = re.compile(r"\b(foil|frontwing|front wing|sonar|glide|halo|solus|enduro|silk)\b", re.I)
BOARD = re.compile(r"\b(wingboard|wing board|wingfoil board|foilboard|midlength|skybrid|drifter|rocket|planche|tavola)\b", re.I)


class HtmlLinks(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.current = None
        self.depth = 0
        self.all_text = []

    def handle_starttag(self, tag, attrs):
        props = dict(attrs)
        if tag == "a":
            if self.current is None:
                self.current = {"href": props.get("href", ""), "text": ""}
                self.depth = 1
            else:
                self.depth += 1

    def handle_data(self, data):
        self.all_text.append(data)
        if self.current is not None:
            self.current["text"] += data

    def handle_endtag(self, tag):
        if tag == "a" and self.current is not None:
            self.depth -= 1
            if self.depth == 0:
                self.current["text"] = " ".join(self.current["text"].split())
                self.links.append(self.current)
                self.current = None


def get_page(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": "FOIL-LAB-ResearchBot/0.1 (public indexes; low rate)",
                                               "Accept": "text/html,application/json"})
    with urllib.request.urlopen(req, timeout=25) as response:
        return response.read(2_000_000).decode("utf-8", errors="replace")


def classify(title: str, hint: str = "") -> str | None:
    if GENERIC.search(title):
        return None
    if not REVIEW.search(title):
        return None
    if BOARD.search(title):
        return "board"
    if FOIL.search(title):
        return "foil"
    return hint or None


def parse_date(text: str):
    match = DAY.search(text)
    if match:
        try:
            return date(int(match[3]), int(match[2]), int(match[1]))
        except ValueError:
            return None
    return None


def video_key(url: str, provider: str):
    if provider == "gleiten.tv":
        match = VIDEO_ID.search(url)
        if match:
            return "gleiten-" + (match.group(1) or match.group(2))
    if provider == "youtube":
        parsed = urllib.parse.urlparse(url)
        vid = urllib.parse.parse_qs(parsed.query).get("v", [None])[0]
        if vid:
            return "youtube-" + vid
    return None


def discover_gleiten(category: str, max_pages: int, fetch=get_page):
    url = GTV[category]
    found, pages, errors = {}, set(), []
    for index in range(max_pages):
        if url in pages:
            break
        pages.add(url)
        try:
            html = fetch(url)
        except Exception as exc:
            errors.append({"url": url, "error": type(exc).__name__})
            break
        parser = HtmlLinks()
        parser.feed(html)
        anchors = parser.links
        for a in anchors:
            item_url = urllib.parse.urljoin(url, a["href"])
            identifier = video_key(item_url, "gleiten.tv")
            if not identifier:
                continue
            # The visible title of a video sometimes omits "Test" despite
            # its placement in the test categories. Preserve it as a lead.
            title = a["text"].strip()
            if not title or GENERIC.search(title):
                continue
            kind = classify(title, category)
            if kind != category:
                # Category pages are curated as foil vs. wingboard, but generic
                # brand titles or translated versions remain candidates.
                if category == "foil" and BOARD.search(title):
                    continue
                if category == "board" and FOIL.search(title) and not BOARD.search(title):
                    continue
                kind = category
            # Only accept dates attributed to the video card, not globally
            # from an unrelated page. Unknown dates remain UNVERIFIED.
            pos = html.find(a["href"])
            segment = html[max(0, pos-400):pos+1200] if pos >= 0 else ""
            published = parse_date(segment)
            # Date must not be guessed from model year in a title.
            if published and not (START <= published <= END):
                continue
            found[identifier] = {
                "id": identifier, "url": item_url, "title": title,
                "provider": "gleiten.tv", "category": kind,
                "published_on": published.isoformat() if published else None,
                "date_status": "nearby_html_candidate_requires_check" if published else "unknown_requires_check",
                "source_status": "video_page_indexed",
                "transcript_status": "not_obtained", "fully_watched": False,
                "review_status": "queued", "qualitative_scores": None,
            }
        next_links = [
            urllib.parse.urljoin(url, a["href"])
            for a in anchors if re.search(r"Ältere|Older|weiter|next", a["text"], re.I)
        ]
        next_links = [u for u in next_links if urllib.parse.urlparse(u).netloc.endswith("gleiten.tv") and u not in pages]
        if not next_links:
            break
        url = next_links[0]
        time.sleep(0.5)
    return list(found.values()), {"pages_requested": len(pages),
                                  "errors": errors, "max_pages_hit": len(pages) >= max_pages}


def youtube_search(key: str, query: str, max_pages: int = 2, fetch=get_page, channel_id=None):
    records, token, errors = {}, None, []
    for _ in range(max_pages):
        params = {
            "part": "snippet", "q": query, "type": "video",
            "order": "date", "maxResults": "50",
            "publishedAfter": START.isoformat() + "T00:00:00Z",
            "publishedBefore": END.isoformat() + "T23:59:59Z", "key": key
        }
        if token:
            params["pageToken"] = token
        if channel_id:
            params['channelId'] = channel_id
        endpoint = "https://www.googleapis.com/youtube/v3/search?" + urllib.parse.urlencode(params)
        try:
            response = json.loads(fetch(endpoint))
        except Exception as exc:
            errors.append({"query": query, "reason": type(exc).__name__})
            break
        for item in response.get("items", []):
            video_id = item.get("id", {}).get("videoId")
            snippet = item.get("snippet", {})
            title = snippet.get("title", "")
            category = classify(title)
            if not video_id or not category:
                continue
            stamp = snippet.get("publishedAt", "")
            try:
                when = date.fromisoformat(stamp[:10])
            except ValueError:
                continue
            if not START <= when <= END:
                continue
            rid = "youtube-" + video_id
            records[rid] = {
                "id": rid, "url": "https://www.youtube.com/watch?v=" + video_id,
                "title": title, "publisher": snippet.get("channelTitle"),
                "channel_id": snippet.get("channelId"),
                "provider": "youtube", "category": category,
                "published_on": stamp[:10], "date_status": "youtube_api",
                "source_status": "search_api_only",
                "transcript_status": "not_obtained", "fully_watched": False,
                "review_status": "queued", "qualitative_scores": None,
                "discovery_query": query,
            }
        token = response.get("nextPageToken")
        if not token:
            break
    return list(records.values()), errors


def combine(records):
    out = {}
    for item in records:
        existing = out.get(item["id"])
        if existing is None:
            out[item["id"]] = item
        elif "discovery_query" in item:
            existing.setdefault("discovery_queries", []).append(item["discovery_query"])
    return sorted(out.values(), key=lambda x: (x["published_on"] or "", x["id"]), reverse=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", default="video-analysis/discovery/latest.json")
    ap.add_argument("--max-pages", type=int, default=12)
    ap.add_argument("--youtube-pages", type=int, default=2)
    ap.add_argument("--sources", choices=["all", "gleiten", "youtube"], default="all")
    args = ap.parse_args(argv)
    if not 1 <= args.max_pages <= 30 or not 1 <= args.youtube_pages <= 5:
        ap.error("Invalid page limits")
    items, report = [], {"gleiten": {}, "youtube": {"status": "not_requested"}}
    if args.sources in {"all", "gleiten"}:
        for category in GTV:
            rows, status = discover_gleiten(category, args.max_pages)
            items += rows
            report["gleiten"][category] = status
    if args.sources in {"all", "youtube"}:
        key = os.environ.get("YOUTUBE_API_KEY")
        if not key:
            report["youtube"] = {"status": "missing_api_key_no_yt_search_performed"}
        else:
            report["youtube"] = {"status": "attempted", "queries": len(SEARCH_QUERIES), "errors": []}
            for query in SEARCH_QUERIES:
                rows, errors = youtube_search(key, query, args.youtube_pages)
                items += rows
                report["youtube"]["errors"].extend(errors)
                time.sleep(0.15)
            # Explicit channel coverage supplements, but does not replace, broad search.
            registry=Path(__file__).resolve().parents[1]/'data/research/monitored_publishers.json'
            publishers=json.loads(registry.read_text(encoding='utf-8')).get('publishers',[]) if registry.exists() else []
            report['youtube']['channel_searches']=[]
            for publisher in publishers:
                rows, errors = youtube_search(key, 'wingfoil', args.youtube_pages,
                                             channel_id=publisher['channel_id'])
                items += rows
                report['youtube']['errors'].extend(errors)
                report['youtube']['channel_searches'].append({'publisher':publisher['name'],
                    'channel_id':publisher['channel_id'],'retained_candidates':len(rows),
                    'errors':errors,'coverage':'bounded_search_not_full_channel_archive'})
                time.sleep(0.15)
    records = combine(items)
    result = {
        "schema_version": 1, "generated_at": datetime.now(timezone.utc).isoformat(),
        "window_start": START.isoformat(), "window_end": END.isoformat(),
        "scope": "Wingfoil equipment TEST videos: boards and foils only",
        "discovered": len(records),
        "verified_publish_dates": sum(r["date_status"] == "youtube_api" for r in records),
        "unknown_or_unconfirmed_dates": sum(r["date_status"] != "youtube_api" for r in records),
        "fully_analyzed_videos": 0, "transcripts_processed": 0,
        "notes_updated": 0,
        "limitations": "Metadata leads, some Gleiten dates heuristically extracted and MUST be verified before use. No video watched.",
        "report": report, "videos": records,
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("discovered", "verified_publish_dates",
          "unknown_or_unconfirmed_dates", "fully_analyzed_videos")}))
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
