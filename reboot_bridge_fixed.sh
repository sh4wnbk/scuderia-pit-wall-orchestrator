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

# Try python3 first, then python
if command -v python3 &> /dev/null; then
    python3 /mnt/c/Users/shawn/bob/reboot/reboot.py "$@"
elif command -v python &> /dev/null; then
    python /mnt/c/Users/shawn/bob/reboot/reboot.py "$@"
else
    echo "Error: Python not found"
    exit 1
fi

# Made with Bob
