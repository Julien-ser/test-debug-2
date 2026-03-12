"""
Output formatters for weather data.

Provides functions to format weather data for terminal display,
supporting both table and JSON formats.
"""

import json
from dataclasses import asdict
from typing import Any

from tabulate import tabulate

from weather_cli.models import CurrentWeather, Forecast


def format_current(
    weather: CurrentWeather, units: str, output_format: str = "table"
) -> str:
    """
    Format current weather data for display.

    Args:
        weather: CurrentWeather instance
        units: 'metric' or 'imperial' (for unit labels)
        output_format: 'table' or 'json'

    Returns:
        Formatted string for terminal output
    """
    if output_format == "json":
        return json.dumps(asdict(weather), indent=2, default=str)

    # Table format
    unit_labels = {"metric": "°C", "imperial": "°F"}
    temp_unit = unit_labels.get(units, "°C")
    wind_unit = "km/h" if units == "metric" else "mph"
    vis_unit = "km" if units == "metric" else "mi"

    headers = ["Metric", "Value"]
    rows = [
        ["Location", weather.location],
        ["Temperature", f"{weather.temperature}{temp_unit}"],
        [
            "Feels Like",
            f"{weather.feels_like}{temp_unit}" if weather.feels_like else "N/A",
        ],
        ["Humidity", f"{weather.humidity}%"],
        ["Wind Speed", f"{weather.wind_speed} {wind_unit}"],
        ["Wind Direction", weather.wind_direction or "N/A"],
        ["Pressure", f"{weather.pressure} hPa" if weather.pressure else "N/A"],
        [
            "Visibility",
            f"{weather.visibility} {vis_unit}" if weather.visibility else "N/A",
        ],
        ["Condition", weather.description],
        ["Observed", weather.timestamp.strftime("%Y-%m-%d %H:%M:%S")],
    ]

    return tabulate(rows, headers=headers, tablefmt="grid")


def format_forecast(
    forecast: Forecast, units: str, output_format: str = "table"
) -> str:
    """
    Format forecast data for display.

    Args:
        forecast: Forecast instance
        units: 'metric' or 'imperial' (for unit labels)
        output_format: 'table' or 'json'

    Returns:
        Formatted string for terminal output
    """
    if output_format == "json":
        return json.dumps(asdict(forecast), indent=2, default=str)

    # Table format
    unit_labels = {"metric": "°C", "imperial": "°F"}
    temp_unit = unit_labels.get(units, "°C")
    wind_unit = "km/h" if units == "metric" else "mph"

    headers = ["Date", "Temp", "Min/Max", "Humidity", "Wind", "Cond.", "Precip%"]
    rows = []

    for item in forecast.days:
        temp_str = f"{item.temperature}{temp_unit}" if item.temperature else "N/A"
        min_max = ""
        if item.temp_min is not None and item.temp_max is not None:
            min_max = f"{item.temp_min}/{item.temp_max}{temp_unit}"
        elif item.temperature:
            min_max = f"{item.temperature}{temp_unit}"

        rows.append(
            [
                item.date.strftime("%Y-%m-%d"),
                temp_str,
                min_max,
                f"{item.humidity}%" if item.humidity else "N/A",
                f"{item.wind_speed} {wind_unit}" if item.wind_speed else "N/A",
                item.description[:20] + ("..." if len(item.description) > 20 else ""),
                f"{item.precipitation_prob}%" if item.precipitation_prob else "N/A",
            ]
        )

    title = f"Weather Forecast for {forecast.location}"
    table = tabulate(rows, headers=headers, tablefmt="grid")
    return f"\n{title}\n{table}\n"
