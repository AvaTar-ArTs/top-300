from datetime import datetime, timedelta, timezone

from top300.canonical import Canonicalizer, lexical_similarity, normalize_topic
from top300.observations import Observation


def observation(
    topic: str,
    source: str,
    hour: int,
) -> Observation:
    return Observation(
        topic=topic,
        source=source,
        metric="attention",
        value=1,
        observed_at=datetime(2026, 8, 25, hour, tzinfo=timezone.utc),
    )


def test_normalize_topic_is_deterministic() -> None:
    assert normalize_topic("  Apple’s iPhone-18 Launch! ") == "apple s iphone 18 launch"
    assert normalize_topic("APPLE'S   iPhone 18 launch") == "apple s iphone 18 launch"


def test_lexical_similarity_matches_reordered_event_phrase() -> None:
    left = "Apple launches iPhone 18"
    right = "iPhone 18 launch from Apple"
    assert lexical_similarity(left, right) >= 0.70


def test_lexical_similarity_rejects_unrelated_sports_matchups() -> None:
    left = "Cubs vs Diamondbacks"
    right = "Pirates vs Padres"
    assert lexical_similarity(left, right) < 0.35


def test_canonicalizer_merges_conservative_aliases_across_sources() -> None:
    rows = [
        observation("Apple launches iPhone 18", "google_trends", 1),
        observation("iPhone 18 launch from Apple", "hacker_news", 2),
        observation("Cubs vs Diamondbacks", "google_trends", 3),
    ]
    clusters = Canonicalizer(threshold=0.70).cluster(rows)
    assert len(clusters) == 2
    merged = next(cluster for cluster in clusters if len(cluster.members) == 2)
    assert merged.anchor == "Apple launches iPhone 18"
    assert merged.sources == frozenset({"google_trends", "hacker_news"})
    assert merged.cross_platform is True


def test_first_seen_anchor_stays_stable_when_later_alias_arrives() -> None:
    start = datetime(2026, 8, 25, 0, tzinfo=timezone.utc)
    early = Observation(
        topic="OpenAI releases GPT 6",
        source="hacker_news",
        metric="attention",
        value=10,
        observed_at=start,
    )
    later = Observation(
        topic="GPT 6 release by OpenAI",
        source="google_trends",
        metric="demand",
        value=100,
        observed_at=start + timedelta(hours=3),
    )
    canonicalizer = Canonicalizer(threshold=0.70)
    first = canonicalizer.cluster([early])[0]
    expanded = canonicalizer.cluster([later, early])[0]
    assert first.canonical_id == expanded.canonical_id
    assert expanded.anchor == "OpenAI releases GPT 6"


def test_duplicate_metrics_do_not_create_duplicate_members() -> None:
    rows = [
        Observation(
            topic="Example Topic",
            source="google_trends",
            metric="attention",
            value=100,
            observed_at=datetime(2026, 8, 25, 1, tzinfo=timezone.utc),
        ),
        Observation(
            topic="Example Topic",
            source="google_trends",
            metric="demand",
            value=100,
            observed_at=datetime(2026, 8, 25, 1, tzinfo=timezone.utc),
        ),
    ]
    cluster = Canonicalizer().cluster(rows)[0]
    assert cluster.members == ("Example Topic",)
