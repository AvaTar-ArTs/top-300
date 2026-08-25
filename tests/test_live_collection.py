import json
from datetime import datetime, timezone

from top300.live import LiveCollector
from top300.observations import Observation
from top300.store import SignalStore


class WorkingAdapter:
    def __init__(self, source: str) -> None:
        self.source = source

    def collect(self, *, observed_at: datetime) -> list[Observation]:
        return [
            Observation(
                topic="shared topic",
                source=self.source,
                metric="attention",
                value=42,
                observed_at=observed_at,
            )
        ]


class FailingAdapter:
    def collect(self, *, observed_at: datetime) -> list[Observation]:
        raise RuntimeError("source unavailable")


def test_live_collection_persists_partial_success(tmp_path) -> None:
    observed_at = datetime(2026, 8, 25, 0, 30, tzinfo=timezone.utc)
    store = SignalStore(tmp_path / "signals.db")
    snapshot_path = tmp_path / "snapshot.json"
    collector = LiveCollector(
        sources={
            "working": WorkingAdapter("working"),
            "broken": FailingAdapter(),
        }
    )

    report = collector.collect(
        store=store,
        observed_at=observed_at,
        snapshot_path=snapshot_path,
    )

    assert report.inserted == 1
    assert report.sources["working"].status == "ok"
    assert report.sources["working"].observations == 1
    assert report.sources["broken"].status == "error"
    assert "source unavailable" in (report.sources["broken"].error or "")
    rows = store.query(as_of=observed_at)
    assert len(rows) == 1
    assert rows[0].observed_at == observed_at

    snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    assert snapshot["schema_version"] == 1
    assert snapshot["collector_version"]
    assert snapshot["source_parameters"] == {}
    assert snapshot["observed_at"] == observed_at.isoformat()
    assert snapshot["sources"]["working"]["status"] == "ok"
    assert snapshot["sources"]["broken"]["status"] == "error"
    assert len(snapshot["observations"]) == 1


def test_live_collection_requires_at_least_one_source() -> None:
    try:
        LiveCollector(sources={})
    except ValueError as exc:
        assert "source" in str(exc).lower()
    else:
        raise AssertionError("expected ValueError")
