from __future__ import annotations

from .models import FeatureSnapshot


WEIGHTS: dict[str, float] = {
    "lead_platform_activity": 8,
    "change_point_probability": 7,
    "burst_intensity": 6,
    "acceleration": 5,
    "jerk": 4,
    "semantic_expansion": 3,
    "geographic_expansion": 2,
    "cross_platform_confirmation": 8,
    "reproduction_rate": 7,
    "creator_diversity": 5,
    "self_excitation": 5,
    "engagement_acceleration": 5,
    "forecast_24h": 7,
    "forecast_72h": 7,
    "forecast_7d": 5,
    "expected_saturation": 3,
    "expected_half_life": 3,
    "demand_supply_forecast": 6,
    "inverse_creator_saturation": 4,
}


def _validate_unit_interval(name: str, value: float) -> None:
    if not 0 <= value <= 1:
        raise ValueError(f"{name} must be between 0 and 1, got {value!r}")


def score_snapshot(snapshot: FeatureSnapshot) -> float:
    """Return the v0 weighted opportunity score on a 0..100 scale.

    This is an intentionally transparent research baseline. Production versions
    should learn/calibrate weights from walk-forward historical backtests.
    """

    values = snapshot.as_dict()
    for name, value in values.items():
        _validate_unit_interval(name, value)

    score = sum(values[name] * weight for name, weight in WEIGHTS.items())
    return round(score, 3)


def percent_growth(previous: float, current: float) -> float | None:
    """Return percent growth, or None when the baseline is zero.

    Zero baselines are deliberately not converted to infinity. A forecasting
    engine should route those observations through absolute-volume and anomaly
    checks instead of creating misleading growth percentages.
    """

    if previous == 0:
        return None
    return ((current - previous) / abs(previous)) * 100


def finite_differences(values: list[float]) -> dict[str, list[float]]:
    """Compute discrete velocity, acceleration, and jerk series."""

    velocity = [b - a for a, b in zip(values, values[1:])]
    acceleration = [b - a for a, b in zip(velocity, velocity[1:])]
    jerk = [b - a for a, b in zip(acceleration, acceleration[1:])]
    return {
        "velocity": velocity,
        "acceleration": acceleration,
        "jerk": jerk,
    }


def opportunity_ratio(demand_forecast: float, supply_forecast: float) -> float | None:
    """Forecast demand/supply ratio; None means supply is zero/undefined."""

    if supply_forecast == 0:
        return None
    return demand_forecast / supply_forecast
