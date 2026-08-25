# Evolution Checkpoint — 2026-08-25

This checkpoint records the transition from live acquisition into evidence-oriented trend intelligence.

## Completed before this checkpoint

- real Google Trends and Hacker News collection
- immutable live snapshots with source health and provenance
- hourly archival workflow on `main`
- replayable JSON/SQLite evidence artifacts
- first genuine live snapshot

## Canonicalization evolution

The new deterministic canonicalization layer creates stable first-seen topic anchors and conservative cross-source alias clusters. It is deliberately precision-first because a false merge can fabricate cross-platform confirmation.

The first live snapshot contained 59 unique topics. A pressure test at the 0.70 threshold produced no accidental merge candidates at or above threshold.

## Research-driven architecture changes

1. Preserve provider-native topic/cluster identity whenever available.
2. Separate source roles into discovery, corroboration/measurement, and outcomes.
3. Treat historical Google trend lifecycle data as benchmark/target material, not automatically as predictor features.
4. Bootstrap historical validation with GoogleTrendArchive rather than waiting months for the new hourly archive.
5. Add independent public-attention and news-coverage probes only after canonical identity is reliable.
6. Require every experiment to expose its cutoff, source roles, target horizon, calibration metric, and naive comparison.

## Next build sequence

1. historical GoogleTrendArchive episode parser and target index
2. alias benchmark generated from provider-native trend breakdowns
3. GDELT candidate coverage probe
4. Wikimedia pageview follow-through probe
5. cluster-aware feature builder
6. real target labeling for 24h / 72h / 7d experiments
7. naive persistence and popularity baselines
8. walk-forward evaluation with Brier score, precision@K, calibration and lead-time distributions
9. only then evaluate embeddings, semantic reranking, survival models or Hawkes-style excitation extensions
