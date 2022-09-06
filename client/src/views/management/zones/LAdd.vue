<script setup>
import IconCode from "~icons/ri/file-code-fill";
import IconMap from "~icons/ri/road-map-fill";
import { geoJSON, map, tileLayer } from "leaflet";
import "leaflet/dist/leaflet.css";

const props = defineProps({
  show: Boolean,
  authorities: Array,
  types: Array
});

const emit = defineEmits(["close", "save"]);

const obj = ref({});
const showMap = ref(true);

var mymap;
var zoneLayer;
let url = "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png";

onMounted(() => {
  initMap();
});

watch(
  () => props.show,
  (nv) => {
    obj.value = {};
  }
);

const toggleMap = () => {
  if (!showMap.value) {
    addLayer();
  }
  showMap.value = !showMap.value;
};

const addLayer = () => {
  if (mymap && obj.value.geojson) {
    if (zoneLayer) mymap.removeLayer(zoneLayer);
    // console.log("AA", JSON.parse(obj.value.geojson));
    zoneLayer = geoJSON(JSON.parse(obj.value.geojson), {
      style: {
        color: "#ff0000",
        fillColor: "#ff0000",
        weight: 1
      }
    }).addTo(mymap);
    mymap.fitBounds(zoneLayer.getBounds());
  }
};

const close = () => {
  obj.value = {};
  emit("close");
};

const save = () => {
  emit("save", Object.assign({}, obj.value));
};

const initMap = () => {
  mymap = map("map-add").setView([50.378472, 14.970598], 3);
  tileLayer(url, {}).addTo(mymap);
};
</script>

<template>
  <side-bar :show="show" @close="close">
    <div class="flex flex-col px-6 py-4 justify-between h-full">
      <div class="flex flex-col h-full">
        <div class="mb-4 font-bold text-base border-b">Required</div>
        <div class="mb-2">
          <div class="font-bold">Id:</div>
          <input type="text" class="n-input !w-80" v-model="obj.id" placeholder="str: A unique id" />
        </div>

        <div class="mb-2">
          <div class="font-bold">Code:</div>
          <input type="text" class="n-input !w-80" v-model="obj.code" placeholder="str: A unique code" />
        </div>

        <div class="mb-2">
          <div class="font-bold">Name:</div>
          <input type="text" class="n-input w-80" v-model="obj.name" placeholder="str: Name of network" />
        </div>

        <div class="mb-2">
          <div class="font-bold">Year:</div>
          <input type="number" class="n-input w-80" v-model="obj.year" placeholder="int: The year zone is added" />
        </div>

        <div class="mb-2">
          <div class="font-bold">Area:</div>
          <input type="number" class="n-input w-80" v-model="obj.area" placeholder="float: Area in km2" />
        </div>

        <div class="mb-2">
          <div class="font-bold">Population:</div>
          <input type="number" class="n-input w-80" v-model="obj.population" placeholder="int: Population of zone" />
        </div>

        <div class="mb-2">
          <div class="font-bold">Population year:</div>
          <input type="number" class="n-input w-80" v-model="obj.population_year" placeholder="int: The year of population count" />
        </div>

        <div class="mb-2">
          <div class="font-bold">Type:</div>
          <n-select v-model="obj.type_id" class="w-80">
            <n-option v-for="a in types" :key="a.value" :value="a.value" :label="a.label" />
          </n-select>
        </div>

        <div class="mb-4">
          <div class="font-bold">Authority:</div>
          <n-select v-model="obj.authority_id" class="w-80">
            <n-option v-for="a in authorities" :key="a.value" :value="a.value" :label="a.label" />
          </n-select>
        </div>

        <div class="flex-1 mb-2 flex flex-col">
          <div class="flex justify-between">
            <div class="font-bold">Zone:</div>
            <div>
              <icon-code v-if="showMap" class="cursor-pointer text-nord15" @click="toggleMap" />
              <icon-map v-if="!showMap" class="cursor-pointer text-nord15" @click="toggleMap" />
            </div>
          </div>
          <div v-show="showMap" class="h-full border border-nord4" id="map-add"></div>
          <textarea
            v-show="!showMap"
            v-model="obj.geojson"
            class="n-input w-80 h-full"
            placeholder='{ 
  "type": "MultiPolygon",
  "crs":{"type":"name","properties":{"name":"EPSG:4258"}},
  "coordinates": [
    [[[102.0, 2.0], [103.0, 2.0], [103.0, 3.0], [102.0, 3.0], [102.0, 2.0]]],
    [[[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]],
    [[100.2, 0.2], [100.8, 0.2], [100.8, 0.8], [100.2, 0.8], [100.2, 0.2]]]
  ]
  }
            '
          ></textarea>
        </div>
      </div>
      <div class="flex justify-between">
        <button class="n-button outline outline-2 outline-nord14" @click="save">Update</button>
        <button class="n-button outline outline-2 outline-nord11" @click="close">Cancel</button>
      </div>
    </div>
  </side-bar>
</template>
<style></style>
