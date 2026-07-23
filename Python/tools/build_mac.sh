#!/usr/bin/env bash
# macOS/Linux equivalent of build.bat
#
# IMPORTANT!!! setup.py gets overridden by a_rdk_set_version.py
# Update a_rdk_set_version.py if setup.py is changed
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ----------------------------------
# Create Python venv
echo "---------------"
echo "Creating env.."
# shellcheck source=env_mac.sh
source ./env_mac.sh

# ----------------------------------
# ./tools -> Python/
cd ..

while true; do

    # ----------------------------------
    # Clean previous build
    echo "---------------"
    echo "Cleaning last build..."
    rm -rf build dist robodk.egg-info build_python2

    # ----------------------------------
    # Build the package with wheel
    echo "---------------"
    read -rp "Press enter to BUILD the Python package..." _
    python setup.py bdist_wheel

    # ----------------------------------
    # Test the install on Python 3
    echo "---------------"
    read -rp "Press enter to TEST the Python package..." _
    for whl in dist/*.whl; do
        python -m pip uninstall -y robodk || true
        python -m pip install "$whl"
    done

    # ----------------------------------
    # Upload the package to PyPi with twine (will ask for credentials)
    echo "---------------"
    read -rp "Press enter to UPLOAD to PyPi..." _
    twine upload dist/*

    # ----------------------------------
    # Clean the build
    echo "---------------"
    read -rp "Press enter to clean the build..." _
    rm -rf build dist robodk.egg-info build_python2

    # ----------------------------------
    # Offer to start over
    read -rp "Enter r to restart, anything else to exit: " choice
    if [[ "$choice" != "r" ]]; then
        break
    fi
done
