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

## Set environment varables

**Create an `.env` file in the `api` folder and set the variables**

```
DB_URI = postgresql://postgres:password@host:5432/database
JWT_ACCESS_TOKEN_EXPIRES_SECONDS = 3600
JWT_SECRET_KEY = make-up-a-secure-key
```

`Hint: Use host.docker.internal if database is local`

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
# activate
.\venv\Scripts\activate
```

**Install required python packages**

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
$env:FLASK_APP = "app.py"
flask run
# from inside the client folder start the frontend
nmp run dev
```
