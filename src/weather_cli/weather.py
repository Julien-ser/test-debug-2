import os
import click
from typing import Optional

from weather_cli.api.client import (
    WeatherClient,
    WeatherAPIError,
    AuthenticationError,
    InvalidLocationError,
    RateLimitError,
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
    # Input validation
    if not location or not location.strip():
        raise click.BadParameter("Location cannot be empty", param_hint="location")

    location = location.strip()

    # Validate forecast days if provided
    if forecast < 0:
        raise click.BadParameter(
            "Forecast days must be non-negative", param_hint="--forecast"
        )
    if forecast > 15:
        raise click.BadParameter(
            "Forecast days cannot exceed 15", param_hint="--forecast"
        )

    # Get API key
    if not api_key:
        api_key = os.environ.get("WEATHER_API_KEY", "").strip()

    if not api_key:
        raise click.UsageError(
            "API key required. Set WEATHER_API_KEY environment variable or use --api-key option."
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
        raise click.UsageError(f"Authentication failed: {str(e)}")
    except InvalidLocationError as e:
        raise click.UsageError(f"Location error: {str(e)}")
    except RateLimitError as e:
        raise click.UsageError(f"Rate limit exceeded: {str(e)}")
    except WeatherAPIError as e:
        raise click.UsageError(f"Weather API error: {str(e)}")
