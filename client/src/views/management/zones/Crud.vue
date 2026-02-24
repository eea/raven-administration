<script setup>
import { computed, ref, watch, nextTick } from "vue";
import Popup from "../../../components/Popup.vue";
import { LMap, LTileLayer, LGeoJson } from "@vue-leaflet/vue-leaflet";
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

const emit = defineEmits(["close", "save"]);

const obj = ref({});
const mapRef = ref(null);
const geoJsonRef = ref(null);
let url = "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png";

const geoJsonData = computed(() => {
  if (obj.value.geojson) {
    try {
      return JSON.parse(obj.value.geojson);
    } catch (e) {
      return null;
    }
  }
  return null;
});

const geoJsonOptions = {
  style: {
    color: "#ff0000",
    fillColor: "#ff0000",
    weight: 1
  }
};

watch(
  () => props.show,
  () => {
    if (!props.selectedValue) {
      obj.value = props.options.properties.reduce((a, v) => ({ ...a, [v.prop]: v.default }), {});
    } else {
      obj.value = Object.assign({}, props.selectedValue);
    }

    if (props.show) {
      // Wait for popup and map to be rendered
      setTimeout(() => {
        if (mapRef.value?.leafletObject) {
          mapRef.value.leafletObject.invalidateSize();
          fitBounds();
        }
      }, 100);
    }
  }
);

watch(geoJsonData, () => {
  if (props.show) {
    nextTick(() => {
      setTimeout(() => {
        if (mapRef.value?.leafletObject) {
          mapRef.value.leafletObject.invalidateSize();
          fitBounds();
        }
      }, 100);
    });
  }
});

const onMapReady = () => {
  if (mapRef.value?.leafletObject) {
    mapRef.value.leafletObject.invalidateSize();
    fitBounds();
  }
};

const fitBounds = () => {
  if (mapRef.value && geoJsonRef.value && geoJsonData.value) {
    const leafletObject = geoJsonRef.value.leafletObject;
    if (leafletObject && leafletObject.getBounds) {
      mapRef.value.leafletObject.fitBounds(leafletObject.getBounds());
    }
  }
};

const handleSave = () => {
  emit("save", Object.assign({}, obj.value));
};

const handleClose = () => {
  emit("close");
};
</script>

<template>
  <popup :show="show" :title="isEdit ? 'Edit Zone' : 'Create Zone'" @on-close="handleClose" class="max-w-[60rem] w-[60rem]">
    <!-- Content Section with Scrollbar -->
    <div class="overflow-y-auto pr-2 max-h-[60vh]">
      <div class="mb-4 font-bold text-base border-b border-nord4">Required</div>

        <div class="mb-2" v-for="p in props.options.properties">
          <div v-if="!p.enableInEdit && p.type != 'gridOnly' && isEdit">
            <div class="font-bold">{{ p.label }}:</div>
            <input class="input w-full" v-model="obj[p.prop]" :disabled="true" />
          </div>

          <div v-else>
            <div v-if="p.type == 'text' || p.type == 'number'">
              <div class="font-bold">{{ p.label }}:</div>
              <input :type="p.type" class="input w-full" v-model="obj[p.prop]" :placeholder="p.placeholder" />
            </div>
            <div v-else-if="p.type == 'lookup'">
              <div class="font-bold">{{ p.label }}:</div>
              <select v-model="obj[p.prop_id]" class="select w-full">
                <option v-for="p in options.lookups[p.lookup]" :key="p.value" :value="p.value">{{ p.label }}</option>
              </select>
            </div>
          </div>
        </div>

        <div class="mb-2 flex flex-col h-96">
          <div class="font-bold">Preview:</div>
          <div class="border border-nord4 h-full w-full flex-1">
            <LMap ref="mapRef" :zoom="3" :center="[0, 0]" :options="{ zoomControl: true, attributionControl: false }" @ready="onMapReady">
              <LTileLayer :url="url" />
              <LGeoJson v-if="geoJsonData" ref="geoJsonRef" :geojson="geoJsonData" :options="geoJsonOptions" />
            </LMap>
          </div>
        </div>
      </div>

    <!-- Footer Section (Always Visible) -->
    <div class="border-t border-gray-300 mt-4"></div>
    <div class="flex justify-end pt-2 gap-4">
      <button class="button" @click="handleSave">Save</button>
      <button class="button" @click="handleClose">Cancel</button>
    </div>
  </popup>
</template>

<style></style>
