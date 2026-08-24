from __future__ import annotations

from dataclasses import dataclass

from .models import ForecastResult


@dataclass(frozen=True)
class RankedForecast:
    rank: int
    opportunity_score: float
    forecast: ForecastResult

    def as_dict(self) -> dict[str, object]:
        return {
            "rank": self.rank,
            "opportunity_score": self.opportunity_score,
            **self.forecast.as_dict(),
        }


def _score(result: ForecastResult) -> float:
    probability = 0.5 * result.prob_24h + 0.3 * result.prob_72h + 0.2 * result.prob_7d
    ratio = result.opportunity_ratio if result.opportunity_ratio is not None else 1.0
    gap_bonus = min(2.5, max(0.25, ratio)) / 2.5
    return 100 * (0.75 * probability + 0.20 * gap_bonus + 0.05 * result.confidence)


def rank_forecasts(results: list[ForecastResult]) -> list[RankedForecast]:
    ordered = sorted(results, key=_score, reverse=True)
    return [
        RankedForecast(index + 1, round(_score(row), 3), row)
        for index, row in enumerate(ordered)
    ]
