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
  samplingPoint: { type: Object, default: null },
});

const emit = defineEmits(["close"]);

const periods = ref([]);
const defaults = ref(null);
const lookups = ref({ station_areas: [], categories: [] });
const loading = ref(false);
const saving = ref(false);

// null = the form is closed; otherwise the key being edited, or {} for a new period.
const editing = ref(null);
const form = ref({});

const BLANK = {
  location_begin: "", location_end: "",
  station_area_id: null, sampling_point_category_id: null,
  hotspot: null, supersite: null,
  latitude: null, longitude: null, altitude: null,
  inlet_height: null, building_distance: null, kerb_distance: null,
  emission_source_distance: null,
};

const isNew = computed(() => editing.value !== null && !editing.value.location_begin);

// Shown next to each empty field: what the export will actually report, since a
// blank override falls back to the sampling point or its station.
const fallback = (key) => {
  const d = defaults.value;
  if (!d) return "";
  const value = d[key];
  if (value === null || value === undefined || value === "") return "not set";
  if (typeof value === "boolean") return value ? "true" : "false";
  return String(value);
};

const load = async () => {
  if (!props.samplingPoint?.id) return;
  loading.value = true;
  try {
    const [data, lk] = await Promise.all([
      Service.locationList(props.samplingPoint.id),
      Service.locationLookups(),
    ]);
    periods.value = data.periods ?? [];
    defaults.value = data.defaults ?? null;
    lookups.value = lk;
  } catch {
    Eventy.showHideMessage("Failed to load location periods.", "error", 4000);
  } finally {
    loading.value = false;
  }
};

const openAdd = () => {
  // A new period usually starts when the last one ended, so prefill that.
  const latest = periods.value[0];
  form.value = { ...BLANK, location_begin: latest?.location_end ?? "" };
  editing.value = {};
};

const openEdit = (row) => {
  form.value = { ...BLANK, ...row };
  editing.value = { sampling_point_id: props.samplingPoint.id, location_begin: row.location_begin };
};

const onSave = async () => {
  if (!form.value.location_begin) return;
  saving.value = true;
  try {
    const values = { ...form.value, sampling_point_id: props.samplingPoint.id };
    // The list carries joined labels for display; they are not columns.
    delete values.station_area;
    delete values.sampling_point_category;

    if (isNew.value) {
      await Service.locationInsert(values);
    } else {
      await Service.locationUpdate(editing.value, values);
    }
    editing.value = null;
    await load();
    Eventy.showHideMessage("Location period saved.", "success", 3000);
  } catch {
    // Request already surfaces the server message (overlap, access, constraint).
  } finally {
    saving.value = false;
  }
};

const onDelete = async (row) => {
  if (!confirm(`Delete the location period starting ${row.location_begin}?`)) return;
  try {
    await Service.locationDelete({
      sampling_point_id: props.samplingPoint.id,
      location_begin: row.location_begin,
    });
    await load();
    Eventy.showHideMessage("Location period deleted.", "success", 3000);
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
  <popup :show="show" :title="`Location history — ${samplingPoint?.id ?? ''}`"
         @on-close="emit('close')" class="max-w-5xl w-full">

    <p class="text-xs text-nord3 mb-3">
      AQR3 reports one location per period (SPL). A relocation closes the current period and
      opens a new one, so a measurement can be traced to where it was taken. Fields left empty
      fall back to the sampling point and its station — the fallback is shown beside each.
    </p>

    <div v-if="!editing" class="flex justify-end mb-3">
      <button class="flex items-center gap-1.5 px-3 py-1.5 text-sm rounded border border-nord10 text-nord10 hover:bg-nord10/10"
              @click="openAdd">
        <icon-add class="text-base" /> Add period
      </button>
    </div>

    <!-- Add / edit form -->
    <div v-if="editing" class="mb-4 p-3 border border-nord4 rounded bg-white">
      <div class="grid grid-cols-3 gap-3 mb-3">
        <div>
          <label class="block text-xs font-semibold text-nord3 mb-1">
            Location begin <span class="text-nord11">*</span>
          </label>
          <input type="datetime-local" v-model="form.location_begin" class="input w-full text-sm" />
          <p class="text-[11px] text-nord3 mt-0.5">AQR3 SPL_03, part of the key</p>
        </div>
        <div>
          <label class="block text-xs font-semibold text-nord3 mb-1">Location end</label>
          <input type="datetime-local" v-model="form.location_end" class="input w-full text-sm" />
          <p class="text-[11px] text-nord3 mt-0.5">Empty means still current</p>
        </div>
        <div>
          <label class="block text-xs font-semibold text-nord3 mb-1">Station area</label>
          <select v-model="form.station_area_id" class="input w-full text-sm">
            <option :value="null">— {{ fallback('station_area') }} —</option>
            <option v-for="o in lookups.station_areas" :key="o.value" :value="o.value">{{ o.label }}</option>
          </select>
        </div>
        <div>
          <label class="block text-xs font-semibold text-nord3 mb-1">Category</label>
          <select v-model="form.sampling_point_category_id" class="input w-full text-sm">
            <option :value="null">— {{ fallback('sampling_point_category') }} —</option>
            <option v-for="o in lookups.categories" :key="o.value" :value="o.value">{{ o.label }}</option>
          </select>
        </div>
        <div>
          <label class="block text-xs font-semibold text-nord3 mb-1">Hotspot</label>
          <select v-model="form.hotspot" class="input w-full text-sm">
            <option :value="null">— {{ fallback('hotspot') }} —</option>
            <option :value="true">true</option>
            <option :value="false">false</option>
          </select>
        </div>
        <div>
          <label class="block text-xs font-semibold text-nord3 mb-1">Supersite</label>
          <select v-model="form.supersite" class="input w-full text-sm">
            <option :value="null">— {{ fallback('supersite') }} —</option>
            <option :value="true">true</option>
            <option :value="false">false</option>
          </select>
        </div>
        <div v-for="f in [
              { k: 'latitude', l: 'Latitude' }, { k: 'longitude', l: 'Longitude' },
              { k: 'altitude', l: 'Altitude (m)' }, { k: 'inlet_height', l: 'Inlet height (m)' },
              { k: 'building_distance', l: 'Building distance (m)' },
              { k: 'kerb_distance', l: 'Kerb distance (m)' },
              { k: 'emission_source_distance', l: 'Emission source distance (m)' }]" :key="f.k">
          <label class="block text-xs font-semibold text-nord3 mb-1">{{ f.l }}</label>
          <input type="number" step="any" v-model.number="form[f.k]" class="input w-full text-sm"
                 :placeholder="fallback(f.k)" />
        </div>
      </div>
      <div class="flex justify-end pt-2 gap-4">
        <button class="button" :disabled="saving || !form.location_begin" @click="onSave">
          {{ saving ? "Saving…" : "Save" }}
        </button>
        <button class="button" @click="editing = null">Cancel</button>
      </div>
    </div>

    <!-- Periods -->
    <div v-if="loading" class="text-nord3 text-sm py-4 text-center">Loading…</div>
    <div v-else-if="periods.length === 0" class="text-nord3 text-sm py-4 text-center">
      No location periods. The export falls back to the sampling point's active period
      ({{ fallback('from_time') }}) and its current coordinates.
    </div>
    <div v-else class="overflow-x-auto">
      <table class="table w-full text-sm">
        <thead>
          <tr>
            <th class="whitespace-nowrap">Begin</th>
            <th class="whitespace-nowrap">End</th>
            <th>Station area</th>
            <th>Category</th>
            <th>Lat</th>
            <th>Lon</th>
            <th>Alt</th>
            <th>Inlet</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in periods" :key="r.location_begin">
            <td class="whitespace-nowrap font-mono text-xs">{{ r.location_begin }}</td>
            <td class="whitespace-nowrap font-mono text-xs">
              {{ r.location_end ?? "current" }}
            </td>
            <td>{{ r.station_area ?? "—" }}</td>
            <td>{{ r.sampling_point_category ?? "—" }}</td>
            <td class="font-mono text-xs">{{ r.latitude ?? "—" }}</td>
            <td class="font-mono text-xs">{{ r.longitude ?? "—" }}</td>
            <td class="font-mono text-xs">{{ r.altitude ?? "—" }}</td>
            <td class="font-mono text-xs">{{ r.inlet_height ?? "—" }}</td>
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
