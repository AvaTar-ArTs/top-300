from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

from .canonical import lexical_similarity
from .historical import TrendEpisode


@dataclass(frozen=True)
class ClusterCollision:
    left_topic: str
    right_topic: str
    geography: str | None
    similarity: float


@dataclass(frozen=True)
class CanonicalBenchmarkReport:
    threshold: float
    native_alias_pairs: int
    native_alias_matches: int
    native_alias_recall: float
    cross_cluster_pairs: int
    cross_cluster_collisions: int
    cross_cluster_collision_rate: float
    collisions: tuple[ClusterCollision, ...]


def _phrase_similarity(left: TrendEpisode, right: TrendEpisode) -> float:
    return max(
        lexical_similarity(left_phrase, right_phrase)
        for left_phrase in (left.topic, *left.aliases)
        for right_phrase in (right.topic, *right.aliases)
    )


def benchmark_canonicalizer(
    episodes: list[TrendEpisode],
    *,
    threshold: float = 0.70,
    cross_cluster_window: timedelta = timedelta(days=2),
    max_cross_cluster_pairs: int | None = 10_000,
) -> CanonicalBenchmarkReport:
    """Evaluate lexical matching against provider-native Google trend structure.

    Native aliases provide positive pairs. Separate provider trend episodes are used only
    to estimate a cross-cluster collision rate; they are not asserted to be semantic
    ground-truth negatives because a provider can split one real-world event into more
    than one trend episode.
    """
    if not 0 <= threshold <= 1:
        raise ValueError("threshold must be between 0 and 1")
    if cross_cluster_window < timedelta(0):
        raise ValueError("cross_cluster_window must be non-negative")
    if max_cross_cluster_pairs is not None and max_cross_cluster_pairs < 0:
        raise ValueError("max_cross_cluster_pairs must be non-negative")

    ordered = sorted(
        episodes,
        key=lambda episode: (
            episode.started,
            episode.geography or "",
            episode.topic.casefold(),
        ),
    )

    alias_pairs = 0
    alias_matches = 0
    for episode in ordered:
        for alias in episode.aliases:
            alias_pairs += 1
            if lexical_similarity(episode.topic, alias) >= threshold:
                alias_matches += 1

    cross_pairs = 0
    collisions: list[ClusterCollision] = []
    stop = False
    for left_index, left in enumerate(ordered):
        if stop:
            break
        for right in ordered[left_index + 1 :]:
            if right.started - left.started > cross_cluster_window:
                break
            if left.geography != right.geography:
                continue
            if max_cross_cluster_pairs is not None and cross_pairs >= max_cross_cluster_pairs:
                stop = True
                break
            cross_pairs += 1
            similarity = _phrase_similarity(left, right)
            if similarity >= threshold:
                collisions.append(
                    ClusterCollision(
                        left_topic=left.topic,
                        right_topic=right.topic,
                        geography=left.geography,
                        similarity=similarity,
                    )
                )

    alias_recall = alias_matches / alias_pairs if alias_pairs else 0.0
    collision_rate = len(collisions) / cross_pairs if cross_pairs else 0.0
    collisions.sort(key=lambda item: (-item.similarity, item.left_topic, item.right_topic))
    return CanonicalBenchmarkReport(
        threshold=threshold,
        native_alias_pairs=alias_pairs,
        native_alias_matches=alias_matches,
        native_alias_recall=alias_recall,
        cross_cluster_pairs=cross_pairs,
        cross_cluster_collisions=len(collisions),
        cross_cluster_collision_rate=collision_rate,
        collisions=tuple(collisions),
    )
