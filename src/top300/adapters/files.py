from __future__ import annotations

from pathlib import Path

from ..ingest import load_observations
from ..observations import Observation


class FileObservationAdapter:
    def load(self, path: Path) -> list[Observation]:
        return load_observations(path)
