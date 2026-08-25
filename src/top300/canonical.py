import hashlib
import unicodedata
from dataclasses import dataclass
from datetime import datetime
from itertools import combinations

from .observations import Observation
from .store import SignalStore

_STOPWORDS = frozenset(
    {
        "a",
        "an",
        "and",
        "as",
        "at",
        "by",
        "for",
        "from",
        "in",
        "of",
        "on",
        "s",
        "the",
        "to",
        "with",
    }
)


def normalize_topic(text: str) -> str:
    """Return a deterministic Unicode-aware normalized topic string."""
    normalized = unicodedata.normalize("NFKC", text).casefold()
    characters = [character if character.isalnum() else " " for character in normalized]
    return " ".join("".join(characters).split())


def _tokens(text: str) -> frozenset[str]:
    return frozenset(
        token
        for token in normalize_topic(text).split()
        if token and token not in _STOPWORDS
    )


def lexical_similarity(left: str, right: str) -> float:
    """Conservative lexical similarity for candidate topic aliases.

    The score uses the larger of Jaccard similarity and overlap coefficient,
    but refuses non-identical pairs with fewer than two meaningful shared
    tokens. If both phrases contain numbers and those number sets are disjoint,
    the pair is treated as incompatible. This prevents obvious version/event
    collisions such as iPhone 17 vs iPhone 18.
    """
    left_normalized = normalize_topic(left)
    right_normalized = normalize_topic(right)
    if not left_normalized or not right_normalized:
        return 0.0
    if left_normalized == right_normalized:
        return 1.0

    left_tokens = _tokens(left)
    right_tokens = _tokens(right)
    if not left_tokens or not right_tokens:
        return 0.0

    left_numbers = {token for token in left_tokens if token.isdigit()}
    right_numbers = {token for token in right_tokens if token.isdigit()}
    if left_numbers and right_numbers and left_numbers.isdisjoint(right_numbers):
        return 0.0

    intersection = left_tokens & right_tokens
    if len(intersection) < 2:
        return 0.0

    union = left_tokens | right_tokens
    jaccard = len(intersection) / len(union)
    overlap = len(intersection) / min(len(left_tokens), len(right_tokens))
    return max(jaccard, overlap)


@dataclass(frozen=True)
class TopicCluster:
    canonical_id: str
    anchor: str
    members: tuple[str, ...]
    sources: frozenset[str]
    first_seen: datetime
    last_seen: datetime

    @property
    def cross_platform(self) -> bool:
        return len(self.sources) > 1


@dataclass
class _TopicStats:
    first_seen: datetime
    last_seen: datetime
    sources: set[str]


def _canonical_id(anchor: str) -> str:
    digest = hashlib.sha256(normalize_topic(anchor).encode("utf-8")).hexdigest()
    return f"topic_{digest[:16]}"


class Canonicalizer:
    """Cluster raw topic strings without using information after a cutoff."""

    def __init__(self, threshold: float = 0.72) -> None:
        if not 0 <= threshold <= 1:
            raise ValueError("threshold must be between 0 and 1")
        self.threshold = threshold

    def cluster_store(self, store: SignalStore, *, as_of: datetime) -> list[TopicCluster]:
        return self.cluster(store.query(as_of=as_of))

    def cluster(self, observations: list[Observation]) -> list[TopicCluster]:
        if not observations:
            return []

        stats: dict[str, _TopicStats] = {}
        for row in observations:
            existing = stats.get(row.topic)
            if existing is None:
                stats[row.topic] = _TopicStats(
                    first_seen=row.observed_at,
                    last_seen=row.observed_at,
                    sources={row.source},
                )
                continue
            existing.first_seen = min(existing.first_seen, row.observed_at)
            existing.last_seen = max(existing.last_seen, row.observed_at)
            existing.sources.add(row.source)

        topics = sorted(
            stats,
            key=lambda topic: (
                stats[topic].first_seen,
                normalize_topic(topic),
                topic,
            ),
        )
        parent = {topic: topic for topic in topics}

        def find(topic: str) -> str:
            root = topic
            while parent[root] != root:
                root = parent[root]
            while parent[topic] != topic:
                next_topic = parent[topic]
                parent[topic] = root
                topic = next_topic
            return root

        def root_key(topic: str) -> tuple[datetime, str, str]:
            return (
                stats[topic].first_seen,
                normalize_topic(topic),
                topic,
            )

        def union(left: str, right: str) -> None:
            left_root = find(left)
            right_root = find(right)
            if left_root == right_root:
                return
            winner, loser = sorted((left_root, right_root), key=root_key)
            parent[loser] = winner

        for left, right in combinations(topics, 2):
            if lexical_similarity(left, right) >= self.threshold:
                union(left, right)

        grouped: dict[str, list[str]] = {}
        for topic in topics:
            grouped.setdefault(find(topic), []).append(topic)

        clusters: list[TopicCluster] = []
        for members in grouped.values():
            ordered_members = sorted(
                members,
                key=lambda topic: (
                    stats[topic].first_seen,
                    normalize_topic(topic),
                    topic,
                ),
            )
            anchor = ordered_members[0]
            sources = frozenset(
                source
                for member in ordered_members
                for source in stats[member].sources
            )
            clusters.append(
                TopicCluster(
                    canonical_id=_canonical_id(anchor),
                    anchor=anchor,
                    members=tuple(ordered_members),
                    sources=sources,
                    first_seen=min(stats[member].first_seen for member in ordered_members),
                    last_seen=max(stats[member].last_seen for member in ordered_members),
                )
            )

        return sorted(clusters, key=lambda cluster: (cluster.first_seen, cluster.canonical_id))
