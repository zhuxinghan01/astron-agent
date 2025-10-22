#!/bin/sh
set -e

echo "===== Initializing Casdoor Configuration ====="
echo "CONSOLE_DOMAIN: ${CONSOLE_DOMAIN:-http://localhost}"

# Generate config from template using sed (no need to install extra packages)
echo "Generating init_data.json from template..."
sed "s|\${CONSOLE_DOMAIN}|${CONSOLE_DOMAIN}|g" /conf/init_data.json.template > /conf/init_data.json

echo "Configuration updated: redirectUris set to [${CONSOLE_DOMAIN}/callback]"
echo "=========================================="

# Start Casdoor
exec /server --createDatabase=true