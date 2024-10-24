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

## Set environment varables

**Create a file called `.env` in the `root` folder and set the variables**

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
Then build and run the `docker-compose` file.

```powershell
# build and run
docker-compose build
docker-compose up
# Access RAVEN at: http://localhost
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

## Pre aggregations

Aggregating data can be triggered manually in the raven app.  
However, it is recommended to set up a schedule to trigger the aggregation on a daily basis.  
The sql command that needs to run is `select raven_refresh_aggregates()`  
One ways is to use the postgres extension `pgagent`. This will enable a schedular within postgres.  
Another way is to set up a `cron` job in linux or a `schtasks` in windows

The `cron` folder has a python script that can be used together with a schedular.  
It does require `psycopg2-binary==2.9.5`, so make sure this is available for the scheduled task.

```powershell
# Example of how to set up a scheduled task in Windows
schtasks /create /SC DAILY /TN raven-refresh-views /TR "<path_to_python> <path_to_raven>\cron\refresh_views.py" /ST 00:10
```
