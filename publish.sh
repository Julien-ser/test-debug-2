#!/usr/bin/env bash
# Publishing Script for Weather CLI
# This script uploads the built packages to Test PyPI or PyPI
#
# Prerequisites:
# - An account on test.pypi.org (for test releases) or pypi.org (for production)
# - An API token (not password) from your account settings
# - Packages already built (run: python -m build)
#
# Setup credentials (one-time):
# 1. Get your API token from:
#    - Test PyPI: https://test.pypi.org/manage/account/apikeys/
#    - PyPI: https://pypi.org/manage/account/apikeys/
# 2. Create or edit ~/.pypirc:
#
#    [distutils]
#    index-servers =
#        testpypi
#        pypi
#
#    [testpypi]
#    repository = https://test.pypi.org/legacy/
#    username = __token__
#    password = pypi-YourTokenHere
#
#    [pypi]
#    repository = https://upload.pypi.org/legacy/
#    username = __token__
#    password = pypi-YourTokenHere
#
# Usage:
#   ./publish.sh test   # Upload to Test PyPI (recommended first)
#   ./publish.sh prod   # Upload to production PyPI (when ready)
#
# Or use twine directly:
#   twine upload --repository testpypi dist/*
#   twine upload --repository pypi dist/*

set -e  # Exit on error

if [ $# -ne 1 ]; then
    echo "Usage: $0 [test|prod]"
    echo "  test - Upload to Test PyPI (https://test.pypi.org)"
    echo "  prod - Upload to production PyPI (https://pypi.org)"
    exit 1
fi

TARGET=$1

# Check if dist directory exists and has packages
if [ ! -d "dist" ] || [ -z "$(ls dist/*.whl 2>/dev/null)" ]; then
    echo "Error: No packages found in dist/ directory."
    echo "Please run: python -m build"
    exit 1
fi

# Check if twine is installed
if ! command -v twine &> /dev/null; then
    echo "Error: twine is not installed."
    echo "Install it with: pip install twine"
    exit 1
fi

if [ "$TARGET" = "test" ]; then
    echo "Uploading to Test PyPI..."
    twine upload --repository testpypi dist/*
    echo "✅ Successfully uploaded to Test PyPI!"
    echo "   View at: https://test.pypi.org/project/weather-cli/"
    echo ""
    echo "To test install from Test PyPI:"
    echo "  pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple weather-cli"
elif [ "$TARGET" = "prod" ]; then
    echo "Uploading to production PyPI..."
    echo "WARNING: This will publish to the live PyPI repository."
    read -p "Are you sure? (yes/no): " -r
    if [[ $REPLY =~ ^yes$ ]]; then
        twine upload --repository pypi dist/*
        echo "✅ Successfully uploaded to PyPI!"
        echo "   View at: https://pypi.org/project/weather-cli/"
    else
        echo "Upload cancelled."
        exit 0
    fi
else
    echo "Error: Unknown target '$TARGET'"
    echo "Valid targets: test, prod"
    exit 1
fi
