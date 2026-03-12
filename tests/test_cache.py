"""
Unit tests for cache module.

Tests cover cache path generation, installation, clearing, and info retrieval.
"""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import tempfile
import os

from weather_cli.cache import (
    get_cache_path,
    install_cache,
    clear_cache,
    get_cache_info,
)
from weather_cli.api.client import WeatherClient


class TestGetCachePath:
    """Tests for get_cache_path function."""

    def test_get_cache_path_returns_correct_path(self):
        """Test cache path is in ~/.cache/weather-cli/weather_cache.sqlite."""
        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = Path("/home/testuser")
            # Patch mkdir to avoid permission errors in test
            with patch.object(Path, "mkdir"):
                cache_path = get_cache_path()
                assert cache_path == Path(
                    "/home/testuser/.cache/weather-cli/weather_cache.sqlite"
                )

    def test_get_cache_path_creates_directory(self):
        """Test that cache directory is created."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_home = Path(temp_dir)
            with patch("pathlib.Path.home", return_value=temp_home):
                cache_path = get_cache_path()
                # The directory should be created
                assert cache_path.parent.exists()
                assert cache_path.parent.is_dir()
                # The expected cache file path
                assert (
                    cache_path
                    == temp_home / ".cache" / "weather-cli" / "weather_cache.sqlite"
                )


class TestInstallCache:
    """Tests for install_cache function."""

    def test_install_cache_with_custom_session(self):
        """Test install_cache installs cache on provided session."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_cache = Path(temp_dir) / "test_cache.sqlite"
            with patch("weather_cli.cache.get_cache_path", return_value=temp_cache):
                mock_session = MagicMock()
                result_session = install_cache(session=mock_session)

                # Should return the same session
                assert result_session is mock_session
                # Should have called requests_cache.install_cache with correct session
                # (verified by other tests)

    def test_install_cache_configures_parameters(self):
        """Test install_cache configures cache with correct parameters."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_cache = Path(temp_dir) / "test_cache.sqlite"
            with patch("weather_cli.cache.get_cache_path", return_value=temp_cache):
                with patch("requests_cache.install_cache") as mock_install:
                    mock_session = MagicMock()
                    install_cache(session=mock_session, ttl=300)

                    # Verify install_cache was called with correct params
                    mock_install.assert_called_once()
                    call_kwargs = mock_install.call_args[1]
                    assert call_kwargs["backend"] == "sqlite"
                    assert call_kwargs["expire_after"] == 300
                    assert call_kwargs["allowable_codes"] == (200,)
                    assert call_kwargs["allowable_methods"] == ["GET"]
                    assert call_kwargs["match_headers"] == ["Accept"]
                    assert call_kwargs["session"] is mock_session

    def test_install_cache_creates_new_session_if_none_provided(self):
        """Test install_cache creates new session when None provided."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_cache = Path(temp_dir) / "test_cache.sqlite"
            with patch("weather_cli.cache.get_cache_path", return_value=temp_cache):
                with patch("requests_cache.install_cache"):
                    session = install_cache()
                    # Should return a session
                    assert session is not None


class TestClearCache:
    """Tests for clear_cache function."""

    def test_clear_cache_removes_existing_cache(self):
        """Test clear_cache removes existing cache file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_cache = Path(temp_dir) / "test_cache.sqlite"
            # Create cache file
            temp_cache.touch()
            assert temp_cache.exists()

            with patch("weather_cli.cache.get_cache_path", return_value=temp_cache):
                clear_cache()
                assert not temp_cache.exists()

    def test_clear_cache_handles_nonexistent_cache(self):
        """Test clear_cache handles non-existent cache gracefully."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_cache = Path(temp_dir) / "nonexistent_cache.sqlite"
            assert not temp_cache.exists()

            with patch("weather_cli.cache.get_cache_path", return_value=temp_cache):
                # Should not raise an exception
                clear_cache()
                assert not temp_cache.exists()

    def test_clear_cache_with_custom_path(self):
        """Test clear_cache works with custom cache path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_cache = Path(temp_dir) / "custom_cache.sqlite"
            temp_cache.touch()
            assert temp_cache.exists()

            clear_cache(cache_path=temp_cache)
            assert not temp_cache.exists()


class TestGetCacheInfo:
    """Tests for get_cache_info function."""

    def test_get_cache_info_nonexistent_cache(self):
        """Test get_cache_info returns empty info for non-existent cache."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_cache = Path(temp_dir) / "nonexistent.sqlite"
            info = get_cache_info(cache_path=temp_cache)

            assert info == {"exists": False, "size_bytes": 0, "entries": 0}

    def test_get_cache_info_existing_cache(self):
        """Test get_cache_info returns size info for existing cache."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_cache = Path(temp_dir) / "existing.sqlite"
            # Create file with some content
            temp_cache.write_bytes(b"test content")

            info = get_cache_info(cache_path=temp_cache)

            assert info["exists"] is True
            assert info["size_bytes"] == len(b"test content")
            assert info["path"] == str(temp_cache)

    def test_get_cache_info_with_custom_path(self):
        """Test get_cache_info uses custom cache path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_cache = Path(temp_dir) / "custom.sqlite"
            temp_cache.write_bytes(b"custom data")

            info = get_cache_info(cache_path=temp_cache)

            assert info["exists"] is True
            assert info["size_bytes"] == len(b"custom data")


class TestWeatherClientCacheIntegration:
    """Tests for WeatherClient caching integration."""

    def test_weather_client_initializes_with_cache(self):
        """Test WeatherClient installs cache on initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_cache = Path(temp_dir) / "client_test.sqlite"
            with patch("weather_cli.cache.get_cache_path", return_value=temp_cache):
                with patch("requests_cache.install_cache") as mock_install:
                    client = WeatherClient("test_key")

                    # Verify cache was installed
                    mock_install.assert_called_once()
                    # Verify TTL is 600 seconds (10 minutes)
                    call_kwargs = mock_install.call_args[1]
                    assert call_kwargs["expire_after"] == 600

    def test_weather_client_cache_configuration(self):
        """Test WeatherClient uses proper cache configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_cache = Path(temp_dir) / "client_config.sqlite"
            with patch("weather_cli.cache.get_cache_path", return_value=temp_cache):
                with patch("requests_cache.install_cache") as mock_install:
                    client = WeatherClient("test_key")

                    call_kwargs = mock_install.call_args[1]
                    assert call_kwargs["backend"] == "sqlite"
                    assert call_kwargs["allowable_codes"] == (200,)
                    assert call_kwargs["allowable_methods"] == ["GET"]

    def test_weather_client_uses_cached_session(self):
        """Test WeatherClient uses cached session for API calls."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_cache = Path(temp_dir) / "caching_test.sqlite"
            with patch("weather_cli.cache.get_cache_path", return_value=temp_cache):
                # Real test with actual cache
                client = WeatherClient("test_key")

                # The session should have caching enabled
                # requests-cache adds a 'cache' attribute to CachedSession
                assert hasattr(client.session, "cache")
