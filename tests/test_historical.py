from datetime import datetime, timedelta, timezone

from top300.historical import (
    GoogleTrendTargetIndex,
    TrendEpisode,
    parse_google_trend_archive_row,
    parse_volume_floor,
)


def test_parse_volume_floor_handles_google_buckets() -> None:
    assert parse_volume_floor("500+") == 500
    assert parse_volume_floor("50K+") == 50_000
    assert parse_volume_floor("2M+") == 2_000_000
    assert parse_volume_floor(None) is None


def test_parse_archive_row_preserves_provider_cluster_provenance() -> None:
    episode = parse_google_trend_archive_row(
        {
            "Trends": "man united vs bodo glimt",
            "Search volume": "50K+",
            "Started": "2025-11-28T14:23:00+00:00",
            "Ended": "2025-11-28T16:45:00+00:00",
            "Trend breakdown": "man utd vs bodo, man united bodo glimt",
            "Explore link": "https://trends.google.com/example",
            "location": "US",
            "duration_is_estimate": False,
        }
    )
    assert episode.topic == "man united vs bodo glimt"
    assert episode.geography == "US"
    assert episode.volume_floor == 50_000
    assert episode.aliases == ("man utd vs bodo", "man united bodo glimt")
    assert episode.started.tzinfo is not None
    assert episode.ended is not None
    assert episode.duration_is_estimate is False


def test_estimated_end_is_not_a_strict_persistence_label() -> None:
    episode = TrendEpisode(
        topic="Example",
        geography="US",
        started=datetime(2026, 1, 1, tzinfo=timezone.utc),
        ended=datetime(2026, 1, 2, tzinfo=timezone.utc),
        duration_is_estimate=True,
    )
    assert episode.persisted_for(timedelta(hours=12), strict=True) is None
    assert episode.persisted_for(timedelta(hours=12), strict=False) is True


def test_target_index_labels_only_future_emergence_inside_horizon() -> None:
    cutoff = datetime(2026, 1, 1, 12, tzinfo=timezone.utc)
    episodes = [
        TrendEpisode(
            topic="OpenAI releases GPT 6",
            geography="US",
            started=cutoff - timedelta(hours=1),
        ),
        TrendEpisode(
            topic="iPhone 18 launch from Apple",
            geography="US",
            started=cutoff + timedelta(hours=6),
        ),
        TrendEpisode(
            topic="far future topic",
            geography="US",
            started=cutoff + timedelta(days=3),
        ),
    ]
    index = GoogleTrendTargetIndex(episodes, threshold=0.70)

    assert index.label("Apple launches iPhone 18", as_of=cutoff, horizon=timedelta(hours=24), geography="US") == 1
    assert index.label("OpenAI releases GPT 6", as_of=cutoff, horizon=timedelta(hours=24), geography="US") == 0
    assert index.label("far future topic", as_of=cutoff, horizon=timedelta(hours=24), geography="US") == 0


def test_target_index_uses_provider_native_breakdown_aliases() -> None:
    cutoff = datetime(2026, 1, 1, 12, tzinfo=timezone.utc)
    episode = TrendEpisode(
        topic="man united vs bodo glimt",
        aliases=("manchester united bodo glimt", "man utd vs bodo"),
        geography="US",
        started=cutoff + timedelta(hours=2),
    )
    index = GoogleTrendTargetIndex([episode], threshold=0.70)
    match = index.first_match(
        "manchester united bodo glimt",
        as_of=cutoff,
        horizon=timedelta(hours=24),
        geography="US",
    )
    assert match is not None
    assert match.episode.topic == "man united vs bodo glimt"
    assert match.matched_alias == "manchester united bodo glimt"
    assert match.lead_time == timedelta(hours=2)


def test_target_index_keeps_geographies_separate() -> None:
    cutoff = datetime(2026, 1, 1, 12, tzinfo=timezone.utc)
    episode = TrendEpisode(
        topic="Example Event",
        geography="GB",
        started=cutoff + timedelta(hours=2),
    )
    index = GoogleTrendTargetIndex([episode])
    assert index.label("Example Event", as_of=cutoff, horizon=timedelta(hours=24), geography="US") == 0
    assert index.label("Example Event", as_of=cutoff, horizon=timedelta(hours=24), geography="GB") == 1
