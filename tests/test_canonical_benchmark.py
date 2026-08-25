from datetime import datetime, timedelta, timezone

from top300.benchmark import benchmark_canonicalizer

from top300.historical import TrendEpisode


def episode(
    topic: str,
    hour: int,
    *,
    aliases: tuple[str, ...] = (),
    geography: str = "US",
) -> TrendEpisode:
    return TrendEpisode(
        topic=topic,
        aliases=aliases,
        geography=geography,
        started=datetime(2026, 1, 1, hour, tzinfo=timezone.utc),
    )


def test_benchmark_measures_provider_alias_recall() -> None:
    report = benchmark_canonicalizer(
        [
            episode(
                "Apple launches iPhone 18",
                1,
                aliases=("iPhone 18 launch from Apple",),
            ),
            episode(
                "Manchester United vs Bodo Glimt",
                2,
                aliases=("Man Utd vs Bodo",),
            ),
        ],
        threshold=0.70,
    )

    assert report.native_alias_pairs == 2
    assert report.native_alias_matches == 2
    assert report.native_alias_recall == 1.0


def test_benchmark_reports_cross_cluster_collision_without_calling_it_ground_truth() -> None:
    report = benchmark_canonicalizer(
        [
            episode("Apple launches iPhone 18", 1),
            episode("iPhone 18 launch from Apple", 2),
            episode("Cubs vs Diamondbacks", 3),
        ],
        threshold=0.70,
        cross_cluster_window=timedelta(hours=24),
    )

    assert report.cross_cluster_pairs == 3
    assert report.cross_cluster_collisions == 1
    assert report.cross_cluster_collision_rate == 1 / 3
    assert report.collisions[0].left_topic == "Apple launches iPhone 18"
    assert report.collisions[0].right_topic == "iPhone 18 launch from Apple"


def test_benchmark_keeps_geographies_separate_for_cross_cluster_pairs() -> None:
    report = benchmark_canonicalizer(
        [
            episode("Example Event", 1, geography="US"),
            episode("Example Event", 2, geography="GB"),
        ],
        threshold=0.70,
    )
    assert report.cross_cluster_pairs == 0
    assert report.cross_cluster_collisions == 0


def test_benchmark_respects_cross_cluster_time_window() -> None:
    early = TrendEpisode(
        topic="Example Event",
        geography="US",
        started=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    late = TrendEpisode(
        topic="Example Event",
        geography="US",
        started=datetime(2026, 1, 10, tzinfo=timezone.utc),
    )
    report = benchmark_canonicalizer(
        [early, late],
        threshold=0.70,
        cross_cluster_window=timedelta(days=2),
    )
    assert report.cross_cluster_pairs == 0


def test_benchmark_caps_cross_cluster_pairs_deterministically() -> None:
    episodes = [episode(f"topic {index} alpha beta", index) for index in range(5)]
    report = benchmark_canonicalizer(
        episodes,
        threshold=0.70,
        max_cross_cluster_pairs=2,
    )
    assert report.cross_cluster_pairs == 2
