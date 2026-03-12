# Weather CLI Tool

A Python command-line tool that fetches and displays weather information using the WeatherAPI.com service.

## Features

- Display current weather conditions for any location
- Multi-day forecasts (up to 15 days)
- Support for metric and imperial units
- Output formats: human-readable table and JSON
- Caching layer for improved performance (10-minute TTL)
- Configuration via environment variable or config file
- Comprehensive error handling with user-friendly messages

## Project Status

**Phase 1: Planning & Setup** - In Progress
- ✅ Requirements documented (see `requirements.md`)
- ✅ API provider selected (WeatherAPI.com) - see `API_COMPARISON.md`
 - ✅ Python project initialization (pyproject.toml, virtual environment)
 - ✅ Project structure and Git repository initialized
 - ✅ Initial Git commit

**Phase 2: Core Development** - Pending

## Technology Stack

- Python 3.9+
- `requests` - HTTP client
- `click` - CLI framework
- `tabulate` - Table formatting
- `pyyaml` - Config file parsing
- `requests-cache` - Response caching
- `pytest` - Testing framework

## Setup

### Prerequisites

- Python 3.9 or higher
- pip package manager

### Installation (once published)

```bash
pip install weather-cli
```

### Current Development Setup

```bash
# Clone and enter project directory
cd projects/test-debug-2

# Activate virtual environment (recommended)
# On Linux/macOS:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate

# Install dependencies in editable mode
pip install -e .

# Run the tool (once implemented)
weather London --units metric
# Or: python -m weather_cli.weather London --units metric
```

### Configuration

1. Get a free API key from [WeatherAPI.com](https://www.weatherapi.com/)
2. Set as environment variable:
   ```bash
   export WEATHER_API_KEY="your_api_key_here"
   ```
   Or save to config file at `~/.config/weather-cli/config.yml`:
   ```yaml
   api_key: "your_api_key_here"
   default_units: "metric"
   ```

## Usage (planned)

```bash
# Current weather
weather London --units metric

# Forecast (5 days)
weather New York --forecast 5

# JSON output
weather Tokyo --format json

# With caching (automatic)
weather Paris  # First call hits API, subsequent within 10min use cache
```

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

## Documentation

- `requirements.md` - Complete non-functional requirements and specs
- `API_COMPARISON.md` - Detailed provider evaluation and recommendation
- `TASKS.md` - Development progress and task breakdown

## Development

This project is developed autonomously using OpenCode agent loop.

```bash
# View tasks
cat TASKS.md

# Run development iteration
opencode /init --yes

# Check iteration logs
cat logs/iteration-2.md
```

## License

MIT

## Contributing

This is an autonomous project. External contributions are not accepted at this time.
