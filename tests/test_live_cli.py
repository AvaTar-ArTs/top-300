import json
from datetime import datetime

import top300.cli as cli
from top300.observations import Observation
from top300.store import SignalStore


class FakeGoogle:
    def collect(
        self,
        *,
        observed_at: datetime,
        geography: str,
    ) -> list[Observation]:
        return [
            Observation(
                topic="google topic",
                source="google_trends",
                metric="demand",
                value=100,
                observed_at=observed_at,
                geography=geography,
            )
        ]


class FakeHackerNews:
    def collect(self, *, observed_at: datetime, limit: int) -> list[Observation]:
        return [
            Observation(
                topic=f"hn top {limit}",
                source="hacker_news",
                metric="attention",
                value=50,
                observed_at=observed_at,
            )
        ]


def test_collect_live_cli_uses_one_cutoff_and_writes_snapshot(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    monkeypatch.setattr(cli, "GoogleTrendsRSSAdapter", FakeGoogle)
    monkeypatch.setattr(cli, "HackerNewsAdapter", FakeHackerNews)
    store_path = tmp_path / "live.db"
    snapshot_path = tmp_path / "snapshot.json"
    observed_at = "2026-08-25T00:55:00+00:00"

    code = cli.main(
        [
            "collect-live",
            str(store_path),
            "--snapshot",
            str(snapshot_path),
            "--geo",
            "US",
            "--hn-limit",
            "5",
            "--observed-at",
            observed_at,
        ]
    )

    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["inserted"] == 2
    assert payload["successful_sources"] == 2
    assert snapshot_path.exists()
    snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    assert snapshot["source_parameters"]["google_trends"] == {"geography": "US"}
    assert snapshot["source_parameters"]["hacker_news"] == {"limit": 5}
    rows = SignalStore(store_path).query()
    assert len(rows) == 2
    assert {row.observed_at.isoformat() for row in rows} == {observed_at}
