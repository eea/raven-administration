<script setup>
import { computed, ref, watch } from "vue";
import Popup from "../../../components/Popup.vue";
import Eventy from "../../../helpers/eventy";
import Service from "./service";
import IconUpload from "~icons/material-symbols/upload-file-outline";

const props = defineProps({
  show: Boolean,
  model: { type: Object, default: null },
  lookups: { type: Object, default: () => ({}) },
});

const emit = defineEmits(["close", "uploaded"]);

const ACCEPT = ".tif,.tiff";

const fileInputRef = ref(null);
const file = ref(null);
const uploading = ref(false);
const result = ref(null);

const form = ref({});

const blank = () => ({
  spatial_resolution: null,
  start: "",
  end: "",
  // Default to the model's own aggregation process and pollutant: results almost
  // always belong to the model that produced them.
  data_aggregation_process_id: props.model?.data_aggregation_process_id ?? null,
  pollutant_id: props.model?.pollutant_id ?? null,
  unit_id: null,
  validity_id: null,
});

const canUpload = computed(() =>
  !!file.value &&
  !!form.value.spatial_resolution &&
  !!form.value.start &&
  !!form.value.data_aggregation_process_id);

const onFileChange = (event) => {
  file.value = event.target.files?.[0] ?? null;
  result.value = null;
};

const onUpload = async () => {
  if (!canUpload.value) return;
  uploading.value = true;
  result.value = null;
  try {
    const data = new FormData();
    data.append("file", file.value);
    for (const [key, value] of Object.entries(form.value)) {
      // Only the four required fields are always sent; an empty optional must be
      // absent rather than "", which the backend would treat as provided.
      if (value !== null && value !== "") data.append(key, value);
    }
    result.value = await Service.uploadResults(props.model.id, data);
    Eventy.showHideMessage(result.value?.msg ?? "Results uploaded.", "success", 4000);
    emit("uploaded");
  } catch {
    // Request already surfaced the server message.
  } finally {
    uploading.value = false;
  }
};

watch(() => props.show, (visible) => {
  if (visible) {
    form.value = blank();
    file.value = null;
    result.value = null;
    if (fileInputRef.value) fileInputRef.value.value = "";
  }
});
</script>

<template>
  <popup :show="show" :title="`Upload gridded results — ${model?.id ?? ''}`"
         @on-close="emit('close')" class="max-w-2xl w-full">

    <p class="text-xs text-nord3 mb-3">
      Loads one timestep of modelled results (AQR3 MRI) from a GeoTIFF. Pixel values are
      reprojected from the raster's own CRS and snapped to the EEA INSPIRE grid in EPSG:3035;
      several pixels falling in one cell are averaged. Re-uploading the same timestep and
      aggregation process replaces the previous cells.
    </p>

    <div class="grid grid-cols-2 gap-3 mb-3">
      <div class="col-span-2">
        <label class="block text-xs font-semibold text-nord3 mb-1">
          GeoTIFF <span class="text-nord11">*</span>
        </label>
        <div class="flex items-center gap-2">
          <button class="button" @click="fileInputRef?.click()">
            <span class="flex items-center gap-1.5">
              <icon-upload class="text-base" /> Choose file
            </span>
          </button>
          <span class="text-sm text-nord3 truncate">{{ file?.name ?? "No file chosen" }}</span>
        </div>
        <input ref="fileInputRef" type="file" :accept="ACCEPT" class="hidden"
               @change="onFileChange" />
      </div>

      <div>
        <label class="block text-xs font-semibold text-nord3 mb-1">
          Spatial resolution <span class="text-nord11">*</span>
        </label>
        <select v-model="form.spatial_resolution" class="input w-full text-sm">
          <option :value="null">— select —</option>
          <option v-for="o in lookups.spatial_resolutions" :key="o.value" :value="o.value">
            {{ o.label }} m
          </option>
        </select>
      </div>

      <div>
        <label class="block text-xs font-semibold text-nord3 mb-1">
          Aggregation process <span class="text-nord11">*</span>
        </label>
        <select v-model="form.data_aggregation_process_id" class="input w-full text-sm">
          <option :value="null">— select —</option>
          <option v-for="o in lookups.aggregation_processes" :key="o.value" :value="o.value">
            {{ o.label }}
          </option>
        </select>
      </div>

      <div>
        <label class="block text-xs font-semibold text-nord3 mb-1">
          Start <span class="text-nord11">*</span>
        </label>
        <input type="datetime-local" v-model="form.start" class="input w-full text-sm" />
      </div>

      <div>
        <label class="block text-xs font-semibold text-nord3 mb-1">End</label>
        <input type="datetime-local" v-model="form.end" class="input w-full text-sm" />
      </div>

      <div>
        <label class="block text-xs font-semibold text-nord3 mb-1">Pollutant</label>
        <select v-model="form.pollutant_id" class="input w-full text-sm">
          <option :value="null">— none —</option>
          <option v-for="o in lookups.pollutants" :key="o.value" :value="o.value">{{ o.label }}</option>
        </select>
      </div>

      <div>
        <label class="block text-xs font-semibold text-nord3 mb-1">Unit</label>
        <select v-model="form.unit_id" class="input w-full text-sm">
          <option :value="null">— none —</option>
          <option v-for="o in lookups.units" :key="o.value" :value="o.value">{{ o.label }}</option>
        </select>
      </div>

      <div>
        <label class="block text-xs font-semibold text-nord3 mb-1">Validity</label>
        <select v-model="form.validity_id" class="input w-full text-sm">
          <option :value="null">— none —</option>
          <option v-for="o in lookups.validities" :key="o.value" :value="o.value">{{ o.label }}</option>
        </select>
      </div>
    </div>

    <div v-if="result" class="mb-3 p-2 rounded bg-nord14/10 text-sm text-nord3">
      Stored <span class="font-semibold">{{ result.cells }}</span> grid cell(s) at
      {{ result.spatial_resolution }} m, EPSG:{{ result.srid }}.
    </div>

    <div class="flex justify-end pt-2 gap-4">
      <button class="button" :disabled="uploading || !canUpload" @click="onUpload">
        {{ uploading ? "Uploading…" : "Upload" }}
      </button>
      <button class="button" @click="emit('close')">Close</button>
    </div>

  </popup>
</template>
