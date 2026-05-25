#!/usr/bin/env bash

# Read .env file and export variables properly
if [ -f "$(dirname "$0")/.env" ]; then
    while IFS='=' read -r key value; do
        # Skip empty lines and comments
        [[ -z "$key" || "$key" =~ ^[[:space:]]*# ]] && continue
        # Trim whitespace from key and value
        key=$(echo "$key" | xargs)
        value=$(echo "$value" | xargs)
        # Export the variable
        export "$key=$value"
    done < "$(dirname "$0")/.env"
fi

export PROJECT_ID="$WATSONX_PROJECT_ID"

# Use venv python if available, else fall back to system python
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_PYTHON="$SCRIPT_DIR/.ibm_scuderia/bin/python"

if [ -f "$VENV_PYTHON" ]; then
    "$VENV_PYTHON" /mnt/c/Users/shawn/bob/reboot/reboot.py "$@"
elif command -v python3 &> /dev/null; then
    python3 /mnt/c/Users/shawn/bob/reboot/reboot.py "$@"
else
    echo "Error: Python not found"
    exit 1
fi

# Made with Bob
