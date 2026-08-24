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
