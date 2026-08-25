import json
from pathlib import Path

import pytest

from top300.ingest import IngestError, load_observations


def test_load_csv(tmp_path: Path) -> None:
    path = tmp_path / "signals.csv"
    path.write_text(
        "topic,source,metric,value,observed_at\n"
        "alpha,reddit,attention,10,2026-08-24T10:00:00+00:00\n",
        encoding="utf-8",
    )
    rows = load_observations(path)
    assert len(rows) == 1
    assert rows[0].topic == "alpha"
    assert rows[0].value == 10


def test_load_csv_reports_bad_row(tmp_path: Path) -> None:
    path = tmp_path / "bad.csv"
    path.write_text(
        "topic,source,metric,value,observed_at\n"
        "alpha,reddit,attention,nope,2026-08-24T10:00:00+00:00\n",
        encoding="utf-8",
    )
    with pytest.raises(IngestError, match="row 2"):
        load_observations(path)


def test_live_snapshot_json_is_reingestable(tmp_path: Path) -> None:
    path = tmp_path / "snapshot.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "collector_version": "1.1.0",
                "observed_at": "2026-08-25T00:54:42+00:00",
                "source_parameters": {"google_trends": {"geography": "US"}},
                "sources": {},
                "observations": [
                    {
                        "observation_id": "ignored-on-import",
                        "topic": "example trend",
                        "source": "google_trends",
                        "metric": "demand",
                        "value": 2000,
                        "observed_at": "2026-08-25T00:54:42+00:00",
                        "geography": "US",
                        "entity": None,
                        "metadata": {"trend_started_at": "2026-08-25T00:00:00+00:00"},
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    rows = load_observations(path)
    assert len(rows) == 1
    assert rows[0].topic == "example trend"
    assert rows[0].source == "google_trends"
    assert rows[0].value == 2000
    assert rows[0].geography == "US"
