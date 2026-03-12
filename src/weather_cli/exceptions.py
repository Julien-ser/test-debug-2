"""
Custom exceptions for weather CLI application.

These exceptions provide clear error categorization for different failure scenarios,
enabling appropriate user messaging and error recovery strategies.
"""

from typing import Optional, Dict, Any


class WeatherCLIError(Exception):
    """Base exception for all weather CLI errors."""

    pass


class AuthenticationError(WeatherCLIError):
    """Raised when API authentication fails."""

    def __init__(self, message: str, status_code: Optional[int] = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class InvalidLocationError(WeatherCLIError):
    """Raised when the location is invalid or not found."""

    def __init__(
        self,
        message: str,
        location: Optional[str] = None,
        status_code: Optional[int] = None,
    ) -> None:
        super().__init__(message)
        self.location = location
        self.status_code = status_code


class RateLimitError(WeatherCLIError):
    """Raised when API rate limit is exceeded."""

    def __init__(
        self,
        message: str,
        retry_after: Optional[int] = None,
        status_code: Optional[int] = None,
    ) -> None:
        super().__init__(message)
        self.retry_after = retry_after
        self.status_code = status_code


class NetworkError(WeatherCLIError):
    """Raised when network/connection issues occur."""

    def __init__(
        self, message: str, original_error: Optional[Exception] = None
    ) -> None:
        super().__init__(message)
        self.original_error = original_error


class APIResponseError(WeatherCLIError):
    """Raised when API returns an unexpected or malformed response."""

    def __init__(
        self, message: str, response_data: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message)
        self.response_data = response_data


class ValidationError(WeatherCLIError):
    """Raised when input validation fails."""

    def __init__(self, message: str, field: Optional[str] = None) -> None:
        super().__init__(message)
        self.field = field
