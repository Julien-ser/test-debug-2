"""
Data models for weather responses.

These dataclasses provide typed structures for weather data,
converting raw API responses into usable objects.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class CurrentWeather:
    """Current weather conditions for a location."""

    temperature: float  # Temperature in the requested units
    humidity: int  # Relative humidity percentage
    wind_speed: float  # Wind speed in the requested units
    description: str  # Weather condition description
    timestamp: datetime  # Observation time
    location: str  # Location name

    # Optional additional fields
    feels_like: Optional[float] = None  # "Feels like" temperature
    wind_direction: Optional[str] = None  # Wind direction (e.g., "N", "SW")
    pressure: Optional[int] = None  # Pressure in hPa
    visibility: Optional[int] = None  # Visibility in km or miles

    @classmethod
    def from_api(cls, data: dict, units: str) -> "CurrentWeather":
        """
        Create CurrentWeather from WeatherAPI.com response.

        Args:
            data: Raw API response dictionary
            units: 'metric' or 'imperial' - determines which value fields to use

        Returns:
            CurrentWeather instance
        """
        location_name = data.get("location", {}).get("name", "Unknown")
        observation_time = data.get("current", {}).get("last_updated", datetime.now())

        if isinstance(observation_time, str):
            try:
                observation_time = datetime.fromisoformat(
                    observation_time.replace("Z", "+00:00")
                )
            except ValueError:
                observation_time = datetime.now()

        current = data.get("current", {})

        # Select appropriate temperature and wind speed fields based on units
        if units == "metric":
            temp = current.get("temp_c")
            wind = current.get("wind_kph")
            feels_like = current.get("feelslike_c")
        else:
            temp = current.get("temp_f")
            wind = current.get("wind_mph")
            feels_like = current.get("feelslike_f")

        return cls(
            temperature=temp,
            humidity=current.get("humidity"),
            wind_speed=wind,
            description=current.get("condition", {}).get("text", ""),
            timestamp=observation_time,
            location=location_name,
            feels_like=feels_like,
            wind_direction=current.get("wind_degree"),
            pressure=current.get("pressure_mb"),
            visibility=current.get("vis_km")
            if units == "metric"
            else current.get("vis_miles"),
        )


@dataclass
class ForecastItem:
    """Weather forecast for a single day."""

    date: datetime  # Forecast date
    temperature: float  # Average temperature in requested units
    humidity: int  # Average humidity percentage
    wind_speed: float  # Maximum wind speed in requested units
    description: str  # Weather condition description
    precipitation_prob: Optional[int] = None  # Chance of precipitation %

    # Optional temperature extremes
    temp_min: Optional[float] = None
    temp_max: Optional[float] = None

    @classmethod
    def from_api(cls, day_data: dict, units: str) -> "ForecastItem":
        """
        Create ForecastItem from WeatherAPI.com forecast day data.

        Args:
            day_data: Dictionary containing day forecast from API
            units: 'metric' or 'imperial' - determines which value fields to use

        Returns:
            ForecastItem instance
        """
        day = day_data.get("day", {})

        # Select appropriate fields based on units
        if units == "metric":
            temp = day.get("avgtemp_c")
            temp_min = day.get("mintemp_c")
            temp_max = day.get("maxtemp_c")
            wind = day.get("maxwind_kph")
        else:
            temp = day.get("avgtemp_f")
            temp_min = day.get("mintemp_f")
            temp_max = day.get("maxtemp_f")
            wind = day.get("maxwind_mph")

        # Parse date
        date_str = day_data.get("date")
        if date_str:
            try:
                date = datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                date = datetime.now()
        else:
            date = datetime.now()

        condition = day.get("condition", {})

        return cls(
            date=date,
            temperature=temp,
            humidity=day.get("avghumidity"),
            wind_speed=wind,
            description=condition.get("text", ""),
            precipitation_prob=day.get("daily_chance_of_rain"),
            temp_min=temp_min,
            temp_max=temp_max,
        )


@dataclass
class Forecast:
    """Container for a multi-day forecast."""

    days: list  # List of ForecastItem
    location: str
    last_updated: datetime

    @classmethod
    def from_api(cls, data: dict, units: str) -> "Forecast":
        """
        Create Forecast from WeatherAPI.com forecast response.

        Args:
            data: Raw API response from get_forecast()
            units: 'metric' or 'imperial'

        Returns:
            Forecast instance with list of ForecastItem
        """
        location_name = data.get("location", {}).get("name", "Unknown")
        last_updated_str = data.get("current", {}).get("last_updated", datetime.now())

        if isinstance(last_updated_str, str):
            try:
                last_updated = datetime.fromisoformat(
                    last_updated_str.replace("Z", "+00:00")
                )
            except ValueError:
                last_updated = datetime.now()
        else:
            last_updated = datetime.now()

        forecast_days = []
        for day_data in data.get("forecast", {}).get("forecastday", []):
            forecast_days.append(ForecastItem.from_api(day_data, units))

        return cls(
            days=forecast_days, location=location_name, last_updated=last_updated
        )
