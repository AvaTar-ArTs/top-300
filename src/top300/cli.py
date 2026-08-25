from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .adapters.google_trends import GoogleTrendsRSSAdapter
from .adapters.hacker_news import HackerNewsAdapter
from .backtest import walk_forward_backtest
from .dataset import load_backtest_rows, load_training_rows
from .features import FeatureBuilder
from .forecast import HeuristicForecaster, LearnedForecaster
from .ingest import ingest_file
from .live import LiveCollector
from .observations import Observation
from .ranking import rank_forecasts
from .store import SignalStore


def _parse_time(value: str) -> datetime:
    if value.lower() == "now":
        return datetime.now(timezone.utc)
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def _demo_rows() -> list[Observation]:
    start = datetime(2026, 8, 20, tzinfo=timezone.utc)
    profiles = {
        "alpha-agent": [10, 11, 13, 18, 30, 55, 100, 190],
        "beta-video": [30, 31, 33, 35, 38, 42, 47, 53],
        "gamma-noise": [20, 19, 21, 20, 22, 19, 20, 21],
    }
    rows: list[Observation] = []
    for topic, values in profiles.items():
        for index, value in enumerate(values):
            observed_at = start + timedelta(hours=index)
            rows.extend(
                [
                    Observation(topic, "reddit", "attention", value, observed_at),
                    Observation(topic, "youtube", "attention", value * 0.8, observed_at),
                    Observation(topic, "google", "demand", value * 1.2, observed_at),
                    Observation(
                        topic,
                        "youtube",
                        "supply",
                        max(2.0, value * (0.12 if topic == "alpha-agent" else 0.35)),
                        observed_at,
                    ),
                    Observation(
                        topic,
                        "reddit",
                        "creator_count",
                        max(1.0, value * 0.08),
                        observed_at,
                    ),
                    Observation(
                        topic,
                        "google",
                        "related_query_count",
                        3 + index * (2 if topic == "alpha-agent" else 1),
                        observed_at,
                    ),
                    Observation(topic, "google", "geo_count", 2 + index, observed_at),
                ]
            )
    return rows


def _forecast_all(store: SignalStore, as_of: datetime) -> list[dict[str, object]]:
    builder = FeatureBuilder()
    engine = HeuristicForecaster()
    forecasts = [
        engine.predict(topic, as_of, builder.build(store, topic, as_of))
        for topic in store.topics(as_of=as_of)
    ]
    return [row.as_dict() for row in rank_forecasts(forecasts)]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="top300",
        description="Forecast breakout trend opportunities",
    )
    commands = parser.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init")
    init.add_argument("path")
    ingest = commands.add_parser("ingest")
    ingest.add_argument("store")
    ingest.add_argument("input")
    live = commands.add_parser("collect-live")
    live.add_argument("store")
    live.add_argument("--snapshot", required=True)
    live.add_argument("--geo", default="US")
    live.add_argument("--hn-limit", type=int, default=30)
    live.add_argument("--observed-at", default="now")
    features = commands.add_parser("features")
    features.add_argument("store")
    features.add_argument("--as-of", default="now")
    forecast = commands.add_parser("forecast")
    forecast.add_argument("store")
    forecast.add_argument("--as-of", default="now")
    rank = commands.add_parser("rank")
    rank.add_argument("store")
    rank.add_argument("--as-of", default="now")
    rank.add_argument("--top", type=int, default=300)
    train = commands.add_parser("train")
    train.add_argument("features_csv")
    train.add_argument("--model", required=True)
    backtest = commands.add_parser("backtest")
    backtest.add_argument("features_csv")
    backtest.add_argument("--min-train", type=int, default=20)
    demo = commands.add_parser("demo")
    demo.add_argument("path")
    return parser


def _run_live(args: argparse.Namespace) -> int:
    observed_at = _parse_time(args.observed_at)
    collector = LiveCollector(
        sources={
            "google_trends": GoogleTrendsRSSAdapter(),
            "hacker_news": HackerNewsAdapter(),
        }
    )
    report = collector.collect(
        store=SignalStore(args.store),
        observed_at=observed_at,
        snapshot_path=args.snapshot,
        source_kwargs={
            "google_trends": {"geography": args.geo},
            "hacker_news": {"limit": args.hn_limit},
        },
    )
    print(
        json.dumps(
            {
                "observed_at": report.observed_at.isoformat(),
                "inserted": report.inserted,
                "successful_sources": report.successful_sources,
                "sources": {
                    name: {
                        "status": health.status,
                        "observations": health.observations,
                        "error": health.error,
                    }
                    for name, health in report.sources.items()
                },
                "snapshot": str(args.snapshot),
            }
        )
    )
    return 0 if report.successful_sources else 1


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "init":
        target = Path(args.path)
        target.mkdir(parents=True, exist_ok=True)
        SignalStore(target / "top300.db")
        return 0
    if args.command == "ingest":
        count = ingest_file(SignalStore(args.store), args.input)
        print(json.dumps({"inserted": count}))
        return 0
    if args.command == "collect-live":
        return _run_live(args)
    if args.command == "train":
        engine = LearnedForecaster().fit(load_training_rows(args.features_csv))
        engine.save(args.model)
        print(json.dumps({"model": str(args.model), "horizons": sorted(engine.models)}))
        return 0
    if args.command == "backtest":
        report = walk_forward_backtest(
            load_backtest_rows(args.features_csv),
            min_train=args.min_train,
        )
        print(
            json.dumps(
                {
                    "predictions": report.predictions,
                    "brier": report.brier,
                    "precision_at_5": report.precision_at_5,
                }
            )
        )
        return 0
    if args.command in {"features", "forecast", "rank"}:
        store = SignalStore(args.store)
        as_of = _parse_time(args.as_of)
        if args.command == "features":
            builder = FeatureBuilder()
            payload = {
                topic: builder.build(store, topic, as_of).as_dict()
                for topic in store.topics(as_of=as_of)
            }
        else:
            payload = _forecast_all(store, as_of)
            if args.command == "rank":
                payload = payload[: args.top]
        print(json.dumps(payload, indent=2))
        return 0
    if args.command == "demo":
        target = Path(args.path)
        target.mkdir(parents=True, exist_ok=True)
        store = SignalStore(target / "top300.db")
        store.add_many(_demo_rows())
        as_of = datetime(2026, 8, 20, 7, tzinfo=timezone.utc)
        ranked = _forecast_all(store, as_of)
        (target / "ranked.json").write_text(
            json.dumps(ranked, indent=2),
            encoding="utf-8",
        )
        with (target / "ranked.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(ranked[0].keys()))
            writer.writeheader()
            writer.writerows(ranked)
        print(
            json.dumps(
                {
                    "store": str(store.path),
                    "ranked": str(target / "ranked.json"),
                }
            )
        )
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
