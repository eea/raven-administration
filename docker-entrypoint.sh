#!/bin/sh
set -e

# Build the Vue frontend on first run (populates the shared client-dist volume).
# Check for dist/assets/ — a Vite-specific directory, not the nginx default index.html.
if [ ! -d /app/client/dist/assets ]; then
    echo "[raven] Building Vue frontend (dist volume is empty)..."
    (cd /app/client && npm run build)
    echo "[raven] Frontend build complete."
fi

# Apply any pending SQL migrations before serving. Every migration is
# idempotent and records itself in schema_version, so this is a no-op once the
# database is up to date. Set RAVEN_SKIP_MIGRATIONS=1 to bypass.
if [ -z "$RAVEN_SKIP_MIGRATIONS" ] && [ -n "$DB_URI" ]; then
    echo "[raven] Applying pending SQL migrations..."
    python /app/sql/apply_migrations.py || {
        echo "[raven] Migration failed — refusing to start." >&2
        exit 1
    }
fi

exec gunicorn \
    --bind 0.0.0.0:5000 \
    --workers 3 \
    --threads 2 \
    --timeout 3600 \
    app:app
