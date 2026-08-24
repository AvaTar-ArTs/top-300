# TOP-300

**Forecast tomorrow's breakout topics before they become obvious.**

TOP-300 is a local-first research and production toolkit for estimating which topics are most likely to enter the top 1–5% of attention over the next 24 hours, 72 hours and 7 days while demand is still outrunning creator/content supply.

It is not a trending dashboard. A dashboard asks **what is hot now?** TOP-300 asks **what is statistically becoming abnormal, how likely is the acceleration to persist, and is there still a supply gap worth acting on?**

## What v1 includes

- immutable SQLite observation store
- CSV/JSON ingestion
- historical replay by `as_of` cutoff
- baseline-aware feature extraction
- velocity, acceleration and jerk
- burst/change-point proxies
- semantic/geographic/creator expansion features
- cross-platform confirmation
- self-excitation/persistence proxy
- transparent 100-point heuristic baseline
- 24h / 72h / 7d heuristic probabilities
- learned logistic horizon models
- model persistence
- Platt-style probability calibrator
- demand/supply opportunity ranking
- lifecycle classification
- walk-forward backtesting
- Brier score and precision@K metrics
- CLI commands for init, ingest, features, train, forecast, rank, backtest and demo
- no-key end-to-end demo
- conversation-evolution checkpoints and repository audit

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
pytest -q
top300 demo ./demo-output
```

See `docs/CONVERSATION_EVOLUTION.md`, `docs/AUDIT_2026-08-24.md`, and `docs/superpowers/` for the complete design history and audit.

## Scientific status

TOP-300 v1 is a forecasting framework and experimentation platform, not a claim that bundled synthetic examples predict the entire internet. Predictive quality depends on historical data, labels, source coverage, niche-specific lead/lag behavior and honest walk-forward validation.

## License

MIT
