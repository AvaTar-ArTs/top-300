# TOP-300

**Forecast tomorrow's breakout topics before they become obvious.**

TOP-300 is a local-first research and production toolkit for estimating which topics are most likely to enter the top 1–5% of attention over the next 24 hours, 72 hours and 7 days while demand is still outrunning creator/content supply.

It is not a trending dashboard. A dashboard asks **what is hot now?** TOP-300 asks **what is statistically becoming abnormal, how likely is the acceleration to persist, and is there still a supply gap worth acting on?**

## What v1.1 includes

- immutable SQLite observation store
- CSV/JSON ingestion and historical replay by `as_of` cutoff
- baseline-aware velocity, acceleration, jerk, burst and change-point features
- semantic/geographic/creator expansion features
- cross-platform confirmation research features
- transparent 100-point heuristic baseline
- 24h / 72h / 7d heuristic and learned logistic horizon models
- model persistence and Platt-style calibration utility
- demand/supply opportunity ranking and lifecycle classification
- walk-forward backtesting with Brier score and precision@K
- no-key Google Trends Trending Now RSS collector
- no-key Hacker News official API collector
- resilient partial-source live snapshots
- collector/version/source-parameter provenance in every snapshot
- hourly GitHub Actions snapshot archive with 90-day artifact retention
- CLI commands for init, ingest, collect-live, features, train, forecast, rank, backtest and demo
- conversation-evolution checkpoints and repository audit

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
pytest -q
top300 demo ./demo-output
```

Capture a real-data snapshot:

```bash
top300 collect-live ./live.db \
  --snapshot ./snapshot.json \
  --geo US \
  --hn-limit 50
```

The snapshot records one shared observation cutoff, source health, collector version, exact collection parameters and every raw observation. It can be archived and replayed later without pretending source publication time was observation time.

See `docs/LIVE_DATA_VALIDATION.md` for the real-data program and `docs/CONVERSATION_EVOLUTION.md`, `docs/AUDIT_2026-08-24.md`, and `docs/superpowers/` for the design history.

## Scientific status

TOP-300 is now collecting genuine live signals, but collection success is not forecasting validation. Predictive claims require a sufficient historical series, cutoff-safe topic canonicalization, outcome labels and walk-forward evaluation against naive baselines and current trending lists.

The first real snapshot was captured successfully on 2026-08-25 UTC. It contained 167 observations from Google Trends and Hacker News. This proves the live acquisition path, not predictive accuracy.

## License

MIT
