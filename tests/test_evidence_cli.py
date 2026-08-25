import csv
import json
from datetime import datetime, timezone

from top300 import cli
from top300.historical import TrendEpisode
from top300.models import FeatureSnapshot


def test_backtest_cli_reports_each_horizon_and_baseline(tmp_path, capsys) -> None:
    path = tmp_path / "backtest.csv"
    names = FeatureSnapshot.feature_names()
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["topic", "as_of", *names, "label_24h", "label_72h", "label_7d"],
        )
        writer.writeheader()
        for index in range(12):
            value = 0.1 if index < 6 else 0.9
            writer.writerow(
                {
                    "topic": f"topic-{index}",
                    "as_of": datetime(2026, 1, index + 1, tzinfo=timezone.utc).isoformat(),
                    **{name: value for name in names},
                    "label_24h": int(index >= 6),
                    "label_72h": int(index >= 5),
                    "label_7d": int(index >= 4),
                }
            )

    code = cli.main(["backtest", str(path), "--min-train", "6"])
    payload = json.loads(capsys.readouterr().out)

    assert code == 0
    assert set(payload["horizons"]) == {"24h", "72h", "7d"}
    assert "baseline_brier" in payload["horizons"]["24h"]
    assert "brier_skill" in payload["horizons"]["7d"]


def test_archive_sample_cli_writes_bounded_jsonl(tmp_path, monkeypatch, capsys) -> None:
    class FakeArchive:
        def stream(self, **kwargs):
            assert kwargs["geography"] == "US"
            assert kwargs["limit"] == 2
            return iter(
                [
                    TrendEpisode(
                        topic="alpha",
                        geography="US",
                        started=datetime(2026, 1, 2, tzinfo=timezone.utc),
                        volume_floor=20_000,
                    ),
                    TrendEpisode(
                        topic="beta",
                        geography="US",
                        started=datetime(2026, 1, 3, tzinfo=timezone.utc),
                        aliases=("beta alias",),
                    ),
                ]
            )

    monkeypatch.setattr(cli, "GoogleTrendArchiveAdapter", FakeArchive, raising=False)
    output = tmp_path / "episodes.jsonl"
    code = cli.main(
        [
            "archive-sample",
            "--output",
            str(output),
            "--geo",
            "US",
            "--start",
            "2026-01-01T00:00:00Z",
            "--end",
            "2026-01-31T23:59:59Z",
            "--limit",
            "2",
        ]
    )
    payload = json.loads(capsys.readouterr().out)
    rows = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]

    assert code == 0
    assert payload["episodes"] == 2
    assert [row["topic"] for row in rows] == ["alpha", "beta"]
    assert rows[1]["aliases"] == ["beta alias"]
