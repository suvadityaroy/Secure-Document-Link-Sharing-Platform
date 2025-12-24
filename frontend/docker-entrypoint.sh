#!/usr/bin/env bash
set -eu

# Default: API_BASE should be set to your public API URL
: "${API_BASE:=http://localhost:8000/api}"

echo "Configuring frontend to use API at: ${API_BASE}" >&2

# Replace the API_BASE constant in index.html so the SPA calls the right endpoint
if [ -f /usr/share/nginx/html/index.html ]; then
  sed -i "s|const API_BASE = 'http://localhost:8000/api'|const API_BASE = '${API_BASE}'|g" /usr/share/nginx/html/index.html
  echo "✓ API_BASE configured in index.html" >&2
else
  echo "⚠ Warning: index.html not found" >&2
fi

echo "Frontend configuration complete" >&2

