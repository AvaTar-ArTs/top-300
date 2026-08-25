from datetime import datetime, timezone

from top300.adapters.google_trends import GoogleTrendsRSSAdapter, parse_traffic
from top300.adapters.hacker_news import HackerNewsAdapter


def test_parse_traffic_suffixes() -> None:
    assert parse_traffic("200K+") == 200_000
    assert parse_traffic("1M+") == 1_000_000
    assert parse_traffic("750+") == 750


def test_google_trends_rss_parses_snapshot() -> None:
    xml = """<?xml version="1.0" encoding="UTF-8"?>
    <rss xmlns:ht="https://trends.google.com/trending/rss" version="2.0">
      <channel>
        <item>
          <title>Example Trend</title>
          <pubDate>Mon, 24 Aug 2026 20:00:00 -0400</pubDate>
          <ht:approx_traffic>200K+</ht:approx_traffic>
          <link>https://trends.google.com/trending?geo=US</link>
        </item>
      </channel>
    </rss>
    observed_at = datetime(2026, 8, 25, 0, 5, tzinfo=timezone.utc)
    rows = GoogleTrendsRSSAdapter.parse(xml, observed_at=observed_at, geography="US")
    assert {row.metric for row in rows} == {"attention", "demand"}
    assert all(row.topic == "Example Trend" for row in rows)
    assert all(row.source == "google_trends" for row in rows)
    assert all(row.value == 200_000 for row in rows)
    assert all(row.observed_at == observed_at for row in rows)
    assert all(row.geography == "US" for row in rows)
    assert all("trend_started_at" in row.metadata for row in rows)


def test_hacker_news_collects_story_metrics() -> None:
    payloads = {
        "https://hacker-news.firebaseio.com/v0/topstories.json": [101, 102],
        "https://hacker-news.firebaseio.com/v0/item/101.json": {
            "id": 101,
            "type": "story",
            "title": "Agent systems are changing",
            "score": 120,
            "descendants": 44,
            "by": "alice",
            "time": 1787626800,
        },
        "https://hacker-news.firebaseio.com/v0/item/102.json": {
            "id": 102,
            "type": "story",
            "title": "A second topic",
            "score": 30,
            "descendants": 4,
            "by": "bob",
            "time": 1787626860,
        },
    }

    def fetch_json(url: str):
        return payloads[url]

    observed_at = datetime(2026, 8, 25, 0, 10, tzinfo=timezone.utc)
    rows = HackerNewsAdapter(fetch_json=fetch_json).collect(limit=2, observed_at=observed_at)
    story_rows = [row for row in rows if row.topic == "Agent systems are changing"]
    assert {row.metric for row in story_rows} == {"attention", "engagement", "supply"}
    assert next(row.value for row in story_rows if row.metric == "attention") == 120
    assert next(row.value for row in story_rows if row.metric == "engagement") == 44
    assert next(row.value for row in story_rows if row.metric == "supply") == 1
    assert all(row.source == "hacker_news" for row in rows)
    assert all(row.observed_at == observed_at for row in rows)
