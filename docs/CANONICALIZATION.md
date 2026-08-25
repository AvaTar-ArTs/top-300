# Topic Canonicalization

TOP-300 treats topic identity as a scientific boundary, not a cosmetic cleanup step.

## Baseline policy

The v1.1 canonicalization baseline is intentionally conservative and deterministic:

- Unicode NFKC normalization and case folding
- punctuation/whitespace normalization
- small stopword set used only for matching
- Jaccard and overlap-coefficient lexical similarity
- at least two meaningful shared tokens for non-identical phrases
- numeric conflict protection (for example, version 17 does not merge with version 18)
- stable first-seen anchors
- stable anchor-derived canonical IDs
- exact-topic metric deduplication
- source-set aggregation and explicit cross-platform status
- cutoff-safe clustering via `cluster_store(..., as_of=...)`

False negatives are preferable to false positive merges because a false merge can manufacture cross-platform confirmation and contaminate downstream forecasts.

## Live falsification checkpoint

The first real TOP-300 live snapshot captured 59 unique topic strings across Google Trends and Hacker News. At the 0.70 matching threshold, the baseline produced no accidental candidate pairs at or above threshold. The strongest unrelated pair in that snapshot scored below the merge threshold.

This is not proof of semantic accuracy. It is evidence that the initial threshold is conservative on one real snapshot.

## Provider-native identity

Where a source already provides a topic/cluster identifier, TOP-300 should preserve it as provenance and treat it as stronger evidence than TOP-300 lexical similarity. Google Trending Now may group related queries into one trend entry, so future adapters should retain Google-native trend identifiers and breakdown queries rather than flattening them into independent topics.

## Next validation steps

1. Build a labeled alias/non-alias benchmark from archived real trends.
2. Measure precision and recall across thresholds.
3. Add source-native cluster identity where available.
4. Evaluate multilingual transliteration/entity methods separately.
5. Only add semantic embeddings or LLM-assisted matching if they outperform this baseline under cutoff-safe evaluation.
