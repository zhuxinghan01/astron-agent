#!/bin/sh

# Casdoor configuration script
# This script dynamically replaces redirectUris in init_data.json

set -e

CONFIG_FILE="/conf/init_data.json"

# Check if CONSOLE_DOMAIN is set
if [ -z "$CONSOLE_DOMAIN" ]; then
    echo "Warning: CONSOLE_DOMAIN environment variable is not set. Using default value."
    CONSOLE_DOMAIN="http://localhost"
fi

# Construct the redirect URI
REDIRECT_URI="${CONSOLE_DOMAIN}/callback"

echo "===== Casdoor Configuration ====="
echo "CONSOLE_DOMAIN: $CONSOLE_DOMAIN"
echo "REDIRECT_URI: $REDIRECT_URI"
echo "================================="

# Use sed to replace the redirectUris value
echo "Updating redirectUris in init_data.json..."
sed -i "s|\"redirectUris\": \[[^]]*\]|\"redirectUris\": [\"${REDIRECT_URI}\"]|g" "$CONFIG_FILE"

echo "Configuration updated successfully!"
echo "RedirectUris set to: [\"${REDIRECT_URI}\"]"