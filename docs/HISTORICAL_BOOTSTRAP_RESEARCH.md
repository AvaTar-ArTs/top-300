# Historical Bootstrap Research

TOP-300 should not wait months for its own live archive before evaluating real trend lifecycles.

## GoogleTrendArchive

The ICWSM 2026 GoogleTrendArchive project publishes a large historical archive of Google Trending Now data. Its companion repository documents streaming access through Hugging Face, allowing TOP-300 to inspect subsets without downloading the complete multi-gigabyte corpus.

The dataset includes trend labels, search-volume buckets, start/end timestamps, geography, related query breakdowns, and Explore links. The public Hugging Face dataset has continued growing beyond the original paper release.

## Recommended role

Treat GoogleTrendArchive as a historical bootstrap / benchmark source, not as a replacement for TOP-300's own immutable live snapshots.

Use it to:

- estimate trend-duration priors
- build geography-specific baselines
- test threshold and lifecycle assumptions
- construct alias/non-alias canonicalization benchmarks from provider-native query clusters
- train and validate breakout-duration / persistence models
- compare naive baselines against TOP-300 forecast features
- create pre-registered walk-forward experiments before expanding source complexity

## Scientific cautions

- The archive is a dataset of already-detected Google Trending Now episodes, so it cannot by itself prove that TOP-300 predicts trends *before Google detects them*.
- It is excellent for lifecycle, persistence, geography, volume-bucket, and canonicalization studies.
- Claims about early prediction must use signals whose timestamps precede the target Google emergence timestamp.
- Estimated end timestamps should be flagged or excluded in sensitivity analyses.
- Historical archive provenance must remain distinct from TOP-300's live observation timestamps.

## Architecture evolution

Split data sources into three roles:

1. **Discovery sources**: surface candidate topics before or near emergence (for example Hacker News and TOP-300 live feeds).
2. **Corroboration / measurement sources**: measure independent attention, coverage, demand, or supply for known candidates (for example Wikimedia Pageviews or GDELT queries).
3. **Outcome sources**: define later success/failure labels without leaking future information into features.

This avoids treating every API as if it were an interchangeable 'trend feed'.
