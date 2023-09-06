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
    layers.push(marker([station.y, station.x]).bindPopup("<b>" + station.station + "</b><br>" + station.timeseries.map((p) => p.pollutant).join(", ")));
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
