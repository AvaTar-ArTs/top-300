# Live Data Validation

TOP-300's first real-data phase captures immutable snapshots before attempting to claim predictive skill.

## Initial no-key sources

### Google Trends Trending Now RSS

The collector records the approximate traffic surfaced by Google's RSS export as raw `attention` and `demand` observations. `observed_at` is the time TOP-300 saw the feed. The RSS publication timestamp is retained separately as `metadata.trend_started_at`.

### Hacker News official API

The collector reads official top-story IDs and story objects. Story score becomes raw `attention`, comment count becomes `engagement`, and each published story contributes one unit of raw `supply`. The HN creation timestamp is retained separately as `metadata.created_at`.

## Why timestamps are separated

A backtest must only use information that TOP-300 could actually have known at its historical cutoff. Therefore source-event times never replace `observed_at`. This prevents a later collection from being backdated and leaking future knowledge into replay.

## Partial source failure

Live collection is intentionally fault-isolated. A Google failure does not erase Hacker News observations, and a Hacker News failure does not erase Google observations. Every snapshot contains per-source status, row counts, and errors.

## Snapshot schedule

The repository workflow captures a snapshot hourly at minute 17 and archives the JSON plus SQLite capture as a GitHub Actions artifact with 90-day retention. Scheduled workflows begin operating from the default branch after merge.

## Current limitation: topic identity

Raw Google search terms and Hacker News titles are not automatically assumed to describe the same topic. Cross-platform confirmation requires a separate canonicalization and clustering layer. That is the next research layer after sufficient snapshots begin accumulating.
