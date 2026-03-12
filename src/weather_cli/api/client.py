"""
Weather API Client for WeatherAPI.com service.

Handles authentication, request building, and response parsing.
"""

import os
from typing import Optional, Dict, Any
import requests
from requests.exceptions import RequestException, Timeout, ConnectionError

from weather_cli.exceptions import (
    WeatherCLIError,
    AuthenticationError,
    InvalidLocationError,
    RateLimitError,
    NetworkError,
    APIResponseError,
)


class WeatherClient:
    """Client for interacting with WeatherAPI.com."""

    BASE_URL = "https://api.weatherapi.com/v1"

    def __init__(self, api_key: str) -> None:
        """
        Initialize the WeatherClient with an API key.

        Args:
            api_key: WeatherAPI.com API key

        Raises:
            ValueError: If api_key is empty or invalid format
        """
        if not api_key or not isinstance(api_key, str) or not api_key.strip():
            raise ValueError("API key must be a non-empty string")

        self.api_key = api_key.strip()
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "weather-cli/0.1.0"})

    def get_current(self, location: str) -> Dict[str, Any]:
        """
        Fetch current weather for a location.

        Args:
            location: City name, coordinates (lat,lon), or other location formats

        Returns:
            Dictionary with current weather data (includes both metric and imperial values)

        Raises:
            InvalidLocationError: If location is not found
            AuthenticationError: If API key is invalid
            RateLimitError: If rate limit is exceeded
            NetworkError: For network/connection issues
            APIResponseError: For malformed API responses
        """
        if not location or not location.strip():
            raise ValueError("Location must be a non-empty string")

        params = {
            "key": self.api_key,
            "q": location.strip(),
            "aqi": "no",  # Skip air quality to reduce data
        }

        try:
            response = self.session.get(
                f"{self.BASE_URL}/current.json", params=params, timeout=10
            )
            self._handle_response_errors(response)

            try:
                data = response.json()
            except ValueError as e:
                raise APIResponseError(
                    f"Invalid response format from API: {str(e)}", response_data=None
                ) from e

            # Validate essential response structure
            if not isinstance(data, dict):
                raise APIResponseError(
                    "API returned non-dictionary response", response_data=data
                )

            return data

        except Timeout as e:
            raise NetworkError(
                f"Request timeout: The server did not respond within 10 seconds",
                original_error=e,
            ) from e
        except ConnectionError as e:
            raise NetworkError(
                f"Connection error: Unable to connect to the weather service",
                original_error=e,
            ) from e
        except RequestException as e:
            raise NetworkError(f"Network error: {str(e)}", original_error=e) from e

    def get_forecast(self, location: str, days: int = 3) -> Dict[str, Any]:
        """
        Fetch weather forecast for a location.

        Args:
            location: City name, coordinates (lat,lon), or other location formats
            days: Number of forecast days (1-15)

        Returns:
            Dictionary with forecast data including current + forecast days (contains both metric and imperial values)

        Raises:
            ValueError: If days is out of valid range (1-15)
            InvalidLocationError: If location is not found
            AuthenticationError: If API key is invalid
            RateLimitError: If rate limit is exceeded
            NetworkError: For network/connection issues
            APIResponseError: For malformed API responses
        """
        if not 1 <= days <= 15:
            raise ValueError("Forecast days must be between 1 and 15")

        if not location or not location.strip():
            raise ValueError("Location must be a non-empty string")

        params = {
            "key": self.api_key,
            "q": location.strip(),
            "days": days,
            "aqi": "no",
            "alerts": "no",
        }

        try:
            response = self.session.get(
                f"{self.BASE_URL}/forecast.json", params=params, timeout=15
            )

            self._handle_response_errors(response)

            try:
                data = response.json()
            except ValueError as e:
                raise APIResponseError(
                    f"Invalid response format from API: {str(e)}", response_data=None
                ) from e

            # Validate essential response structure
            if not isinstance(data, dict):
                raise APIResponseError(
                    "API returned non-dictionary response", response_data=data
                )

            return data

        except Timeout as e:
            raise NetworkError(
                f"Request timeout: The server did not respond within 15 seconds",
                original_error=e,
            ) from e
        except ConnectionError as e:
            raise NetworkError(
                f"Connection error: Unable to connect to the weather service",
                original_error=e,
            ) from e
        except RequestException as e:
            raise NetworkError(f"Network error: {str(e)}", original_error=e) from e

    def _handle_response_errors(self, response: requests.Response) -> None:
        """
        Handle HTTP response errors and raise appropriate exceptions.

        Args:
            response: requests.Response object

        Raises:
            AuthenticationError: 401, 403
            InvalidLocationError: 400, 404
            RateLimitError: 429
            WeatherCLIError: Other error codes
        """
        if response.status_code == 200:
            return

        error_data = {}
        try:
            error_data = response.json()
        except (ValueError, KeyError):
            pass

        error_message = error_data.get("error", {}).get(
            "message", f"HTTP {response.status_code}"
        )

        if response.status_code in (401, 403):
            raise AuthenticationError(f"API authentication failed: {error_message}")
        elif response.status_code in (400, 404):
            raise InvalidLocationError(f"Location not found: {error_message}")
        elif response.status_code == 429:
            raise RateLimitError(f"Rate limit exceeded: {error_message}")
        else:
            raise APIResponseError(
                f"API error ({response.status_code}): {error_message}"
            )

    def close(self) -> None:
        """Close the underlying session."""
        self.session.close()

    def __enter__(self) -> "WeatherClient":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()
