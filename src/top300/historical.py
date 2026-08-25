from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Mapping

from .canonical import lexical_similarity, normalize_topic

_VOLUME_PATTERN = re.compile(r"^\s*([0-9]+(?:\.[0-9]+)?)\s*([KMB]?)\s*\+?\s*$", re.I)
_VOLUME_SCALES = {"": 1, "K": 1_000, "M": 1_000_000, "B": 1_000_000_000}


def parse_volume_floor(value: object) -> int | None:
    """Parse a Google search-volume bucket into its lower bound."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return int(value)
    text = str(value).strip().replace(",", "")
    if not text:
        return None
    match = _VOLUME_PATTERN.match(text)
    if match is None:
        raise ValueError(f"unsupported search-volume bucket: {value!r}")
    amount, suffix = match.groups()
    return int(float(amount) * _VOLUME_SCALES[suffix.upper()])


def _parse_datetime(value: object, *, required: bool = False) -> datetime | None:
    if value is None or str(value).strip() == "":
        if required:
            raise ValueError("timestamp is required")
        return None
    if isinstance(value, datetime):
        parsed = value
    else:
        parsed = datetime.fromisoformat(str(value).strip().replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("historical timestamps must be timezone-aware")
    return parsed


def _truthy(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().casefold() in {"1", "true", "yes", "y", "estimated"}


def _aliases(value: object, primary: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, (list, tuple, set)):
        candidates = [str(item).strip() for item in value]
    else:
        candidates = [item.strip() for item in str(value).split(",")]
    primary_normalized = normalize_topic(primary)
    result: list[str] = []
    seen: set[str] = set()
    for candidate in candidates:
        if not candidate:
            continue
        normalized = normalize_topic(candidate)
        if not normalized or normalized == primary_normalized or normalized in seen:
            continue
        seen.add(normalized)
        result.append(candidate)
    return tuple(result)


def _field(row: Mapping[str, Any], *names: str) -> object:
    for name in names:
        if name in row:
            return row[name]
    return None


@dataclass(frozen=True)
class TrendEpisode:
    """One provider-detected trend episode and its later-known lifecycle data."""

    topic: str
    started: datetime
    geography: str | None = None
    ended: datetime | None = None
    aliases: tuple[str, ...] = ()
    volume_floor: int | None = None
    duration_is_estimate: bool = False
    explore_link: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.topic.strip():
            raise ValueError("topic must not be empty")
        if self.started.tzinfo is None:
            raise ValueError("started must be timezone-aware")
        if self.ended is not None:
            if self.ended.tzinfo is None:
                raise ValueError("ended must be timezone-aware")
            if self.ended < self.started:
                raise ValueError("ended must not precede started")

    def persisted_for(self, horizon: timedelta, *, strict: bool = True) -> bool | None:
        """Return persistence label, respecting censored/estimated end times."""
        if horizon < timedelta(0):
            raise ValueError("horizon must be non-negative")
        if self.ended is None:
            return None
        if strict and self.duration_is_estimate:
            return None
        return self.ended - self.started >= horizon


@dataclass(frozen=True)
class TargetMatch:
    episode: TrendEpisode
    matched_alias: str
    similarity: float
    lead_time: timedelta


def parse_google_trend_archive_row(row: Mapping[str, Any]) -> TrendEpisode:
    """Convert one GoogleTrendArchive record while preserving native provenance."""
    topic_value = _field(row, "Trends", "trends", "trend", "topic")
    topic = "" if topic_value is None else str(topic_value).strip()
    if not topic:
        raise ValueError("GoogleTrendArchive row is missing Trends")
    started = _parse_datetime(_field(row, "Started", "started"), required=True)
    assert started is not None
    ended = _parse_datetime(_field(row, "Ended", "ended"))
    geography_value = _field(row, "location", "Location", "geography", "geo")
    geography = None if geography_value is None else str(geography_value).strip() or None
    breakdown = _field(row, "Trend breakdown", "trend_breakdown", "breakdown", "aliases")
    volume = _field(row, "Search volume", "search_volume", "volume")
    estimate = _field(
        row,
        "duration_is_estimate",
        "duration is estimate",
        "Duration is estimate",
        "is_estimated",
    )
    explore_value = _field(row, "Explore link", "explore_link", "explore")
    explore_link = None if explore_value is None else str(explore_value).strip() or None

    known_fields = {
        "Trends",
        "trends",
        "trend",
        "topic",
        "Started",
        "started",
        "Ended",
        "ended",
        "location",
        "Location",
        "geography",
        "geo",
        "Trend breakdown",
        "trend_breakdown",
        "breakdown",
        "aliases",
        "Search volume",
        "search_volume",
        "volume",
        "duration_is_estimate",
        "duration is estimate",
        "Duration is estimate",
        "is_estimated",
        "Explore link",
        "explore_link",
        "explore",
    }
    metadata = {key: value for key, value in row.items() if key not in known_fields}

    return TrendEpisode(
        topic=topic,
        started=started,
        geography=geography,
        ended=ended,
        aliases=_aliases(breakdown, topic),
        volume_floor=parse_volume_floor(volume),
        duration_is_estimate=_truthy(estimate),
        explore_link=explore_link,
        metadata=metadata,
    )


class GoogleTrendTargetIndex:
    """Cutoff-safe lookup for future Google trend emergence labels."""

    def __init__(self, episodes: list[TrendEpisode], threshold: float = 0.72) -> None:
        if not 0 <= threshold <= 1:
            raise ValueError("threshold must be between 0 and 1")
        self.threshold = threshold
        self.episodes = tuple(sorted(episodes, key=lambda episode: episode.started))

    def first_match(
        self,
        topic: str,
        *,
        as_of: datetime,
        horizon: timedelta,
        geography: str | None = None,
    ) -> TargetMatch | None:
        if as_of.tzinfo is None:
            raise ValueError("as_of must be timezone-aware")
        if horizon < timedelta(0):
            raise ValueError("horizon must be non-negative")
        end = as_of + horizon
        matches: list[TargetMatch] = []
        for episode in self.episodes:
            if episode.started <= as_of:
                continue
            if episode.started > end:
                break
            if geography is not None and episode.geography != geography:
                continue
            best_alias: str | None = None
            best_similarity = 0.0
            for alias in (episode.topic, *episode.aliases):
                similarity = lexical_similarity(topic, alias)
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_alias = alias
            if best_alias is None or best_similarity < self.threshold:
                continue
            matches.append(
                TargetMatch(
                    episode=episode,
                    matched_alias=best_alias,
                    similarity=best_similarity,
                    lead_time=episode.started - as_of,
                )
            )
        if not matches:
            return None
        return min(
            matches,
            key=lambda match: (
                match.episode.started,
                -match.similarity,
                normalize_topic(match.episode.topic),
            ),
        )

    def label(
        self,
        topic: str,
        *,
        as_of: datetime,
        horizon: timedelta,
        geography: str | None = None,
    ) -> int:
        return int(
            self.first_match(
                topic,
                as_of=as_of,
                horizon=horizon,
                geography=geography,
            )
            is not None
        )
