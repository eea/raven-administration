#!/bin/sh
set -e

# Build the Vue frontend on first run (populates the shared client-dist volume).
# Check for dist/assets/ — a Vite-specific directory, not the nginx default index.html.
if [ ! -d /app/client/dist/assets ]; then
    echo "[raven] Building Vue frontend (dist volume is empty)..."
    (cd /app/client && npm run build)
    echo "[raven] Frontend build complete."
fi

exec gunicorn \
    --bind 0.0.0.0:5000 \
    --workers 3 \
    --threads 2 \
    --timeout 3600 \
    app:app
