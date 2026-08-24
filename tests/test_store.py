from datetime import datetime, timezone

from top300.observations import Observation
from top300.store import SignalStore


def obs(value: float, hour: int) -> Observation:
    return Observation(
        topic="alpha", source="reddit", metric="attention", value=value,
        observed_at=datetime(2026, 8, 24, hour, tzinfo=timezone.utc),
    )


def test_store_is_idempotent(tmp_path) -> None:
    store = SignalStore(tmp_path / "signals.db")
    row = obs(10, 10)
    assert store.add_many([row]) == 1
    assert store.add_many([row]) == 0
    assert len(store.query(topic="alpha")) == 1


def test_store_replay_respects_cutoff(tmp_path) -> None:
    store = SignalStore(tmp_path / "signals.db")
    store.add_many([obs(10, 10), obs(20, 11), obs(999, 12)])
    cutoff = datetime(2026, 8, 24, 11, tzinfo=timezone.utc)
    rows = store.query(topic="alpha", as_of=cutoff)
    assert [r.value for r in rows] == [10, 20]
