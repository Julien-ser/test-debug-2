import os
import click
from typing import Optional

from weather_cli.api.client import (
    WeatherClient,
    WeatherCLIError,
    AuthenticationError,
    InvalidLocationError,
    RateLimitError,
    NetworkError,
)
from weather_cli.validation import (
    validate_location,
    validate_units,
    validate_forecast_days,
)
from weather_cli.models import CurrentWeather, Forecast
from weather_cli.display.format import format_current, format_forecast


@click.command()
@click.argument("location")
@click.option(
    "--units",
    type=click.Choice(["imperial", "metric"]),
    default="metric",
    help="Units for temperature: imperial (°F) or metric (°C)",
)
@click.option(
    "--format",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format: table or json",
)
@click.option(
    "--forecast",
    type=int,
    default=0,
    help="Number of days for forecast (0 for current weather only)",
)
@click.option(
    "--api-key",
    envvar="WEATHER_API_KEY",
    help="WeatherAPI.com API key (can also set WEATHER_API_KEY env var)",
)
def main(
    location: str, units: str, format: str, forecast: int, api_key: Optional[str]
) -> None:
    """
    Weather CLI tool - Fetch and display weather information for any location.

    Example: weather London --units metric

    Requires a WeatherAPI.com API key. Set WEATHER_API_KEY environment variable
    or use --api-key option.
    """
    # Comprehensive input validation
    location = location.strip()

    # Validate location format
    is_valid_loc, loc_error = validate_location(location)
    if not is_valid_loc:
        raise click.BadParameter(
            f"Invalid location: {loc_error}. Please provide a valid city name, "
            "coordinates (lat,lon), or postal code.",
            param_hint="location",
        )

    # Validate units
    is_valid_units, units_error = validate_units(units)
    if not is_valid_units:
        raise click.BadParameter(units_error, param_hint="--units")

    # Validate forecast days
    is_valid_days, days_error = validate_forecast_days(forecast)
    if not is_valid_days:
        raise click.BadParameter(days_error, param_hint="--forecast")

    # Get API key
    if not api_key:
        api_key = os.environ.get("WEATHER_API_KEY", "").strip()

    if not api_key:
        raise click.UsageError(
            "API key required. Set WEATHER_API_KEY environment variable or use --api-key option.\n"
            "Example: export WEATHER_API_KEY=your_key_here"
        )

    try:
        with WeatherClient(api_key) as client:
            if forecast > 0:
                # Get forecast
                raw_forecast = client.get_forecast(location, days=forecast)
                forecast_obj = Forecast.from_api(raw_forecast, units)
                output = format_forecast(forecast_obj, units, format)
            else:
                # Get current weather only
                raw_current = client.get_current(location)
                current_obj = CurrentWeather.from_api(raw_current, units)
                output = format_current(current_obj, units, format)

            click.echo(output)

    except AuthenticationError as e:
        raise click.UsageError(
            f"Authentication failed: {str(e)}\n"
            "Please check your API key is correct and active."
        )
    except InvalidLocationError as e:
        raise click.UsageError(
            f"Location not found: {str(e)}\n"
            "Try using a different city name, coordinates (lat,lon), or postal code."
        )
    except RateLimitError as e:
        raise click.UsageError(
            f"Rate limit exceeded: {str(e)}\n"
            "Please wait a moment before trying again. Consider upgrading your API plan if this persists."
        )
    except NetworkError as e:
        raise click.UsageError(
            f"Network error: {str(e)}\n"
            "Please check your internet connection and try again."
        )
    except WeatherCLIError as e:
        raise click.UsageError(
            f"Error: {str(e)}\n"
            "If this problem persists, please check your network connection and API key."
        )
    except Exception as e:
        raise click.UsageError(
            f"Unexpected error: {str(e)}\nPlease report this issue if it continues."
        )
