#!/bin/sh
set -e

echo "===== Initializing Casdoor Configuration ====="
echo "CONSOLE_DOMAIN: ${CONSOLE_DOMAIN:-http://localhost}"

# Install envsubst if not available
if ! command -v envsubst >/dev/null 2>&1; then
    echo "Installing gettext-base for envsubst..."
    apk add --no-cache gettext
fi

# Generate config from template using envsubst
echo "Generating init_data.json from template..."
envsubst < /conf/init_data.json.template > /conf/init_data.json

echo "Configuration updated: redirectUris set to [${CONSOLE_DOMAIN}/callback]"
echo "=========================================="

# Start Casdoor
exec /server --createDatabase=true