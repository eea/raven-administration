<script setup>
import { ref, watch, computed, nextTick } from "vue";
import Popup from "../../../components/Popup.vue";
import { LMap, LGeoJson } from "@vue-leaflet/vue-leaflet";
import { addBasemap } from "../../../helpers/basemap";
import "leaflet/dist/leaflet.css";
import Service from "./service";

const props = defineProps({
  show:            { type: Boolean },
  isEdit:          { type: Boolean },
  options:         { type: Object },
  selectedValue:   { type: Object, default: null },
  duplicateSource: { type: Object, default: null }
});

const emit = defineEmits(["close", "save"]);

const ACCEPT     = ".geojson,.json,.gpkg,.shp,.zip,.parquet,.geoparquet,.tif,.tiff";
const MAX_PREVIEW = 2000;

const obj           = ref({});
const sourceEpsg    = ref(4326);
const fileInputRef  = ref(null);
const mapRef        = ref(null);
const geoJsonRef    = ref(null);
const parsing       = ref(false);
const previewPoints = ref([]);   // [{x, y}] in WGS84: a sample to draw, not the area
const totalPoints   = ref(0);
const truncated     = ref(false);
// The last file picked, kept so a change of Spatial Resolution can parse it again:
// polygons and lines are filled with cells of that size.
const lastFile      = ref(null);
// The parsed file, staged on the server with every point. The save sends this, not
// the preview, so an area is saved whole however large.
const uploadToken   = ref(null);
// Whether the user typed the SRS Application Id. Until then it follows the SRS Id and
// the application, as <SRSId>_spo / <SRSId>_exc -- what the API derives too.
const appIdTouched  = ref(false);
const SUFFIX = { spo_sr: "spo", exc_sr: "exc" };

const isExternal = computed(() => obj.value.result_encoding_id === "external");

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
    // Duplicate: everything but the key, which is derived again -- usually for the
    // same area's other application.
    const { srs_application_id, point_count, created_at, ...rest } = props.duplicateSource;
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
  lastFile.value      = null;
  uploadToken.value   = null;
  appIdTouched.value  = props.isEdit;
  if (fileInputRef.value) fileInputRef.value.value = "";

  // Load the existing application (with a sample of its cells) to edit or duplicate
  const loadId = props.isEdit ? props.selectedValue?.srs_application_id
                              : props.duplicateSource?.srs_application_id;
  if (props.show && loadId) {
    try {
      const record = await Service.getById(loadId);
      if (record.points?.length) {
        previewPoints.value = record.points;
        totalPoints.value   = record.point_count ?? record.points.length;
        truncated.value     = !!record.sampled;
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
    addBasemap(mapRef.value.leafletObject);
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
  lastFile.value = file;
  await parse(file);
};

const parse = async (file) => {
  parsing.value       = true;
  previewPoints.value = [];
  totalPoints.value   = 0;
  truncated.value     = false;
  try {
    const form = new FormData();
    form.append("file", file);
    form.append("source_epsg", sourceEpsg.value);
    form.append("spatial_resolution", obj.value.spatial_resolution ?? "");
    const result = await Service.parseFile(form);
    previewPoints.value = result.points;
    uploadToken.value   = result.upload_token;
    totalPoints.value   = result.total;
    truncated.value     = result.truncated;
  } catch {
    // Request() has already shown the API's reason, e.g. "choose the resolution first".
    if (fileInputRef.value) fileInputRef.value.value = "";
  } finally {
    parsing.value = false;
  }
};

// The cells an area covers depend on their size, so a new resolution re-reads the
// file. Points and rasters come back the same; the insert snaps them either way.
watch(() => obj.value.spatial_resolution, (now, before) => {
  if (lastFile.value && now && now !== before && !parsing.value) parse(lastFile.value);
});

watch(() => [obj.value.srs_id, obj.value.srs_application], ([srsId, application]) => {
  if (appIdTouched.value || !srsId || !SUFFIX[application]) return;
  obj.value.srs_application_id = `${srsId}_${SUFFIX[application]}`;
});

const onFieldInput = (p) => {
  if (p.prop === "srs_application_id") appIdTouched.value = true;
};

const title = computed(() => props.isEdit ? "Edit Spatial Representativeness" : "Add Spatial Representativeness");

// A property may apply only to one encoding: the GeoTIFF Attachment to external areas.
const applies = (p) => !p.encoding || p.encoding === (obj.value.result_encoding_id || "inline");

const formProps = computed(() =>
  props.options?.properties?.filter((p) => p.type !== "gridOnly" && p.type !== "numeric" && applies(p)) ?? []
);
const requiredProps = computed(() => formProps.value.filter((p) => p.required));
const optionalProps = computed(() => formProps.value.filter((p) => !p.required));

const isFormValid = computed(() => {
  const metaValid = requiredProps.value.every((p) => {
    const v = obj.value[p.prop_id ?? p.prop];
    return v !== null && v !== undefined && v !== "";
  });
  // An inline area needs cells: a new file, the ones it has (edit), or the source's
  // (Duplicate). An external one is its GeoTIFF, which is a required field above.
  const areaValid = isExternal.value || props.isEdit || previewPoints.value.length > 0;
  return metaValid && areaValid && !parsing.value;
});

// The area travels by reference: a new file by its upload token, a Duplicate by the
// application it copies. With neither, an edit keeps its stored cells. An external
// area has no cells, so it sends neither.
const handleSave = () => {
  const { points, ...values } = obj.value;
  if (!isExternal.value) {
    if (uploadToken.value) values.upload_token = uploadToken.value;
    else if (props.duplicateSource) values.copy_cells_from = props.duplicateSource.srs_application_id;
  }
  emit("save", values);
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
            v-model="obj[p.prop]" :disabled="isEdit && !p.enableInEdit"
            :placeholder="p.placeholder" @input="onFieldInput(p)" />
          <select v-else-if="p.type === 'lookup'" class="select w-full" v-model="obj[p.prop_id]">
            <option v-for="opt in options.lookups[p.lookup]" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
          </select>
          <div v-if="p.help" class="text-xs text-nord3 mt-0.5">{{ p.help }}</div>
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

      <!-- Area: inline grid cells. An external area is its GeoTIFF Attachment instead. -->
      <div v-if="isExternal" class="border-t border-nord4 pt-3 text-xs text-nord3">
        An external area is reported as the GeoTIFF named above (AQR3 SRE), which you upload
        to Reportnet3 yourself. It has no grid cells here; choose Result Encoding "inline"
        to upload the area as cells instead.
      </div>
      <div v-else class="border-t border-nord4 pt-3">
        <div class="font-bold text-base mb-3">
          Area (grid cells)
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
            <span v-if="truncated" class="text-nord3 text-xs">(the map shows {{ previewPoints.length.toLocaleString() }} of them; all are saved)</span>
          </span>
          <span v-else-if="!parsing && !isEdit" class="text-nord11 text-sm">No file selected</span>
        </div>
        <div class="text-xs text-nord3 mb-3">GeoJSON · GeoPackage · Shapefile (.shp or .zip) · GeoParquet · GeoTIFF → stored as EPSG:3035.
          Polygons and lines are filled with grid cells of the chosen Spatial Resolution, so choose it first.</div>

        <!-- Map preview -->
        <div v-if="previewGeoJson" class="flex flex-col h-64 border border-nord4">
          <div class="font-bold text-xs px-2 py-1 border-b border-nord4 text-nord3">Preview</div>
          <div class="flex-1">
            <LMap ref="mapRef" :zoom="4" :center="[52, 10]"
              :options="{ zoomControl: true, attributionControl: false }"
              :use-global-leaflet="true" @ready="onMapReady">
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