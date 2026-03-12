import click
from typing import Optional


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
def main(location: str, units: str, format: str, forecast: int) -> None:
    """
    Weather CLI tool - Fetch and display weather information for any location.

    Example: weather London --units metric
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

    click.echo(f"Fetching weather for '{location}' in {units} units...")
    if forecast > 0:
        click.echo(f"Getting {forecast}-day forecast")
    click.echo(f"Output format: {format}")
    click.echo("✓ Command structure working!")


if __name__ == "__main__":
    main()
