"""
Unit tests for Weather API Client.

Tests cover successful requests, error handling, and edge cases
using mocking to avoid real API calls.
"""

import json
import pytest
from unittest.mock import Mock, patch, MagicMock
from requests.exceptions import Timeout, ConnectionError, RequestException

from weather_cli.api.client import WeatherClient
from weather_cli.exceptions import (
    AuthenticationError,
    InvalidLocationError,
    RateLimitError,
    NetworkError,
    APIResponseError,
    WeatherCLIError,
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
            with pytest.raises(APIResponseError, match="non-dictionary response"):
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
            with pytest.raises(APIResponseError, match="API error \\(500\\)"):
                client.get_current("London")


class TestGetForecast:
    """Tests for get_forecast method."""

    @pytest.fixture
    def mock_forecast_response(self):
        """Create a mock successful forecast response."""
        return {
            "location": {"name": "London", "country": "GB"},
            "current": {"last_updated": "2024-01-15 10:30"},
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


class TestInheritance:
    """Tests to ensure proper exception inheritance."""

    def test_all_custom_exceptions_inherit_from_weather_cli_error(self):
        """Verify all custom exceptions inherit from WeatherCLIError."""
        assert issubclass(AuthenticationError, WeatherCLIError)
        assert issubclass(InvalidLocationError, WeatherCLIError)
        assert issubclass(RateLimitError, WeatherCLIError)
        assert issubclass(NetworkError, WeatherCLIError)
        assert issubclass(APIResponseError, WeatherCLIError)
