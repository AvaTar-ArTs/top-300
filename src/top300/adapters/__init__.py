from .base import ObservationAdapter
from .files import FileObservationAdapter
from .google_trend_archive import GoogleTrendArchiveAdapter
from .google_trends import GoogleTrendsRSSAdapter
from .hacker_news import HackerNewsAdapter

__all__ = [
    "FileObservationAdapter",
    "GoogleTrendArchiveAdapter",
    "GoogleTrendsRSSAdapter",
    "HackerNewsAdapter",
    "ObservationAdapter",
]
