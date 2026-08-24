from __future__ import annotations

import math
from collections import defaultdict
from datetime import datetime
from statistics import fmean, pstdev

from .core import finite_differences
from .models import FeatureSnapshot
from .observations import Observation
from .store import SignalStore


def _clip(value: float) -> float:
    return max(0.0, min(1.0, value))


def _sigmoid(value: float) -> float:
    if value >= 0:
        z = math.exp(-value)
        return 1 / (1 + z)
    z = math.exp(value)
    return z / (1 + z)


def _growth_signal(values: list[float]) -> float:
    if len(values) < 2:
        return 0.5
    previous, current = values[-2], values[-1]
    scale = max(abs(previous), 1.0)
    return _clip(0.5 + 0.5 * math.tanh((current - previous) / scale))


def _series_by_source(rows: list[Observation], metric: str) -> dict[str, list[float]]:
    grouped: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        if row.metric == metric:
            grouped[row.source].append(row.value)
    return dict(grouped)


def _metric_values(rows: list[Observation], metric: str) -> list[float]:
    return [row.value for row in rows if row.metric == metric]


class FeatureBuilder:
    def build(self, store: SignalStore, topic: str, as_of: datetime) -> FeatureSnapshot:
        rows = store.query(topic=topic, as_of=as_of)
        attention_by_source = _series_by_source(rows, "attention")
        aggregate = (
            [sum(values) for values in zip(*attention_by_source.values(), strict=False)]
            if attention_by_source
            else []
        )
        if not aggregate:
            aggregate = _metric_values(rows, "attention")

        if len(aggregate) >= 4:
            split = max(2, len(aggregate) // 2)
            baseline = aggregate[:split]
            recent = aggregate[split:]
            base_mean = fmean(baseline)
            sigma = pstdev(baseline) or max(abs(base_mean) * 0.1, 1.0)
            recent_mean = fmean(recent) if recent else aggregate[-1]
            z = (recent_mean - base_mean) / sigma
        else:
            z = 0.0

        diffs = finite_differences(aggregate)
        last_velocity = diffs["velocity"][-1] if diffs["velocity"] else 0.0
        last_accel = diffs["acceleration"][-1] if diffs["acceleration"] else 0.0
        last_jerk = diffs["jerk"][-1] if diffs["jerk"] else 0.0
        scale = max(abs(aggregate[-1]) if aggregate else 1.0, 1.0)

        abnormal_sources = 0
        for values in attention_by_source.values():
            if len(values) >= 2 and values[-1] > values[0] * 1.2:
                abnormal_sources += 1
        source_count = len(attention_by_source)
        cross_platform = abnormal_sources / source_count if source_count else 0.0

        related = _metric_values(rows, "related_query_count")
        geo = _metric_values(rows, "geo_count")
        creators = _metric_values(rows, "creator_count")
        engagement = _metric_values(rows, "engagement")
        demand = _metric_values(rows, "demand") or aggregate
        supply = _metric_values(rows, "supply") or creators

        positive_velocity_share = (
            sum(1 for value in diffs["velocity"] if value > 0) / len(diffs["velocity"])
            if diffs["velocity"]
            else 0.0
        )
        creator_diversity = 0.5
        if creators and aggregate and aggregate[-1] > 0:
            creator_diversity = _clip(creators[-1] / max(aggregate[-1], 1.0))

        demand_signal = _growth_signal(demand)
        supply_signal = _growth_signal(supply) if supply else 0.5
        gap = _clip(0.5 + (demand_signal - supply_signal) / 2)

        accel_norm = _clip(0.5 + 0.5 * math.tanh(last_accel / scale))
        jerk_norm = _clip(0.5 + 0.5 * math.tanh(last_jerk / scale))
        velocity_norm = _clip(0.5 + 0.5 * math.tanh(last_velocity / scale))
        burst = _clip(_sigmoid(z - 1.5))
        change = _clip(_sigmoid(abs(z) - 1.0))

        forecast_24h = _clip(0.35 * burst + 0.35 * accel_norm + 0.30 * cross_platform)
        forecast_72h = _clip(
            0.25 * burst
            + 0.25 * accel_norm
            + 0.25 * cross_platform
            + 0.25 * positive_velocity_share
        )
        forecast_7d = _clip(
            0.20 * velocity_norm
            + 0.20 * cross_platform
            + 0.30 * positive_velocity_share
            + 0.30 * gap
        )

        return FeatureSnapshot(
            lead_platform_activity=_clip(_sigmoid(z)),
            change_point_probability=change,
            burst_intensity=burst,
            acceleration=accel_norm,
            jerk=jerk_norm,
            semantic_expansion=_growth_signal(related) if related else 0.5,
            geographic_expansion=_growth_signal(geo) if geo else 0.5,
            cross_platform_confirmation=_clip(cross_platform),
            reproduction_rate=_growth_signal(creators) if creators else velocity_norm,
            creator_diversity=creator_diversity,
            self_excitation=_clip(positive_velocity_share),
            engagement_acceleration=_growth_signal(engagement) if engagement else velocity_norm,
            forecast_24h=forecast_24h,
            forecast_72h=forecast_72h,
            forecast_7d=forecast_7d,
            expected_saturation=_clip(1.0 - 0.5 * supply_signal),
            expected_half_life=_clip(positive_velocity_share),
            demand_supply_forecast=gap,
            inverse_creator_saturation=_clip(1.0 - supply_signal),
        )
