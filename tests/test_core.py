import pytest

from top300 import FeatureSnapshot, finite_differences, opportunity_ratio, percent_growth, score_snapshot


def full_snapshot(value: float) -> FeatureSnapshot:
    return FeatureSnapshot(**{field: value for field in FeatureSnapshot.__dataclass_fields__})


def test_score_snapshot_extremes() -> None:
    assert score_snapshot(full_snapshot(0.0)) == 0
    assert score_snapshot(full_snapshot(1.0)) == 100


def test_score_snapshot_rejects_invalid_values() -> None:
    snapshot = full_snapshot(0.5)
    snapshot.jerk = 1.2
    with pytest.raises(ValueError):
        score_snapshot(snapshot)


def test_percent_growth() -> None:
    assert percent_growth(100, 400) == 300
    assert percent_growth(0, 10) is None


def test_finite_differences_detect_acceleration() -> None:
    result = finite_differences([100, 105, 120, 180, 390])
    assert result["velocity"] == [5, 15, 60, 210]
    assert result["acceleration"] == [10, 45, 150]
    assert result["jerk"] == [35, 105]


def test_opportunity_ratio() -> None:
    assert opportunity_ratio(8.0, 2.0) == 4.0
    assert opportunity_ratio(8.0, 0.0) is None
