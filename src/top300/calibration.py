from __future__ import annotations

import math

import numpy as np
from sklearn.linear_model import LogisticRegression


class PlattCalibrator:
    def __init__(self) -> None:
        self.model: LogisticRegression | None = None

    def fit(self, probabilities: list[float], labels: list[int]) -> "PlattCalibrator":
        if not probabilities or len(set(labels)) < 2:
            return self
        eps = 1e-6
        logits = np.asarray(
            [
                [math.log(max(eps, min(1 - eps, p)) / (1 - max(eps, min(1 - eps, p))))]
                for p in probabilities
            ],
            dtype=float,
        )
        self.model = LogisticRegression(max_iter=500, random_state=7).fit(logits, labels)
        return self

    def transform(self, probability: float) -> float:
        if self.model is None:
            return probability
        eps = 1e-6
        p = max(eps, min(1 - eps, probability))
        logit = np.asarray([[math.log(p / (1 - p))]], dtype=float)
        return float(self.model.predict_proba(logit)[0, 1])
