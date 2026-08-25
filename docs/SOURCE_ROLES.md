# Source Roles

TOP-300 classifies external data sources by the role they play in an experiment. This prevents future information from leaking into features and prevents every API from being treated as an interchangeable trend feed.

## Discovery

Discovery sources surface candidate topics before or near emergence. Their timestamps can become predictive features if they are known at the forecast cutoff.

Examples:

- Hacker News story appearance, score and comment activity
- TOP-300 live Google Trending Now observations, when the research question is persistence rather than pre-Google emergence
- future niche/community feeds with reliable observation timestamps

## Corroboration / measurement

These sources measure independent attention, coverage, demand or supply for an already identified candidate.

Examples:

- GDELT DOC/Context coverage volume for a candidate topic
- Wikimedia pageview or edit activity for a resolved article/entity
- GitHub activity for software/developer topics

Corroboration must be timestamped at or before the forecast cutoff.

## Outcomes / targets

Outcome sources define whether a forecast later succeeded. They must never be fed back into the feature set at an earlier cutoff.

Examples:

- future Google Trending Now emergence
- future trend persistence/duration
- later search-volume bucket
- later independent public-attention thresholds

GoogleTrendArchive is primarily an outcome/lifecycle benchmark for TOP-300. Its future end time or eventual duration is label information, not an input feature at the start of the trend.

## Invariant

Every experiment should be able to answer:

1. What information was observable at cutoff T?
2. Which sources were queried only after T to determine the outcome?
3. Which transformations were fit only on training data before T?
4. Which provider-native identifiers or clusters were preserved?

If any of those answers are ambiguous, the experiment is not publishable evidence.
