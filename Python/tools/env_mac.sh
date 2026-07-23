#!/usr/bin/env bash
# macOS/Linux equivalent of env.bat
set -e

echo "Creating Python env.."
python3 -m venv ./env

echo "Activating Python env.."
# shellcheck source=/dev/null
source ./env/bin/activate

echo "Installing requirements.."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo "Using Python env at: $VIRTUAL_ENV"
