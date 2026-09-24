# RAVEN Administration

**RAVEN** is an open source web based Air Quality data validation and e-reporting system, with the aim to control the flow, metadata inventory, the quality of the monitoring data and producing the XML files required for the Air Quality B-G, except from D1b (Information on the assessment methods - for models and objective estimation) and E1b (Information on primary validated assessment data – modelled).  
The system is managed and developed by `NILU`, with support from `4sFera`, on the behalf of the `European Environmental Agency`.

## Requirements

Python version `3.10.8`  
Node version `18.12.1`  
Postgres version `12+`  
Postgis extension  
NPM

## **Clone repository from git**

```powershell
git clone https://git.nilu.no/raven/raven-administration
```

## Setup the database

**Run db scripts to create the database**

1. Create a postgres database, ie `ravendb`
2. Install Postgis (https://postgis.net/install/) and enable it on the database `CREATE EXTENSION postgis;`
3. Run the `sql\schema.sql` script
4. Run the `sql\data.sql` script
5. Run the `sql\pre_aggregates.sql` script
6. Run the `sql\use_in_public_api.sql` script
7. Run the `sql\meteo.sql` script
8. Run the `sql\aqi.sql` script
9. Run the `sql\notifications.sql` script
10. Run the `sql\meteo_concentration.sql` script

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

MAIL_METHOD=smtp # smtp or graph
```

**Sending with SMTP (default):**

```
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your.email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=noreply@yourorg.com
```

**Sending with Microsoft Graph API (`MAIL_METHOD=graph`):**

```
GRAPH_TENANT_ID=your-tenant-id
GRAPH_CLIENT_ID=your-client-id
GRAPH_CLIENT_SECRET=your-client-secret
GRAPH_SENDER=raven@yourorg.com
```

Requirements in Microsoft Entra ID (Azure AD):

1. Register an app and create a client secret. The Tenant ID and Client ID are on the app's overview page.
2. Add the **application** permission `Mail.Send` for Microsoft Graph (not delegated), and click **Grant admin consent**.
3. `GRAPH_SENDER` must be an existing mailbox (user or shared mailbox) in the tenant. All notifications are sent from this address.
4. Recommended: `Mail.Send` lets the app send as any mailbox in the tenant. Limit it to the sender mailbox with [RBAC for Applications in Exchange Online](https://learn.microsoft.com/en-us/exchange/permissions-exo/application-rbac).

Errors from Microsoft (for example an invalid secret or missing consent) are logged in the `notifications_runs` table.

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
```
