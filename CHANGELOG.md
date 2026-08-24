# Changelog

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
