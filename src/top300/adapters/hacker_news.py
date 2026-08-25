import json
from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any
from urllib.request import Request, urlopen

from ..observations import Observation


BASE_URL = "https://hacker-news.firebaseio.com/v0"
FetchJSON = Callable[[str], Any]


def _default_fetch_json(url: str) -> Any:
    request = Request(url, headers={"User-Agent": "TOP-300/1.1 trend-research"})
    with urlopen(request, timeout=20) as response:
        return json.load(response)


class HackerNewsAdapter:
    def __init__(self, *, fetch_json: FetchJSON | None = None) -> None:
        self.fetch_json = fetch_json or _default_fetch_json

    def collect(
        self,
        *,
        limit: int = 30,
        observed_at: datetime | None = None,
    ) -> list[Observation]:
        if limit < 1:
            raise ValueError("limit must be at least 1")
        observed_at = observed_at or datetime.now(timezone.utc)
        if observed_at.tzinfo is None:
            raise ValueError("observed_at must be timezone-aware")

        ids = self.fetch_json(f"{BASE_URL}/topstories.json") or []
        rows: list[Observation] = []
        for item_id in list(ids)[:limit]:
            item = self.fetch_json(f"{BASE_URL}/item/{item_id}.json") or {}
            if item.get("deleted") or item.get("dead") or item.get("type") != "story":
                continue
            title = str(item.get("title") or "").strip()
            if not title:
                continue
            created_at = item.get("time")
            metadata = {
                "item_id": item.get("id", item_id),
                "author": item.get("by"),
                "created_at": (
                    datetime.fromtimestamp(created_at, tz=timezone.utc).isoformat()
                    if isinstance(created_at, (int, float))
                    else None
                ),
                "url": item.get("url"),
            }
            metrics = {
                "attention": float(item.get("score") or 0),
                "engagement": float(item.get("descendants") or 0),
                "supply": 1.0,
            }
            for metric, value in metrics.items():
                rows.append(
                    Observation(
                        topic=title,
                        source="hacker_news",
                        metric=metric,
                        value=value,
                        observed_at=observed_at,
                        entity=str(item.get("id", item_id)),
                        metadata=metadata,
                    )
                )
        return rows
