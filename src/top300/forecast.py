from __future__ import annotations

import math
import pickle
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression

from .core import opportunity_ratio, score_snapshot
from .lifecycle import classify_lifecycle
from .models import FeatureSnapshot, ForecastResult


@dataclass(frozen=True)
class TrainingRow:
    snapshot: FeatureSnapshot
    label_24h: int
    label_72h: int
    label_7d: int


def _logistic_from_score(score: float, center: float, scale: float) -> float:
    x = (score - center) / scale
    return 1.0 / (1.0 + math.exp(-x))


class HeuristicForecaster:
    def predict(self, topic: str, as_of: datetime, snapshot: FeatureSnapshot) -> ForecastResult:
        score = score_snapshot(snapshot)
        p24 = _logistic_from_score(score, 67, 9)
        p72 = _logistic_from_score(score, 60, 10)
        p7d = _logistic_from_score(score, 55, 11)
        demand = 0.5 + snapshot.demand_supply_forecast
        supply = max(0.05, 1.5 - snapshot.inverse_creator_saturation)
        ratio = opportunity_ratio(demand, supply)
        confidence = min(
            0.95,
            0.45
            + 0.4 * snapshot.cross_platform_confirmation
            + 0.1 * snapshot.expected_half_life,
        )
        return ForecastResult(
            topic=topic,
            as_of=as_of,
            state=classify_lifecycle(snapshot, score),
            prob_24h=p24,
            prob_72h=p72,
            prob_7d=p7d,
            heuristic_score=score,
            demand_forecast=demand,
            supply_forecast=supply,
            opportunity_ratio=ratio,
            confidence=confidence,
            model_kind="heuristic",
        )


class LearnedForecaster:
    def __init__(self) -> None:
        self.models: dict[str, LogisticRegression] = {}
        self.fallback = HeuristicForecaster()

    def fit(self, rows: list[TrainingRow]) -> "LearnedForecaster":
        if not rows:
            return self
        x = np.asarray([row.snapshot.as_vector() for row in rows], dtype=float)
        for horizon, attr in (("24h", "label_24h"), ("72h", "label_72h"), ("7d", "label_7d")):
            y = np.asarray([getattr(row, attr) for row in rows], dtype=int)
            if len(set(y.tolist())) < 2:
                continue
            model = LogisticRegression(max_iter=1000, class_weight="balanced", random_state=7)
            model.fit(x, y)
            self.models[horizon] = model
        return self

    def save(self, path: str | Path) -> None:
        with Path(path).open("wb") as handle:
            pickle.dump(self.models, handle)

    @classmethod
    def load(cls, path: str | Path) -> "LearnedForecaster":
        engine = cls()
        with Path(path).open("rb") as handle:
            engine.models = pickle.load(handle)
        return engine

    def predict(self, topic: str, as_of: datetime, snapshot: FeatureSnapshot) -> ForecastResult:
        if len(self.models) < 3:
            return self.fallback.predict(topic, as_of, snapshot)
        vector = np.asarray([snapshot.as_vector()], dtype=float)
        baseline = self.fallback.predict(topic, as_of, snapshot)
        return ForecastResult(
            topic=topic,
            as_of=as_of,
            state=baseline.state,
            prob_24h=float(self.models["24h"].predict_proba(vector)[0, 1]),
            prob_72h=float(self.models["72h"].predict_proba(vector)[0, 1]),
            prob_7d=float(self.models["7d"].predict_proba(vector)[0, 1]),
            heuristic_score=baseline.heuristic_score,
            demand_forecast=baseline.demand_forecast,
            supply_forecast=baseline.supply_forecast,
            opportunity_ratio=baseline.opportunity_ratio,
            confidence=min(0.98, baseline.confidence + 0.05),
            model_kind="learned",
        )
