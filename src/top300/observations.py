from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class Observation:
    topic: str
    source: str
    metric: str
    value: float
    observed_at: datetime
    geography: str | None = None
    entity: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.topic.strip():
            raise ValueError("topic must not be empty")
        if not self.source.strip():
            raise ValueError("source must not be empty")
        if not self.metric.strip():
            raise ValueError("metric must not be empty")
        if self.observed_at.tzinfo is None:
            raise ValueError("observed_at must be timezone-aware")

    @property
    def observation_id(self) -> str:
        payload = {
            "topic": self.topic,
            "source": self.source,
            "metric": self.metric,
            "value": float(self.value),
            "observed_at": self.observed_at.isoformat(),
            "geography": self.geography,
            "entity": self.entity,
            "metadata": self.metadata,
        }
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        return hashlib.sha256(encoded).hexdigest()
