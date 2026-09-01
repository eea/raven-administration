<script setup>
import { computed, ref, watch } from "vue";
import Popup from "../../../components/Popup.vue";
import Eventy from "../../../helpers/eventy";
import Service from "./service";
import IconAdd from "~icons/material-symbols/add";
import IconEdit from "~icons/material-symbols/edit-outline";
import IconDelete from "~icons/material-symbols/delete-outline";

const props = defineProps({
  show: Boolean,
  model: { type: Object, default: null },
  lookups: { type: Object, default: () => ({}) },
});

const emit = defineEmits(["close", "changed"]);

const rows = ref([]);
const loading = ref(false);
const saving = ref(false);

// null = form closed; {} = adding; otherwise the key being edited.
const editing = ref(null);
const form = ref({});

const BLANK = {
  start_time: "",
  end_time: "",
  data_aggregation_process_id: null,
  pollutant_id: null,
  unit_id: null,
  validity_id: null,
  spatial_resolution: null,
  geotiff_attachment: "",
};

const isNew = computed(() => editing.value !== null && !editing.value.start_time);
const canSave = computed(() =>
  !!form.value.start_time && !!form.value.data_aggregation_process_id);

const load = async () => {
  if (!props.model?.id) return;
  loading.value = true;
  try {
    rows.value = await Service.externalList(props.model.id);
  } catch {
    Eventy.showHideMessage("Failed to load external results.", "error", 4000);
  } finally {
    loading.value = false;
  }
};

const openAdd = () => {
  form.value = {
    ...BLANK,
    data_aggregation_process_id: props.model?.data_aggregation_process_id ?? null,
    pollutant_id: props.model?.pollutant_id ?? null,
  };
  editing.value = {};
};

const openEdit = (row) => {
  form.value = { ...BLANK, ...row };
  editing.value = {
    start_time: row.start_time,
    data_aggregation_process_id: row.data_aggregation_process_id,
  };
};

const onSave = async () => {
  if (!canSave.value) return;
  saving.value = true;
  try {
    const values = { ...form.value };
    // The list carries joined labels for display; they are not columns.
    for (const k of ["data_aggregation_process", "pollutant", "unit", "result_time"]) {
      delete values[k];
    }
    if (isNew.value) {
      await Service.externalInsert(props.model.id, values);
    } else {
      await Service.externalUpdate(props.model.id, editing.value, values);
    }
    editing.value = null;
    await load();
    emit("changed");
    Eventy.showHideMessage("External result saved.", "success", 3000);
  } catch {
    // Request already surfaced the server message (bad filename, key clash, FK).
  } finally {
    saving.value = false;
  }
};

const onDelete = async (row) => {
  if (!confirm(`Delete the external result starting ${row.start_time}?`)) return;
  try {
    await Service.externalDelete(props.model.id, {
      start_time: row.start_time,
      data_aggregation_process_id: row.data_aggregation_process_id,
    });
    await load();
    emit("changed");
    Eventy.showHideMessage("External result deleted.", "success", 3000);
  } catch {
    /* message already shown */
  }
};

watch(() => props.show, (visible) => {
  if (visible) {
    editing.value = null;
    load();
  }
});
</script>

<template>
  <!-- body-class: the table below owns the scrolling, so its horizontal scrollbar
       stays at the visible bottom edge instead of below the full table. -->
  <popup :show="show" :title="`External gridded results — ${model?.id ?? ''}`"
         @on-close="emit('close')" class="max-w-5xl w-full" body-class="flex-1 min-h-0 flex flex-col">

    <p class="text-xs text-nord3 mb-3 shrink-0">
      One row per timestep (AQR3 MRE), each naming a GeoTIFF that carries the values. Unlike
      inline results, the raster is uploaded to Reportnet 3 by you and raven records only the
      file name — so the name here must match the file you attach there.
    </p>

    <div v-if="!editing" class="flex justify-end mb-3 shrink-0">
      <button class="button" @click="openAdd">
        <span class="flex items-center gap-1.5"><icon-add class="text-base" /> Add result</span>
      </button>
    </div>

    <div v-if="editing" class="mb-4 p-3 border border-nord4 rounded bg-white shrink-0">
      <div class="grid grid-cols-3 gap-3 mb-3">
        <div>
          <label class="block text-xs font-semibold text-nord3 mb-1">
            Start <span class="text-nord11">*</span>
          </label>
          <input type="datetime-local" v-model="form.start_time" class="input w-full text-sm" />
          <p class="text-[11px] text-nord3 mt-0.5">Part of the AQR3 key</p>
        </div>
        <div>
          <label class="block text-xs font-semibold text-nord3 mb-1">End</label>
          <input type="datetime-local" v-model="form.end_time" class="input w-full text-sm" />
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
          <p class="text-[11px] text-nord3 mt-0.5">Part of the AQR3 key</p>
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
        <div>
          <label class="block text-xs font-semibold text-nord3 mb-1">Spatial resolution</label>
          <select v-model="form.spatial_resolution" class="input w-full text-sm">
            <option :value="null">— none —</option>
            <option v-for="o in lookups.spatial_resolutions" :key="o.value" :value="o.value">
              {{ o.label }} m
            </option>
          </select>
        </div>
        <div class="col-span-2">
          <label class="block text-xs font-semibold text-nord3 mb-1">GeoTIFF file name</label>
          <input type="text" v-model="form.geotiff_attachment" class="input w-full text-sm"
                 placeholder="e.g. pm10_2024_NO.tif — max 100 chars, .tif or .tiff" />
          <p class="text-[11px] text-nord3 mt-0.5">
            The name of the file you upload to Reportnet 3; raven does not store the raster.
          </p>
        </div>
      </div>
      <div class="flex justify-end pt-2 gap-4">
        <button class="button" :disabled="saving || !canSave" @click="onSave">
          {{ saving ? "Saving…" : "Save" }}
        </button>
        <button class="button" @click="editing = null">Cancel</button>
      </div>
    </div>

    <div v-if="loading" class="text-nord3 text-sm py-4 text-center">Loading…</div>
    <div v-else-if="rows.length === 0" class="text-nord3 text-sm py-4 text-center">
      No external results for this model.
    </div>
    <div v-else class="flex-1 min-h-0 overflow-auto">
      <table class="table w-full text-sm">
        <thead class="sticky top-0 z-10">
          <tr>
            <th class="whitespace-nowrap">Start</th>
            <th class="whitespace-nowrap">End</th>
            <th>Aggregation</th>
            <th>Pollutant</th>
            <th>Unit</th>
            <th>Res. (m)</th>
            <th>GeoTIFF</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in rows" :key="`${r.start_time}|${r.data_aggregation_process_id}`">
            <td class="whitespace-nowrap font-mono text-xs">{{ r.start_time }}</td>
            <td class="whitespace-nowrap font-mono text-xs">{{ r.end_time ?? "—" }}</td>
            <td>{{ r.data_aggregation_process ?? r.data_aggregation_process_id }}</td>
            <td>{{ r.pollutant ?? "—" }}</td>
            <td>{{ r.unit ?? "—" }}</td>
            <td class="font-mono text-xs">{{ r.spatial_resolution ?? "—" }}</td>
            <td class="font-mono text-xs">{{ r.geotiff_attachment ?? "—" }}</td>
            <td class="whitespace-nowrap">
              <button class="text-nord10 hover:text-nord9 mr-2" title="Edit" @click="openEdit(r)">
                <icon-edit class="text-base" />
              </button>
              <button class="text-nord11 hover:opacity-70" title="Delete" @click="onDelete(r)">
                <icon-delete class="text-base" />
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

  </popup>
</template>
