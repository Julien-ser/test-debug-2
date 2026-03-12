"""
Weather API Client for WeatherAPI.com service.

Handles authentication, request building, and response parsing.
"""

import os
import time
import logging
from typing import Optional, Dict, Any, Tuple
import requests
from requests.exceptions import (
    RequestException,
    Timeout,
    ConnectionError,
    SSLError,
    HTTPError,
)

from weather_cli import cache
from weather_cli.exceptions import (
    WeatherCLIError,
    AuthenticationError,
    InvalidLocationError,
    RateLimitError,
    NetworkError,
    DNSLookupError,
    SSLVerificationError,
    APIResponseError,
)

logger = logging.getLogger(__name__)


class WeatherClient:
    """Client for interacting with WeatherAPI.com."""

    BASE_URL = "https://api.weatherapi.com/v1"
    MAX_RETRIES = 3
    RETRY_BACKOFF_FACTOR = 0.5
    REQUIRED_CURRENT_FIELDS = {"location", "current"}
    REQUIRED_FORECAST_FIELDS = {"location", "current", "forecast"}

    def __init__(self, api_key: str, max_retries: int = MAX_RETRIES) -> None:
        """
        Initialize the WeatherClient with an API key.

        Args:
            api_key: WeatherAPI.com API key
            max_retries: Maximum number of retry attempts for transient failures (default: 3)

        Raises:
            ValueError: If api_key is empty or invalid format
        """
        if not api_key or not isinstance(api_key, str) or not api_key.strip():
            raise ValueError("API key must be a non-empty string")

        self.api_key = api_key.strip()
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "weather-cli/0.1.0"})
        # Install caching on this session with 10-minute TTL
        cache.install_cache(self.session, ttl=600)

    def get_current(self, location: str) -> Dict[str, Any]:
        """
        Fetch current weather for a location with retry logic for transient failures.

        Args:
            location: City name, coordinates (lat,lon), or other location formats

        Returns:
            Dictionary with current weather data (includes both metric and imperial values)

        Raises:
            InvalidLocationError: If location is not found
            AuthenticationError: If API key is invalid
            RateLimitError: If rate limit is exceeded
            NetworkError: For network/connection issues
            APIResponseError: For malformed API responses or missing required fields
        """
        if not location or not location.strip():
            raise ValueError("Location must be a non-empty string")

        params = {
            "key": self.api_key,
            "q": location.strip(),
            "aqi": "no",  # Skip air quality to reduce data
        }

        last_exception = None
        for attempt in range(self.max_retries):
            try:
                logger.debug(
                    f"Attempt {attempt + 1}/{self.max_retries} for location: {location}"
                )
                response = self.session.get(
                    f"{self.BASE_URL}/current.json", params=params, timeout=10
                )
                self._handle_response_errors(response, attempt)

                try:
                    data = response.json()
                except ValueError as e:
                    raise APIResponseError(
                        f"Invalid response format from API: {str(e)}",
                        response_data=None,
                    ) from e

                # Validate essential response structure
                self._validate_response_structure(
                    data, self.REQUIRED_CURRENT_FIELDS, "current weather"
                )

                # Log successful request
                logger.info(f"Successfully fetched current weather for {location}")
                return data

            except (Timeout, ConnectionError, SSLError) as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    wait_time = self.RETRY_BACKOFF_FACTOR * (2**attempt)
                    logger.warning(
                        f"Network error (attempt {attempt + 1}/{self.max_retries}). Retrying in {wait_time}s..."
                    )
                    time.sleep(wait_time)
                    continue
                else:
                    # All retries exhausted
                    if isinstance(e, Timeout):
                        raise NetworkError(
                            f"Request timeout after {self.max_retries} retries: The server did not respond within 10 seconds. "
                            "This could be due to high server load or network congestion.",
                            original_error=e,
                        ) from e
                    elif isinstance(e, SSLError):
                        raise SSLVerificationError(
                            f"SSL/TLS verification failed after {self.max_retries} retries. "
                            "This may indicate a network issue, outdated certificates, or security intervention.",
                            original_error=e,
                        ) from e
                    elif isinstance(e, ConnectionError):
                        # Check if it's likely a DNS error
                        if "Name or service not known" in str(
                            e
                        ) or "getaddrinfo" in str(e):
                            raise DNSLookupError(
                                f"DNS lookup failed after {self.max_retries} retries. "
                                "Please check your internet connection and verify the location name.",
                                original_error=e,
                            ) from e
                        raise NetworkError(
                            f"Connection error after {self.max_retries} retries: Unable to connect to the weather service. "
                            "Please check your internet connection and try again.",
                            original_error=e,
                        ) from e
                    else:
                        raise NetworkError(
                            f"Network error: {str(e)}", original_error=e
                        ) from e
            except RequestException as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    wait_time = self.RETRY_BACKOFF_FACTOR * (2**attempt)
                    logger.warning(
                        f"Request exception (attempt {attempt + 1}/{self.max_retries}). Retrying in {wait_time}s..."
                    )
                    time.sleep(wait_time)
                    continue
                else:
                    raise NetworkError(
                        f"Network error after {self.max_retries} retries: {str(e)}",
                        original_error=e,
                    ) from e
            except Exception as e:
                # Non-retryable error, re-raise immediately
                raise

    def get_forecast(self, location: str, days: int = 3) -> Dict[str, Any]:
        """
        Fetch weather forecast for a location with retry logic for transient failures.

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
            APIResponseError: For malformed API responses or missing required fields
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

        last_exception = None
        for attempt in range(self.max_retries):
            try:
                logger.debug(
                    f"Attempt {attempt + 1}/{self.max_retries} for forecast: {location}, days: {days}"
                )
                response = self.session.get(
                    f"{self.BASE_URL}/forecast.json", params=params, timeout=15
                )
                self._handle_response_errors(response, attempt)

                try:
                    data = response.json()
                except ValueError as e:
                    raise APIResponseError(
                        f"Invalid response format from API: {str(e)}",
                        response_data=None,
                    ) from e

                # Validate essential response structure
                self._validate_response_structure(
                    data, self.REQUIRED_FORECAST_FIELDS, "forecast"
                )

                # Log successful request
                logger.info(
                    f"Successfully fetched forecast for {location}, days: {days}"
                )
                return data

            except (Timeout, ConnectionError, SSLError) as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    wait_time = self.RETRY_BACKOFF_FACTOR * (2**attempt)
                    logger.warning(
                        f"Network error (attempt {attempt + 1}/{self.max_retries}). Retrying in {wait_time}s..."
                    )
                    time.sleep(wait_time)
                    continue
                else:
                    # All retries exhausted
                    if isinstance(e, Timeout):
                        raise NetworkError(
                            f"Request timeout after {self.max_retries} retries: The server did not respond within 15 seconds. "
                            "This could be due to high server load or network congestion.",
                            original_error=e,
                        ) from e
                    elif isinstance(e, SSLError):
                        raise SSLVerificationError(
                            f"SSL/TLS verification failed after {self.max_retries} retries. "
                            "This may indicate a network issue, outdated certificates, or security intervention.",
                            original_error=e,
                        ) from e
                    elif isinstance(e, ConnectionError):
                        if "Name or service not known" in str(
                            e
                        ) or "getaddrinfo" in str(e):
                            raise DNSLookupError(
                                f"DNS lookup failed after {self.max_retries} retries. "
                                "Please check your internet connection and verify the location name.",
                                original_error=e,
                            ) from e
                        raise NetworkError(
                            f"Connection error after {self.max_retries} retries: Unable to connect to the weather service. "
                            "Please check your internet connection and try again.",
                            original_error=e,
                        ) from e
                    else:
                        raise NetworkError(
                            f"Network error: {str(e)}", original_error=e
                        ) from e
            except RequestException as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    wait_time = self.RETRY_BACKOFF_FACTOR * (2**attempt)
                    logger.warning(
                        f"Request exception (attempt {attempt + 1}/{self.max_retries}). Retrying in {wait_time}s..."
                    )
                    time.sleep(wait_time)
                    continue
                else:
                    raise NetworkError(
                        f"Network error after {self.max_retries} retries: {str(e)}",
                        original_error=e,
                    ) from e
            except Exception as e:
                # Non-retryable error, re-raise immediately
                raise

    def _handle_response_errors(
        self, response: requests.Response, attempt: int = 0
    ) -> None:
        """
        Handle HTTP response errors and raise appropriate exceptions.

        Args:
            response: requests.Response object
            attempt: Current retry attempt number (for logging)

        Raises:
            AuthenticationError: 401, 403
            InvalidLocationError: 400, 404
            RateLimitError: 429
            APIResponseError: Other error codes (5xx, etc.)
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

        # Check for Retry-After header for rate limiting
        retry_after = None
        if response.status_code == 429:
            retry_after_header = response.headers.get("Retry-After")
            if retry_after_header:
                try:
                    retry_after = int(str(retry_after_header))
                except (ValueError, TypeError):
                    pass

        if response.status_code in (401, 403):
            logger.error(
                f"Authentication failed (attempt {attempt + 1}): {error_message}"
            )
            raise AuthenticationError(
                f"API authentication failed: {error_message}. "
                "Please check your API key is correct and active.",
                status_code=response.status_code,
            )
        elif response.status_code in (400, 404):
            logger.warning(
                f"Location not found (attempt {attempt + 1}): {error_message}"
            )
            raise InvalidLocationError(
                f"Location not found: {error_message}. "
                "Try using a different city name, coordinates (lat,lon), or postal code. "
                "Check for typos and ensure the location is recognized by WeatherAPI.com.",
                location=response.headers.get("location", ""),
                status_code=response.status_code,
            )
        elif response.status_code == 429:
            logger.warning(
                f"Rate limit exceeded (attempt {attempt + 1}): {error_message}"
            )
            raise RateLimitError(
                f"Rate limit exceeded: {error_message}. "
                f"Please wait {'retry-after header missing' if retry_after is None else f'{retry_after} seconds'} before trying again. "
                "Consider upgrading your API plan if this persists.",
                retry_after=retry_after,
                status_code=response.status_code,
            )
        elif 500 <= response.status_code < 600:
            # Server errors - potentially transient
            logger.error(
                f"Server error {response.status_code} (attempt {attempt + 1}): {error_message}"
            )
            raise APIResponseError(
                f"WeatherAPI server error ({response.status_code}): {error_message}. "
                "This is likely a temporary issue. Please try again in a moment."
            )
        else:
            logger.error(
                f"Unexpected HTTP {response.status_code} (attempt {attempt + 1}): {error_message}"
            )
            raise APIResponseError(
                f"API error ({response.status_code}): {error_message}. "
                "Please check your request parameters and try again."
            )

    def _validate_response_structure(
        self, data: Dict[str, Any], required_fields: set, context: str
    ) -> None:
        """
        Validate that API response contains all required fields.

        Args:
            data: Response data dictionary
            required_fields: Set of required top-level field names
            context: Context for error message (e.g., "current weather")

        Raises:
            APIResponseError: If required fields are missing or data is not a dict
        """
        if not isinstance(data, dict):
            raise APIResponseError(
                f"API response is not a dictionary for {context}. "
                f"Received type: {type(data).__name__}. "
                "This may indicate an API change or malformed response."
            )

        missing = required_fields - set(data.keys())
        if missing:
            raise APIResponseError(
                f"API response missing required fields for {context}: {', '.join(sorted(missing))}. "
                f"Received fields: {', '.join(sorted(data.keys()))}. "
                "This may indicate an API change or incomplete response."
            )

        # Validate nested structure for current weather
        if "current" in required_fields and "current" in data:
            if not isinstance(data["current"], dict):
                raise APIResponseError(
                    f"API response 'current' field is not a dictionary for {context}."
                )
            current = data["current"]
            # Check for essential current weather fields
            essential_current = {"temp_c", "temp_f"}  # At least one should exist
            if not any(field in current for field in essential_current):
                raise APIResponseError(
                    f"API response 'current' object missing temperature data for {context}. "
                    f"Available fields: {', '.join(sorted(current.keys()))}"
                )

    def close(self) -> None:
        """Close the underlying session."""
        self.session.close()

    def __enter__(self) -> "WeatherClient":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()
