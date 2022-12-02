# RAVEN Administration

**RAVEN** is an open source web based Air Quality data validation and e-reporting system, with the aim to control the flow, metadata inventory, the quality of the monitoring data and producing the XML files required for the Air Quality B-G, except from D1b (Information on the assessment methods - for models and objective estimation) and E1b (Information on primary validated assessment data – modelled).  
The system is managed and developed by `NILU`, with support from `4sFera`, on the behalf of the `European Environmental Agency`.

## Requirements

Python version `3.9.12`  
Node version `14.18+`  
Postgres version `12+`  
Postgis extension  
Yarn or NPM (mixing is not recommended)

## Installation

#### **Clone repository from git**

```sh
git clone https://git.nilu.no/raven/raven-administration
```

#### **Run db scripts to create the database**

1. Create a postgres database, ie `ravendb`
2. Install Postgis (https://postgis.net/install/) and enable it on the database `CREATE EXTENSION postgis;`
3. Run the `sql\schema.sql` script
4. Run the `sql\data.sql` script

#### **Create a .env file and set the variables**

```
DB_URI = postgresql://postgres:password@localhost:5432/database
JWT_ACCESS_TOKEN_EXPIRES_SECONDS = 3600
JWT_SECRET_KEY = make-up-a-secure-key
```

#### **Create a virtual environment and activate it**

```powershell
# create
python -m venv venv
# activate
.\venv\Scripts\activate
```

#### **Install required python packages**

```powershell
pip install -r requirements.txt
```

#### **In the _client_ folder install the required js packages**

```powershell
# Chose either yarn or npm
yarn install
npm install
```

#### **Create the administartor**

```powershell
python .\create-admin-user.py -n name  -u username -p password
```

## Run Raven (not production)

```powershell
# start backend server
$env:FLASK_APP = "raven.py"
flask run
# from inside the client folder start the frontend
yarn dev
```
