from datetime import datetime, timezone

from top300.models import ForecastResult, TrendState
from top300.ranking import rank_forecasts


def result(topic: str, probability: float, ratio: float) -> ForecastResult:
    return ForecastResult(
        topic=topic,
        as_of=datetime(2026, 8, 24, tzinfo=timezone.utc),
        state=TrendState.IGNITION,
        prob_24h=probability,
        prob_72h=probability,
        prob_7d=probability,
        heuristic_score=probability * 100,
        demand_forecast=ratio,
        supply_forecast=1.0,
        opportunity_ratio=ratio,
        confidence=0.8,
        model_kind="heuristic",
    )


def test_rank_rewards_probability_and_supply_gap() -> None:
    ranked = rank_forecasts([result("crowded", 0.9, 0.8), result("gap", 0.82, 3.0)])
    assert ranked[0].forecast.topic == "gap"
