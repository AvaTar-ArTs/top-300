# TOP-300

**Forecast tomorrow's breakout topics before they become obvious.**

TOP-300 is a local-first research and production toolkit for estimating which topics are most likely to enter the top 1–5% of attention over the next 24 hours, 72 hours and 7 days while demand is still outrunning creator/content supply.

It is not a trending dashboard. A dashboard asks **what is hot now?** TOP-300 asks **what is statistically becoming abnormal, how likely is the acceleration to persist, and is there still a supply gap worth acting on?**

## What v1.2 includes

- immutable SQLite observation store and replay by explicit `as_of` cutoff
- CSV/JSON ingestion
- no-key Google Trends Trending Now RSS and Hacker News live collectors
- resilient, provenance-rich live snapshots and hourly GitHub Actions archival
- deterministic cutoff-safe topic canonicalization with stable first-seen anchors
- provider-native alias preservation and conservative cross-platform clustering
- baseline-aware velocity, acceleration, jerk, burst and change-point features
- transparent heuristic forecasting plus learned logistic horizon models
- per-horizon learned/heuristic hybrid fallback when a target is still sparse
- true independent 24h / 72h / 7d backtest labels
- expanding-window walk-forward evaluation
- per-horizon Brier score, precision@5, prior-only base-rate Brier and Brier skill
- GoogleTrendArchive historical target/lifecycle parser and cutoff-safe target index
- optional streaming GoogleTrendArchive adapter for bounded historical research
- `archive-sample` CLI export to JSONL
- explicit source roles: discovery, corroboration/measurement and outcomes
- demand/supply opportunity ranking and lifecycle classification
- model persistence and calibration utilities

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
pytest -q
top300 demo ./demo-output
```

Capture a genuine live-data snapshot:

```bash
top300 collect-live ./live.db \
  --snapshot ./snapshot.json \
  --geo US \
  --hn-limit 50
```

The snapshot records one shared observation cutoff, source health, collector version, exact collection parameters and every raw observation. It can be archived and replayed later without pretending source publication time was observation time.

For historical Google Trending Now research, install the optional archive dependency and stream only the slice you need:

```bash
pip install -e '.[archive]'

top300 archive-sample \
  --output ./research/google-us-2026-01.jsonl \
  --geo US \
  --start 2026-01-01T00:00:00Z \
  --end 2026-01-31T23:59:59Z \
  --limit 1000
```

Run an evidence-oriented backtest:

```bash
top300 backtest ./examples/training_features.csv --min-train 20
```

The result includes separate 24h, 72h and 7d metrics plus a walk-forward base-rate Brier benchmark. Positive `brier_skill` means the model improved on the prior-only base-rate probability for that horizon.

See `docs/LIVE_DATA_VALIDATION.md`, `docs/CANONICALIZATION.md`, `docs/HISTORICAL_BOOTSTRAP_RESEARCH.md`, `docs/SOURCE_ROLES.md`, and `docs/EVOLUTION_2026-08-25.md` for the evidence program and design history.

## Scientific status

TOP-300 now has real acquisition, replay, identity, target and evaluation infrastructure. That is still not a claim of predictive skill. Forecasting claims require overlapping pre-outcome discovery signals and later outcome labels, evaluated by genuine walk-forward experiments against naive baselines.

GoogleTrendArchive is deliberately treated primarily as historical outcome/lifecycle material. Eventual end times, durations and later outcomes are not silently exposed as features at the forecast cutoff.

The first TOP-300 live snapshot was captured successfully on 2026-08-25 UTC with 167 observations from Google Trends and Hacker News. It proves the acquisition path, not forecast accuracy.

## License

MIT
