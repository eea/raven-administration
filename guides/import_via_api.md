# Import via API

You can import data with csv files into the Raven database.  
Examples of csv file can be found in the [csv_examples folder](/csv_examples)

## Authentication

Before importing data you will need to retrieve a bearer token.

```yaml
POST api/auth/signin
BODY {"username":"username", "password":"password"}
```

Keep in mind, that the user needs to have access to `management` and `all networks`  
This can configured within the Raven website

# Importing

Set the bearer token as authorization  
Attach the csv file as `form-data` with the key `file`

**Curl syntax**

```bash
curl -i -X POST -H "Authorization: Bearer <MY_TOKEN>" -F 'file=@<MY_FILE_CSV>' <MY_URL>
```

**Python code**

```python
import requests

headers = {'Authorization': f'Bearer {<MY_TOKEN>}'}
files = {'file': open("<MY_FILE_CSV>", 'rb')}
response = requests.post(<MY_URL>, files=files, headers=headers)
```

### Authorities

[CSV Example](/csv_examples/responsible_authorities.csv)

```yaml
# Endpoint
POST api/imports/authorities
# CSV headers
id,name,organisation,address,locator,postcode,email,phone,website,is_responsible_reporter
```

### Networks

[CSV Example](/csv_examples/networks.csv)

```yaml
# Endpoint
POST api/imports/networks
# CSV headers
id,name,media_monitored,responsible_authority_id,organisational,begin_position,end_position,aggregation_timezone
```

### Stations

[CSV Example](/csv_examples/stations.csv)

```yaml
# Endpoint
POST api/imports/stations
# CSV headers
id,national_station_code,name,network_id,measurement_regime,city,eoi_code,municipality,geom,mobile,area_classification,distance_junction,traffic_volume,heavy_duty_fraction,street_width,height_facades,begin_position,end_position
```

### Sampling points

[CSV Example](/csv_examples/sampling_points.csv)

```yaml
# Endpoint
POST api/imports/sampling_points
# CSV headers
id,station_id,assessment_type,station_classification,industrial_emissions,distance_source,mobile,used_aqd,media_monitored,measurement_regime,main_emission_sources,traffic_emissions,heating_emissions,industrial_emissions,change_aei_stations,logger_id,pollutant,begin_position,end_position,concentration,timestep
```

### Observing capabilities

[CSV Example](/csv_examples/observation_capability.csv)

```yaml
# Endpoint
POST api/imports/observing_capabilities
# CSV headers
id,sampling_point_id,sample_id,process_id,begin_position,end_position,process_type,result_nature
```

### Samples

[CSV Example](/csv_examples/samples.csv)

```yaml
# Endpoint
POST api/imports/samples
# CSV headers
id,kerb_distance,inlet_height,building_distance
```

### Processes

[CSV Example](/csv_examples/processes.csv)

```yaml
# Endpoint
POST api/imports/processes
# CSV headers
id,responsible_authority_id,measurement_type,measurement_method,measurement_equipment,detection_limit,detection_limit_uom,equiv_demonstration,equiv_demonstration_report,documentation,qa_report,duration_unit,duration_number,cadence_unit,cadence_number,uncertainty_estimate,sampling_method,other_sampling_method,analytical_tech,other_analytical_tech,other_measurement_method,sampling_equipment,other_sampling_equipment,other_measurement_equipment
```

### Observations

[CSV Example](/csv_examples/obs-2019.csv)

Values that already exists in the database will be updated, unless the verification_flag is 1

```yaml
# Endpoint
POST api/imports/observations
# CSV headers
sampling_point_id,begin_position,end_position,value,validation_flag,verification_flag
```

### Zones

[GPKG Example](/csv_examples/zones.gpkg)

The zones file must be a geopackage file

```yaml
# Endpoint
POST api/imports/zones
# GEOPACKAGE attributes
id,area,code,population,population_year,type,year,responsible_authority
```
