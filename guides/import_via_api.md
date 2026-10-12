# Import and export via API

Raven's management tables can be round-tripped as CSV. Export a table, edit it,
import it back.

## API versions

The CSV headers for these endpoints **are** the database column names, derived at
runtime from `information_schema`. Aligning the schema with Reportnet3 AQR3 v5.02
therefore renamed several of them, so both contracts are served:

| Version | Path | Headers |
|---|---|---|
| v1 (frozen) | `/api/exports/<table>`, `/api/imports/<table>` | The pre-AQR3 names — unchanged, for existing callers |
| v2 | `/api/v2/exports/<table>`, `/api/v2/imports/<table>` | AQR3 v5.02 aligned column names |

Renamed columns, v1 header → v2 header:

| Table | v1 | v2 |
|---|---|---|
| `authorities` | `organisation_name` | `authority_name` |
| `authorities` | `organisation_url` | `authority_url` |
| `authorities` | `organisation_address` | `authority_address` |
| `authorities` | `instance_id` | `authority_instance_id` |
| `authorities` | `object_id` | `authority_role_id` |
| `authorities` | `status_id` | `authority_status_id` |
| `networks` | `administration_level_id` | `network_organisational_level_id` |
| `stations` | `eoi_code` | `station_eoi_code` |
| `stations` | `national_code` | `station_national_code` |
| `stations` | `area_classification_id` | `station_area_id` |
| `sampling_points` | `sampling_point_ref` | `sampling_point_reference_id` |
| `sampling_points` | `spo_category_id` | `sampling_point_category_id` |
| `processes` | `activity_begin` | `process_activity_begin` |
| `processes` | `activity_end` | `process_activity_end` |
| `zones` | `code` | `zone_national_code` |
| `zones` | `area` | `zone_area` |

Everything else is identical between the two versions.

## Authentication

```yaml
POST /api/auth/signin
BODY {"username":"username", "password":"password"}
```

The user needs both the `management` and `all networks` claims, granted in the
Raven web UI.

```bash
curl -H "Content-Type: application/json" -X POST \
     -d '{"username":"username", "password":"password"}' <MY_URL>/api/auth/signin
```

## Exporting

```bash
curl -H "Authorization: Bearer <TOKEN>" <MY_URL>/api/exports/stations      # v1
curl -H "Authorization: Bearer <TOKEN>" <MY_URL>/api/v2/exports/stations   # v2
```

## Importing

Attach the file as `form-data` under the key `file`.

```bash
curl -i -X POST -H "Authorization: Bearer <TOKEN>" \
     -F 'file=@stations.csv' <MY_URL>/api/imports/stations
```

```python
import requests

headers = {'Authorization': f'Bearer {token}'}
files = {'file': open('stations.csv', 'rb')}
requests.post(f'{url}/api/imports/stations', files=files, headers=headers)
```

## Tables

`authorities`, `zones`, `networks`, `stations`, `sampling_points`, `processes`,
`documents`.

To discover the exact headers for a table and version, export it first — the
header row is authoritative and always matches what the import will accept.
`sampling_points` includes `from_time` (the default AQR3 SPL_03 LocationBegin).

`zones` also accepts a GeoPackage (`.gpkg`) instead of CSV, in which case the
geometry comes from the file's geometry column.

## Pages with their own import

Four pages import through their own route instead, because each row must pass the
same checks as the page's form. The generic importer writes rows straight into the
table and would skip them. These routes take CSV only, and have no v2 variant.

| Page | Import | Export / template |
|---|---|---|
| Assessment data | `POST /api/management/assessmentdata/import` | `GET /api/management/assessmentdata/export` |
| Models / OBE | `POST /api/management/models/import` | `GET /api/management/models/export` |
| Pollution level adjustments | `POST /api/management/pollutionleveladjustment/import` | `GET /api/management/pollutionleveladjustment/export` |
| Spatial representativeness | `POST /api/management/spatialrepresentativeness/import` | `GET /api/management/spatialrepresentativeness/export` |

- The export's header is exactly what the import accepts. Required columns must be present; optional ones may be left out. An unknown column is refused.
- A file is saved whole or not at all. An error names its CSV line (`Row 3: ...`; the header is line 1).
- Rows are inserted, never updated. A row that already exists is an error.
- Assessment data: `id` may be empty, and is then derived as the form does. Each row names a `sampling_point_id` or a `model_id`, not both.
- Spatial representativeness: the CSV carries the records only. The area's grid cells come from a spatial file in the page's form.

## Observations

Separate endpoint, not part of the versioned management round-trip.

```yaml
POST /api/imports/observations
# CSV headers
sampling_point_id,from_time,to_time,value,observationverification_id,observationvalidity_id
```

Values that already exist are updated, unless `observationverification_id = 1`
(manually verified), which is never overwritten.

There is also `POST /api/imports/logger`, which takes JSON keyed by `logger_id`
rather than `sampling_point_id`:

```json
{"values": [{"logger_id": "...", "from_time": "...", "to_time": "...", "value": 12.3}]}
```

## Reportnet3 reporting export

The AQR3 v5.02 reporting CSVs are a different thing entirely — they are the EEA
submission format, not Raven's internal round-trip. See
**Data → Dataflow Export** in the UI, or:

```yaml
GET  /api/dataflow/csv/tables            # the registry: codes, filenames, columns
POST /api/dataflow/csv/<TABLE_CODE>      # one table, e.g. STA, SPO, OMR
POST /api/dataflow/csv/download_all      # everything as a ZIP
```
