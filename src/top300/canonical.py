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


class PhraseAliasResolver:
    """Resolve explicitly supplied phrase aliases on normalized token boundaries.

    Aliases are data, not inferred heuristics. Longer aliases are applied first so a
    specific entity phrase can win over a shorter overlapping alias. Resolution is a
    single deterministic pass and therefore cannot recurse or learn from future data.
    """

    def __init__(self, aliases: dict[str, str]) -> None:
        rules: list[tuple[tuple[str, ...], tuple[str, ...]]] = []
        for alias, canonical in aliases.items():
            alias_tokens = tuple(normalize_topic(alias).split())
            canonical_tokens = tuple(normalize_topic(canonical).split())
            if not alias_tokens or not canonical_tokens:
                raise ValueError("alias and canonical phrase must be non-empty")
            rules.append((alias_tokens, canonical_tokens))
        self._rules = tuple(
            sorted(
                rules,
                key=lambda item: (-len(item[0]), item[0], item[1]),
            )
        )

    def resolve(self, text: str) -> str:
        tokens = normalize_topic(text).split()
        if not tokens or not self._rules:
            return " ".join(tokens)

        resolved: list[str] = []
        index = 0
        while index < len(tokens):
            matched = False
            for alias_tokens, canonical_tokens in self._rules:
                end = index + len(alias_tokens)
                if tuple(tokens[index:end]) != alias_tokens:
                    continue
                resolved.extend(canonical_tokens)
                index = end
                matched = True
                break
            if not matched:
                resolved.append(tokens[index])
                index += 1
        return " ".join(resolved)


def _tokens(text: str) -> frozenset[str]:
    return frozenset(
        token
        for token in normalize_topic(text).split()
        if token and token not in _STOPWORDS
    )


def lexical_similarity(
    left: str,
    right: str,
    *,
    alias_resolver: PhraseAliasResolver | None = None,
) -> float:
    """Conservative lexical similarity for candidate topic aliases.

    The score uses the larger of Jaccard similarity and overlap coefficient,
    but refuses non-identical pairs with fewer than two meaningful shared
    tokens. If both phrases contain numbers and those number sets are disjoint,
    the pair is treated as incompatible. This prevents obvious version/event
    collisions such as iPhone 17 vs iPhone 18.

    An optional explicit phrase-alias resolver may normalize known entity aliases
    before scoring. The resolver does not infer aliases and therefore does not
    weaken the conservative default matcher.
    """
    left_normalized = (
        alias_resolver.resolve(left) if alias_resolver is not None else normalize_topic(left)
    )
    right_normalized = (
        alias_resolver.resolve(right) if alias_resolver is not None else normalize_topic(right)
    )
    if not left_normalized or not right_normalized:
        return 0.0
    if left_normalized == right_normalized:
        return 1.0

    left_tokens = _tokens(left_normalized)
    right_tokens = _tokens(right_normalized)
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

    def __init__(
        self,
        threshold: float = 0.72,
        *,
        alias_resolver: PhraseAliasResolver | None = None,
    ) -> None:
        if not 0 <= threshold <= 1:
            raise ValueError("threshold must be between 0 and 1")
        self.threshold = threshold
        self.alias_resolver = alias_resolver

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
            if (
                lexical_similarity(
                    left,
                    right,
                    alias_resolver=self.alias_resolver,
                )
                >= self.threshold
            ):
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
