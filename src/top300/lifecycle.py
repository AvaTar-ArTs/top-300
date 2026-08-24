from __future__ import annotations

from .models import FeatureSnapshot, TrendState


def classify_lifecycle(snapshot: FeatureSnapshot, score: float) -> TrendState:
    if snapshot.acceleration < 0.35 and snapshot.self_excitation < 0.35:
        return TrendState.DECLINING
    if score >= 80 and snapshot.inverse_creator_saturation < 0.35:
        return TrendState.SATURATED
    if score >= 75 and snapshot.acceleration < 0.55:
        return TrendState.MAINSTREAM
    if score >= 60:
        return TrendState.BREAKOUT
    if score >= 35 or snapshot.change_point_probability >= 0.65:
        return TrendState.IGNITION
    return TrendState.EMERGING
