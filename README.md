# RAVEN Administration

## Requirements

Python version `3.9.12`  
Node
yarn/npm

## Installation

Clone repository from git

```powershell
git clone https://git.nilu.no/raven/raven-administration
```

Create a virtual environment and activate it

```powershell
python -m venv venv

.\venv\Scripts\activate

deactivate
```

Install required python packages

```powershell
pip install -r requirements.txt
```

In the client folder install the required js packages

```powershell
yarn or npm install
```

Create a .env file and set the variables

```
DB_URI = postgresql://postgres:password@localhost:5432/database
JWT_ACCESS_TOKEN_EXPIRES_SECONDS = 3600
JWT_SECRET_KEY = super-secret-key
```

Create an admin user

```
python .\create-user.py -n "Some name"  -u username -p password
```
