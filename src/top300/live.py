import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any, Protocol

from .observations import Observation
from .store import SignalStore


class LiveAdapter(Protocol):
    def collect(self, *, observed_at: datetime, **kwargs: Any) -> list[Observation]: ...


@dataclass(frozen=True)
class SourceHealth:
    status: str
    observations: int
    error: str | None = None


@dataclass(frozen=True)
class LiveReport:
    observed_at: datetime
    inserted: int
    sources: dict[str, SourceHealth]
    observations: list[Observation]
    collector_version: str
    source_parameters: dict[str, dict[str, Any]]

    @property
    def successful_sources(self) -> int:
        return sum(1 for source in self.sources.values() if source.status == "ok")

    def as_dict(self) -> dict[str, object]:
        return {
            "schema_version": 1,
            "collector_version": self.collector_version,
            "observed_at": self.observed_at.isoformat(),
            "inserted": self.inserted,
            "source_parameters": self.source_parameters,
            "sources": {name: asdict(value) for name, value in self.sources.items()},
            "observations": [_observation_dict(row) for row in self.observations],
        }


def _collector_version() -> str:
    try:
        return version("top-300")
    except PackageNotFoundError:
        return "development"


def _observation_dict(row: Observation) -> dict[str, object]:
    return {
        "observation_id": row.observation_id,
        "topic": row.topic,
        "source": row.source,
        "metric": row.metric,
        "value": row.value,
        "observed_at": row.observed_at.isoformat(),
        "geography": row.geography,
        "entity": row.entity,
        "metadata": row.metadata,
    }


class LiveCollector:
    def __init__(self, *, sources: dict[str, LiveAdapter]) -> None:
        if not sources:
            raise ValueError("at least one live source is required")
        self.sources = sources

    def collect(
        self,
        *,
        store: SignalStore,
        observed_at: datetime | None = None,
        snapshot_path: str | Path | None = None,
        source_kwargs: dict[str, dict[str, Any]] | None = None,
    ) -> LiveReport:
        observed_at = observed_at or datetime.now(timezone.utc)
        if observed_at.tzinfo is None:
            raise ValueError("observed_at must be timezone-aware")
        source_parameters = {
            name: dict(parameters)
            for name, parameters in (source_kwargs or {}).items()
        }
        observations: list[Observation] = []
        health: dict[str, SourceHealth] = {}

        for name, adapter in self.sources.items():
            try:
                rows = adapter.collect(
                    observed_at=observed_at,
                    **source_parameters.get(name, {}),
                )
            except Exception as exc:  # A source boundary must not erase other sources.
                health[name] = SourceHealth(
                    status="error",
                    observations=0,
                    error=f"{type(exc).__name__}: {exc}",
                )
                continue
            observations.extend(rows)
            health[name] = SourceHealth(status="ok", observations=len(rows))

        inserted = store.add_many(observations)
        report = LiveReport(
            observed_at=observed_at,
            inserted=inserted,
            sources=health,
            observations=observations,
            collector_version=_collector_version(),
            source_parameters=source_parameters,
        )
        if snapshot_path is not None:
            path = Path(snapshot_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                json.dumps(report.as_dict(), indent=2, sort_keys=True),
                encoding="utf-8",
            )
        return report
