<script setup>
// import { featureGroup, map, tileLayer, marker } from "leaflet";
import "leaflet/dist/leaflet.css";
import { LMap, LTileLayer, LCircleMarker, LTooltip } from "@vue-leaflet/vue-leaflet";

import { onMounted } from "vue";
import Service from "./service";
var mymap;
let url = "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png";
const map = ref(null);
const markerRefs = ref([]);
const stations = ref([]);
const legend = ref([]);

onMounted(async () => {
  stations.value = await Service.get();
  legend.value = await Service.legend();
  init();
});

const init = () => {
  fit(stations.value.map((s) => [s.y, s.x]));
};

const fit = (latlng) => {
  if (map) map.value.leafletObject.fitBounds(latlng, { padding: [100, 100] });
};

const hexByAqi = (aqi) => {
  const entry = legend.value.find((l) => l.index === aqi);
  return entry ? entry.color : "gray";
};

const rectByAqi = (aqi) => {
  if (aqi == 0) return;
  var hex = hexByAqi(aqi);

  return {
    backgroundColor: hex,
    borderColor: hex,
    borderWidth: "1px",
    backgroundColor: hex + "BB",
    borderColor: hex,
    borderStyle: "solid"
  };
};
</script>

<template>
  <common-layout>
    <tool-bar title="Map" :show-column-picker="false" :show-add="false" :show-download="false" :show-filter="false" />
    <div class="border border-nord4 h-full w-full flex-1">
      <LMap ref="map" :zoom="2" :center="[0, 0]" :options="{ zoomControl: false, attributionControl: false }" class="relative">
        <LTileLayer :url="url" attribution="" layer-type="base" />

        <LCircleMarker :name="station.name" :radius="12" v-for="station in stations" :lat-lng="[station.y, station.x]" :color="hexByAqi(station.aqi)" :fill-opacity="0.4" :weight="2" ref="markerRefs">
          <l-tooltip :options="{ interactive: true, offset: [15, 0], className: 'map-tooltip' }">
            <div class="font-bold text-xl">{{ station.name }}</div>
            <div class="text-base">{{ station.network }}</div>
            <div class="w-full border-t border-gray-400 mt-2"></div>
            <table class="text-sm mt-2 w-full border-spacing-2">
              <tr v-for="timeserie in station.timeseries">
                <td class=""><div class="w-4 h-4 rounded-full" :style="rectByAqi(timeserie.aqi)"></div></td>
                <td class="font-bold pr-3 pl-1">{{ timeserie.pollutant }}</td>
                <td class="px-6">{{ timeserie.timestep }}</td>
                <td class="px-3">{{ timeserie.value }}</td>
                <td>{{ timeserie.unit }}</td>
              </tr>
            </table>
          </l-tooltip>
        </LCircleMarker>
        <div class="absolute left-5 bottom-5 z-[888] flex gap-3 shadow border border-nord4 bg-white p-2">
          <div class="font-bold self-center" v-if="legend.length > 0">{{ legend[0].description }}</div>
          <div v-for="item in legend" class="w-8 h-8 rounded-full flex items-center justify-center" :style="rectByAqi(item.index)" v-tooltip="item.description"></div>
          <!-- <div class="w-full text-center font-bold text-xs">{{ item.description }}</div> -->
          <div class="font-bold self-center" v-if="legend.length > 0">{{ legend[legend.length - 1].description }}</div>
        </div>
      </LMap>
    </div>
  </common-layout>
</template>

<style>
.map-tooltip {
  @apply bg-gray-100 text-gray-600 flex flex-col gap-0  px-4;
}
</style>
