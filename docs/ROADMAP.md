# TOP-300 Roadmap

## Phase 0 — Research scaffold ✅

- [x] define forecasting objective
- [x] distinguish detection from prediction
- [x] define trend lifecycle
- [x] define 24h / 72h / 7d horizons
- [x] document burst, change-point, Hawkes, diffusion, entropy, and lead/lag methods
- [x] create transparent v0 scoring baseline
- [x] add typed forecast schema
- [x] add unit tests for baseline utilities

## Phase 1 — Historical data foundation

Goal: make backtesting possible before pretending to have predictive accuracy.

- [ ] common observation schema
- [ ] immutable raw-snapshot storage
- [ ] DuckDB/Parquet local research store
- [ ] topic canonicalization + alias table
- [ ] time-window feature registry
- [ ] outcome-label registry
- [ ] source coverage metadata
- [ ] historical replay CLI

Acceptance criterion:

> Given a cutoff timestamp, the system can reconstruct features using only observations available at that time.

## Phase 2 — Baseline forecasting

Implement deliberately simple models first:

- [ ] seasonal robust baseline
- [ ] z-score / MAD anomaly detector
- [ ] derivative features
- [ ] EWMA forecasts
- [ ] naive persistence forecast
- [ ] trend-shape heuristics
- [ ] initial calibrated logistic/GBM classifier

Acceptance criterion:

> All later models must beat at least one clearly documented simple baseline out of sample.

## Phase 3 — Topic intelligence

- [ ] embedding-based alias clustering
- [ ] hierarchical topic graph
- [ ] semantic branch-rate feature
- [ ] related-query expansion
- [ ] over-merge / under-merge evaluation set

Acceptance criterion:

> A root topic and its microtrends remain separately forecastable while sharing lineage.

## Phase 4 — Burst and change-point stack

- [ ] Kleinberg-style burst detector
- [ ] Bayesian online change-point detection
- [ ] robust CUSUM alternative
- [ ] detector ensemble
- [ ] false-alarm benchmark

Acceptance criterion:

> Detect known historical regime shifts earlier than a raw +300% alert with fewer false positives.

## Phase 5 — Cross-platform lead/lag engine

- [ ] lagged cross-correlation
- [ ] Granger-style predictive tests
- [ ] learned source graph by niche
- [ ] lag confidence intervals
- [ ] relationship decay / re-estimation

Acceptance criterion:

> Demonstrate at least one domain where a leading source measurably improves future-target forecasts versus target history alone.

## Phase 6 — Propagation modeling

- [ ] creator-diversity entropy
- [ ] geographic entropy
- [ ] approximate trend reproduction rate
- [ ] derivative-content detection
- [ ] Hawkes-process features/model
- [ ] exogenous event controls

Acceptance criterion:

> Distinguish one-source publicity spikes from multi-source self-propagating breakouts with improved Precision@Top5%.

## Phase 7 — Demand/supply opportunity model

- [ ] demand forecast
- [ ] creator/upload supply forecast
- [ ] saturation estimate
- [ ] demand/supply opportunity ratio
- [ ] uncertainty-aware ranking

Acceptance criterion:

> Opportunity ranking beats ranking by demand forecast alone on a defined publishing-opportunity outcome.

## Phase 8 — Diffusion and trend-shape models

- [ ] FLASH classifier
- [ ] SUSTAINED classifier
- [ ] MULTI_WAVE classifier
- [ ] S_CURVE classifier
- [ ] SEASONAL classifier
- [ ] EVENT_DRIVEN classifier
- [ ] MEMETIC_CASCADE classifier
- [ ] Bass/logistic/Gompertz fits where appropriate
- [ ] decay models for flash trends

## Phase 9 — Forecast ensemble

- [ ] tree-based model
- [ ] temporal/state-space model
- [ ] propagation model outputs
- [ ] meta learner
- [ ] horizon-specific models
- [ ] probability calibration

Acceptance criterion:

> Calibrated probabilities and statistically meaningful out-of-sample improvement over baseline.

## Phase 10 — Evaluation laboratory

- [ ] walk-forward backtester
- [ ] Precision@K
- [ ] Precision@Top5%
- [ ] PR-AUC
- [ ] Brier score
- [ ] calibration curves
- [ ] mean useful lead time
- [ ] peak-time error
- [ ] forecast-growth error
- [ ] ablation tests
- [ ] model comparison reports

## Phase 11 — Live ranking service

- [ ] scheduler / collector orchestration
- [ ] rolling features
- [ ] forecast registry
- [ ] top-opportunity API
- [ ] alert thresholds
- [ ] source-health monitoring
- [ ] stale-data protection

Example output:

```json
{
  "topic": "example microtrend",
  "state": "ignition",
  "rank": 3,
  "p_top5_24h": 0.48,
  "p_top5_72h": 0.86,
  "p_top5_7d": 0.91,
  "expected_peak_hours": 78,
  "opportunity_ratio": 4.2,
  "confidence": 0.83
}
```

## Phase 12 — Research dashboard

Views:

- [ ] top forecast opportunities
- [ ] ignition map
- [ ] source propagation graph
- [ ] topic lineage graph
- [ ] demand vs supply forecast
- [ ] signal timeline
- [ ] calibration report
- [ ] historical prediction ledger

## Phase 13 — Production hardening

- [ ] typed configuration
- [ ] secrets management
- [ ] rate-limit handling
- [ ] retry/dead-letter strategy
- [ ] source terms/compliance audit
- [ ] structured logging
- [ ] model/data versioning
- [ ] reproducible releases
- [ ] CI lint/test/typecheck
- [ ] security review

## Research questions

1. Which platforms reliably lead YouTube attention by niche?
2. How stable are lead/lag relationships over time?
3. Does semantic branching add predictive lift after controlling for raw volume?
4. Is creator entropy a leading or confirming signal?
5. Can self-excitation parameters distinguish transient PR spikes from durable adoption?
6. What horizon produces the best tradeoff between precision and useful lead time?
7. How should forecast confidence degrade under missing-source coverage?
8. Does forecasting creator supply materially improve real publishing opportunity selection?
9. Which trend-shape classifier is most useful before model selection?
10. What is the simplest model that captures most of the benefit?

## Definition of success

TOP-300 succeeds if, under strict walk-forward testing, its highest-ranked forecasts consistently identify future breakout opportunities earlier and more precisely than:

1. current platform trending lists,
2. raw percentage growth,
3. raw popularity,
4. single-source forecasts,
5. naive persistence baselines.

The target is not clairvoyance. It is **measurably better early warning**.
