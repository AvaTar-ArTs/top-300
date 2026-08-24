from top300.core import finite_differences, opportunity_ratio, percent_growth, score_snapshot
from top300.models import FeatureSnapshot


def full_snapshot(value: float) -> FeatureSnapshot:
    return FeatureSnapshot(**{name: value for name in FeatureSnapshot.feature_names()})


def test_full_snapshot_scores_100() -> None:
    assert score_snapshot(full_snapshot(1.0)) == 100.0


def test_percent_growth_300_percent() -> None:
    assert percent_growth(100, 400) == 300.0


def test_percent_growth_zero_baseline_is_none() -> None:
    assert percent_growth(0, 10) is None


def test_finite_differences() -> None:
    result = finite_differences([100, 105, 120, 180, 390])
    assert result["velocity"] == [5, 15, 60, 210]
    assert result["acceleration"] == [10, 45, 150]
    assert result["jerk"] == [35, 105]


def test_opportunity_ratio_zero_supply_is_none() -> None:
    assert opportunity_ratio(10, 0) is None
