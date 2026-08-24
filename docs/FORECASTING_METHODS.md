# Forecasting Methods

TOP-300 is designed around a simple distinction:

> Detection asks what is rising now. Forecasting asks what is most likely to rise next.

This document turns that distinction into a research program.

## 1. Baseline-aware anomaly detection

Raw percentage growth is not enough. A topic going from 2 mentions to 10 mentions is up 400%, but may still be noise.

For each topic and source, estimate an expected baseline that accounts for:

- hour of day
- day of week
- seasonality
- holidays and scheduled events
- source-specific volatility
- topic age
- geography

A simple standardized anomaly is:

```text
z_t = (x_t - μ_t) / σ_t
```

where `x_t` is observed activity, `μ_t` expected activity, and `σ_t` historical variation.

## 2. Velocity, acceleration, and jerk

Let attention be `A_t`.

```text
velocity:      v_t = A_t - A_(t-1)
acceleration:  a_t = v_t - v_(t-1)
jerk:          j_t = a_t - a_(t-1)
```

A topic whose absolute growth is moderate but whose acceleration and jerk are sharply positive may be more useful than a topic with high but steady growth.

## 3. Burst detection

Jon Kleinberg's classic burst-detection model treats streams as moving between latent states with different activity intensities. This is a stronger framing than a single growth threshold because it asks whether the observation stream has entered a statistically different regime.

Suggested TOP-300 abstraction:

```text
NORMAL → ELEVATED → BURST_1 → BURST_2 → EXTREME
```

Reference:

- Kleinberg, J. (2002), *Bursty and Hierarchical Structure in Streams*. DOI: 10.1145/775047.775061

## 4. Online change-point detection

Change-point methods should estimate whether the generating process itself has changed. Candidate monitored properties include:

- mean activity
- variance
- growth rate
- creator count
- engagement rate
- geographic distribution
- query composition

The useful moment is often the transition, not the later peak.

## 5. Cross-platform lead/lag modeling

Different sources may lead different niches. A technology topic might appear first in GitHub or specialist communities, while a music or meme trend may be led by short-form video platforms.

TOP-300 should learn this from historical data rather than hard-code it.

For each niche and source pair, estimate whether earlier values from source A improve forecasts of later source B. Candidate methods:

- lagged cross-correlation
- Granger-style predictive tests
- vector autoregression where appropriate
- transfer entropy / nonlinear dependency measures for later research

The output should be a learned lead/lag matrix per domain.

## 6. Self-excitation and Hawkes processes

Social events are not independent. One post can induce reactions, remixes, replies, searches, and derivative posts.

A Hawkes-process intensity can be written conceptually as:

```text
λ(t) = μ + Σ g(t - t_i)
```

where `μ` is background intensity and past events temporarily raise future event intensity.

This helps distinguish:

- exogenous attention: a press release, launch, scheduled event, celebrity post
- endogenous propagation: the topic begins reproducing through the network itself

Reference:

- Rizoiu et al. (2017), *Expecting to be HIP: Hawkes Intensity Processes for Social Media Popularity*. Earlier arXiv version: arXiv:1602.06033.

## 7. Trend reproduction rate

TOP-300 can maintain an approximate reproduction metric inspired by epidemic modeling:

```text
R_t ≈ derivative activity / current active sources
```

Possible proxies:

- new creators / active creators
- derivative posts / source posts
- new query clusters / prior query clusters
- remixes / originals

The number is operational rather than causal unless the attribution model is validated.

## 8. Creator diversity and entropy

A spike dominated by one giant account is less robust than similar attention distributed across many independent creators.

Creator entropy:

```text
H = -Σ p_i log(p_i)
```

where `p_i` is each creator's share of attention.

Track both absolute creator count and distribution entropy.

## 9. Semantic expansion

Maturing trends tend to create branches. A root query may expand into:

```text
product
product review
product tutorial
product vs competitor
product fail
product workflow
product alternatives
```

Candidate feature:

```text
semantic_branch_rate = new stable query/topic clusters / hour
```

This should be measured using embeddings plus density/topic clustering, while preserving a human-readable canonical topic graph.

## 10. Geographic diffusion

Track whether attention remains concentrated or spreads into new regions.

Useful features:

- number of active regions
- geo entropy
- rate of new-region adoption
- cross-country lag structure

Google Trends can provide relative regional-interest signals, but normalized values must be treated carefully.

## 11. YouTube outlier modeling

Raw view count is not an adequate signal. Estimate expected performance for each creator/video using factors such as:

- channel baseline views
- subscriber scale
- content format
- video age
- normal VPH curve
- topic baseline

Then compute an outlier score relative to expectation.

A cluster of independent videos becoming 4x–20x outliers on the same emerging topic can be a strong propagation signal.

## 12. Demand and supply forecasts

TOP-300 should forecast both sides of the opportunity.

```text
D(t+h) = future attention/search demand
S(t+h) = future content/creator supply

Opportunity(t+h) = D(t+h) / S(t+h)
```

This is one of the most important design choices. A huge trend may be a poor publishing opportunity if supply is growing faster than demand.

## 13. Diffusion curves

Longer-lived adoption trends may be modeled using logistic, Gompertz, or Bass-style diffusion models.

A logistic form:

```text
N(t) = K / (1 + exp(-r(t - t0)))
```

can estimate saturation `K`, growth rate `r`, and midpoint `t0` when the trend actually follows an adoption curve.

Do not force diffusion models onto flash-news spikes.

## 14. Trend-shape classification

Classify candidate time series before choosing a forecasting family:

- FLASH
- SUSTAINED
- MULTI_WAVE
- S_CURVE
- SEASONAL
- EVENT_DRIVEN
- MEMETIC_CASCADE

Possible model families:

| Shape | Candidate models |
|---|---|
| Flash | Hawkes + exponential decay |
| Sustained | ETS / ARIMA / state-space |
| Adoption | logistic / Gompertz / Bass |
| Seasonal | seasonal state-space / Prophet-like decomposition |
| Meme | Hawkes + network features |
| Event-driven | event priors + pre-event search ramp |

## 15. Multi-horizon forecasting

Maintain separate targets:

- 6–24h
- 2–7d
- 2–8w

Do not assume one model or feature mix works equally well at all horizons.

## 16. Probabilistic outputs

TOP-300 should return calibrated probabilities, for example:

```text
P(top 5% in 24h) = 0.41
P(top 5% in 72h) = 0.79
P(top 5% in 7d) = 0.88
```

Probability is more operationally useful than a decorative score because it supports thresholds, expected-value decisions, and calibration testing.

## 17. Bayesian/streaming updates

As new evidence arrives, update the posterior forecast rather than rebuilding the interpretation from scratch.

Conceptually:

```text
P(T | D_new) ∝ P(D_new | T) P(T)
```

A candidate could move from 34% to 90% breakout probability as multiple independent signals confirm propagation.

## 18. Ensembles

Recommended eventual ensemble:

```text
change-point model ─┐
burst model ────────┤
gradient boosting ──┤
Hawkes features ─────┤→ meta-model → calibrated forecast
diffusion model ─────┤
temporal model ──────┘
```

LLMs are useful for semantic clustering, event extraction, topic naming, and explanation, but numerical probability should be grounded in measurable historical time-series features.

## 19. Walk-forward backtesting

Backtesting is mandatory.

For each historical timestamp `T`:

1. expose only data that existed at or before `T`
2. generate forecasts for the configured horizon
3. observe what actually happened after `T`
4. store forecast, outcome, lead time, and error

Primary metrics:

- Precision@K
- Precision@Top5%
- recall
- PR-AUC
- ROC-AUC where useful
- Brier score
- calibration error
- mean lead time
- peak timing error
- growth forecast error

For an opportunity-ranking product, `Precision@Top5%` and useful lead time matter more than generic accuracy.

## 20. Preventing hindsight leakage

Special care is required for normalized public data. Google Trends Explore, for example, normalizes values to the maximum within the selected time/geography window. Reconstructing historical features with a future-inclusive range can leak future information backward.

Backtests must use historically valid query windows and persist raw snapshots when possible.

## 21. Calibration

If TOP-300 labels 100 independent cases as 80% breakout probability, roughly 80 should break out under the defined outcome rule.

Candidate calibration methods:

- isotonic regression
- Platt scaling
- beta calibration

Evaluate with reliability diagrams and Brier score.

## 22. Outcome definition

Before training, define `breakout` precisely. Example candidate label:

> Topic enters the top 5th percentile of baseline-adjusted attention for its niche within horizon H and remains above the 90th percentile for at least N consecutive observation windows.

The exact label should be versioned. Changing it changes the task.

## 23. Core research references

- Kleinberg, J. (2002). *Bursty and Hierarchical Structure in Streams*.
- Choi & Varian (2009/2012). *Predicting the Present with Google Trends* / nowcasting work using search data.
- Rizoiu et al. Hawkes-process research for online popularity forecasting.
- Bass, F. (1969). *A New Product Growth Model for Consumer Durables*.
- Google Trends documentation and methodology on normalization, related/rising queries, geography, and Year in Search trend methodology.
- YouTube Data / Analytics API documentation for video statistics and time-series analytics where access allows.

## 24. Research caveat

No methodology guarantees viral prediction. TOP-300 should be evaluated as a probabilistic ranking and early-warning system. Its value is measured by whether it consistently improves lead time and precision over simpler baselines such as raw growth, current popularity, or platform-native trending lists.
