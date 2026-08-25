from datetime import datetime, timezone

from top300.adapters.google_trend_archive import GoogleTrendArchiveAdapter


def archive_rows():
    return [
        {
            "Trends": "US first",
            "Search volume": "20K+",
            "Started": "2026-01-02T12:00:00+00:00",
            "Ended": "2026-01-02T14:00:00+00:00",
            "Trend breakdown": "us first alias",
            "location": "US",
        },
        {
            "Trends": "GB item",
            "Search volume": "10K+",
            "Started": "2026-01-02T13:00:00+00:00",
            "location": "GB",
        },
        {
            "Trends": "US second",
            "Search volume": "50K+",
            "Started": "2026-01-03T12:00:00+00:00",
            "location": "US",
        },
        {
            "Trends": "US late",
            "Search volume": "100K+",
            "Started": "2026-02-01T12:00:00+00:00",
            "location": "US",
        },
    ]


def test_archive_adapter_requests_streaming_dataset_and_filters() -> None:
    calls = []

    def loader(repo_id, *, split, streaming):
        calls.append((repo_id, split, streaming))
        return archive_rows()

    adapter = GoogleTrendArchiveAdapter(loader=loader)
    episodes = list(
        adapter.stream(
            geography="US",
            start=datetime(2026, 1, 1, tzinfo=timezone.utc),
            end=datetime(2026, 1, 31, 23, 59, tzinfo=timezone.utc),
            limit=2,
        )
    )

    assert calls == [("aurman/GoogleTrendArchive", "train", True)]
    assert [episode.topic for episode in episodes] == ["US first", "US second"]
    assert all(episode.geography == "US" for episode in episodes)


def test_archive_adapter_limit_counts_matching_rows_not_scanned_rows() -> None:
    adapter = GoogleTrendArchiveAdapter(loader=lambda *args, **kwargs: archive_rows())
    episodes = list(adapter.stream(geography="US", limit=1))
    assert [episode.topic for episode in episodes] == ["US first"]


def test_archive_adapter_explains_optional_dependency_when_missing() -> None:
    def missing_loader(*args, **kwargs):
        raise ModuleNotFoundError("No module named 'datasets'")

    adapter = GoogleTrendArchiveAdapter(loader=missing_loader)
    try:
        list(adapter.stream(limit=1))
    except RuntimeError as exc:
        assert "top-300[archive]" in str(exc)
    else:
        raise AssertionError("expected optional dependency error")
