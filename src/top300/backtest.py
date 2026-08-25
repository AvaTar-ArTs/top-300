from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .forecast import LearnedForecaster, TrainingRow
from .models import FeatureSnapshot

_HORIZONS = ("24h", "72h", "7d")
_LABEL_ATTRS = {
    "24h": "label_24h",
    "72h": "label_72h",
    "7d": "label_7d",
}
_PROB_ATTRS = {
    "24h": "prob_24h",
    "72h": "prob_72h",
    "7d": "prob_7d",
}


@dataclass(frozen=True)
class BacktestRow:
    topic: str
    as_of: datetime
    snapshot: FeatureSnapshot
    label_24h: int
    label_72h: int
    label_7d: int

    def __post_init__(self) -> None:
        if self.as_of.tzinfo is None:
            raise ValueError("as_of must be timezone-aware")
        for horizon, attr in _LABEL_ATTRS.items():
            if getattr(self, attr) not in {0, 1}:
                raise ValueError(f"{horizon} label must be 0 or 1")

    @property
    def labels(self) -> dict[str, int]:
        return {horizon: getattr(self, attr) for horizon, attr in _LABEL_ATTRS.items()}


@dataclass(frozen=True)
class BacktestPrediction:
    topic: str
    as_of: datetime
    probabilities: dict[str, float]
    labels: dict[str, int]
    baseline_probabilities: dict[str, float]
    train_max_time: datetime

    @property
    def probability(self) -> float:
        """Compatibility alias for the historical 24h headline probability."""
        return self.probabilities["24h"]

    @property
    def label(self) -> int:
        """Compatibility alias for the historical 24h headline label."""
        return self.labels["24h"]


@dataclass(frozen=True)
class HorizonBacktestReport:
    horizon: str
    predictions: int
    brier: float
    precision_at_5: float
    baseline_brier: float
    brier_skill: float


@dataclass(frozen=True)
class BacktestReport:
    predictions: int
    horizons: dict[str, HorizonBacktestReport]
    records: list[BacktestPrediction]

    @property
    def brier(self) -> float:
        """Compatibility alias for the 24h Brier score."""
        return self.horizons["24h"].brier

    @property
    def precision_at_5(self) -> float:
        """Compatibility alias for the 24h precision@5 score."""
        return self.horizons["24h"].precision_at_5


def brier_score(probabilities: list[float], labels: list[int]) -> float:
    if not probabilities:
        return 0.0
    return (
        sum((p - y) ** 2 for p, y in zip(probabilities, labels, strict=True))
        / len(probabilities)
    )


def precision_at_k(probabilities: list[float], labels: list[int], k: int) -> float:
    if not probabilities or k <= 0:
        return 0.0
    indexes = sorted(range(len(probabilities)), key=probabilities.__getitem__, reverse=True)[:k]
    return sum(labels[index] for index in indexes) / len(indexes)


def _base_rate(rows: list[BacktestRow], horizon: str) -> float:
    if not rows:
        return 0.0
    attr = _LABEL_ATTRS[horizon]
    return sum(getattr(row, attr) for row in rows) / len(rows)


def _horizon_report(
    records: list[BacktestPrediction],
    horizon: str,
) -> HorizonBacktestReport:
    probabilities = [record.probabilities[horizon] for record in records]
    labels = [record.labels[horizon] for record in records]
    baselines = [record.baseline_probabilities[horizon] for record in records]
    model_brier = brier_score(probabilities, labels)
    baseline_brier = brier_score(baselines, labels)
    return HorizonBacktestReport(
        horizon=horizon,
        predictions=len(records),
        brier=model_brier,
        precision_at_5=(
            precision_at_k(probabilities, labels, min(5, len(records))) if records else 0.0
        ),
        baseline_brier=baseline_brier,
        brier_skill=baseline_brier - model_brier,
    )


def walk_forward_backtest(rows: list[BacktestRow], min_train: int = 20) -> BacktestReport:
    if min_train < 1:
        raise ValueError("min_train must be at least 1")
    ordered = sorted(rows, key=lambda row: row.as_of)
    records: list[BacktestPrediction] = []
    for index in range(min_train, len(ordered)):
        current = ordered[index]
        train = ordered[:index]
        training_rows = [
            TrainingRow(
                snapshot=row.snapshot,
                label_24h=row.label_24h,
                label_72h=row.label_72h,
                label_7d=row.label_7d,
            )
            for row in train
        ]
        engine = LearnedForecaster().fit(training_rows)
        forecast = engine.predict(current.topic, current.as_of, current.snapshot)
        probabilities = {
            horizon: float(getattr(forecast, attr))
            for horizon, attr in _PROB_ATTRS.items()
        }
        baselines = {horizon: _base_rate(train, horizon) for horizon in _HORIZONS}
        records.append(
            BacktestPrediction(
                topic=current.topic,
                as_of=current.as_of,
                probabilities=probabilities,
                labels=current.labels,
                baseline_probabilities=baselines,
                train_max_time=train[-1].as_of,
            )
        )
    horizons = {horizon: _horizon_report(records, horizon) for horizon in _HORIZONS}
    return BacktestReport(
        predictions=len(records),
        horizons=horizons,
        records=records,
    )
