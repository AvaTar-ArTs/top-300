from __future__ import annotations

from pathlib import Path
from typing import Protocol

from ..observations import Observation


class ObservationAdapter(Protocol):
    def load(self, path: Path) -> list[Observation]: ...
