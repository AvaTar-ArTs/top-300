from __future__ import annotations

import csv
from datetime import datetime, timedelta, timezone
from pathlib import Path

from top300.cli import _demo_rows
from top300.models import FeatureSnapshot


def write_signals(path: Path) -> None:
    fields = [
        "topic",
        "source",
        "metric",
        "value",
        "observed_at",
        "geography",
        "entity",
        "metadata",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in _demo_rows():
            writer.writerow(
                {
                    "topic": row.topic,
                    "source": row.source,
                    "metric": row.metric,
                    "value": row.value,
                    "observed_at": row.observed_at.isoformat(),
                    "geography": row.geography or "",
                    "entity": row.entity or "",
                    "metadata": "",
                }
            )


def write_training(path: Path) -> None:
    names = FeatureSnapshot.feature_names()
    fields = ["topic", "as_of", *names, "label_24h", "label_72h", "label_7d"]
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for i in range(40):
            positive = i >= 20
            base = 0.82 + ((i % 4) * 0.02) if positive else 0.12 + ((i % 4) * 0.02)
            writer.writerow(
                {
                    "topic": f"demo-{i:02d}",
                    "as_of": (start + timedelta(days=i)).isoformat(),
                    **{name: min(0.98, base) for name in names},
                    "label_24h": int(positive),
                    "label_72h": int(positive),
                    "label_7d": int(positive),
                }
            )


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1] / "examples"
    root.mkdir(exist_ok=True)
    write_signals(root / "signals.csv")
    write_training(root / "training_features.csv")
