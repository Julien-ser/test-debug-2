# Installation Guide

This guide covers all methods to install the Weather CLI tool.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Method 1: Install from PyPI (Recommended)](#method-1-install-from-pypi-recommended)
- [Method 2: Install from Wheel File](#method-2-install-from-wheel-file)
- [Method 3: Install from Source](#method-3-install-from-source)
- [Post-Installation Configuration](#post-installation-configuration)
- [Verifying Installation](#verifying-installation)
- [Troubleshooting](#troubleshooting)
- [Upgrading](#upgrading)
- [Uninstalling](#uninstalling)

---

## Prerequisites

Before installing, ensure you have:

- **Python 3.9 or higher** installed
  ```bash
  python --version
  ```
- **pip** package manager (comes with Python)
  ```bash
  pip --version
  ```
- **Git** (optional, for source installation)

---

## Method 1: Install from PyPI (Recommended)

Once the package is published to PyPI, install with a single command:

```bash
pip install weather-cli
```

That's it! The `weather-cli` command will be available in your PATH.

### Using pip with User Installation

If you don't have administrator privileges:

```bash
pip install --user weather-cli
```

This installs to `~/.local/bin/` (Linux/macOS) or `%APPDATA%\Python\Scripts\` (Windows).

Make sure this directory is in your PATH:

**Linux/macOS:**
```bash
export PATH="$HOME/.local/bin:$PATH"
# Add to ~/.bashrc or ~/.zshrc to persist
```

**Windows:**
```powershell
$env:Path += ";$env:APPDATA\Python\Scripts"
```

### Using pip with Virtual Environment (Best Practice)

```bash
# Create virtual environment
python -m venv .venv

# Activate it
# Linux/macOS:
source .venv/bin/activate
# Windows:
# .venv\Scripts\activate

# Install
pip install weather-cli
```

---

## Method 2: Install from Wheel File

If PyPI is not accessible or you need an offline install:

1. Download the latest wheel from the [releases page](../../releases) or from the `dist/` directory:

   ```bash
   # Example: download weather_cli-0.1.0-py3-none-any.whl
   wget https://example.com/path/to/weather_cli-0.1.0-py3-none-any.whl
   ```

2. Install the wheel directly:

   ```bash
   pip install weather_cli-0.1.0-py3-none-any.whl
   ```

   Or with user installation:

   ```bash
   pip install --user weather_cli-0.1.0-py3-none-any.whl
   ```

**Note:** The `py3-none-any` wheel is universal and works on all platforms (Windows, Linux, macOS) and Python versions ≥3.9.

---

## Method 3: Install from Source

For development or if you need the latest unreleased version:

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/weather-cli.git
   cd weather-cli
   ```

2. **Install in editable mode** (recommended for development):

   ```bash
   pip install -e .
   ```

   This installs the package but links it to the source directory, so changes to the code take effect immediately without reinstalling.

3. **Or install normally** (for production use from source):

   ```bash
   pip install .
   ```

### Installing Development Dependencies

To run tests and development tools:

```bash
pip install -e ".[dev]"
```

---

## Post-Installation Configuration

### 1. Obtain an API Key

Sign up for a free account at [WeatherAPI.com](https://www.weatherapi.com/):

1. Go to https://www.weatherapi.com/ and click "Sign Up"
2. Complete registration (email verification required)
3. Log in and navigate to your Dashboard
4. Copy your API key (looks like: `abc123def456ghi789`)

### 2. Set Your API Key

Choose one of these methods:

#### Option A: Environment Variable (Temporary)

```bash
# Linux/macOS
export WEATHER_API_KEY="your_api_key_here"

# Windows Command Prompt
set WEATHER_API_KEY=your_api_key_here

# Windows PowerShell
$env:WEATHER_API_KEY="your_api_key_here"
```

Add to shell profile (`~/.bashrc`, `~/.zshrc`, or PowerShell profile) to make persistent.

#### Option B: Configuration File (Recommended)

Create a config file at `~/.config/weather-cli/config.yml` (Linux/macOS) or `%APPDATA%\weather-cli\config.yml` (Windows):

```yaml
# Weather CLI Configuration
api_key: "your_api_key_here"
default_units: metric  # optional: metric or imperial
```

Create the directory and file:

**Linux/macOS:**
```bash
mkdir -p ~/.config/weather-cli
nano ~/.config/weather-cli/config.yml  # paste the YAML content
chmod 600 ~/.config/weather-cli/config.yml  # secure the file
```

**Windows PowerShell:**
```powershell
New-Item -ItemType Directory -Force -Path "$env:APPDATA\weather-cli"
notepad "$env:APPDATA\weather-cli\config.yml"
```

#### Option C: Pass API Key on Command Line

```bash
weather-cli London --api-key your_api_key_here
```

**Note:** API keys in command history may be visible; use environment variables or config file for security.

### 3. Verify Configuration

Test that your API key is recognized:

```bash
weather-cli London --debug
```

If you see authentication errors, double-check your API key.

---

## Verifying Installation

After installation, verify everything works:

### 1. Check Installation

```bash
weather-cli --version
```

Should output: `weather-cli, version 0.1.0`

### 2. Test with Help Command

```bash
weather-cli --help
```

Should display usage information.

### 3. Test with Real API Call

```bash
weather-cli London --units metric
```

Expected output: weather data table for London.

If you get an "API key required" error, review configuration steps above.

---

## Troubleshooting

### Command Not Found

**Error:** `weather-cli: command not found` or `'weather-cli' is not recognized...`

**Causes & Solutions:**

1. **pip's bin directory not in PATH**
   ```bash
   # Find where pip installed the package
   python -c "import sys; print(sys.prefix)"
   
   # Check bin directory
   ls ~/.local/bin/weather-cli  # user install
   ls /usr/local/bin/weather-cli  # system install
   
   # Add to PATH (example for Linux user install)
   export PATH="$HOME/.local/bin:$PATH"
   ```

2. **Multiple Python versions** - You may have installed to Python 3 but are using Python 2
   ```bash
   # Use explicit Python 3
   python3 -m pip install weather-cli
   weather-cli  # or python3 -m weather_cli
   ```

3. **Virtual environment not activated**
   ```bash
   # If you installed in a venv, activate it first
   source .venv/bin/activate  # Linux/macOS
   .venv\Scripts\activate     # Windows
   ```

### Permission Denied

**Error:** `Permission denied` when installing globally

**Solution:** Use `--user` flag:

```bash
pip install --user weather-cli
```

Or install in a virtual environment.

### SSL Certificate Errors

**Error:** `SSLCertVerificationError` or `certificate verify failed`

**Solutions:**

1. Update CA certificates:
   ```bash
   # Ubuntu/Debian
   sudo apt-get update && sudo apt-get install ca-certificates
   
   # macOS
   brew install ca-certificates
   
   # Update Python certs
   python -m pip install --upgrade certifi
   ```

2. Set certificate bundle (if behind corporate proxy):
   ```bash
   export REQUESTS_CA_BUNDLE=/path/to/ca-bundle.crt
   ```

### API Key Issues

See [Troubleshooting section in README.md](../README.md#troubleshooting) for API-specific issues.

---

## Upgrading

To upgrade to the latest version:

```bash
pip install --upgrade weather-cli
```

Or for a specific version:

```bash
pip install --upgrade weather-cli==0.2.0
```

If you installed with `--user`, use:

```bash
pip install --user --upgrade weather-cli
```

After upgrading, verify the new version:

```bash
weather-cli --version
```

---

## Uninstalling

To remove the package:

```bash
pip uninstall weather-cli
```

To also remove configuration and cache:

```bash
rm -rf ~/.config/weather-cli          # Linux/macOS
# or delete %APPDATA%\weather-cli    # Windows

rm -rf ~/.cache/weather-cli          # Linux/macOS
# or delete %LOCALAPPDATA%\weather-cli\Cache  # Windows
```

---

## Advanced Installation Options

### Installing Specific Python Version

```bash
# Use python3.9 explicitly
python3.9 -m pip install weather-cli

# Or
py -3.9 -m pip install weather-cli  # Windows
```

### Offline Installation

1. On a machine with internet, download:
   - The wheel file (`weather_cli-*.whl`)
   - All dependency wheels (will be downloaded automatically with `pip download`)

2. Transfer to target machine and install:

   ```bash
   pip install --no-index --find-links=/path/to/wheels weather_cli-*.whl
   ```

### Installing from Test PyPI

For testing pre-release versions:

```bash
# First, install build and twine
pip install build twine

# Build and upload to Test PyPI
python -m build
twine upload --repository testpypi dist/*

# Then install from Test PyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple weather-cli
```

---

## Installation Best Practices

1. **Use Virtual Environments** - Isolate your projects to avoid version conflicts
2. **Prefer PyPI** - Automatic dependency resolution and easy updates
3. **Secure Your API Key** - Use config file with restricted permissions (chmod 600)
4. **Pin Versions** - For production use, freeze dependencies:
   ```bash
   pip freeze > requirements.txt
   ```
5. **Regular Updates** - Keep the package and dependencies updated:
   ```bash
   pip install --upgrade weather-cli
   ```

---

## Additional Resources

- [PyPI Package Page](https://pypi.org/project/weather-cli/) *(once published)*
- [GitHub Repository](https://github.com/yourusername/weather-cli)
- [README.md](../README.md) - Usage guide and reference
- [API Documentation](https://www.weatherapi.com/docs/) - WeatherAPI.com

---

## Need Help?

If you encounter issues not covered here:

1. Check the [full troubleshooting section](../README.md#troubleshooting) in the README
2. Search [existing issues](../../issues) on GitHub
3. Open a new issue with:
   - Your operating system
   - Python version (`python --version`)
   - Exact error message
   - Steps to reproduce

We're here to help!
