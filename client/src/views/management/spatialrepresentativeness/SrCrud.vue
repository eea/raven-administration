<script setup>
import { ref, watch, computed, nextTick } from "vue";
import Popup from "../../../components/Popup.vue";
import { LMap, LTileLayer, LGeoJson } from "@vue-leaflet/vue-leaflet";
import "leaflet/dist/leaflet.css";
import Service from "./service";
import Eventy from "../../../helpers/eventy";

const props = defineProps({
  show:            { type: Boolean },
  isEdit:          { type: Boolean },
  options:         { type: Object },
  selectedValue:   { type: Object, default: null },
  duplicateSource: { type: Object, default: null }
});

const emit = defineEmits(["close", "save"]);

const ACCEPT     = ".geojson,.json,.gpkg,.shp,.zip,.parquet,.geoparquet,.tif,.tiff";
const MAP_URL    = "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png";
const MAX_PREVIEW = 2000;

const obj           = ref({});
const sourceEpsg    = ref(4326);
const fileInputRef  = ref(null);
const mapRef        = ref(null);
const geoJsonRef    = ref(null);
const parsing       = ref(false);
const previewPoints = ref([]);   // [{x, y}] in WGS84
const totalPoints   = ref(0);
const truncated     = ref(false);

// GeoJSON FeatureCollection for Leaflet — limit to MAX_PREVIEW points
const previewGeoJson = computed(() => {
  const pts = previewPoints.value.slice(0, MAX_PREVIEW);
  if (!pts.length) return null;
  return {
    type: "FeatureCollection",
    features: pts.map(p => ({
      type: "Feature",
      geometry: { type: "Point", coordinates: [p.x, p.y] }
    }))
  };
});

watch(() => props.show, async () => {
  if (props.duplicateSource) {
    // Duplicate: pre-fill everything from source except id
    const { id, point_count, created_at, ...rest } = props.duplicateSource;
    obj.value = { ...rest };
  } else if (!props.selectedValue) {
    obj.value = props.options.properties.reduce((a, v) => ({ ...a, [v.prop]: v.default }), {});
  } else {
    obj.value = Object.assign({}, props.selectedValue);
  }
  sourceEpsg.value    = 4326;
  previewPoints.value = [];
  totalPoints.value   = 0;
  truncated.value     = false;
  if (fileInputRef.value) fileInputRef.value.value = "";

  // Load existing record (with points) in edit mode or duplicate
  const loadId = props.isEdit ? props.selectedValue?.id : props.duplicateSource?.id;
  if (props.show && loadId) {
    try {
      const record = await Service.getById(loadId);
      if (record.points?.length) {
        previewPoints.value = record.points;
        totalPoints.value   = record.points.length;
        if (record.spatial_resolution) obj.value.spatial_resolution = record.spatial_resolution;
        fitBoundsAfterRender();
      }
    } catch { /* non-fatal */ }
  }
});

watch(previewGeoJson, () => {
  if (previewGeoJson.value) fitBoundsAfterRender();
});

const fitBoundsAfterRender = () => {
  nextTick(() => setTimeout(() => {
    if (mapRef.value?.leafletObject) {
      mapRef.value.leafletObject.invalidateSize();
      fitBounds();
    }
  }, 150));
};

const onMapReady = () => {
  if (mapRef.value?.leafletObject) {
    mapRef.value.leafletObject.invalidateSize();
    fitBounds();
  }
};

const fitBounds = () => {
  if (mapRef.value && geoJsonRef.value && previewGeoJson.value) {
    const lObj = geoJsonRef.value.leafletObject;
    if (lObj?.getBounds) {
      const bounds = lObj.getBounds();
      if (bounds.isValid()) mapRef.value.leafletObject.fitBounds(bounds, { padding: [20, 20] });
    }
  }
};

const triggerFileInput = () => fileInputRef.value?.click();

const onFileChange = async (e) => {
  const file = e.target.files[0];
  if (!file) return;
  parsing.value       = true;
  previewPoints.value = [];
  totalPoints.value   = 0;
  truncated.value     = false;
  try {
    const form = new FormData();
    form.append("file", file);
    form.append("source_epsg", sourceEpsg.value);
    const result = await Service.parseFile(form);
    previewPoints.value = result.points;
    totalPoints.value   = result.total;
    truncated.value     = result.truncated;
  } catch {
    Eventy.showHideMessage("Failed to parse spatial file.", "error", 5000);
    if (fileInputRef.value) fileInputRef.value.value = "";
  } finally {
    parsing.value = false;
  }
};

const title = computed(() => props.isEdit ? "Edit Spatial Representativeness" : "Add Spatial Representativeness");

const requiredProps = computed(() =>
  props.options?.properties?.filter((p) => p.required && p.type !== "gridOnly" && p.type !== "numeric") ?? []
);
const optionalProps = computed(() =>
  props.options?.properties?.filter((p) => !p.required && p.type !== "gridOnly" && p.type !== "numeric") ?? []
);

const isFormValid = computed(() => {
  const metaValid = requiredProps.value.every((p) => {
    const v = obj.value[p.prop_id ?? p.prop];
    return v !== null && v !== undefined && v !== "";
  });
  const pointsValid = props.isEdit || previewPoints.value.length > 0;
  return metaValid && pointsValid && !parsing.value;
});

const handleSave = () => {
  emit("save", {
    ...obj.value,
    points: previewPoints.value
  });
};

const geoJsonStyle = { color: "#5e81ac", weight: 0, fillColor: "#5e81ac", fillOpacity: 0.8, radius: 3 };
const pointToLayer = (_, latlng) => {
  const L = window.L;
  return L ? L.circleMarker(latlng, { radius: 3, color: "#5e81ac", fillColor: "#5e81ac", fillOpacity: 0.8, weight: 0 }) : undefined;
};
</script>

<template>
  <Popup :show="show" :title="title" @on-close="$emit('close')" class="max-w-[52rem] w-[52rem]">
    <div class="overflow-y-auto pr-2 max-h-[75vh] flex flex-col gap-4">

      <!-- Metadata fields -->
      <div>
        <div class="font-bold text-base border-b border-nord4 mb-3">Details</div>
        <div v-for="p in requiredProps" :key="p.prop" class="mb-2">
          <div class="font-bold">{{ p.label }}</div>
          <input v-if="p.type === 'text'" type="text" class="input w-full"
            v-model="obj[p.prop]" :disabled="isEdit && !p.enableInEdit" />
          <select v-else-if="p.type === 'lookup'" class="select w-full" v-model="obj[p.prop_id]">
            <option v-for="opt in options.lookups[p.lookup]" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
          </select>
        </div>
        <div v-for="p in optionalProps" :key="p.prop" class="mb-2">
          <div class="font-bold">{{ p.label }} <span class="text-nord3 font-normal text-xs">(optional)</span></div>
          <input v-if="p.type === 'text'" type="text" class="input w-full"
            v-model="obj[p.prop]" :disabled="isEdit && !p.enableInEdit" />
          <select v-else-if="p.type === 'lookup'" class="select w-full" v-model="obj[p.prop_id]">
            <option value="">—</option>
            <option v-for="opt in options.lookups[p.lookup]" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
          </select>
        </div>
      </div>

      <!-- Points section -->
      <div class="border-t border-nord4 pt-3">
        <div class="font-bold text-base mb-3">
          Area points
          <span v-if="isEdit" class="text-nord3 font-normal text-xs">(upload new file to replace)</span>
          <span v-else class="text-nord11 font-normal text-xs">*</span>
        </div>

        <!-- Import utility: EPSG + file button inline -->
        <div class="flex items-center gap-3 mb-1 flex-wrap">
          <select class="select text-sm" v-model="sourceEpsg">
            <option :value="4326">EPSG:4326 (WGS84)</option>
            <option :value="4258">EPSG:4258 (ETRS89)</option>
            <option :value="3035">EPSG:3035 (LAEA Europe)</option>
          </select>
          <input ref="fileInputRef" type="file" :accept="ACCEPT" @change="onFileChange" class="hidden" />
          <button type="button" class="button" @click="triggerFileInput" :disabled="parsing">
            {{ parsing ? "Parsing…" : "Upload spatial file" }}
          </button>
          <span v-if="previewPoints.length" class="text-nord14 text-sm">
            ✓ {{ totalPoints.toLocaleString() }} points
            <span v-if="truncated" class="text-nord3 text-xs">(preview capped at {{ previewPoints.length.toLocaleString() }})</span>
          </span>
          <span v-else-if="!parsing && !isEdit" class="text-nord11 text-sm">No file selected</span>
        </div>
        <div class="text-xs text-nord3 mb-3">GeoJSON · GeoPackage · Shapefile (.shp or .zip) · GeoParquet · GeoTIFF → stored as EPSG:3035</div>

        <!-- Map preview -->
        <div v-if="previewGeoJson" class="flex flex-col h-64 border border-nord4">
          <div class="font-bold text-xs px-2 py-1 border-b border-nord4 text-nord3">Preview</div>
          <div class="flex-1">
            <LMap ref="mapRef" :zoom="4" :center="[52, 10]"
              :options="{ zoomControl: true, attributionControl: false }"
              @ready="onMapReady">
              <LTileLayer :url="MAP_URL" />
              <LGeoJson ref="geoJsonRef" :geojson="previewGeoJson"
                :options="{ pointToLayer, style: () => geoJsonStyle }" />
            </LMap>
          </div>
        </div>
      </div>

    </div>

    <div class="border-t border-gray-300 mt-4"></div>
    <div class="flex justify-end pt-2 gap-4">
      <button class="button" @click="handleSave" :disabled="!isFormValid">Save</button>
      <button class="button" @click="$emit('close')">Cancel</button>
    </div>
  </Popup>
</template>