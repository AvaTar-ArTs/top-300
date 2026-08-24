from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path

from .observations import Observation


class SignalStore:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS observations (
                    observation_id TEXT PRIMARY KEY,
                    topic TEXT NOT NULL,
                    source TEXT NOT NULL,
                    metric TEXT NOT NULL,
                    value REAL NOT NULL,
                    observed_at TEXT NOT NULL,
                    geography TEXT,
                    entity TEXT,
                    metadata_json TEXT NOT NULL
                )
            """)
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_obs_topic_time "
                "ON observations(topic, observed_at)"
            )

    def add_many(self, observations: list[Observation]) -> int:
        inserted = 0
        with self._connect() as conn:
            for row in observations:
                cursor = conn.execute(
                    """
                    INSERT OR IGNORE INTO observations
                    (observation_id, topic, source, metric, value, observed_at,
                     geography, entity, metadata_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        row.observation_id, row.topic, row.source, row.metric,
                        float(row.value), row.observed_at.isoformat(), row.geography,
                        row.entity, json.dumps(row.metadata, sort_keys=True),
                    ),
                )
                inserted += cursor.rowcount
        return inserted

    def query(self, *, topic: str | None = None, metric: str | None = None,
              as_of: datetime | None = None) -> list[Observation]:
        clauses: list[str] = []
        params: list[object] = []
        if topic is not None:
            clauses.append("topic = ?")
            params.append(topic)
        if metric is not None:
            clauses.append("metric = ?")
            params.append(metric)
        if as_of is not None:
            if as_of.tzinfo is None:
                raise ValueError("as_of must be timezone-aware")
            clauses.append("observed_at <= ?")
            params.append(as_of.isoformat())
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        with self._connect() as conn:
            rows = conn.execute(
                f"SELECT * FROM observations {where} ORDER BY observed_at, observation_id",
                params,
            ).fetchall()
        return [Observation(
            topic=row["topic"], source=row["source"], metric=row["metric"],
            value=float(row["value"]), observed_at=datetime.fromisoformat(row["observed_at"]),
            geography=row["geography"], entity=row["entity"],
            metadata=json.loads(row["metadata_json"]),
        ) for row in rows]

    def topics(self, *, as_of: datetime | None = None) -> list[str]:
        if as_of is None:
            sql, params = "SELECT DISTINCT topic FROM observations ORDER BY topic", ()
        else:
            sql = "SELECT DISTINCT topic FROM observations WHERE observed_at <= ? ORDER BY topic"
            params = (as_of.isoformat(),)
        with self._connect() as conn:
            return [row[0] for row in conn.execute(sql, params).fetchall()]
