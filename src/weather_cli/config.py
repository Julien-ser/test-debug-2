"""
Configuration loader for weather-cli.

Supports loading API key and default settings from:
1. Environment variables (WEATHER_API_KEY, WEATHER_UNITS)
2. Config file in YAML format (~/.config/weather-cli/config.yml or ~/.weather-cli/config.yml)

Environment variables take precedence over config file.
"""

import os
from pathlib import Path
from typing import Optional
import yaml


class ConfigError(Exception):
    """Base configuration error."""

    pass


class ConfigFileError(ConfigError):
    """Configuration file format or permission error."""

    pass


def get_config_dir() -> Path:
    """Get the configuration directory path."""
    # Use XDG_CONFIG_HOME if set, otherwise default to ~/.config
    config_home = os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")
    return Path(config_home) / "weather-cli"


def get_config_path() -> Path:
    """Get the configuration file path, checking multiple locations."""
    config_dir = get_config_dir()
    primary_config = config_dir / "config.yml"

    # Check primary location first
    if primary_config.exists():
        return primary_config

    # Fallback to legacy location
    legacy_config = Path.home() / ".weather-cli" / "config.yml"
    if legacy_config.exists():
        return legacy_config

    # Return primary path even if it doesn't exist (for creation)
    return primary_config


def load_config() -> dict:
    """
    Load configuration from file and environment variables.

    Returns a dictionary with keys: api_key, default_units (if set).

    Environment variables (WEATHER_API_KEY, WEATHER_UNITS) take precedence
    over config file settings.
    """
    config = {}

    # First, try to load from config file
    config_path = get_config_path()
    if config_path.exists():
        try:
            with open(config_path, "r") as f:
                file_config = yaml.safe_load(f) or {}

            if isinstance(file_config, dict):
                # Extract api_key if present
                if "api_key" in file_config:
                    api_key = str(file_config["api_key"]).strip()
                    if api_key:
                        config["api_key"] = api_key

                # Extract default_units if present
                if "default_units" in file_config:
                    units = str(file_config["default_units"]).strip().lower()
                    if units in {"metric", "imperial"}:
                        config["default_units"] = units
        except yaml.YAMLError as e:
            raise ConfigFileError(
                f"Invalid YAML in config file {config_path}: {str(e)}"
            ) from e
        except PermissionError as e:
            raise ConfigFileError(
                f"Permission denied reading config file {config_path}"
            ) from e
        except Exception as e:
            raise ConfigFileError(
                f"Error reading config file {config_path}: {str(e)}"
            ) from e

    # Override with environment variables (they take precedence)
    env_api_key = os.environ.get("WEATHER_API_KEY", "").strip()
    if env_api_key:
        config["api_key"] = env_api_key

    env_units = os.environ.get("WEATHER_UNITS", "").strip().lower()
    if env_units in {"metric", "imperial"}:
        config["default_units"] = env_units

    return config


def get_api_key() -> Optional[str]:
    """Get API key from config or environment."""
    config = load_config()
    return config.get("api_key")


def get_default_units() -> str:
    """Get default units from config or environment, defaulting to 'metric'."""
    config = load_config()
    return config.get("default_units", "metric")


def create_config_dir() -> Path:
    """
    Create configuration directory if it doesn't exist.

    Returns the path to the config directory.
    """
    config_dir = get_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)
    # Set secure permissions (0700) - only user can read/write/execute
    try:
        config_dir.chmod(0o700)
    except Exception:
        pass  # Ignore permission errors; not critical
    return config_dir


def create_default_config() -> Path:
    """
    Create a default configuration file.

    Returns the path to the created config file.
    """
    config_dir = create_config_dir()
    config_path = config_dir / "config.yml"

    default_content = """# Weather CLI Configuration
# https://github.com/your-repo/weather-cli

# Your WeatherAPI.com API key (required)
# You can also set this via WEATHER_API_KEY environment variable
api_key: "YOUR_API_KEY_HERE"

# Default temperature units: 'metric' (°C) or 'imperial' (°F)
# You can also set this via WEATHER_UNITS environment variable
default_units: metric
"""

    with open(config_path, "w") as f:
        f.write(default_content)

    # Set secure permissions (0600) - only user can read/write
    try:
        config_path.chmod(0o600)
    except Exception:
        pass

    return config_path
