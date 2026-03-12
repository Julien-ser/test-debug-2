import pytest
from click.testing import CliRunner
from weather_cli.weather import main


@pytest.fixture
def runner():
    """Create a CLI runner for testing."""
    return CliRunner()


def test_weather_command_with_valid_location(runner):
    """Test weather command with a valid location."""
    result = runner.invoke(main, ["London"])
    assert result.exit_code == 0
    assert "Fetching weather for 'London'" in result.output
    assert "metric units" in result.output


def test_weather_command_with_imperial_units(runner):
    """Test weather command with imperial units."""
    result = runner.invoke(main, ["New York", "--units", "imperial"])
    assert result.exit_code == 0
    assert "imperial units" in result.output


def test_weather_command_with_forecast(runner):
    """Test weather command with forecast option."""
    result = runner.invoke(main, ["Paris", "--forecast", "5"])
    assert result.exit_code == 0
    assert "5-day forecast" in result.output


def test_weather_command_with_json_format(runner):
    """Test weather command with JSON format."""
    result = runner.invoke(main, ["Tokyo", "--format", "json"])
    assert result.exit_code == 0
    assert "Output format: json" in result.output


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
    assert "non-negative" in result.output.lower()


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
