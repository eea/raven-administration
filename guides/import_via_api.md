# Import via API

You can import data with csv files into the Raven database.  
Examples of csv file can be found in the [csv_examples folder](/csv_examples)

## Authentication

Before importing data you will need to retrieve a bearer token.

```yaml
POST api/auth/signin
BODY {"username":"username", "password":"password"}
```

Keep in mind, that the user needs to have access to _**management**_ and _**all networks**_  
This can configured within the Raven website

# Importing

Set the bearer token as authorization  
Attach the csv file as _**form-data**_ with the key _**file**_

### Authorities

[Example](/csv_examples/responsible_authorities.csv)

```yaml
# Endpoint
POST api/imports/authorities
# CSV headers
id,name,organisation,address,locator,postcode,email,phone,website,is_responsible_reporter
```

### Networks

[Example](/csv_examples/networks.csv)

```yaml
# Endpoint
POST api/imports/networks
# CSV headers
id,name,media_monitored,responsible_authority_id,organisational,begin_position,end_position,aggregation_timezone
```

### Stations

[Example](/csv_examples/stations.csv)

```yaml
# Endpoint
POST api/imports/stations
# CSV headers
id,national_station_code,name,network_id,measurement_regime,city,eoi_code,municipality,geom,mobile,area_classification,distance_junction,traffic_volume,heavy_duty_fraction,street_width,height_facades,begin_position,end_position
```

### Sampling points

[Example](/csv_examples/sampling_points.csv)

```yaml
# Endpoint
POST api/imports/sampling_points
# CSV headers
id,station_id,assessment_type,station_classification,industrial_emissions,distance_source,mobile,used_aqd,media_monitored,measurement_regime,main_emission_sources,traffic_emissions,heating_emissions,industrial_emissions,change_aei_stations,logger_id,pollutant,begin_position,end_position,concentration,timestep
```
