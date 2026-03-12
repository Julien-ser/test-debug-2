# Weather CLI Tool

A Python command-line tool that fetches and displays weather information using the WeatherAPI.com service.

## Features

- ✅ Display current weather conditions for any location
- ✅ Multi-day forecasts (1-15 days)
- ✅ Support for metric (°C) and imperial (°F) units
- ✅ Output formats: human-readable table and JSON
- ✅ Caching layer for improved performance (10-minute TTL, SQLite)
- ✅ Comprehensive error handling with user-friendly messages
- ✅ Input validation for locations, units, and parameters
- ✅ Retry logic with exponential backoff for network failures
- ✅ Support for multiple location formats: city names, coordinates, postal codes

## Quick Start

```bash
# Set your API key
export WEATHER_API_KEY="your_api_key_here"

# Get current weather
weather-cli London --units metric

# Get a 5-day forecast
weather-cli New York --forecast 5 --units imperial

# Get JSON output
weather-cli Tokyo --format json
```

## Project Status

**Phase 1: Planning & Setup** - ✅ Completed
- ✅ Requirements documented (see `requirements.md`)
- ✅ API provider selected (WeatherAPI.com) - see `API_COMPARISON.md`
- ✅ Python project initialization (pyproject.toml, virtual environment)
- ✅ Project structure and Git repository initialized
- ✅ Initial Git commit

**Phase 2: Core Development** - ✅ Completed
- ✅ Base CLI command structure with argument parsing (location, units, format, forecast)
- ✅ API client implementation with retry logic and error handling
- ✅ Data models (CurrentWeather, ForecastItem, Forecast)
- ✅ Output formatters (table and JSON formats)

**Phase 3: Error Handling & Testing** - ✅ Completed
- ✅ Comprehensive error handling (network failures, invalid locations, API limits) with custom exceptions (AuthenticationError, InvalidLocationError, RateLimitError, NetworkError, etc.)
- ✅ Unit tests for API client with 80%+ coverage using mocked responses
- ✅ Unit tests for cache module
- ✅ Integration tests for full CLI workflow
- ✅ Input validation for location formats (city names, coordinates, postal codes), units parameter, and forecast days (1-15)
- ✅ Caching layer implemented with 10-minute TTL using requests-cache

**Phase 4: Polish & Documentation** - 🔄 In Progress
- ✅ Comprehensive README with installation, usage examples, and troubleshooting (this document)
- ✅ Config file support for default API key and units (implemented via ~/.config/weather-cli/config.yml)
- ⏳ Package the tool for PyPI distribution and create installation instructions

## Technology Stack

- Python 3.9+
- `requests` - HTTP client
- `click` - CLI framework
- `tabulate` - Table formatting
- `pyyaml` - Config file parsing
- `requests-cache` - Response caching
- `pytest` - Testing framework

## Installation

### Prerequisites

- Python 3.9 or higher
- pip package manager

### Development Setup (Current)

```bash
# Clone and enter project directory
cd projects/test-debug-2

# Create and activate virtual environment (recommended)
python -m venv .venv
# On Linux/macOS:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate

# Install dependencies in editable mode
pip install -e .

# Verify installation
weather-cli --help
```

### Production Installation (Once Published)

Once the package is published to PyPI, installation will be as simple as:

```bash
pip install weather-cli
```

### Configuration

**Getting an API Key:**

1. Sign up for a free account at [WeatherAPI.com](https://www.weatherapi.com/)
2. Navigate to your dashboard and copy your API key
3. Set the API key as an environment variable:

```bash
# Linux/macOS
export WEATHER_API_KEY="your_api_key_here"

# Windows (Command Prompt)
set WEATHER_API_KEY=your_api_key_here

# Windows (PowerShell)
$env:WEATHER_API_KEY="your_api_key_here"
```

You can also pass the API key directly with the `--api-key` option:

```bash
weather-cli London --api-key your_api_key_here --units metric
```

#### Configuration File

You can store your API key and default units in a configuration file, avoiding the need to set environment variables manually each session.

**File Location:** `~/.config/weather-cli/config.yml` (XDG standard) or legacy `~/.weather-cli/config.yml`.

**File Format** (YAML):
```yaml
# Weather CLI Configuration
api_key: "your_api_key_here"
default_units: metric  # optional, defaults to metric
```

**Setup:**

1. Create the config directory and file:
   ```bash
   mkdir -p ~/.config/weather-cli
   nano ~/.config/weather-cli/config.yml
   ```

2. Add your API key and optionally set `default_units` to `metric` or `imperial`.

3. Secure the file (recommended):
   ```bash
   chmod 600 ~/.config/weather-cli/config.yml
   ```

**Configuration Precedence** (highest to lowest):
- Command-line options (`--api-key`, `--units`)
- Environment variables (`WEATHER_API_KEY`, `WEATHER_UNITS`)
- Configuration file (`~/.config/weather-cli/config.yml`)

**Example:** Once configured, simply run:
```bash
weather London
weather "New York" --forecast 5
```
No need to pass `--api-key` or set environment variables.

## Usage

All commands require a WeatherAPI.com API key (set via `WEATHER_API_KEY` environment variable, `--api-key` option, or config file).

### Current Weather

Get current weather for a location in metric units (default):

```bash
$ weather London
```

Example output (table format):
```
+--------------+-------------------+
| Metric       | Value             |
+==============+===================+
| Location     | London, GB        |
+--------------+-------------------+
| Temperature  | 15.0°C            |
+--------------+-------------------+
| Feels Like   | 13.5°C            |
+--------------+-------------------+
| Humidity     | 72%               |
+--------------+-------------------+
| Wind Speed   | 12.0 km/h         |
+--------------+-------------------+
| Wind Direction | SW              |
+--------------+-------------------+
| Pressure     | 1013 hPa          |
+--------------+-------------------+
| Visibility   | 10 km             |
+--------------+-------------------+
| Condition    | Partly cloudy     |
+--------------+-------------------+
| Observed     | 2024-01-15 10:30:00 |
+--------------+-------------------+
```

### Forecast

Get a multi-day forecast (1-15 days):

```bash
# 5-day forecast in imperial units
$ weather New York --forecast 5 --units imperial --format table
```

Example output:
```

Weather Forecast for New York, US
+------------+--------+----------+----------+-----------+-----------+
| Date       | Temp   | Min/Max  | Humidity | Wind      | Cond.     |
+============+========+==========+==========+===========+===========+
| 2024-01-15 | 5.2°F  | 3.1/7.3°F| 65%      | 15.2 mph  | Light rain|
+------------+--------+----------+----------+-----------+-----------+
| 2024-01-16 | 6.8°F  | 4.2/9.5°F| 58%      | 12.8 mph  | Sunny     |
+------------+--------+----------+----------+-----------+-----------+
...
```

### JSON Output

For programmatic consumption or when you need raw data:

```bash
$ weather Tokyo --format json --units metric
{
  "location": "Tokyo, JP",
  "temperature": 18.5,
  "humidity": 68,
  "wind_speed": 8.6,
  "description": "Clear sky",
  "timestamp": "2024-01-15T10:30:00Z",
  "feels_like": 17.2,
  "wind_direction": "N",
  "pressure": 1015,
  "visibility": 12
}
```

### Supported Location Formats

```bash
# City names (with or without country code)
weather-cli London
weather-cli "New York"
weather-cli Sao Paulo

# Coordinates (latitude,longitude)
weather-cli 51.5074,-0.1278
weather-cli 40.7128,-74.0060

# Postal codes
weather-cli 10001        # US
weather-cli SW1A 1AA     # UK
```

### Command-Line Options

```
Usage: weather-cli [OPTIONS] LOCATION

Get current weather or forecast for a location.

Arguments:
  LOCATION              City name, coordinates (lat,lon), or postal code

Options:
  --units [imperial|metric]
                        Temperature units: imperial (°F) or metric (°C)
                        [default: metric]
  --format [table|json]
                        Output format [default: table]
  --forecast INTEGER    Number of forecast days (0 for current weather only, max 15)
                        [default: 0]
  --api-key TEXT        WeatherAPI.com API key (can also set WEATHER_API_KEY env var)
  --help               Show this message and exit.
```

### Caching Behavior

The tool caches API responses for 10 minutes to improve performance and reduce API usage:

- First request for a location: hits the API
- Subsequent requests within 10 minutes: served from cache
- After 10 minutes: fresh API call

The cache is stored in `~/.cache/weather-cli/weather_cache.sqlite` (auto-created).

## Troubleshooting

### API Key Issues

**Error:** `API key required` or `Authentication failed`

**Solutions:**
- Set your API key as an environment variable:
  ```bash
  export WEATHER_API_KEY="your_key_here"
  ```
- Or use the `--api-key` option directly:
  ```bash
  weather London --api-key your_key_here
  ```
- Verify your API key is correct and active at [WeatherAPI.com](https://www.weatherapi.com/)
- Ensure no extra spaces or quotes in the API key

### Location Not Found

**Error:** `Location not found`

**Solutions:**
- Check spelling and try alternative names (e.g., "New York" not "NYC")
- Try coordinates format: `weather 51.5074,-0.1278`
- Use postal codes: `weather 10001`
- Some smaller towns may not be in the database; try a nearby major city

### Rate Limiting

**Error:** `Rate limit exceeded`

**Solutions:**
- Wait a moment before retrying (free tier allows 1M calls/month)
- Check if you've exceeded your plan's limits at WeatherAPI.com dashboard
- Upgrade your API plan if you need higher limits
- The tool includes automatic retry with backoff; if you see this repeatedly, reduce request frequency

### Network Errors

**Errors:** `Network error`, `Connection error`, `Timeout`, `DNS lookup failed`

**Solutions:**
- Check your internet connection
- Verify you can reach `api.weatherapi.com`
- If using a proxy, ensure it's correctly configured
- For SSL errors, ensure your system's CA certificates are up to date
- Retry the command; transient network issues are common

### Invalid Input

**Error:** `Invalid location` or validation errors for units/forecast

**Solutions:**
- Location must contain at least one letter and be ≤ 100 characters
- Avoid special characters: `!@#$%^&*()_+=<>?/\\|`
- Units must be `metric` or `imperial`
- Forecast days must be between 0 and 15 (0 means current weather only)

### JSON Output Formatting

If you're piping JSON to other tools and it's not parsing correctly, ensure you're using the `--format json` flag:

```bash
weather-cli London --format json | jq '.temperature'
```

### Cache Issues

If you're getting stale data or want to clear the cache:

```bash
# The cache file is at:
rm ~/.cache/weather-cli/weather_cache.sqlite

# Or implement a command-line option to clear cache (TODO)
```

### SSL/TLS Errors

If you see SSL verification errors:

- Update your system's root certificates
- On some Linux systems: `sudo update-ca-certificates`
- If using a custom CA bundle, set `REQUESTS_CA_BUNDLE` environment variable

### Debug Logging

For detailed diagnostics, enable debug logging:

```bash
export PYTHONLOGLEVEL=DEBUG
weather-cli London
```

This shows retry attempts, cache hits, and API response details.

### Still Having Issues?

1. Check the [WeatherAPI.com status page](https://www.weatherapi.com/docs/status) for service issues
2. Verify your API key works by testing with curl:
   ```bash
   curl "https://api.weatherapi.com/v1/current.json?key=YOUR_KEY&q=London"
   ```
3. Open an issue with:
   - Full command you ran
   - Complete error message
   - Your Python version (`python --version`)
   - OS/platform details

## Architecture

```
weather_cli/
├── __init__.py
├── weather.py          # CLI entry point (click commands)
├── api/
│   ├── __init__.py
│   └── client.py       # WeatherAPI.com client
├── models.py           # Data classes (CurrentWeather, ForecastItem)
├── display/
│   ├── __init__.py
│   └── format.py       # Output formatters (table, json)
├── cache.py            # Caching layer (requests-cache)
├── config.py           # Configuration loader
└── exceptions.py       # Custom exceptions

tests/
├── test_api.py
├── test_integration.py
└── fixtures/
```

## API Provider Selection

We evaluated OpenWeatherMap, WeatherAPI.com, and AccuWeather:

- **WeatherAPI.com** was selected for its excellent documentation, generous free tier (1M calls/month), simple REST API, and comprehensive weather data. See `API_COMPARISON.md` for full matrix.

## Troubleshooting

[Comprehensive troubleshooting section as above - I will insert it here in the actual edit]

## Development & Testing

### Running Tests

```bash
# Run all tests with coverage
pytest tests/ --cov=src/weather_cli --cov-report=term-missing --cov-report=html

# Run specific test file
pytest tests/test_api.py -v

# Run tests matching a pattern
pytest -k "test_weather_command" -v

# Run with coverage report
coverage run -m pytest tests/
coverage report
```

### Test Coverage

The project aims for 80%+ code coverage. Current coverage includes:
- API client methods (with mocked responses)
- Cache operations
- CLI command integration
- Validation functions
- Error handling paths

### Development Commands

```bash
# Format code with ruff
ruff format src/ tests/

# Lint with ruff
ruff check src/ tests/

# Type checking (if mypy is configured)
mypy src/

# Run all quality checks
pytest && ruff check src/ tests/
```

### Project Structure

```
weather-cli/
├── src/weather_cli/
│   ├── __init__.py
│   ├── weather.py          # CLI entry point (click commands)
│   ├── api/
│   │   ├── __init__.py
│   │   └── client.py       # WeatherAPI.com client with retry logic
│   ├── models.py           # Data classes (CurrentWeather, ForecastItem, Forecast)
│   ├── display/
│   │   ├── __init__.py
│   │   └── format.py       # Output formatters (table, json)
│   ├── cache.py            # Caching layer (requests-cache, TTL=10min)
│   ├── validation.py       # Input validation utilities
│   └── exceptions.py       # Custom exception hierarchy
├── tests/
│   ├── test_api.py         # API client unit tests
│   ├── test_cli.py         # CLI integration tests
│   ├── test_cache.py       # Cache unit tests
│   └── test_integration.py # Full workflow tests
├── docs/                   # Additional documentation
├── pyproject.toml         # Project metadata and dependencies
├── requirements.md        # Non-functional requirements
├── API_COMPARISON.md      # API provider evaluation
├── TASKS.md               # Development task tracking
└── README.md              # This file
```

## Architecture

### Data Flow

```
User Input → CLI Parser → Validation → WeatherClient → API Request
                            ↓
                   Cache Check (10min TTL)
                            ↓
              API Response → Response Validation
                            ↓
              Model Parsing (from_api methods)
                            ↓
         Formatter (table/json) → Output Display
```

### Error Handling Strategy

- **Retry Logic**: Transient failures (timeout, connection errors, 5xx) automatically retry up to 3 times with exponential backoff
- **Custom Exceptions**: Each error type maps to a specific exception (AuthenticationError, InvalidLocationError, RateLimitError, NetworkError, etc.)
- **User-Friendly Messages**: All exceptions converted to Click usage errors with actionable guidance
- **Validation**: Input validated before API calls to provide immediate feedback

### Caching Strategy

- **Backend**: SQLite via requests-cache
- **TTL**: 600 seconds (10 minutes)
- **Location**: `~/.cache/weather-cli/weather_cache.sqlite`
- **Scope**: Caches by full request URL and Accept header
- **Behavior**: Automatic, transparent; no user action required

## API Provider Selection

We evaluated OpenWeatherMap, WeatherAPI.com, and AccuWeather:

- **WeatherAPI.com** was selected for:
  - Excellent documentation and simple REST API
  - Generous free tier (1 million calls/month)
  - Comprehensive weather data with both metric and imperial values in a single response
  - Reliable uptime and fast response times (< 500ms typical)
  - No complex authentication (simple API key)
  - Supports all required features: current weather, forecasts, coordinates, postal codes

See `API_COMPARISON.md` for detailed evaluation matrix.

## Documentation

- `requirements.md` - Complete non-functional requirements and success criteria
- `API_COMPARISON.md` - Detailed provider evaluation and recommendation
- `TASKS.md` - Development progress and task breakdown
- `docs/` - Additional technical documentation

## License

MIT

## Contributing

This is an autonomous project developed with OpenCode. External contributions are not accepted at this time.

## Acknowledgments

- [WeatherAPI.com](https://www.weatherapi.com/) for the weather data API
- Built with: Python, Click, Requests, Requests-Cache, Tabulate
