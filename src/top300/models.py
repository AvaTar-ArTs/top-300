from __future__ import annotations

from dataclasses import asdict, dataclass, fields
from datetime import datetime
from enum import StrEnum


class TrendState(StrEnum):
    EMERGING = "emerging"
    IGNITION = "ignition"
    BREAKOUT = "breakout"
    MAINSTREAM = "mainstream"
    SATURATED = "saturated"
    DECLINING = "declining"


@dataclass(frozen=True)
class FeatureSnapshot:
    lead_platform_activity: float = 0.0
    change_point_probability: float = 0.0
    burst_intensity: float = 0.0
    acceleration: float = 0.0
    jerk: float = 0.0
    semantic_expansion: float = 0.0
    geographic_expansion: float = 0.0
    cross_platform_confirmation: float = 0.0
    reproduction_rate: float = 0.0
    creator_diversity: float = 0.0
    self_excitation: float = 0.0
    engagement_acceleration: float = 0.0
    forecast_24h: float = 0.0
    forecast_72h: float = 0.0
    forecast_7d: float = 0.0
    expected_saturation: float = 0.0
    expected_half_life: float = 0.0
    demand_supply_forecast: float = 0.0
    inverse_creator_saturation: float = 0.0

    def as_dict(self) -> dict[str, float]:
        return asdict(self)

    def as_vector(self) -> list[float]:
        return [getattr(self, name) for name in self.feature_names()]

    @classmethod
    def feature_names(cls) -> list[str]:
        return [field.name for field in fields(cls)]


@dataclass(frozen=True)
class ForecastResult:
    topic: str
    as_of: datetime
    state: TrendState
    prob_24h: float
    prob_72h: float
    prob_7d: float
    heuristic_score: float
    demand_forecast: float
    supply_forecast: float
    opportunity_ratio: float | None
    confidence: float
    model_kind: str

    def as_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["as_of"] = self.as_of.isoformat()
        data["state"] = self.state.value
        return data
