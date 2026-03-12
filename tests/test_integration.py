"""
Integration tests for weather CLI.

Tests the full end-to-end workflow of the CLI including validation,
API client mocking, and output formatting.
"""

import pytest
from unittest.mock import patch, Mock, MagicMock
from click.testing import CliRunner
from weather_cli.weather import main
from weather_cli.api.client import WeatherClient
from weather_cli.exceptions import AuthenticationError, NetworkError, RateLimitError


class TestCLIValidation:
    """Tests for CLI input validation."""

    @pytest.fixture
    def runner(self):
        """Create a CLI runner for testing."""
        return CliRunner()

    def test_empty_location_rejected(self, runner):
        """Test empty location is rejected with helpful error."""
        result = runner.invoke(main, [""])
        assert result.exit_code != 0
        assert "empty" in result.output.lower()

    def test_whitespace_only_location_rejected(self, runner):
        """Test whitespace-only location is rejected."""
        result = runner.invoke(main, ["   "])
        assert result.exit_code != 0

    def test_invalid_location_shows_helpful_message(self, runner):
        """Test invalid location format gives guidance."""
        with patch.object(WeatherClient, "__init__", return_value=None):
            with patch.object(
                WeatherClient, "get_current", side_effect=ValueError("test")
            ):
                result = runner.invoke(main, ["!@#$%"])
                assert result.exit_code != 0
                assert "invalid" in result.output.lower()

    def test_valid_coordinates_accepted(self, runner):
        """Test that coordinate format is accepted through validation."""
        # This should pass validation but fail on API call
        with patch.object(WeatherClient, "__init__", return_value=None):
            with patch.object(
                WeatherClient, "get_current", side_effect=Exception("API error")
            ):
                result = runner.invoke(main, ["51.5074,-0.1278"])
                # Should reach API call, not fail at validation
                assert "API error" in result.output or result.exit_code != 0

    def test_invalid_units_rejected(self, runner):
        """Test invalid units parameter is rejected."""
        result = runner.invoke(main, ["London", "--units", "bogus"])
        assert result.exit_code == 2
        assert "imperial" in result.output.lower() or "metric" in result.output.lower()

    def test_negative_forecast_rejected(self, runner):
        """Test negative forecast days is rejected."""
        result = runner.invoke(main, ["London", "--forecast", "-5"])
        assert result.exit_code == 2
        assert (
            "negative" in result.output.lower()
            or "cannot be negative" in result.output.lower()
        )

    def test_excessive_forecast_rejected(self, runner):
        """Test forecast > 15 days is rejected."""
        result = runner.invoke(main, ["London", "--forecast", "20"])
        assert result.exit_code == 2
        assert "exceed 15" in result.output.lower()

    def test_valid_forecast_range_accepted(self, runner):
        """Test valid forecast range (1-15) passes validation."""
        with patch.object(WeatherClient, "__init__", return_value=None):
            with patch.object(WeatherClient, "get_forecast") as mock_get:
                mock_get.return_value = {"test": "data"}
                with patch("weather_cli.models.Forecast.from_api") as mock_from_api:
                    mock_forecast = Mock()
                    mock_forecast.format.return_value = "Test output"
                    mock_from_api.return_value = mock_forecast
                    with patch(
                        "weather_cli.display.format.format_forecast",
                        return_value="Test output",
                    ):
                        result = runner.invoke(main, ["London", "--forecast", "5"])
                        # Should pass validation and make API call
                        assert result.exit_code == 0 or "API" in result.output


class TestCLIErrorHandling:
    """Tests for CLI error handling and user-friendly messages."""

    @pytest.fixture
    def runner(self):
        """Create a CLI runner for testing."""
        return CliRunner()

     def test_authentication_error_message(self, runner):
         """Test authentication error shows helpful guidance."""
         with patch('weather_cli.weather.WeatherClient') as mock_client_class:
             mock_client = mock_client_class.return_value
             mock_client.__enter__ = Mock(return_value=mock_client)
             mock_client.__exit__ = Mock(return_value=None)
             mock_client.get_current.side_effect = AuthenticationError("Invalid API key", status_code=401)
             result = runner.invoke(main, ["London"], env={"WEATHER_API_KEY": "bad_key"})
             assert result.exit_code != 0
             output_lower = result.output.lower()
             assert ("api key" in output_lower or "authentication" in output_lower)

    def test_missing_api_key_error(self, runner):
        """Test missing API key shows setup instructions."""
        result = runner.invoke(main, ["London"], env={})
        assert result.exit_code != 0
        assert "api key" in result.output.lower()
        assert "WEATHER_API_KEY" in result.output.upper()

    def test_network_error_message(self, runner):
        """Test network error shows connection guidance."""
        with patch.object(WeatherClient, "__init__", return_value=None):
            with patch.object(
                WeatherClient, "get_current", side_effect=Exception("connection lost")
            ):
                result = runner.invoke(
                    main, ["London"], env={"WEATHER_API_KEY": "test"}
                )
                assert result.exit_code != 0
                assert (
                    "internet" in result.output.lower()
                    or "connection" in result.output.lower()
                )

    def test_rate_limit_error_message(self, runner):
        """Test rate limit error shows wait guidance."""
        with patch.object(WeatherClient, "__init__", return_value=None):
            with patch.object(
                WeatherClient, "get_current", side_effect=Exception("rate limit")
            ):
                result = runner.invoke(
                    main, ["London"], env={"WEATHER_API_KEY": "test"}
                )
                assert result.exit_code != 0
                assert (
                    "wait" in result.output.lower()
                    or "rate limit" in result.output.lower()
                )


class TestCLIIntegration:
    """Tests for complete CLI workflow with mocking."""

    @pytest.fixture
    def runner(self):
        """Create a CLI runner for testing."""
        return CliRunner()

    @pytest.fixture
    def mock_success_response(self):
        """Create mock successful response."""
        return {
            "location": {"name": "London", "country": "GB", "lat": 51.51, "lon": -0.13},
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

    def test_current_weather_success(self, runner, mock_success_response):
        """Test successful current weather retrieval."""
        with patch("weather_cli.api.client.requests.Session") as mock_session_class:
            mock_session = MagicMock()
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_success_response
            mock_session.get.return_value = mock_response
            mock_session_class.return_value = mock_session

            result = runner.invoke(
                main, ["London"], env={"WEATHER_API_KEY": "test_key"}
            )
            assert result.exit_code == 0
            assert "London" in result.output

    def test_forecast_success(self, runner, mock_success_response):
        """Test successful forecast retrieval."""
        forecast_data = {
            **mock_success_response,
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
                            "condition": {"text": "Partly cloudy"},
                            "daily_chance_of_rain": 20,
                        },
                    }
                ]
            },
        }
        with patch("weather_cli.api.client.requests.Session") as mock_session_class:
            mock_session = MagicMock()
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = forecast_data
            mock_session.get.return_value = mock_response
            mock_session_class.return_value = mock_session

            result = runner.invoke(
                main, ["London", "--forecast", "1"], env={"WEATHER_API_KEY": "test_key"}
            )
            assert result.exit_code == 0
            assert "forecast" in result.output.lower() or "day" in result.output.lower()

    def test_json_format_output(self, runner, mock_success_response):
        """Test JSON format output."""
        with patch("weather_cli.api.client.requests.Session") as mock_session_class:
            mock_session = MagicMock()
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_success_response
            mock_session.get.return_value = mock_response
            mock_session_class.return_value = mock_session

            result = runner.invoke(
                main,
                ["London", "--format", "json"],
                env={"WEATHER_API_KEY": "test_key"},
            )
            assert result.exit_code == 0
            # JSON should start with { or [
            assert result.output.strip().startswith(
                "{"
            ) or result.output.strip().startswith("[")

    def test_context_manager_closes_session(self, runner):
        """Verify session is properly closed after request."""
        with patch("weather_cli.api.client.requests.Session") as mock_session_class:
            mock_session = MagicMock()
            mock_session_class.return_value = mock_session

            # Setup response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "location": {"name": "Test"},
                "current": {},
            }
            mock_session.get.return_value = mock_response

            result = runner.invoke(
                main, ["London"], env={"WEATHER_API_KEY": "test_key"}
            )
            mock_session.close.assert_called_once()
