from datetime import datetime, timezone

from top300.forecast import HeuristicForecaster, LearnedForecaster, TrainingRow
from top300.models import FeatureSnapshot


def snap(value: float) -> FeatureSnapshot:
    return FeatureSnapshot(**{name: value for name in FeatureSnapshot.feature_names()})


def training_rows() -> list[TrainingRow]:
    rows = []
    for i in range(20):
        value = 0.1 if i < 10 else 0.9
        label = 0 if i < 10 else 1
        rows.append(TrainingRow(snap(value), label, label, label))
    return rows


def test_heuristic_forecast_is_monotonic() -> None:
    engine = HeuristicForecaster()
    now = datetime(2026, 8, 24, tzinfo=timezone.utc)
    assert engine.predict("high", now, snap(0.9)).prob_24h > engine.predict(
        "low", now, snap(0.2)
    ).prob_24h


def test_learned_forecaster_learns_separable_data() -> None:
    engine = LearnedForecaster().fit(training_rows())
    now = datetime(2026, 8, 24, tzinfo=timezone.utc)
    assert engine.predict("high", now, snap(0.9)).prob_24h > 0.5
    assert engine.predict("low", now, snap(0.1)).prob_24h < 0.5


def test_learned_forecaster_falls_back_on_single_class() -> None:
    rows = [TrainingRow(snap(0.2), 0, 0, 0) for _ in range(4)]
    result = LearnedForecaster().fit(rows).predict(
        "x", datetime(2026, 8, 24, tzinfo=timezone.utc), snap(0.8)
    )
    assert result.model_kind == "heuristic"


def test_learned_forecaster_round_trips(tmp_path) -> None:
    path = tmp_path / "model.pkl"
    LearnedForecaster().fit(training_rows()).save(path)
    restored = LearnedForecaster.load(path)
    result = restored.predict("high", datetime(2026, 8, 24, tzinfo=timezone.utc), snap(0.9))
    assert result.model_kind == "learned"
