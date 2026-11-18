# RAVEN Administration

**RAVEN** is an open source web based Air Quality data validation and e-reporting system, with the aim to control the flow, metadata inventory, the quality of the monitoring data and producing the XML files required for the Air Quality B-G, except from D1b (Information on the assessment methods - for models and objective estimation) and E1b (Information on primary validated assessment data – modelled).  
The system is managed and developed by `NILU`, with support from `4sFera`, on the behalf of the `European Environmental Agency`.

## Requirements

Python version `3.12+`  
Node version `24.5.0`  
Postgres version `12+`  
Postgis extension  
NPM

R requirements:

- R must be installed and Rscript available on PATH.
- Minimum required R packages: `plumber`, `jsonlite`
- For using 4sfera code snippets: `RPostgres`, `DBI`, `tidyr`, `dplyr`, `lubridate`, `openair`, `ggplot2`

## **Clone repository from git**

```powershell
git clone https://git.nilu.no/raven/raven-administration
```

## Setup the database

> **Migrating from Raven v3?** Do not use these steps: follow
> [`sql/raven4_migrate/README.md`](sql/raven4_migrate/README.md) instead. Some of the scripts
> below must not be run on a migrated database.

**Run db scripts to create the database**

1. Create a postgres database, ie `ravendb`
2. Install Postgis (https://postgis.net/install/) and enable it on the database `CREATE EXTENSION postgis;`
3. Run the `sql\schema.sql` script
4. Run the `sql\data.sql` script
5. ~~Run the `sql\pre_aggregates.sql` script~~ — `schema.sql` creates the pre-aggregate
   views since 4.502.25 (migration 025). Run it only to drop and rebuild them from scratch.
6. Run the `sql\use_in_public_api.sql` script
7. Run the `sql\meteo.sql` script
8. Run the `sql\aqi.sql` script
9. Run the `sql\notifications.sql` script
10. Run the `sql\statistics.sql` script

`sql\meteo_concentration.sql` used to be step 10. It seeded ten `uom/meteo` units into
`eea_concentrations`, which reports the `uom/concentration` vocabulary (AQR3 OMR_11), and it
keyed them by their full URI. Non-concentration units are handled properly now: since
migration 012 a series with no vocabulary unit carries `unit_id = NULL` and the real unit as
text in `plugin_sp_extended.unit`. Migration `016_vocabulary_id_normalisation.sql` removes
the rows from databases that already have them.

## Set environment varables

**Create a file called `.env` in the `root` folder and set the variables**  
See `.env.example` for all variables

```
API_PORT=5000
CLIENT_PORT=80
DB_URI = postgresql://dbuser:password@host:5432/database
JWT_ACCESS_TOKEN_EXPIRES_SECONDS = 3600
JWT_SECRET_KEY = make-up-a-secure-key
CONTAINER_NAME_API = raven-api
CONTAINER_NAME_CLIENT = raven-client
CONTAINER_NAME_RNOTEBOOK = raven-rnotebook
R_PORT = 8888

```

`Hint: Use host.docker.internal if database is local. Ip 172.17.0.1 for Linux`

## Docker

Make sure you have Docker engine installed. (https://www.docker.com/)

**Main application only (API + Client):**

```powershell
docker-compose up -d --build
# Access RAVEN at: http://localhost

```

**Full stack with background jobs (API + Client + Cron):**

```powershell
docker-compose -f docker-compose.cron.yml up -d --build
# Access RAVEN at: http://localhost
```

## Background Jobs

RAVEN includes configurable background jobs for data aggregation and notifications.

### Aggregation

Refreshes materialized views and pre-aggregated data. Can be triggered manually in the app or automated via cron.

**Environment variables:**

```
CRON_AGGREGATION_ENABLED=true
CRON_AGGREGATION_SCHEDULE=30 2 * * *
```

### Notifications

Sends email alerts for missing data (sampling points not updated within specified interval).

**Environment variables:**

```
CRON_NOTIFICATIONS_ENABLED=true
CRON_NOTIFICATIONS_SCHEDULE=10 * * * *
CRON_NOTIFICATIONS_MIN_INTERVAL_HOURS=3

SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your.email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=noreply@yourorg.com
```

**Cron schedule format:** `minute hour day month weekday` ([crontab.guru](https://crontab.guru) for examples)

### Manual Setup (Alternative)

For non-Docker deployments, use system schedulers:

**Linux cron:**

```bash
# Daily aggregation at 2:30 AM
30 2 * * * cd /path/to/raven && python3 cron/refresh_views.py

# Hourly notifications at minute 10
10 * * * * cd /path/to/raven && python3 cron/email_when_missing.py
```

**Windows schtasks:**

```powershell
schtasks /create /SC DAILY /TN raven-aggregation /TR "python <path>\cron\refresh_views.py" /ST 02:30
schtasks /create /SC HOURLY /TN raven-notifications /TR "python <path>\cron\email_when_missing.py"
```

## Development

**Create a virtual environment and activate it**

```powershell
# create
python -m venv venv
# activate on Windows
.\venv\Scripts\activate
# activate on Mac and Linux
source venv/bin/activate
```

**In the `api` folder install the required python packages**

```powershell
pip install -r requirements.txt
```

**In the `client` folder install the required js packages**

```powershell
npm install
```

**Run Raven**

```powershell
# from inside the api folder start backend server
# on Windows
$env:FLASK_APP = "app.py"
flask run

# on Mac and Linux
export FLASK_APP=app.py
flask run

# from inside the client folder start the frontend
npm run dev

# from the r folder start r notebook backend server
Rscript r/app.R
```

## MCP server (AI assistants)

Raven can let AI assistants such as Claude query its data: series, latest values, statistics,
exceedances, zones, assessment regimes and the observation log. It is read-only, and each user signs in
with their own Raven username and password, so they see exactly what they see in the web client.

Examples of what you can ask:

- "Which stations measure NO2, and what are the latest values?"
- "Show monthly PM10 averages at station X for 2025."
- "What was the annual mean NO2 per station in 2025, and how good was the data coverage?"
- "Which PM10 sampling points exceeded the 2024/2881 limit values in 2025?"
- "Which zones and assessment regimes do we have for O3, and does zone X meet its objectives?"
- "Who changed the validity flags for this series last month, and when?"

Questions about zones need the management and all-networks permissions, and questions about change
history need the quality control permission.

### Enable it

1. In `.env`, set:

   ```
   MCP_ENABLED=true
   ```

2. Rebuild and start:

   ```bash
   docker compose up -d --build
   ```

3. The MCP server is now available at `https://<raven-host>/mcp`.

Serve Raven over HTTPS only: the MCP connection sends the user's password with every request.
To turn it off again, set `MCP_ENABLED=false` and run `docker compose up -d` again.

### Connect an AI assistant

**Claude Code:** run, with your own Raven username and password. `--scope user` makes Raven available in
all your Claude Code sessions:

```bash
claude mcp add --scope user --transport http raven https://<raven-host>/mcp -H "X-Raven-Username: your-username" -H "X-Raven-Password: your-password"
```

**Claude Desktop:** requires [Node.js](https://nodejs.org). Open Settings, Developer, Edit Config, add the
following to `claude_desktop_config.json`, then restart Claude Desktop:

```json
{
  "mcpServers": {
    "raven": {
      "command": "npx",
      "args": ["mcp-remote", "https://<raven-host>/mcp",
               "--header", "X-Raven-Username:${RAVEN_USERNAME}",
               "--header", "X-Raven-Password:${RAVEN_PASSWORD}"],
      "env": { "RAVEN_USERNAME": "your-username", "RAVEN_PASSWORD": "your-password" }
    }
  }
}
```
