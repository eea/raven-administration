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
const fileInput = ref(null);
const sourceEpsg = ref(4326);
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

const handleFileUpload = async (event) => {
  const file = event.target.files[0];
  if (file) {
    try {
      const text = await file.text();
      const json = JSON.parse(text);
      
      // Extract geometry from GeoJSON
      let geometry;
      if (json.type === 'FeatureCollection' && json.features && json.features.length > 0) {
        // Take the first feature's geometry
        geometry = json.features[0].geometry;
      } else if (json.type === 'Feature' && json.geometry) {
        // Single feature
        geometry = json.geometry;
      } else if (json.type && json.coordinates) {
        // Already a geometry object
        geometry = json;
      } else {
        alert("Invalid GeoJSON format. Must be a FeatureCollection, Feature, or Geometry.");
        return;
      }
      
      obj.value.geojson = JSON.stringify(geometry);
    } catch (error) {
      alert("Error reading GeoJSON file: " + error.message);
    }
  }
};

const triggerFileInput = () => {
  fileInput.value.click();
};

const handleSave = () => {
  const data = Object.assign({}, obj.value);
  data.source_epsg = sourceEpsg.value;
  emit("save", data);
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

        <div class="mb-2">
          <div class="font-bold">Geometry (GeoJSON):</div>
          <div class="flex gap-2 items-center mb-2">
            <div class="flex flex-col gap-1">
              <label class="text-sm">Source EPSG Code:</label>
              <select v-model="sourceEpsg" class="select">
                <option :value="4326">EPSG:4326 (WGS84)</option>
                <option :value="4258">EPSG:4258 (ETRS89)</option>
                <option :value="3035">EPSG:3035 (LAEA)</option>
              </select>
            </div>
          </div>
          <div class="flex gap-2 items-center">
            <input 
              ref="fileInput" 
              type="file" 
              accept=".json,.geojson" 
              @change="handleFileUpload" 
              class="hidden"
            />
            <button 
              type="button" 
              class="button bg-nord10 hover:bg-nord10/80" 
              @click="triggerFileInput"
            >
              Upload GeoJSON File
            </button>
            <span v-if="geoJsonData" class="text-nord14 text-sm">
              ✓ Geometry loaded
            </span>
            <span v-else class="text-nord11 text-sm">
              No geometry
            </span>
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
