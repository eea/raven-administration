<script setup>
// import { featureGroup, map, tileLayer, marker } from "leaflet";
import "leaflet/dist/leaflet.css";
import { LMap, LTileLayer, LCircleMarker, LTooltip } from "@vue-leaflet/vue-leaflet";

import { onMounted, ref, watch } from "vue";
import Service from "./service";
import Eventy from "../../../helpers/eventy";

let url = "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png";
const map = ref(null);
const markerRefs = ref([]);
const stations = ref([]);
const legends = ref([]);
const aqi_type = ref(localStorage.getItem("aqi_type") || "eea");

onMounted(async () => {
  legends.value = await Service.legend();
  await loadStations();
});

watch(aqi_type, (val) => {
  localStorage.setItem("aqi_type", val);
});

const init = () => {
  fit(stations.value.map((s) => [s.y, s.x]));
};

const loadStations = async () => {
  Eventy.showMessage("Loading stations. Please wait", "loading");
  stations.value = await Service.get(aqi_type.value);
  init();
  Eventy.hideMessage();
};

const fit = (latlng) => {
  if (map) map.value.leafletObject.fitBounds(latlng, { padding: [100, 100] });
};

const rectByAqi = (color, hideNoData) => {
  if (hideNoData && color === "#cccccc") return;

  var hex = color || "#cccccc";

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

        <LCircleMarker :name="station.name" :radius="6 + station.aqi" v-for="station in stations" :lat-lng="[station.y, station.x]" :color="station.aqi_color" :fill-opacity="0.7" :weight="2" ref="markerRefs">
          <l-tooltip :options="{ interactive: true, offset: [15, 0], className: 'map-tooltip' }">
            <div class="font-bold text-xl">{{ station.name }}</div>
            <div class="text-base">{{ station.network }}</div>
            <div class="w-full border-t border-gray-400 mt-2"></div>
            <table class="text-sm mt-2 w-full border-spacing-2">
              <tr v-for="timeserie in station.timeseries">
                <td class=""><div class="w-4 h-4 rounded-full" :style="rectByAqi(timeserie.aqi_color, true)"></div></td>
                <td class="font-bold pr-3 pl-1">{{ timeserie.pollutant }}</td>
                <td class="px-6">{{ timeserie.timestep }}</td>
                <td class="px-3">{{ timeserie.value }}</td>
                <td>{{ timeserie.unit }}</td>
              </tr>
            </table>
          </l-tooltip>
        </LCircleMarker>

        <div class="absolute left-5 bottom-20 z-[888] flex gap-3 shadow border border-nord4 bg-white p-2 !flex-col" v-if="legends[aqi_type] && legends[aqi_type].length > 0 && Object.keys(legends).length > 1">
          <div v-if="Object.keys(legends).length > 1" class="flex gap-3">
            <div class="flex items-center gap-1">
              <input v-model="aqi_type" type="radio" value="eea" id="aqi_eea" class="cursor-pointer accent-[#74992e]" @change="loadStations()" />
              <label for="aqi_eea" class="cursor-pointer">EEA AQI</label>
            </div>
            <div class="flex items-center gap-1">
              <input v-model="aqi_type" type="radio" value="local" id="aqi_local" class="cursor-pointer accent-[#74992e]" @change="loadStations()" />
              <label for="aqi_local" class="cursor-pointer">LOCAL AQI</label>
            </div>
          </div>
        </div>

        <div class="absolute left-5 bottom-5 z-[888] flex gap-3 shadow border border-nord4 bg-white p-2 !flex-col" v-if="legends[aqi_type] && legends[aqi_type].length > 0">
          <div class="flex gap-3">
            <div class="font-bold self-center" v-if="legends[aqi_type].length > 0">{{ legends[aqi_type][0].description }}</div>
            <div v-for="item in legends[aqi_type]" class="w-8 h-8 rounded-full flex items-center justify-center" :style="rectByAqi(item.color)" v-tooltip="item.description"></div>
            <div class="font-bold self-center" v-if="legends[aqi_type].length > 0">{{ legends[aqi_type][legends[aqi_type].length - 1].description }}</div>
          </div>
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
