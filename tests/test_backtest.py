from datetime import datetime, timedelta, timezone

from top300.backtest import BacktestRow, brier_score, precision_at_k, walk_forward_backtest
from top300.models import FeatureSnapshot


def snap(value: float) -> FeatureSnapshot:
    return FeatureSnapshot(**{name: value for name in FeatureSnapshot.feature_names()})


def test_brier_score() -> None:
    assert brier_score([0.0, 1.0], [0, 1]) == 0.0


def test_precision_at_k() -> None:
    assert precision_at_k([0.9, 0.8, 0.1], [1, 0, 1], 2) == 0.5


def test_walk_forward_uses_prior_rows_only() -> None:
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    rows = []
    for day in range(20):
        value = 0.1 if day < 10 else 0.9
        label = 0 if day < 10 else 1
        rows.append(
            BacktestRow(
                topic=f"t{day}",
                as_of=start + timedelta(days=day),
                snapshot=snap(value),
                label_24h=label,
                label_72h=label,
                label_7d=label,
            )
        )
    report = walk_forward_backtest(rows, min_train=6)
    assert report.predictions > 0
    assert all(prediction.train_max_time < prediction.as_of for prediction in report.records)


def test_walk_forward_keeps_horizon_labels_and_metrics_distinct() -> None:
    start = datetime(2026, 2, 1, tzinfo=timezone.utc)
    rows = []
    for day in range(30):
        rows.append(
            BacktestRow(
                topic=f"h{day}",
                as_of=start + timedelta(days=day),
                snapshot=snap((day % 10) / 10),
                label_24h=day % 2,
                label_72h=int(day % 3 != 0),
                label_7d=int(day >= 12),
            )
        )

    report = walk_forward_backtest(rows, min_train=12)

    assert set(report.horizons) == {"24h", "72h", "7d"}
    assert all(metric.predictions == report.predictions for metric in report.horizons.values())
    assert all(metric.baseline_brier >= 0 for metric in report.horizons.values())
    assert report.brier == report.horizons["24h"].brier
    assert report.precision_at_5 == report.horizons["24h"].precision_at_5
    assert any(
        record.labels["24h"] != record.labels["72h"]
        or record.labels["72h"] != record.labels["7d"]
        for record in report.records
    )
    assert all(set(record.probabilities) == {"24h", "72h", "7d"} for record in report.records)
    assert all(
        set(record.baseline_probabilities) == {"24h", "72h", "7d"}
        for record in report.records
    )


def test_walk_forward_baseline_uses_prior_labels_only() -> None:
    start = datetime(2026, 3, 1, tzinfo=timezone.utc)
    rows = [
        BacktestRow(
            topic=f"b{day}",
            as_of=start + timedelta(days=day),
            snapshot=snap(0.5),
            label_24h=int(day >= 4),
            label_72h=int(day >= 3),
            label_7d=int(day >= 2),
        )
        for day in range(8)
    ]

    report = walk_forward_backtest(rows, min_train=4)
    first = report.records[0]

    assert first.baseline_probabilities["24h"] == 0.0
    assert first.baseline_probabilities["72h"] == 0.25
    assert first.baseline_probabilities["7d"] == 0.5
