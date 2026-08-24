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
        rows.append(BacktestRow(f"t{day}", start + timedelta(days=day), snap(value), label))
    report = walk_forward_backtest(rows, min_train=6)
    assert report.predictions > 0
    assert all(p.train_max_time < p.as_of for p in report.records)
