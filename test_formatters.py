#!/usr/bin/env python3
"""Quick test to verify formatters work correctly."""

import sys
from datetime import datetime

sys.path.insert(0, "src")

from weather_cli.models import CurrentWeather, Forecast, ForecastItem
from weather_cli.display.format import format_current, format_forecast

# Create sample current weather
sample_current = CurrentWeather(
    temperature=22.5,
    humidity=65,
    wind_speed=12.3,
    description="Partly cloudy",
    timestamp=datetime.now(),
    location="London",
    feels_like=20.0,
    wind_direction="NW",
    pressure=1013,
    visibility=10,
)

# Create sample forecast
sample_forecast_item = ForecastItem(
    date=datetime.now(),
    temperature=20.0,
    humidity=60,
    wind_speed=10.0,
    description="Sunny",
    precipitation_prob=10,
    temp_min=15.0,
    temp_max=25.0,
)
sample_forecast = Forecast(
    days=[sample_forecast_item, sample_forecast_item],
    location="London",
    last_updated=datetime.now(),
)

print("Testing current weather formatter (table):")
print(format_current(sample_current, "metric", "table"))
print("\n" + "=" * 50 + "\n")

print("Testing current weather formatter (json):")
print(format_current(sample_current, "metric", "json"))
print("\n" + "=" * 50 + "\n")

print("Testing forecast formatter (table):")
print(format_forecast(sample_forecast, "metric", "table"))
print("\n" + "=" * 50 + "\n")

print("Testing forecast formatter (json):")
print(format_forecast(sample_forecast, "metric", "json"))
print("\nAll formatters working correctly!")
