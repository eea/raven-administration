<script setup>
import { geoJSON, map, tileLayer } from "leaflet";
import "leaflet/dist/leaflet.css";

const props = defineProps({
  show: Boolean,
  isEdit: Boolean,
  options: Object,
  selectedValue: {
    type: Object,
    default: null
  }
});

const obj = ref({});

var mymap;
var zoneLayer;
let url = "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png";

watch(
  () => props.show,
  () => {
    if (!props.selectedValue) {
      obj.value = props.options.properties.reduce((a, v) => ({ ...a, [v.prop]: v.default }), {});
    } else {
      obj.value = Object.assign({}, props.selectedValue);
    }

    initMap();
  }
);

const initMap = () => {
  if (mymap) mymap.remove();
  mymap = map("map").setView([0, 0], 3);
  tileLayer(url, {}).addTo(mymap);
  if (mymap && obj.value.geojson) {
    if (zoneLayer) mymap.removeLayer(zoneLayer);
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
</script>

<template>
  <side-bar-crud :show="show" @cancel="$emit('close')" @commit="$emit('save', Object.assign({}, obj))">
    <div class="mb-4 font-bold text-base border-b">Required</div>

    <div class="mb-2" v-for="p in props.options.properties">
      <div v-if="!p.enableInEdit && p.type != 'gridOnly' && isEdit">
        <div class="font-bold">{{ p.label }}:</div>
        <input class="n-input w-[40rem]" v-model="obj[p.prop]" :disabled="true" />
      </div>

      <div v-else>
        <div v-if="p.type == 'text' || p.type == 'number'">
          <div class="font-bold">{{ p.label }}:</div>
          <input :type="p.type" class="n-input w-[40rem]" v-model="obj[p.prop]" :placeholder="p.placeholder" />
        </div>
        <div v-else-if="p.type == 'lookup'">
          <div class="font-bold">{{ p.label }}:</div>
          <n-select v-model="obj[p.prop_id]" class="!w-[40rem]">
            <n-option v-for="p in options.lookups[p.lookup]" :key="p.value" :value="p.value" :label="p.label" />
          </n-select>
        </div>
      </div>
    </div>
    <div class="flex-1 mb-2 flex flex-col">
      <div class="font-bold">Preview:</div>
      <div class="border border-nord4 h-full w-full flex-1" id="map"></div>
    </div>
  </side-bar-crud>
</template>

<style></style>
