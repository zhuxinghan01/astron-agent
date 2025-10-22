#!/bin/sh

# Casdoor entrypoint script
# This script dynamically replaces redirectUris in init_data.json before starting Casdoor

set -e

CONFIG_FILE="/conf/init_data.json"
CONFIG_BACKUP="/conf/init_data.json.backup"

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

# Create backup if it doesn't exist
if [ ! -f "$CONFIG_BACKUP" ]; then
    echo "Creating backup of original init_data.json..."
    cp "$CONFIG_FILE" "$CONFIG_BACKUP"
fi

# Restore from backup to ensure we start with the original template
cp "$CONFIG_BACKUP" "$CONFIG_FILE"

# Use sed to replace the redirectUris value
# This replaces the entire redirectUris array with the new value
echo "Updating redirectUris in init_data.json..."
sed -i "s|\"redirectUris\": \[[^]]*\]|\"redirectUris\": [\"${REDIRECT_URI}\"]|g" "$CONFIG_FILE"

echo "Configuration updated successfully!"
echo "RedirectUris set to: [\"${REDIRECT_URI}\"]"

# Start Casdoor
echo "Starting Casdoor..."
exec /casdoor --createDatabase=true