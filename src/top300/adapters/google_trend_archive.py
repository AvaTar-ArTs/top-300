from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator, Mapping
from datetime import datetime
from typing import Any

from ..historical import TrendEpisode, parse_google_trend_archive_row

DatasetLoader = Callable[..., Iterable[Mapping[str, Any]]]


def _default_loader(repo_id: str, *, split: str, streaming: bool):
    try:
        from datasets import load_dataset
    except ModuleNotFoundError as exc:  # pragma: no cover - dependency boundary
        raise RuntimeError(
            "GoogleTrendArchive streaming requires the optional archive dependency; "
            "install top-300[archive]"
        ) from exc
    return load_dataset(repo_id, split=split, streaming=streaming)


class GoogleTrendArchiveAdapter:
    """Stream bounded GoogleTrendArchive episodes without downloading the full corpus."""

    def __init__(
        self,
        *,
        loader: DatasetLoader | None = None,
        repo_id: str = "aurman/GoogleTrendArchive",
        split: str = "train",
    ) -> None:
        self.loader = loader or _default_loader
        self.repo_id = repo_id
        self.split = split

    def stream(
        self,
        *,
        geography: str | None = None,
        start: datetime | None = None,
        end: datetime | None = None,
        limit: int | None = None,
    ) -> Iterator[TrendEpisode]:
        if start is not None and start.tzinfo is None:
            raise ValueError("start must be timezone-aware")
        if end is not None and end.tzinfo is None:
            raise ValueError("end must be timezone-aware")
        if start is not None and end is not None and end < start:
            raise ValueError("end must not precede start")
        if limit is not None and limit < 0:
            raise ValueError("limit must be non-negative")
        if limit == 0:
            return

        try:
            rows = self.loader(self.repo_id, split=self.split, streaming=True)
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "GoogleTrendArchive streaming requires the optional archive dependency; "
                "install top-300[archive]"
            ) from exc

        emitted = 0
        for row in rows:
            episode = parse_google_trend_archive_row(row)
            if geography is not None and episode.geography != geography:
                continue
            if start is not None and episode.started < start:
                continue
            if end is not None and episode.started > end:
                continue
            yield episode
            emitted += 1
            if limit is not None and emitted >= limit:
                break
