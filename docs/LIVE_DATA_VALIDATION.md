# Live Data Validation

TOP-300's real-data phase captures immutable snapshots before attempting to claim predictive skill.

## Initial no-key sources

### Google Trends Trending Now RSS

The collector records approximate traffic from Google's RSS export as raw `attention` and `demand` observations. `observed_at` is when TOP-300 saw the feed. The RSS publication timestamp is retained separately as `metadata.trend_started_at`.

### Hacker News official API

The collector reads official top-story IDs and story objects. Story score becomes raw `attention`, comment count becomes `engagement`, and each published story contributes one unit of raw `supply`. The Hacker News creation timestamp is retained separately as `metadata.created_at`.

## Observation-time invariant

A backtest must only use information TOP-300 could actually have known at its historical cutoff. Source-event times therefore never replace `observed_at`. A later collection cannot be backdated simply because the underlying source item was created earlier.

Every snapshot also records `collector_version` and `source_parameters`, making the collection process itself part of the historical evidence.

## Partial source failure

Live collection is fault-isolated. A Google failure does not erase Hacker News observations, and a Hacker News failure does not erase Google observations. Every snapshot contains per-source status, row counts and error details.

## First real evidence checkpoint

The first successful end-to-end capture occurred at:

`2026-08-25T00:54:42.452814+00:00`

It produced 167 immutable observations:

| Source | Raw observations | Underlying items |
|---|---:|---:|
| Google Trends | 20 | 10 rising searches |
| Hacker News | 147 | 49 stories |
| **Total** | **167** | **59 source items** |

The workflow archived both `snapshot.json` and `live.db`. The GitHub Actions artifact was `top300-live-32795467084` with artifact ID `9544664401`.

This checkpoint proves that the production acquisition path works against real public sources. It does **not** prove that TOP-300 predicts future breakouts.

## Snapshot schedule

The default-branch workflow captures a snapshot hourly at minute 17 and archives the JSON plus SQLite capture as a GitHub Actions artifact with 90-day retention. `workflow_dispatch` also permits an explicit manual capture.

GitHub artifact retention is deliberately treated as a staging archive, not permanent research storage. Snapshots should eventually be harvested into a longer-lived immutable dataset before expiration.

## Current limitation: topic identity

Raw Google search terms and Hacker News titles are not automatically assumed to describe the same topic. Exact-string grouping is insufficient for genuine cross-platform confirmation.

The next research layer is cutoff-safe canonicalization and clustering:

1. deterministic text normalization
2. named-entity/token signatures
3. conservative lexical matching
4. optional semantic similarity
5. canonical topic IDs and aliases
6. per-cutoff cluster versioning
7. evaluation of false merges and false splits

Only after that layer is validated should cross-platform confirmation contribute strongly to learned breakout probabilities.
