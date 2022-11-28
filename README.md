# RAVEN Administration

## Requirements

Python version `3.9.12`  
Node version `14.18+`  
Postgres version `12+`  
Postgis extension  
Yarn or NPM (mixing is not recommended)

## Installation

### Clone repository from git

```sh
git clone https://git.nilu.no/raven/raven-administration
```

### Run db scripts to create the database.

TBD

### Create a .env file and set the variables

```
DB_URI = postgresql://postgres:password@localhost:5432/database
JWT_ACCESS_TOKEN_EXPIRES_SECONDS = 3600
JWT_SECRET_KEY = make-up-a-secure-key
```

### Create a virtual environment and activate it

```sh
# create
python -m venv venv
# activate
.\venv\Scripts\activate
```

### Install required python packages

```sh
pip install -r requirements.txt
```

### In the **client** folder install the required js packages

```sh
yarn install
npm install
```

### Create the administartor

```sh
python .\create-admin-user.py -n name  -u username -p password
```

## Run Raven (not production)

```sh
# start backend server
flask run
# from inside the client folder start the frontend
yarn dev
```
