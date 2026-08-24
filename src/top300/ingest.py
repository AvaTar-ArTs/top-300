from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from .observations import Observation
from .store import SignalStore


class IngestError(ValueError):
    pass


def _parse_row(row: dict[str, Any], row_number: int) -> Observation:
    try:
        observed_at = datetime.fromisoformat(str(row["observed_at"]).replace("Z", "+00:00"))
        metadata = row.get("metadata", {})
        if isinstance(metadata, str) and metadata.strip():
            metadata = json.loads(metadata)
        elif not metadata:
            metadata = {}
        return Observation(
            topic=str(row["topic"]).strip(), source=str(row["source"]).strip(),
            metric=str(row["metric"]).strip(), value=float(row["value"]),
            observed_at=observed_at,
            geography=str(row["geography"]).strip() if row.get("geography") else None,
            entity=str(row["entity"]).strip() if row.get("entity") else None,
            metadata=metadata,
        )
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise IngestError(f"invalid row {row_number}: {exc}") from exc


def load_observations(path: str | Path) -> list[Observation]:
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix == ".csv":
        with path.open(newline="", encoding="utf-8") as handle:
            return [_parse_row(row, index) for index, row in enumerate(csv.DictReader(handle), 2)]
    if suffix == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            data = data.get("observations", [])
        if not isinstance(data, list):
            raise IngestError("JSON input must be a list or an object with observations")
        return [_parse_row(row, index) for index, row in enumerate(data, 1)]
    raise IngestError(f"unsupported input type: {suffix or '<none>'}")


def ingest_file(store: SignalStore, path: str | Path) -> int:
    return store.add_many(load_observations(path))
