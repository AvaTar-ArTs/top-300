from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import StrEnum
from typing import Any


class TrendState(StrEnum):
    EMERGING = "emerging"
    IGNITION = "ignition"
    BREAKOUT = "breakout"
    MAINSTREAM = "mainstream"
    SATURATED = "saturated"
    DECLINING = "declining"


@dataclass(slots=True)
class FeatureSnapshot:
    """Normalized 0..1 features for the v0 research scoring baseline."""

    lead_platform_activity: float
    change_point_probability: float
    burst_intensity: float
    acceleration: float
    jerk: float
    semantic_expansion: float
    geographic_expansion: float
    cross_platform_confirmation: float
    reproduction_rate: float
    creator_diversity: float
    self_excitation: float
    engagement_acceleration: float
    forecast_24h: float
    forecast_72h: float
    forecast_7d: float
    expected_saturation: float
    expected_half_life: float
    demand_supply_forecast: float
    inverse_creator_saturation: float

    def as_dict(self) -> dict[str, float]:
        return asdict(self)


@dataclass(slots=True)
class ForecastResult:
    topic: str
    current_state: TrendState
    score: float
    breakout_probability_24h: float
    breakout_probability_72h: float
    breakout_probability_7d: float
    expected_growth_24h: float | None = None
    expected_growth_72h: float | None = None
    expected_growth_7d: float | None = None
    burst_probability: float | None = None
    change_point_probability: float | None = None
    trend_reproduction_rate: float | None = None
    demand_forecast: float | None = None
    supply_forecast: float | None = None
    opportunity_ratio: float | None = None
    expected_peak_hours: float | None = None
    expected_half_life_days: float | None = None
    confidence: float | None = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["current_state"] = self.current_state.value
        return data
