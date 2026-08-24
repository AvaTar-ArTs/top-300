# TOP-300

**Forecast tomorrow's breakout topics before they become obvious.**

TOP-300 is an experimental trend-forecasting engine designed to estimate which topics are most likely to enter the top 1–5% of attention over the next 24 hours, 72 hours, and 7 days.

It is deliberately different from a trending dashboard. A trending dashboard asks **what is hot now?** TOP-300 asks **what has the highest probability of becoming abnormally hot next?**

## Core thesis

A strong early trend is not necessarily the topic growing fastest right now. The strongest candidate is the topic whose behavior has changed abnormally, is propagating from leading communities into lagging ones, is becoming self-sustaining, is expanding semantically and geographically, and whose forecast demand is likely to outrun content supply.

TOP-300 combines:

- baseline-aware anomaly detection
- velocity, acceleration, and jerk
- statistical burst detection
- online change-point detection
- cross-platform lead/lag modeling
- Granger-style predictive testing
- self-exciting/Hawkes-process signals
- diffusion and adoption-curve modeling
- semantic branch-rate measurement
- geographic and creator-diversity entropy
- trend reproduction-rate estimates
- demand forecasting
- supply forecasting
- calibrated breakout probabilities
- walk-forward backtesting with strict no-future leakage

## Forecast targets

For every topic, the system should eventually estimate:

```text
P(top 5% of attention within 24h)
P(top 5% of attention within 72h)
P(top 5% of attention within 7d)
expected growth
expected time to peak
expected saturation
expected half-life
expected creator saturation
expected demand/supply opportunity ratio
confidence / calibration quality
```

## Why +300% is not the forecast

`+300% growth` is useful as an alert feature, but it is not a forecasting methodology. Tiny denominators, seasonal effects, one-account spikes, and external publicity can all create spectacular percentages that have little predictive value.

TOP-300 treats raw growth as one feature among many. The actual decision is probabilistic.

## Trend lifecycle

```text
EMERGING → IGNITION → BREAKOUT → MAINSTREAM → SATURATED → DECLINING
```

The primary hunting zone is **IGNITION → BREAKOUT**.

## Forecast horizons

| Horizon | Typical use | Dominant signals |
|---|---|---|
| 6–24 hours | breaking topic, reaction, short-form | bursts, change points, jerk, lead-platform diffusion |
| 2–7 days | feature, comparison, experiment | search acceleration, creator adoption, semantic expansion, outlier clustering |
| 2–8 weeks | durable opportunity, major investment | adoption curves, developer/community activity, persistence, event graph |

## Initial scoring model

TOP-300 v0 uses a research-informed feature grouping, not a claim of production-grade predictive accuracy:

```text
EARLY SIGNALS                         35
  lead-platform activity              8
  change-point probability            7
  burst intensity                     6
  acceleration                        5
  jerk                                4
  semantic expansion                  3
  geographic expansion                2

PROPAGATION                           30
  cross-platform confirmation         8
  trend reproduction rate             7
  creator diversity                   5
  self-excitation                     5
  engagement acceleration             5

FUTURE POTENTIAL                     25
  24h forecast                        7
  72h forecast                        7
  7d forecast                         5
  expected saturation                 3
  expected half-life                  3

MARKET GAP                            10
  demand/supply forecast              6
  creator saturation                  4
```

The weights are hypotheses to be backtested and learned, not sacred constants.

## Repository layout

```text
.
├── docs/
│   ├── ARCHITECTURE.md
│   ├── DATA_SOURCES.md
│   ├── FORECASTING_METHODS.md
│   └── ROADMAP.md
├── examples/
│   └── sample_forecast.json
├── src/top300/
│   ├── __init__.py
│   ├── core.py
│   └── models.py
├── tests/
│   └── test_core.py
├── pyproject.toml
└── README.md
```

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
pytest
```

Example:

```python
from top300 import FeatureSnapshot, score_snapshot

snapshot = FeatureSnapshot(
    lead_platform_activity=0.9,
    change_point_probability=0.95,
    burst_intensity=0.88,
    acceleration=0.82,
    jerk=0.75,
    semantic_expansion=0.7,
    geographic_expansion=0.6,
    cross_platform_confirmation=0.9,
    reproduction_rate=0.8,
    creator_diversity=0.72,
    self_excitation=0.84,
    engagement_acceleration=0.79,
    forecast_24h=0.68,
    forecast_72h=0.86,
    forecast_7d=0.91,
    expected_saturation=0.75,
    expected_half_life=0.68,
    demand_supply_forecast=0.9,
    inverse_creator_saturation=0.77,
)

print(score_snapshot(snapshot))
```

## Research principles

1. **No hindsight leakage.** Backtests must only use data available at the simulated decision time.
2. **Normalize against baseline.** Raw percentage growth is insufficient.
3. **Forecast demand and supply separately.** A huge trend can still be a poor opportunity if content supply grows faster.
4. **Learn lead platforms by niche.** Different domains propagate differently.
5. **Probability must be calibrated.** An 80% breakout forecast should become true roughly 80% of the time.
6. **Measure precision at the top.** The key operating metric is `Precision@TopK` / `Precision@Top5%`, not vanity accuracy.
7. **Use ensembles.** Change-point, burst, Hawkes, diffusion, tree-based, and temporal models each capture different structures.

## Research foundation

The design draws on established work in burst detection, nowcasting with search data, self-exciting processes for online popularity, diffusion modeling, time-series forecasting, lead/lag inference, probabilistic calibration, and strict walk-forward evaluation.

See [docs/FORECASTING_METHODS.md](docs/FORECASTING_METHODS.md) for the detailed methodology and references.

## Status

**v0 research scaffold.** The repository currently provides the architecture, schemas, scoring baseline, tests, and implementation roadmap. Data collectors and trained forecast models are intentionally separate milestones so they can be validated rather than disguised as finished prediction machinery.

## License

MIT
