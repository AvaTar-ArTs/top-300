from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .forecast import LearnedForecaster, TrainingRow
from .models import FeatureSnapshot


@dataclass(frozen=True)
class BacktestRow:
    topic: str
    as_of: datetime
    snapshot: FeatureSnapshot
    label_24h: int


@dataclass(frozen=True)
class BacktestPrediction:
    topic: str
    as_of: datetime
    probability: float
    label: int
    train_max_time: datetime


@dataclass(frozen=True)
class BacktestReport:
    predictions: int
    brier: float
    precision_at_5: float
    records: list[BacktestPrediction]


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


def walk_forward_backtest(rows: list[BacktestRow], min_train: int = 20) -> BacktestReport:
    ordered = sorted(rows, key=lambda row: row.as_of)
    records: list[BacktestPrediction] = []
    for index in range(min_train, len(ordered)):
        current = ordered[index]
        train = ordered[:index]
        training_rows = [
            TrainingRow(
                snapshot=row.snapshot,
                label_24h=row.label_24h,
                label_72h=row.label_24h,
                label_7d=row.label_24h,
            )
            for row in train
        ]
        engine = LearnedForecaster().fit(training_rows)
        forecast = engine.predict(current.topic, current.as_of, current.snapshot)
        records.append(
            BacktestPrediction(
                topic=current.topic,
                as_of=current.as_of,
                probability=forecast.prob_24h,
                label=current.label_24h,
                train_max_time=train[-1].as_of,
            )
        )
    probabilities = [row.probability for row in records]
    labels = [row.label for row in records]
    return BacktestReport(
        predictions=len(records),
        brier=brier_score(probabilities, labels),
        precision_at_5=(
            precision_at_k(probabilities, labels, min(5, len(records))) if records else 0.0
        ),
        records=records,
    )
