<script setup>
import { geoJSON, map, tileLayer } from "leaflet";
import "leaflet/dist/leaflet.css";

import IconCode from "~icons/ri/file-code-fill";
import IconMap from "~icons/ri/road-map-fill";

const props = defineProps({
  show: Boolean,
  zone: Object,
  authorities: Array,
  types: Array
});

const obj = ref({});
const showMap = ref(true);

var mymap;
var zoneLayer;
let url = "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png";

watch(
  () => props.zone,
  (nv) => {
    obj.value = Object.assign({}, props.zone);
    if (mymap && obj.value.geojson) {
      if (zoneLayer) mymap.removeLayer(zoneLayer);
      showMap.value = true;
      zoneLayer = geoJSON(JSON.parse(obj.value.geojson), {
        style: {
          color: "#ff0000",
          fillColor: "#ff0000",
          weight: 1
        }
      }).addTo(mymap);
      mymap.fitBounds(zoneLayer.getBounds());
    }
  }
);

onMounted(() => {
  initMap();
});

const initMap = () => {
  mymap = map("map").setView([50.378472, 14.970598], 3);
  tileLayer(url, {}).addTo(mymap);
};
</script>

<template>
  <side-bar-crud :show="show" @cancel="$emit('close')" @commit="$emit('save', Object.assign({}, obj))">
    <div class="mb-4 font-bold text-base border-b">Required</div>
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
          <icon-code v-if="showMap" class="cursor-pointer text-nord15" @click="showMap = !showMap" />
          <icon-map v-if="!showMap" class="cursor-pointer text-nord15" @click="showMap = !showMap" />
        </div>
      </div>
      <div v-show="showMap" class="h-full border border-nord4" id="map"></div>
      <textarea v-show="!showMap" v-model="obj.geojson" class="n-input w-80 h-full"></textarea>
    </div>
  </side-bar-crud>
</template>
<style></style>
