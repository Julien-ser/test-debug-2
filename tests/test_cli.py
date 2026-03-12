import pytest
from unittest.mock import patch, Mock, MagicMock
from click.testing import CliRunner
from weather_cli.weather import main
from weather_cli.api.client import WeatherClient


@pytest.fixture
def runner():
    """Create a CLI runner for testing."""
    return CliRunner()


def test_weather_command_with_valid_location(runner):
    """Test weather command with a valid location."""
    mock_response = {
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
    with patch("weather_cli.api.client.requests.Session") as mock_session_class:
        mock_session = MagicMock()
        mock_response_obj = Mock()
        mock_response_obj.status_code = 200
        mock_response_obj.json.return_value = mock_response
        mock_session.get.return_value = mock_response_obj
        mock_session_class.return_value = mock_session

        result = runner.invoke(main, ["London"], env={"WEATHER_API_KEY": "test_key"})
        assert result.exit_code == 0
        assert "London" in result.output


def test_weather_command_with_imperial_units(runner):
    """Test weather command with imperial units."""
    mock_response = {
        "location": {"name": "New York", "country": "US"},
        "current": {
            "temp_c": 20.0,
            "temp_f": 68.0,
            "feelslike_c": 18.0,
            "feelslike_f": 65.0,
            "humidity": 65,
            "wind_kph": 15.0,
            "wind_mph": 9.3,
            "wind_degree": 270,
            "pressure_mb": 1012,
            "vis_km": 12,
            "vis_miles": 7,
            "last_updated": "2024-01-15 10:30",
            "condition": {"text": "Sunny", "code": 1000},
        },
    }
    with patch("weather_cli.api.client.requests.Session") as mock_session_class:
        mock_session = MagicMock()
        mock_response_obj = Mock()
        mock_response_obj.status_code = 200
        mock_response_obj.json.return_value = mock_response
        mock_session.get.return_value = mock_response_obj
        mock_session_class.return_value = mock_session

        result = runner.invoke(
            main,
            ["New York", "--units", "imperial"],
            env={"WEATHER_API_KEY": "test_key"},
        )
        assert result.exit_code == 0
        assert "New York" in result.output


def test_weather_command_with_forecast(runner):
    """Test weather command with forecast option."""
    forecast_data = {
        "location": {"name": "Paris", "country": "FR"},
        "current": {
            "last_updated": "2024-01-15 10:30",
            "temp_c": 15.0,  # Required by validation
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
    with patch("weather_cli.api.client.requests.Session") as mock_session_class:
        mock_session = MagicMock()
        mock_response_obj = Mock()
        mock_response_obj.status_code = 200
        mock_response_obj.json.return_value = forecast_data
        mock_session.get.return_value = mock_response_obj
        mock_session_class.return_value = mock_session

        result = runner.invoke(
            main, ["Paris", "--forecast", "5"], env={"WEATHER_API_KEY": "test_key"}
        )
        assert result.exit_code == 0
        assert "forecast" in result.output.lower() or "day" in result.output.lower()


def test_weather_command_with_json_format(runner):
    """Test weather command with JSON format."""
    mock_response = {
        "location": {"name": "Tokyo", "country": "JP"},
        "current": {
            "temp_c": 25.0,
            "temp_f": 77.0,
            "feelslike_c": 26.0,
            "feelslike_f": 79.0,
            "humidity": 80,
            "wind_kph": 10.0,
            "wind_mph": 6.2,
            "wind_degree": 90,
            "pressure_mb": 1010,
            "vis_km": 8,
            "vis_miles": 5,
            "last_updated": "2024-01-15 10:30",
            "condition": {"text": "Clear", "code": 1000},
        },
    }
    with patch("weather_cli.api.client.requests.Session") as mock_session_class:
        mock_session = MagicMock()
        mock_response_obj = Mock()
        mock_response_obj.status_code = 200
        mock_response_obj.json.return_value = mock_response
        mock_session.get.return_value = mock_response_obj
        mock_session_class.return_value = mock_session

        result = runner.invoke(
            main, ["Tokyo", "--format", "json"], env={"WEATHER_API_KEY": "test_key"}
        )
        assert result.exit_code == 0
        # JSON should start with { or [
        assert result.output.strip().startswith(
            "{"
        ) or result.output.strip().startswith("[")


def test_weather_command_with_invalid_units(runner):
    """Test weather command rejects invalid units."""
    result = runner.invoke(main, ["London", "--units", "invalid"])
    assert result.exit_code == 2  # Click returns 2 for bad parameters
    assert "invalid" in result.output.lower()


def test_weather_command_with_invalid_format(runner):
    """Test weather command rejects invalid format."""
    result = runner.invoke(main, ["London", "--format", "xml"])
    assert result.exit_code == 2
    assert "invalid" in result.output.lower()


def test_weather_command_with_negative_forecast(runner):
    """Test weather command rejects negative forecast days."""
    result = runner.invoke(main, ["London", "--forecast", "-1"])
    assert result.exit_code == 2
    assert (
        "negative" in result.output.lower()
        or "cannot be negative" in result.output.lower()
    )


def test_weather_command_with_excessive_forecast(runner):
    """Test weather command rejects forecast > 15 days."""
    result = runner.invoke(main, ["London", "--forecast", "20"])
    assert result.exit_code == 2
    assert "cannot exceed 15" in result.output.lower()


def test_weather_command_with_empty_location(runner):
    """Test weather command handles empty location gracefully."""
    result = runner.invoke(main, [""])
    # Empty argument might be caught differently; check for error
    assert result.exit_code != 0


def test_weather_command_with_whitespace_location(runner):
    """Test weather command with whitespace-only location."""
    result = runner.invoke(main, ["   "])
    assert result.exit_code != 0


def test_weather_command_help(runner):
    """Test weather command shows help."""
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "Fetch and display weather information" in result.output
    assert "--units" in result.output
    assert "--format" in result.output
    assert "--forecast" in result.output
