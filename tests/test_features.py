from datetime import datetime, timedelta, timezone

from top300.features import FeatureBuilder
from top300.observations import Observation
from top300.store import SignalStore


def add_series(store: SignalStore, topic: str, values: list[float], start: datetime) -> None:
    rows = [
        Observation(
            topic=topic, source="reddit", metric="attention", value=value,
            observed_at=start + timedelta(hours=i),
        )
        for i, value in enumerate(values)
    ]
    store.add_many(rows)


def test_future_data_cannot_change_earlier_features(tmp_path) -> None:
    start = datetime(2026, 8, 24, 0, tzinfo=timezone.utc)
    store = SignalStore(tmp_path / "signals.db")
    add_series(store, "alpha", [10, 11, 12, 14, 18, 25], start)
    builder = FeatureBuilder()
    cutoff = start + timedelta(hours=5)
    before = builder.build(store, "alpha", cutoff)
    store.add_many([Observation(
        topic="alpha", source="reddit", metric="attention", value=10000,
        observed_at=start + timedelta(hours=6),
    )])
    after = builder.build(store, "alpha", cutoff)
    assert before == after


def test_rising_series_has_more_acceleration_than_flat_series(tmp_path) -> None:
    start = datetime(2026, 8, 24, 0, tzinfo=timezone.utc)
    store = SignalStore(tmp_path / "signals.db")
    add_series(store, "rising", [10, 10, 11, 14, 22, 40, 75, 140], start)
    add_series(store, "flat", [10, 10, 10, 10, 10, 10, 10, 10], start)
    builder = FeatureBuilder()
    cutoff = start + timedelta(hours=7)
    assert builder.build(store, "rising", cutoff).acceleration > builder.build(
        store, "flat", cutoff
    ).acceleration
