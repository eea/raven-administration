# CREATE A NEW MODULE IN RAVEN

Show stations on a map

## Backend

### Create an api endpoint to retrive stations and location

File: api/endpoints/data/test/routes.py

```python
from flask import jsonify, Blueprint
from core.database import CursorFromPool
from core.jwt_ext_custom import jwt_required_with_data_claim
test_endpoint = Blueprint('test', __name__)


@test_endpoint.route('/api/test', methods=['GET'])
@jwt_required_with_data_claim()
def test():
    with CursorFromPool() as cursor:
        sql = f"""
            select name, st_x(geom) lon, st_y(geom) lat
            from stations

        """
        cursor.execute(sql)
        values = cursor.fetchall()
        return jsonify(values)
```

### Register route

File: api/core/endpoints.py

```python
...

# TEST
from endpoints.data.test.routes import test_endpoint
app.register_blueprint(test_endpoint)
```

## FRONTEND

### Create the map service file

File: client/src/views/data/test/service.js

```javascript
import { Get } from "../../../helpers/request";

const Service = {
  get: async () => Get("/api/data/test")
};

export default Service;
```

### Create the map module

File: client/src/views/data/test/Map.vue

```vue
<script setup>
import { featureGroup, map, tileLayer, marker } from "leaflet";
import { onMounted } from "vue";
import Service from "./service";
var mymap;
let url = "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png";

onMounted(async () => {
  const stations = await Service.get();
  var layers = [];
  stations.forEach((station) => {
    layers.push(marker([station.lat, station.lon]).bindPopup("<b>" + station.name + "</b>"));
  });

  var group = featureGroup(layers);
  mymap = map("map", {
    layers: [tileLayer(url, {}), group]
  }).setView([0, 0], 3);
  mymap.fitBounds(group.getBounds());
});
</script>

<template>
  <common-layout>
    <tool-bar title="Map" :show-column-picker="false" :show-add="false" :show-download="false" :show-filter="false" />
    <div class="border border-nord4 h-full w-full flex-1" id="map"></div>
  </common-layout>
</template>

<style></style>
```

### Register route

File: client/src/router.js

```javascript
...
const Map = () => import("./views/data/test/Map.vue");
...
const routes = [
...
{ path: "/data/test", component: Map, name: "Map" }
...
]
```

### Add to menu

File: client/src/components/MenuBar.vue

```javascript
...

const getmodules = () => {
  var token = sessionStorage.getItem("token");
  if (!token) return [];
  const jwt = jwt_decode(token);
  return [
    ...
    {
      group: "Data",
      show: jwt.data || jwt.exporting,
      items: [
        ...
        { name: "Map", comp: "Map", show: jwt.data },
      ]
    },
    ...
  ]
...
```
