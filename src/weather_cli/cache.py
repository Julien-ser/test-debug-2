"""
Caching layer for Weather API responses using requests-cache.

Provides transparent caching for API responses with configurable TTL.
"""

import os
from pathlib import Path
from typing import Optional
import requests_cache
from requests import Session


def get_cache_path() -> Path:
    """
    Get the cache file path.

    Returns:
        Path to SQLite cache database
    """
    cache_dir = Path.home() / ".cache" / "weather-cli"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / "weather_cache.sqlite"


def install_cache(
    session: Optional[Session] = None, ttl: int = 600, cache_path: Optional[Path] = None
) -> Session:
    """
    Install caching on a requests session.

    Args:
        session: Session to install cache on (creates new if None)
        ttl: Time-to-live in seconds (default 600 = 10 minutes)
        cache_path: Override default cache location

    Returns:
        Session with caching enabled
    """
    if session is None:
        session = Session()

    if cache_path is None:
        cache_path = get_cache_path()

    requests_cache.install_cache(
        str(cache_path),
        backend="sqlite",
        expire_after=ttl,
        allowable_codes=(200,),  # Only cache successful responses
        allowable_methods=["GET"],
        session=session,
        match_headers=["Accept"],  # Vary by Accept header
    )

    return session


def clear_cache(cache_path: Optional[Path] = None) -> None:
    """
    Clear the cache database.

    Args:
        cache_path: Override default cache location
    """
    if cache_path is None:
        cache_path = get_cache_path()

    if cache_path.exists():
        cache_path.unlink()


def get_cache_info(cache_path: Optional[Path] = None) -> dict:
    """
    Get information about the cache.

    Args:
        cache_path: Override default cache location

    Returns:
        Dictionary with cache stats (size, entries, etc.)
    """
    if cache_path is None:
        cache_path = get_cache_path()

    if not cache_path.exists():
        return {"exists": False, "size_bytes": 0, "entries": 0}

    stat = cache_path.stat()
    return {
        "exists": True,
        "size_bytes": stat.st_size,
        "path": str(cache_path),
    }
