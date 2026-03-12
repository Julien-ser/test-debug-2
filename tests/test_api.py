"""
Unit tests for Weather API Client.

Tests cover successful requests, error handling, and edge cases
using mocking to avoid real API calls.
"""

import json
import pytest
from unittest.mock import Mock, patch, MagicMock
from requests.exceptions import Timeout, ConnectionError, RequestException, SSLError

from weather_cli.api.client import WeatherClient
from weather_cli.exceptions import (
    AuthenticationError,
    InvalidLocationError,
    RateLimitError,
    NetworkError,
    APIResponseError,
    WeatherCLIError,
    SSLVerificationError,
    DNSLookupError,
)


class TestWeatherClientInitialization:
    """Tests for WeatherClient initialization and validation."""

    def test_init_with_valid_api_key(self):
        """Test client initializes with valid API key."""
        client = WeatherClient("test_api_key")
        assert client.api_key == "test_api_key"

    def test_init_strips_whitespace_from_api_key(self):
        """Test client strips whitespace from API key."""
        client = WeatherClient("  test_api_key  ")
        assert client.api_key == "test_api_key"

    def test_init_rejects_empty_api_key(self):
        """Test client rejects empty API key."""
        with pytest.raises(ValueError, match="API key must be a non-empty string"):
            WeatherClient("")

    def test_init_rejects_none_api_key(self):
        """Test client rejects None API key."""
        with pytest.raises(ValueError, match="API key must be a non-empty string"):
            WeatherClient(None)

    def test_init_rejects_whitespace_only_api_key(self):
        """Test client rejects whitespace-only API key."""
        with pytest.raises(ValueError, match="API key must be a non-empty string"):
            WeatherClient("   ")


class TestGetCurrent:
    """Tests for get_current method."""

    @pytest.fixture
    def mock_success_response(self):
        """Create a mock successful API response."""
        return {
            "location": {"name": "London", "country": "GB"},
            "current": {
                "temp_c": 15.0,
                "temp_f": 59.0,
                "feelslike_c": 14.0,
                "feelslike_f": 57.0,
                "humidity": 72,
                "wind_kph": 12.0,
                "wind_mph": 7.5,
                "wind_degree": 180,
                "pressure_mb": 1013,
                "vis_km": 10,
                "vis_miles": 6,
                "last_updated": "2024-01-15 10:30",
                "condition": {"text": "Partly cloudy", "code": 1003},
            },
        }

    def test_get_current_success(self, mock_success_response):
        """Test successful current weather fetch."""
        with patch("requests.Session") as mock_session_class:
            mock_session = MagicMock()
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_success_response
            mock_session.get.return_value = mock_response
            mock_session_class.return_value = mock_session

            client = WeatherClient("test_key")
            result = client.get_current("London")

            assert result == mock_success_response
            mock_session.get.assert_called_once()
            call_args = mock_session.get.call_args
            assert "current.json" in call_args[0][0]
            assert call_args[1]["params"]["q"] == "London"

    def test_get_current_strips_location_whitespace(self, mock_success_response):
        """Test location is stripped of whitespace."""
        with patch("requests.Session") as mock_session_class:
            mock_session = MagicMock()
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_success_response
            mock_session.get.return_value = mock_response
            mock_session_class.return_value = mock_session

            client = WeatherClient("test_key")
            client.get_current("  London  ")

            call_args = mock_session.get.call_args
            assert call_args[1]["params"]["q"] == "London"

    def test_get_current_rejects_empty_location(self):
        """Test get_current rejects empty location."""
        client = WeatherClient("test_key")
        with pytest.raises(ValueError, match="Location must be a non-empty string"):
            client.get_current("")
        with pytest.raises(ValueError, match="Location must be a non-empty string"):
            client.get_current("   ")

    def test_get_current_handles_authentication_error(self):
        """Test get_current handles 401 authentication error."""
        with patch("requests.Session") as mock_session_class:
            mock_session = MagicMock()
            mock_response = Mock()
            mock_response.status_code = 401
            mock_response.json.return_value = {"error": {"message": "Invalid API key"}}
            mock_session.get.return_value = mock_response
            mock_session_class.return_value = mock_session

            client = WeatherClient("test_key")
            with pytest.raises(AuthenticationError, match="API authentication failed"):
                client.get_current("London")

    def test_get_current_handles_invalid_location_400(self):
        """Test get_current handles 400 bad request."""
        with patch("requests.Session") as mock_session_class:
            mock_session = MagicMock()
            mock_response = Mock()
            mock_response.status_code = 400
            mock_response.json.return_value = {
                "error": {"message": "No matching location found"}
            }
            mock_session.get.return_value = mock_response
            mock_session_class.return_value = mock_session

            client = WeatherClient("test_key")
            with pytest.raises(InvalidLocationError, match="Location not found"):
                client.get_current("InvalidCity12345")

    def test_get_current_handles_invalid_location_404(self):
        """Test get_current handles 404 not found."""
        with patch("requests.Session") as mock_session_class:
            mock_session = MagicMock()
            mock_response = Mock()
            mock_response.status_code = 404
            mock_response.json.return_value = {
                "error": {"message": "Location not found"}
            }
            mock_session.get.return_value = mock_response
            mock_session_class.return_value = mock_session

            client = WeatherClient("test_key")
            with pytest.raises(InvalidLocationError):
                client.get_current("Nowhere")

    def test_get_current_handles_rate_limit_429(self):
        """Test get_current handles 429 rate limit."""
        with patch("requests.Session") as mock_session_class:
            mock_session = MagicMock()
            mock_response = Mock()
            mock_response.status_code = 429
            mock_response.json.return_value = {
                "error": {"message": "Rate limit exceeded"}
            }
            mock_session.get.return_value = mock_response
            mock_session_class.return_value = mock_session

            client = WeatherClient("test_key")
            with pytest.raises(RateLimitError, match="Rate limit exceeded"):
                client.get_current("London")

    def test_get_current_handles_timeout(self):
        """Test get_current handles timeout."""
        with patch("requests.Session") as mock_session_class:
            mock_session = MagicMock()
            mock_session.get.side_effect = Timeout("Request timed out")
            mock_session_class.return_value = mock_session

            client = WeatherClient("test_key")
            with pytest.raises(NetworkError, match="Request timeout"):
                client.get_current("London")

    def test_get_current_handles_connection_error(self):
        """Test get_current handles connection error."""
        with patch("requests.Session") as mock_session_class:
            mock_session = MagicMock()
            mock_session.get.side_effect = ConnectionError("Connection failed")
            mock_session_class.return_value = mock_session

            client = WeatherClient("test_key")
            with pytest.raises(NetworkError, match="Connection error"):
                client.get_current("London")

    def test_get_current_handles_generic_request_exception(self):
        """Test get_current handles generic request exception."""
        with patch("requests.Session") as mock_session_class:
            mock_session = MagicMock()
            mock_session.get.side_effect = RequestException("Some network error")
            mock_session_class.return_value = mock_session

            client = WeatherClient("test_key")
            with pytest.raises(NetworkError, match="Network error"):
                client.get_current("London")

    def test_get_current_handles_malformed_json_response(self):
        """Test get_current handles non-JSON response."""
        with patch("requests.Session") as mock_session_class:
            mock_session = MagicMock()
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.side_effect = json.JSONDecodeError("msg", "doc", 0)
            mock_session.get.return_value = mock_response
            mock_session_class.return_value = mock_session

            client = WeatherClient("test_key")
            with pytest.raises(APIResponseError, match="Invalid response format"):
                client.get_current("London")

    def test_get_current_handles_non_dict_response(self):
        """Test get_current handles non-dictionary JSON response."""
        with patch("requests.Session") as mock_session_class:
            mock_session = MagicMock()
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = ["not", "a", "dict"]
            mock_session.get.return_value = mock_response
            mock_session_class.return_value = mock_session

            client = WeatherClient("test_key")
            with pytest.raises(
                APIResponseError, match="API response is not a dictionary"
            ):
                client.get_current("London")

    def test_get_current_handles_unexpected_http_status(self):
        """Test get_current handles unexpected HTTP status codes."""
        with patch("requests.Session") as mock_session_class:
            mock_session = MagicMock()
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.json.return_value = {
                "error": {"message": "Internal server error"}
            }
            mock_session.get.return_value = mock_response
            mock_session_class.return_value = mock_session

            client = WeatherClient("test_key")
            with pytest.raises(
                APIResponseError, match="WeatherAPI server error \\(500\\)"
            ):
                client.get_current("London")


class TestGetForecast:
    """Tests for get_forecast method."""

    @pytest.fixture
    def mock_forecast_response(self):
        """Create a mock successful forecast response."""
        return {
            "location": {"name": "London", "country": "GB"},
            "current": {
                "temp_c": 15.0,
                "temp_f": 59.0,
                "last_updated": "2024-01-15 10:30",
            },
            "forecast": {
                "forecastday": [
                    {
                        "date": "2024-01-15",
                        "day": {
                            "avgtemp_c": 15.0,
                            "avgtemp_f": 59.0,
                            "mintemp_c": 10.0,
                            "mintemp_f": 50.0,
                            "maxtemp_c": 18.0,
                            "maxtemp_f": 64.0,
                            "maxwind_kph": 20.0,
                            "maxwind_mph": 12.0,
                            "avghumidity": 70,
                            "condition": {"text": "Partly cloudy", "code": 1003},
                            "daily_chance_of_rain": 20,
                        },
                    },
                    {
                        "date": "2024-01-16",
                        "day": {
                            "avgtemp_c": 14.0,
                            "avgtemp_f": 57.0,
                            "mintemp_c": 9.0,
                            "mintemp_f": 48.0,
                            "maxtemp_c": 17.0,
                            "maxtemp_f": 62.0,
                            "maxwind_kph": 18.0,
                            "maxwind_mph": 11.0,
                            "avghumidity": 75,
                            "condition": {"text": "Light rain", "code": 1189},
                            "daily_chance_of_rain": 60,
                        },
                    },
                ]
            },
        }

    def test_get_forecast_success(self, mock_forecast_response):
        """Test successful forecast fetch."""
        with patch("requests.Session") as mock_session_class:
            mock_session = MagicMock()
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_forecast_response
            mock_session.get.return_value = mock_response
            mock_session_class.return_value = mock_session

            client = WeatherClient("test_key")
            result = client.get_forecast("London", days=2)

            assert result == mock_forecast_response
            mock_session.get.assert_called_once()
            call_args = mock_session.get.call_args
            assert "forecast.json" in call_args[0][0]
            assert call_args[1]["params"]["q"] == "London"
            assert call_args[1]["params"]["days"] == 2

    def test_get_forecast_default_days(self, mock_forecast_response):
        """Test get_forecast with default days (3)."""
        with patch("requests.Session") as mock_session_class:
            mock_session = MagicMock()
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_forecast_response
            mock_session.get.return_value = mock_response
            mock_session_class.return_value = mock_session

            client = WeatherClient("test_key")
            result = client.get_forecast("London")

            call_args = mock_session.get.call_args
            assert call_args[1]["params"]["days"] == 3

    def test_get_forecast_validates_days_range(self):
        """Test get_forecast validates days parameter."""
        client = WeatherClient("test_key")

        # Test 0 days (should fail)
        with pytest.raises(ValueError, match="Forecast days must be between 1 and 15"):
            client.get_forecast("London", days=0)

        # Test negative days
        with pytest.raises(ValueError, match="Forecast days must be between 1 and 15"):
            client.get_forecast("London", days=-5)

        # Test > 15 days
        with pytest.raises(ValueError, match="Forecast days must be between 1 and 15"):
            client.get_forecast("London", days=16)

    def test_get_forecast_rejects_empty_location(self):
        """Test get_forecast rejects empty location."""
        client = WeatherClient("test_key")
        with pytest.raises(ValueError, match="Location must be a non-empty string"):
            client.get_forecast("", days=3)

    def test_get_forecast_strips_location_whitespace(self, mock_forecast_response):
        """Test location is stripped of whitespace."""
        with patch("requests.Session") as mock_session_class:
            mock_session = MagicMock()
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_forecast_response
            mock_session.get.return_value = mock_response
            mock_session_class.return_value = mock_session

            client = WeatherClient("test_key")
            client.get_forecast("  London  ", days=2)

            call_args = mock_session.get.call_args
            assert call_args[1]["params"]["q"] == "London"


class TestWeatherClientContextManager:
    """Tests for context manager functionality."""

    def test_client_context_manager(self):
        """Test client can be used as context manager."""
        with patch("requests.Session") as mock_session_class:
            mock_session = MagicMock()
            mock_session_class.return_value = mock_session

            with WeatherClient("test_key") as client:
                assert isinstance(client, WeatherClient)
                assert client.api_key == "test_key"

            # Verify session was closed
            mock_session.close.assert_called_once()

    def test_client_close(self):
        """Test close method closes session."""
        with patch("requests.Session") as mock_session_class:
            mock_session = MagicMock()
            mock_session_class.return_value = mock_session

            client = WeatherClient("test_key")
            client.close()

            mock_session.close.assert_called_once()


class TestErrorHandlingEdgeCases:
    """Tests for edge cases in error handling."""

    def test_response_error_without_json_body(self):
        """Test handling of error response without JSON body."""
        with patch("requests.Session") as mock_session_class:
            mock_session = MagicMock()
            mock_response = Mock()
            mock_response.status_code = 403
            mock_response.json.side_effect = ValueError("No JSON")
            mock_session.get.return_value = mock_response
            mock_session_class.return_value = mock_session

            client = WeatherClient("test_key")
            with pytest.raises(AuthenticationError):
                client.get_current("London")

    def test_500_error_with_json_contains_error_message(self):
        """Test 500 error properly extracts message from response."""
        with patch("requests.Session") as mock_session_class:
            mock_session = MagicMock()
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.json.return_value = {"error": {"message": "Server on fire"}}
            mock_session.get.return_value = mock_response
            mock_session_class.return_value = mock_session

            client = WeatherClient("test_key")
            with pytest.raises(APIResponseError, match="Server on fire"):
                client.get_current("London")


class TestRetryLogic:
    """Tests for retry mechanism and backoff."""

    def test_get_current_retries_on_timeout_then_succeeds(self):
        """Test get_current retries after timeout and eventually succeeds."""
        mock_success_response = {
            "location": {"name": "London"},
            "current": {
                "temp_c": 15.0,
                "humidity": 70,
                "wind_kph": 10.0,
                "condition": {"text": "Cloudy"},
            },
        }

        with patch("requests.Session") as mock_session_class:
            mock_session = MagicMock()
            # First two attempts fail with Timeout, third succeeds
            mock_session.get.side_effect = [
                Timeout("Timeout 1"),
                Timeout("Timeout 2"),
                Mock(status_code=200, json=lambda: mock_success_response),
            ]
            mock_session_class.return_value = mock_session

            client = WeatherClient("test_key", max_retries=3)
            result = client.get_current("London")

            assert result == mock_success_response
            assert mock_session.get.call_count == 3

    def test_get_current_retries_on_connection_error_then_succeeds(self):
        """Test get_current retries after connection errors and eventually succeeds."""
        mock_success_response = {
            "location": {"name": "London"},
            "current": {
                "temp_c": 15.0,
                "humidity": 70,
                "wind_kph": 10.0,
                "condition": {"text": "Cloudy"},
            },
        }

        with patch("requests.Session") as mock_session_class:
            mock_session = MagicMock()
            # First attempt fails with ConnectionError, second succeeds
            mock_session.get.side_effect = [
                ConnectionError("Connection failed"),
                Mock(status_code=200, json=lambda: mock_success_response),
            ]
            mock_session_class.return_value = mock_session

            client = WeatherClient("test_key", max_retries=2)
            result = client.get_current("London")

            assert result == mock_success_response
            assert mock_session.get.call_count == 2

    def test_get_current_exhausts_retries_on_timeout(self):
        """Test get_current exhausts all retries on persistent timeout."""
        with patch("requests.Session") as mock_session_class:
            mock_session = MagicMock()
            mock_session.get.side_effect = Timeout("Persistent timeout")
            mock_session_class.return_value = mock_session

            client = WeatherClient("test_key", max_retries=3)
            with pytest.raises(NetworkError, match="Request timeout after 3 retries"):
                client.get_current("London")

            assert mock_session.get.call_count == 3

    def test_get_current_exhausts_retries_on_connection_error(self):
        """Test get_current exhausts all retries on persistent connection error."""
        with patch("requests.Session") as mock_session_class:
            mock_session = MagicMock()
            mock_session.get.side_effect = ConnectionError(
                "Persistent connection error"
            )
            mock_session_class.return_value = mock_session

            client = WeatherClient("test_key", max_retries=2)
            with pytest.raises(NetworkError, match="Connection error after 2 retries"):
                client.get_current("London")

            assert mock_session.get.call_count == 2

    def test_get_forecast_retries_on_ssl_error_then_succeeds(self):
        """Test get_forecast retries after SSL error and eventually succeeds."""
        mock_success_response = {
            "location": {"name": "London"},
            "current": {"temp_c": 15.0, "last_updated": "2024-01-15 10:30"},
            "forecast": {
                "forecastday": [
                    {
                        "date": "2024-01-15",
                        "day": {
                            "avgtemp_c": 15.0,
                            "maxwind_kph": 20.0,
                            "avghumidity": 70,
                            "condition": {"text": "Cloudy"},
                        },
                    }
                ]
            },
        }

        with patch("requests.Session") as mock_session_class:
            mock_session = MagicMock()
            mock_session.get.side_effect = [
                SSLError("SSL error"),
                Mock(status_code=200, json=lambda: mock_success_response),
            ]
            mock_session_class.return_value = mock_session

            client = WeatherClient("test_key", max_retries=2)
            result = client.get_forecast("London", days=1)

            assert result == mock_success_response
            assert mock_session.get.call_count == 2

    def test_retry_backoff_factor(self):
        """Test that retry backoff uses exponential backoff with correct factor."""
        with patch("requests.Session") as mock_session_class:
            mock_session = MagicMock()
            mock_session.get.side_effect = Timeout("Timeout")
            mock_session_class.return_value = mock_session

            # Mock time.sleep to verify backoff intervals
            with patch("weather_cli.api.client.time.sleep") as mock_sleep:
                client = WeatherClient("test_key", max_retries=3)
                with pytest.raises(NetworkError):
                    client.get_current("London")

                # Verify sleep was called with correct backoff intervals
                # With backoff factor 0.5: 0.5*2^0=0.5, 0.5*2^1=1.0
                assert mock_sleep.call_count == 2  # Called between retries
                calls = [call[0][0] for call in mock_sleep.call_args_list]
                assert 0.5 in calls  # First retry wait
                assert 1.0 in calls  # Second retry wait


class TestSSLErrorHandling:
    """Tests for SSL/TLS error handling."""

    def test_get_current_handles_ssl_error(self):
        """Test get_current handles SSL verification error."""
        with patch("requests.Session") as mock_session_class:
            mock_session = MagicMock()
            mock_session.get.side_effect = SSLError(
                "SSL certificate verification failed"
            )
            mock_session_class.return_value = mock_session

            client = WeatherClient("test_key")
            with pytest.raises(
                SSLVerificationError, match="SSL/TLS verification failed"
            ):
                client.get_current("London")

    def test_get_forecast_handles_ssl_error(self):
        """Test get_forecast handles SSL verification error."""
        with patch("requests.Session") as mock_session_class:
            mock_session = MagicMock()
            mock_session.get.side_effect = SSLError(
                "SSL certificate verification failed"
            )
            mock_session_class.return_value = mock_session

            client = WeatherClient("test_key")
            with pytest.raises(SSLVerificationError):
                client.get_forecast("London", days=1)


class TestDNSLookupErrorHandling:
    """Tests for DNS lookup error handling."""

    def test_get_current_handles_dns_error(self):
        """Test get_current identifies DNS lookup failure."""
        with patch("requests.Session") as mock_session_class:
            mock_session = MagicMock()
            # Simulate DNS error with typical error message
            mock_session.get.side_effect = ConnectionError("Name or service not known")
            mock_session_class.return_value = mock_session

            client = WeatherClient("test_key")
            with pytest.raises(DNSLookupError, match="DNS lookup failed"):
                client.get_current("London")

    def test_get_current_handles_dns_error_getaddrinfo(self):
        """Test get_current identifies DNS lookup failure with getaddrinfo error."""
        with patch("requests.Session") as mock_session_class:
            mock_session = MagicMock()
            mock_session.get.side_effect = ConnectionError("getaddrinfo failed")
            mock_session_class.return_value = mock_session

            client = WeatherClient("test_key")
            with pytest.raises(DNSLookupError, match="DNS lookup failed"):
                client.get_current("London")

    def test_get_current_handles_generic_connection_error(self):
        """Test get_current raises NetworkError for non-DNS connection errors."""
        with patch("requests.Session") as mock_session_class:
            mock_session = MagicMock()
            # Connection error without DNS keywords should raise NetworkError
            mock_session.get.side_effect = ConnectionError("Connection refused")
            mock_session_class.return_value = mock_session

            client = WeatherClient("test_key")
            with pytest.raises(NetworkError, match="Connection error"):
                client.get_current("London")


class TestResponseValidation:
    """Tests for response structure validation."""

    def test_get_current_validates_missing_location_field(self):
        """Test get_current detects missing 'location' field."""
        with patch("requests.Session") as mock_session_class:
            mock_session = MagicMock()
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "current": {
                    "temp_c": 15.0,
                    "humidity": 70,
                }
            }
            mock_session.get.return_value = mock_response
            mock_session_class.return_value = mock_session

            client = WeatherClient("test_key")
            with pytest.raises(
                APIResponseError,
                match="missing required fields for current weather: location",
            ):
                client.get_current("London")

    def test_get_current_validates_missing_current_field(self):
        """Test get_current detects missing 'current' field."""
        with patch("requests.Session") as mock_session_class:
            mock_session = MagicMock()
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"location": {"name": "London"}}
            mock_session.get.return_value = mock_response
            mock_session_class.return_value = mock_session

            client = WeatherClient("test_key")
            with pytest.raises(
                APIResponseError,
                match="missing required fields for current weather: current",
            ):
                client.get_current("London")

    def test_get_current_validates_missing_temperature_data(self):
        """Test get_current detects missing temperature fields in 'current'."""
        with patch("requests.Session") as mock_session_class:
            mock_session = MagicMock()
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "location": {"name": "London"},
                "current": {
                    "humidity": 70,
                    "wind_kph": 10.0,
                    # Missing temp_c and temp_f
                },
            }
            mock_session.get.return_value = mock_response
            mock_session_class.return_value = mock_session

            client = WeatherClient("test_key")
            with pytest.raises(
                APIResponseError, match="missing temperature data for current weather"
            ):
                client.get_current("London")

    def test_get_forecast_validates_missing_forecast_field(self):
        """Test get_forecast detects missing 'forecast' field."""
        with patch("requests.Session") as mock_session_class:
            mock_session = MagicMock()
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "location": {"name": "London"},
                "current": {"temp_c": 15.0, "last_updated": "2024-01-15 10:30"},
            }
            mock_session.get.return_value = mock_response
            mock_session_class.return_value = mock_session

            client = WeatherClient("test_key")
            with pytest.raises(
                APIResponseError, match="missing required fields for forecast: forecast"
            ):
                client.get_forecast("London", days=1)


class TestRateLimitHandling:
    """Tests for rate limit error handling with Retry-After header."""

    def test_rate_limit_includes_retry_after_when_present(self):
        """Test RateLimitError includes retry_after from header."""
        with patch("requests.Session") as mock_session_class:
            mock_session = MagicMock()
            mock_response = Mock()
            mock_response.status_code = 429
            mock_response.json.return_value = {
                "error": {"message": "Rate limit exceeded"}
            }
            mock_response.headers = {"Retry-After": "120"}
            mock_session.get.return_value = mock_response
            mock_session_class.return_value = mock_session

            client = WeatherClient("test_key")
            with pytest.raises(RateLimitError) as exc_info:
                client.get_current("London")

            assert exc_info.value.retry_after == 120
            assert "120 seconds" in str(exc_info.value)

    def test_rate_limit_without_retry_after_header(self):
        """Test RateLimitError when Retry-After header is missing."""
        with patch("requests.Session") as mock_session_class:
            mock_session = MagicMock()
            mock_response = Mock()
            mock_response.status_code = 429
            mock_response.json.return_value = {
                "error": {"message": "Rate limit exceeded"}
            }
            mock_response.headers = {}
            mock_session.get.return_value = mock_response
            mock_session_class.return_value = mock_session

            client = WeatherClient("test_key")
            with pytest.raises(RateLimitError) as exc_info:
                client.get_current("London")

            assert exc_info.value.retry_after is None
            assert "retry-after header missing" in str(exc_info.value)

    def test_rate_limit_with_invalid_retry_after_header(self):
        """Test RateLimitError when Retry-After header is non-integer."""
        with patch("requests.Session") as mock_session_class:
            mock_session = MagicMock()
            mock_response = Mock()
            mock_response.status_code = 429
            mock_response.json.return_value = {
                "error": {"message": "Rate limit exceeded"}
            }
            mock_response.headers = {"Retry-After": "invalid"}
            mock_session.get.return_value = mock_response
            mock_session_class.return_value = mock_session

            client = WeatherClient("test_key")
            with pytest.raises(RateLimitError) as exc_info:
                client.get_current("London")

            assert exc_info.value.retry_after is None
