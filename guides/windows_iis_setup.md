# Setup Raven on Windows and IIS

Work in progress

## Requirements

- Git
- Application request routing installed and enabled
  - https://www.iis.net/downloads/microsoft/application-request-routing
  - https://bmscloud.no/vapcloud/help/engineeringhelp/en-us/23598993547.html

## Setup

### Clone repository:

```powershell
git clone https://git.nilu.no/raven/raven-administration
```

### Install and build client

Inside the client folder run these commands.  
This will create a `dist` folder

```powershell
npm install
npm build
```

### Create a web.config file in the `dist` folder

Change the api port if needed

```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <system.webServer>
    <rewrite>
      <rules>
        <rule name="backend" enabled="true" stopProcessing="true">
          <match url="^api/(.*)$" />
          <action type="Rewrite" url="http://localhost:5000/api/{R:1}"/>
        </rule>
        <rule name="frontend" stopProcessing="true">
          <match url="^(?!api/)(.*)" />
          <conditions logicalGrouping="MatchAll">
            <add input="{REQUEST_FILENAME}" matchType="IsFile" negate="true" />
            <add input="{REQUEST_FILENAME}" matchType="IsDirectory" negate="true" />
          </conditions>
          <action type="Rewrite" url="/" />
        </rule>
      </rules>
    </rewrite>
  </system.webServer>
</configuration>
```

### Install and build api

Inside the `api`folder, create a virtual environment, activate it and install packages

```powershell
python -m venv venv
\venv\Scripts\activate
pip install -r requirements.txt
```

### Create a web.config file

```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <system.webServer>
        <handlers>
            <add name="raven-administration-handler" path="*" verb="*" modules="FastCgiModule" scriptProcessor="<path_to_raven>\api\venv\Scripts\python.exe|<path_to_raven>\api\venv\Lib\site-packages\wfastcgi.py" resourceType="Unspecified" />
        </handlers>
        <urlCompression doStaticCompression="true" doDynamicCompression="true" />
    </system.webServer>
<appSettings>
<add key="WSGI_HANDLER" value="app.app" />
</appSettings>
</configuration>
```

### Enable wfastcgi

```powershell
pip install wfastcgi
wfastcgi-enable
```

### Add .env file

```
DB_URI = postgresql://postgres:password@host:5432/database
JWT_ACCESS_TOKEN_EXPIRES_SECONDS = 3600
JWT_SECRET_KEY = make-up-a-secure-key
```

### IIS

Setup a new website on port 80 (or use the default website)  
Set the path to the `dist` folder

Setup a new website on port 5000  
Set the path to the `api` folder  
Set The applicationpool to `No managed code`
