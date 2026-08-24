from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

from .backtest import BacktestRow
from .forecast import TrainingRow
from .models import FeatureSnapshot


def _snapshot_from_row(row: dict[str, str]) -> FeatureSnapshot:
    values = {name: float(row[name]) for name in FeatureSnapshot.feature_names()}
    return FeatureSnapshot(**values)


def load_training_rows(path: str | Path) -> list[TrainingRow]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    return [
        TrainingRow(
            snapshot=_snapshot_from_row(row),
            label_24h=int(row["label_24h"]),
            label_72h=int(row["label_72h"]),
            label_7d=int(row["label_7d"]),
        )
        for row in rows
    ]


def load_backtest_rows(path: str | Path) -> list[BacktestRow]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    return [
        BacktestRow(
            topic=row["topic"],
            as_of=datetime.fromisoformat(row["as_of"].replace("Z", "+00:00")),
            snapshot=_snapshot_from_row(row),
            label_24h=int(row["label_24h"]),
        )
        for row in rows
    ]
