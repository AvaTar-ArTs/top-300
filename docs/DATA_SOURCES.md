# Data Sources

TOP-300 is intended to learn cross-platform propagation rather than depend on any single trending list.

## Source classes

### Search demand

**Google Trends**

Potential signals:

- relative interest over time
- rising related queries
- related topics
- geographic interest
- topic-vs-search-term distinctions

Important caveat: public Explore values are normalized and sampled. Historical backtests must avoid future-inclusive normalization leakage. Persist requested windows and raw responses where permitted.

### Video consumption and creator supply

**YouTube**

Potential signals:

- video publish velocity
- views and engagement
- views-per-hour or derived velocity where available
- channel-normalized outlier performance
- title/topic cluster growth
- number of independent creators entering a topic
- Shorts vs long-form split

Raw views should never be interpreted without creator/video baseline context.

**TikTok / short-form trend sources**

Potential signals:

- hashtag/topic rank movement
- creator count
- post velocity
- regional spread
- related hashtags
- derivative formats and remix behavior

Use official/public trend products where available and ensure collection follows platform rules.

### Community weak signals

**Reddit**

Potential signals:

- thread/post count
- subreddit diversity
- comment acceleration
- unique author count
- semantic branching
- transition from specialist to general-interest communities

**Hacker News / specialist communities**

Useful especially for technology and developer-tool trends.

### Developer activity

**GitHub**

Potential signals:

- repository creation
- stars/forks/watchers velocity
- issue/PR activity
- number of independent derivative repositories
- release/tag activity
- dependency adoption

Developer activity may lead broader technology-search/video attention in some niches; the lag must be learned rather than assumed.

### News and event sources

Potential signals:

- publication count
- source diversity
- first-publish time
- event type
- entity co-occurrence
- scheduled-vs-unscheduled trigger

News data is especially useful for identifying exogenous shocks so TOP-300 does not confuse a press cycle with self-sustaining propagation.

### Optional future sources

- Wikipedia pageviews
- app-store rankings
- product-review sites
- podcast feeds
- arXiv / scholarly indexes
- package registries
- public marketplaces
- public music charts
- public game-platform statistics

Each source should be added only when its historical coverage and terms allow meaningful evaluation.

## Common observation schema

Every connector should normalize to a shared envelope:

```json
{
  "schema_version": "1",
  "source": "source_name",
  "observed_at": "2026-08-24T18:00:00Z",
  "ingested_at": "2026-08-24T18:00:20Z",
  "entity_type": "post|video|query|repo|article|topic",
  "entity_id": "source-native-id",
  "topic_text": "raw text used for clustering",
  "creator_id": "optional",
  "geo": "optional-region",
  "language": "en",
  "metrics": {},
  "raw_ref": "stable source reference when allowed"
}
```

## Coverage metadata

Every feature window should carry:

```text
sources_expected
sources_available
sources_delayed
sources_failed
coverage_fraction
first_observation_at
last_observation_at
```

Forecast confidence should fall when important leading sources are missing.

## Source-specific normalization

Do not directly add together values such as:

```text
Google Trends 0–100
YouTube views
Reddit comments
GitHub stars
TikTok post counts
```

Normalize within source using baselines, percentiles, standardized anomalies, or learned transformations, then combine features at the model layer.

## Data-retention principle

For scientific backtesting, preserve immutable snapshots whenever permitted. Re-querying a platform months later may return revised, normalized, deleted, or otherwise different data and can silently corrupt historical evaluation.
