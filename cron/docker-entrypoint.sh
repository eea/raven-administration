#!/bin/bash
set -e

# Function to handle signals
cleanup() {
    echo "Shutting down cron services..."
    kill -TERM $CRON_PID 2>/dev/null || true
    wait $CRON_PID 2>/dev/null || true
    exit 0
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT

echo "Starting Raven Cron Services..."
echo "================================"

# Create log directory if it doesn't exist
mkdir -p /var/log/cron

# Test database connection
echo "Testing database connection..."
python3 -c "
import os
from dotenv import load_dotenv
import psycopg2
load_dotenv()
try:
    conn = psycopg2.connect(os.environ.get('DB_URI'))
    conn.close()
    print('✅ Database connection successful')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    exit(1)
"

# Test SMTP configuration
echo "Testing SMTP configuration..."
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()
smtp_server = os.environ.get('SMTP_SERVER', 'localhost')
smtp_port = os.environ.get('SMTP_PORT', '25')
print(f'✅ SMTP configured: {smtp_server}:{smtp_port}')
"

# Generate crontab based on environment variables
echo "Generating crontab from environment configuration..."

# Load specific environment variables from .env file
if [ -f /app/.env ]; then
    # Extract only CRON-related variables and remove carriage returns
    CRON_NOTIFICATIONS_ENABLED=$(grep -E "^CRON_NOTIFICATIONS_ENABLED" /app/.env | cut -d'=' -f2 | tr -d ' \r\n')
    CRON_NOTIFICATIONS_SCHEDULE=$(grep -E "^CRON_NOTIFICATIONS_SCHEDULE" /app/.env | cut -d'=' -f2- | tr -d '\r')
    CRON_AGGREGATION_ENABLED=$(grep -E "^CRON_AGGREGATION_ENABLED" /app/.env | cut -d'=' -f2 | tr -d ' \r\n')
    CRON_AGGREGATION_SCHEDULE=$(grep -E "^CRON_AGGREGATION_SCHEDULE" /app/.env | cut -d'=' -f2- | tr -d '\r')
fi

cat > /tmp/crontab << 'EOF'
# RAVEN Cron Jobs - Generated from environment variables
EOF

# Add notifications email job if enabled
NOTIFICATIONS_ENABLED=${CRON_NOTIFICATIONS_ENABLED:-false}
NOTIFICATIONS_SCHEDULE=${CRON_NOTIFICATIONS_SCHEDULE:-"10 * * * *"}

if [ "$NOTIFICATIONS_ENABLED" = "true" ] || [ "$NOTIFICATIONS_ENABLED" = "1" ] || [ "$NOTIFICATIONS_ENABLED" = "yes" ] || [ "$NOTIFICATIONS_ENABLED" = "on" ]; then
    echo "# Run notifications - Schedule: $NOTIFICATIONS_SCHEDULE" >> /tmp/crontab
    echo "$NOTIFICATIONS_SCHEDULE cd /app && /usr/local/bin/python3 cron/email_when_missing.py >> /var/log/cron/missing_data.log 2>&1" >> /tmp/crontab
    echo "✅ Notifications job enabled with schedule: $NOTIFICATIONS_SCHEDULE"
else
    echo "⚠️  Notifications job disabled"
fi

# Add aggregation job if enabled
AGGREGATION_ENABLED=${CRON_AGGREGATION_ENABLED:-false}
AGGREGATION_SCHEDULE=${CRON_AGGREGATION_SCHEDULE:-"30 2 * * *"}

if [ "$AGGREGATION_ENABLED" = "true" ] || [ "$AGGREGATION_ENABLED" = "1" ] || [ "$AGGREGATION_ENABLED" = "yes" ] || [ "$AGGREGATION_ENABLED" = "on" ]; then
    echo "# Run aggregation - Schedule: $AGGREGATION_SCHEDULE" >> /tmp/crontab
    echo "$AGGREGATION_SCHEDULE cd /app && /usr/local/bin/python3 cron/refresh_views.py >> /var/log/cron/refresh_views.log 2>&1" >> /tmp/crontab
    echo "✅ Aggregation job enabled with schedule: $AGGREGATION_SCHEDULE"
else
    echo "⚠️  Aggregation job disabled"
fi

# Install the generated crontab
if [ -s /tmp/crontab ]; then
    crontab /tmp/crontab
    echo "✅ Crontab installed successfully"
    echo "Current crontab contents:"
    crontab -l | sed 's/^/  /'
else
    echo "⚠️  No cron jobs enabled - empty crontab"
    echo "" | crontab -
fi

# Start cron in foreground
echo "Starting cron daemon..."
cron -f &
CRON_PID=$!

echo "Cron services started successfully!"
echo "Logs available in /var/log/cron/"
echo "================================"

# Keep the container running
wait $CRON_PID