"""
Input validation utilities for weather CLI.

Provides functions to validate user inputs like location and units
before they are sent to the API or used in processing.
"""

import re
from typing import Tuple


def validate_location(location: str) -> Tuple[bool, str]:
    """
    Validate location input format.

    Supports:
    - City names (e.g., "London", "New York")
    - Coordinates (e.g., "51.5074,-0.1278")
    - Postal codes (e.g., "10001", "SW1A 1AA")

    Args:
        location: The location string to validate

    Returns:
        Tuple of (is_valid, error_message). If valid, error_message is empty string.
    """
    if not location or not location.strip():
        return False, "Location cannot be empty"

    location = location.strip()

    # Check for coordinates format (lat,lon)
    coord_pattern = r"^[-+]?([1-8]?\d(\.\d+)?|90(\.0+)?),\s*[-+]?(180(\.0+)?|((1[0-7]\d)|([1-9]?\d))(\.\d+)?)$"
    if re.match(coord_pattern, location):
        return True, ""

    # Check for postal code patterns (basic validation)
    # US/CA postal codes: 5 digits or 5+4 format
    us_ca_pattern = r"^\d{5}(-\d{4})?$"
    # UK postal codes: basic pattern
    uk_pattern = r"^[A-Z]{1,2}\d{1,2}[A-Z]? \d[A-Z]{2}$"
    # Generic: alphanumeric with spaces/hyphens (for international codes)
    postal_pattern = r"^[A-Za-z0-9\s\-]{3,10}$"

    if re.match(us_ca_pattern, location.upper()) or re.match(
        uk_pattern, location.upper()
    ):
        return True, ""

    if re.match(postal_pattern, location) and any(c.isdigit() for c in location):
        return True, ""

    # City names: should contain letters, spaces, hyphens, and possibly periods
    # Should not be all digits or special characters
    if not re.search(r"[a-zA-Z]", location):
        return False, "Location must contain at least one letter"

    if len(location) > 100:
        return False, "Location is too long (max 100 characters)"

    # Check for suspicious characters that are unlikely in real locations
    suspicious_chars = r"[!@#$%^&*()_+=<>?/\\|`~]"
    if re.search(suspicious_chars, location):
        return False, "Location contains invalid characters"

    return True, ""


def validate_units(units: str) -> Tuple[bool, str]:
    """
    Validate units parameter.

    Args:
        units: The units string ('metric' or 'imperial')

    Returns:
        Tuple of (is_valid, error_message). If valid, error_message is empty string.
    """
    valid_units = {"metric", "imperial"}

    if not units:
        return False, "Units cannot be empty"

    if units.lower() not in valid_units:
        return False, f"Units must be one of: {', '.join(sorted(valid_units))}"

    return True, ""


def validate_forecast_days(days: int) -> Tuple[bool, str]:
    """
    Validate forecast days parameter.

    Args:
        days: Number of forecast days

    Returns:
        Tuple of (is_valid, error_message). If valid, error_message is empty string.
    """
    if not isinstance(days, int):
        return False, "Forecast days must be an integer"

    if days < 0:
        return False, "Forecast days cannot be negative"

    if days > 15:
        return False, "Forecast days cannot exceed 15"

    return True, ""
