from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from xml.etree import ElementTree

from ..observations import Observation

RSS_URL = "https://trends.google.com/trending/rss"


def parse_traffic(value: str) -> float:
    cleaned = value.strip().upper().replace(",", "").replace("+", "")
    if not cleaned:
        return 0.0
    multiplier = 1.0
    if cleaned[-1:] in {"K", "M", "B"}:
        suffix = cleaned[-1]
        cleaned = cleaned[:-1]
        multiplier = {"K": 1_000.0, "M": 1_000_000.0, "B": 1_000_000_000.0}[suffix]
    return float(cleaned) * multiplier


def _child_text(element: ElementTree.Element, local_name: str) -> str | None:
    for child in element:
        if child.tag.rsplit("}", 1)[-1] == local_name:
            text = child.text.strip() if child.text else ""
            return text or None
    return None


def _fetch_text(url: str) -> str:
    request = Request(url, headers={"User-Agent": "TOP-300/1.1 trend-research"})
    with urlopen(request, timeout=20) as response:
        return response.read().decode("utf-8")


class GoogleTrendsRSSAdapter:
    @staticmethod
    def parse(
        xml_text: str,
        *,
        observed_at: datetime,
        geography: str,
    ) -> list[Observation]:
        if observed_at.tzinfo is None:
            raise ValueError("observed_at must be timezone-aware")
        root = ElementTree.fromstring(xml_text)
        rows: list[Observation] = []
        for item in root.findall(".//item"):
            title = _child_text(item, "title")
            traffic_text = _child_text(item, "approx_traffic")
            if not title or not traffic_text:
                continue
            traffic = parse_traffic(traffic_text)
            published = _child_text(item, "pubDate")
            link = _child_text(item, "link")
            trend_started_at: str | None = None
            if published:
                try:
                    trend_started_at = parsedate_to_datetime(published).astimezone(
                        timezone.utc
                    ).isoformat()
                except (TypeError, ValueError):
                    trend_started_at = published
            metadata = {
                "approx_traffic_text": traffic_text,
                "trend_started_at": trend_started_at,
                "source_url": link,
            }
            for metric in ("attention", "demand"):
                rows.append(
                    Observation(
                        topic=title,
                        source="google_trends",
                        metric=metric,
                        value=traffic,
                        observed_at=observed_at,
                        geography=geography,
                        metadata=metadata,
                    )
                )
        return rows

    def collect(
        self,
        *,
        geography: str = "US",
        observed_at: datetime | None = None,
    ) -> list[Observation]:
        observed_at = observed_at or datetime.now(timezone.utc)
        url = f"{RSS_URL}?{urlencode({'geo': geography})}"
        return self.parse(
            _fetch_text(url),
            observed_at=observed_at,
            geography=geography,
        )
