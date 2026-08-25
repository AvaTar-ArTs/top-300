# Changelog

## 1.1.0 — 2026-08-24

### Added

- Google Trends Trending Now RSS live collector
- Hacker News official API live collector
- resilient `LiveCollector` with partial-source failure isolation
- `collect-live` CLI command with a shared explicit observation cutoff
- immutable JSON snapshot alongside the SQLite signal store
- collector-version and source-parameter provenance
- hourly GitHub Actions live snapshot workflow with 90-day artifact retention
- live-data validation documentation and first real evidence checkpoint

### Verified

- first real capture at `2026-08-25T00:54:42.452814+00:00`
- 167 observations collected
- Google Trends: 20 observations across 10 rising searches
- Hacker News: 147 observations across 49 stories
- both initial live sources completed successfully

### Scientific boundary

- the live capture demonstrates acquisition and replay infrastructure, not forecasting skill
- raw Google query strings and Hacker News titles are not yet treated as equivalent cross-platform topics
- semantic topic canonicalization remains required before cross-platform confirmation is considered valid

## 1.0.0 — 2026-08-24

### Added

- immutable signal store and replay
- CSV/JSON ingestion
- cutoff-aware feature extraction
- heuristic and learned 24h/72h/7d forecasting
- model persistence and calibration utility
- demand/supply opportunity ranking
- lifecycle classification
- walk-forward backtesting
- CLI and no-key demo
- conversation checkpoints, audit, Superpowers design and plan

### Fixed

- original CI import-format defects
- original Ruff RUF007 successive-pair implementation by switching to `itertools.pairwise`
- console module execution path

### Changed

- demoted `+300%` from decision rule to signal
- removed personal-history weighting
- made explicit `as_of` cutoff isolation a core invariant
