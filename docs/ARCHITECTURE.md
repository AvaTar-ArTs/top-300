# TOP-300 Architecture

## System objective

TOP-300 ingests weak signals from multiple sources, clusters them into canonical topics, estimates whether each topic has entered an abnormal propagation regime, forecasts breakout probability at multiple horizons, forecasts content-supply response, and ranks opportunities by expected demand/supply asymmetry.

## High-level architecture

```text
                  TOP-300 FORECAST ENGINE
                           │
            ┌──────────────┴──────────────┐
            │                             │
      SIGNAL INGESTION               EVENT GRAPH
            │                             │
 Google Trends                     launches
 TikTok                            announcements
 Reddit                            releases
 YouTube                           news
 GitHub                            scheduled events
 news                              cultural events
 social                            product updates
            │                             │
            └──────────────┬──────────────┘
                           ↓
                   TOPIC CLUSTERING
                           ↓
                    BASELINE MODEL
                           ↓
                  ANOMALY DETECTION
                           │
             ┌─────────────┼─────────────┐
             ↓             ↓             ↓
          BURSTS       CHANGE POINTS    JERK
             └─────────────┬─────────────┘
                           ↓
                   LEAD-LAG ENGINE
                           ↓
                    PROPAGATION MODEL
                           │
                ┌──────────┴──────────┐
                ↓                     ↓
             HAWKES               DIFFUSION
                └──────────┬──────────┘
                           ↓
                    SUPPLY FORECAST
                           ↓
                    DEMAND FORECAST
                           ↓
                  OPPORTUNITY FORECAST
                           ↓
             ┌─────────────┼─────────────┐
             ↓             ↓             ↓
            24H           72H            7D
             ↓             ↓             ↓
                BREAKOUT PROBABILITY
                           ↓
                   RANK / ALERT / API
```

## Modules

### 1. Collectors

Each collector should emit a common observation envelope rather than leaking source-specific payloads downstream.

Suggested envelope:

```json
{
  "source": "youtube",
  "observed_at": "2026-08-24T18:00:00Z",
  "entity_type": "video",
  "entity_id": "...",
  "topic_text": "...",
  "metrics": {
    "views": 12345,
    "likes": 500,
    "creator_id": "..."
  },
  "geo": "US",
  "language": "en",
  "raw_ref": "..."
}
```

Collectors should preserve raw snapshots for reproducible backtests.

### 2. Topic identity and clustering

The same trend appears under aliases, acronyms, misspellings, versions, hashtags, and related phrases. The topic layer should maintain:

- canonical topic ID
- canonical name
- aliases
- embedding centroid(s)
- parent/child topic graph
- related query clusters
- entity links
- first-seen timestamp

Avoid over-merging. `AI video` and `Seedance 2.5 character consistency` may belong to the same hierarchy but should remain forecastable at different granularity.

### 3. Feature store

Persist time-indexed, source-aware features. Example namespaces:

```text
baseline.*
derivative.velocity.*
derivative.acceleration.*
derivative.jerk.*
burst.*
change_point.*
lead_lag.*
propagation.*
entropy.creator
entropy.geo
semantic.branch_rate
outlier.youtube
forecast.demand
forecast.supply
```

Feature definitions must be versioned.

### 4. Baseline model

Estimate expected activity by source/topic/time context. Start simple with robust seasonal medians and exponentially weighted statistics, then compare more sophisticated state-space models.

### 5. Event graph

External events can generate attention without organic propagation. Represent known triggers such as:

- product announcements
- release dates
- patches
- conferences
- scheduled sports/entertainment events
- major news

This makes exogenous-vs-endogenous interpretation possible.

### 6. Anomaly stack

Run several detectors in parallel:

- robust z-score anomaly
- burst state
- online change-point probability
- derivative features

No one detector should own the final verdict.

### 7. Lead-lag engine

Learn source ordering by domain and horizon. Persist relationships with uncertainty and decay old relationships as platform behavior changes.

### 8. Propagation engine

Estimate whether a topic is reproducing:

- creator adoption rate
- cross-platform spread
- derivative content rate
- engagement acceleration
- Hawkes/self-excitation features
- geographic spread
- semantic spread

### 9. Demand model

Predict future attention/search/consumption intensity per horizon.

### 10. Supply model

Predict competing content creation:

- creator count
- upload count
- publication velocity
- duplicate/near-duplicate concept count
- expected ranking competition

### 11. Opportunity model

Rank by a calibrated function of future demand, future supply, lead time, confidence, and expected half-life.

A useful raw diagnostic remains:

```text
opportunity_ratio = demand_forecast / supply_forecast
```

but production ranking should also account for uncertainty.

### 12. Forecast ensemble

Candidate stack:

```text
interpretable baseline
+ gradient-boosted trees
+ change-point probabilities
+ Hawkes features
+ diffusion fit features
+ temporal model
→ meta learner
→ calibration layer
```

Always retain simple baselines for comparison.

### 13. Evaluation service

Every prediction becomes an immutable forecast record with:

- issued_at
- input data cutoff
- feature version
- model version
- horizon
- probability
- rank
- confidence
- eventual outcome

This enables proper walk-forward evaluation.

## Suggested storage

Early prototype:

- Parquet for raw observations and snapshots
- DuckDB for local analytics/backtests
- SQLite/Postgres for metadata and forecast registry

Larger deployment:

- object storage for immutable raw events
- Postgres for canonical entities
- time-series/columnar warehouse for features
- Redis only for operational caching, never as sole historical storage

## Pipeline modes

### Historical replay

```text
raw snapshots → historical cutoff → features → forecast → score outcome
```

### Live mode

```text
collect → normalize → cluster → update features → forecast → calibrate → rank
```

### Research mode

```text
feature/model candidate → walk-forward replay → compare against baseline → promote/reject
```

## API sketch

```text
GET /v1/topics/hot?horizon=72h&limit=20
GET /v1/topics/{id}
GET /v1/topics/{id}/forecast
GET /v1/topics/{id}/signals
GET /v1/models/calibration
GET /v1/backtests/{run_id}
```

## Reliability rules

1. Never overwrite historical predictions.
2. Persist source timestamps and ingestion timestamps separately.
3. Record missing-source states explicitly.
4. Do not compare normalized platform metrics as if they share units.
5. Version outcome definitions.
6. Version clustering behavior.
7. Separate observed values from inferred values.
8. Attach confidence/coverage metadata to every forecast.
9. Flag one-source dominance.
10. Reject model upgrades that do not beat the baseline out of sample.

## Security and compliance

- Prefer official APIs and documented exports.
- Respect platform terms, robots policies, rate limits, and privacy requirements.
- Do not collect private-person data not needed for aggregate forecasting.
- Store only the minimal raw content necessary for reproducibility.
- Treat API credentials as runtime secrets, never repository configuration.
