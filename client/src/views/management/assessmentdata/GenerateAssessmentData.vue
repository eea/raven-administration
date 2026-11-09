<script setup>
import { computed, ref, watch } from "vue";
import { useRouter } from "vue-router";
import Popup from "../../../components/Popup.vue";
import DataTable from "../../../components/DataTable.vue";
import Eventy from "../../../helpers/eventy";
import Service from "./service";

// Step 2 of the assessment setup wizard: regimes -> assessment data -> compliance.
//
// For every regime of the classification year, the reporting sampling points that
// measure the regime's pollutant and whose station lies inside the regime's zone --
// matched by coordinates, since a sampling point has no zone of its own -- and are not
// linked to it yet. Zones may overlap (a PAH zone often covers the whole country),
// which is why the pollutant has to match too. Models have no location; link those
// per regime from Assessment regimes -> Linked sampling points / models.
//
// Writes through insert-many: all or nothing, insert only, an existing link is never
// touched.

const props = defineProps({
  show: Boolean,
  initialYear: { type: Number, default: null }
});
const emit = defineEmits(["close", "linked"]);
const router = useRouter();

const now = new Date().getFullYear();
const years = Array.from({ length: 6 }, (_, i) => now - i);

const year = ref(now - 1);
const rows = ref([]);
const regimes = ref(0);
const loading = ref(false);
const saving = ref(false);
const loaded = ref(false);
const linked = ref(0);
const gridApi = ref(null);

const columns = [
  { field: "zone_national_code", headerName: "Zone Code", sortable: true, filter: true, minWidth: 100, flex: 0.8 },
  { field: "pollutant", headerName: "Pollutant", sortable: true, filter: true, minWidth: 100, flex: 0.8 },
  { field: "objective_type", headerName: "Objective", sortable: true, filter: true, minWidth: 90, flex: 0.7 },
  { field: "reporting_metric", headerName: "Metric", sortable: true, filter: true, minWidth: 90, flex: 0.7 },
  { field: "assessment_regime_id", headerName: "Assessment Regime", sortable: true, filter: true, minWidth: 220, flex: 2 },
  { field: "station_name", headerName: "Station", sortable: true, filter: true, minWidth: 140, flex: 1.2 },
  { field: "sampling_point_id", headerName: "Sampling Point", sortable: true, filter: true, minWidth: 160, flex: 1.4 },
  { field: "assessmenttype", headerName: "Assessment Type", sortable: true, filter: true, minWidth: 110, flex: 0.8,
    headerTooltip: "The type the point was linked with before, else fixed measurement" }
];

const getRowId = (params) => `${params.data.assessment_regime_id}|${params.data.sampling_point_id}`;
const onGridReady = (api) => (gridApi.value = api);
const canLink = computed(() => !saving.value && rows.value.length > 0);

const reset = () => {
  rows.value = [];
  loaded.value = false;
  linked.value = 0;
};

watch(() => props.show, (open) => {
  if (!open) return reset();
  if (props.initialYear) year.value = props.initialYear;
  load();
});

const load = async () => {
  loading.value = true;
  loaded.value = false;
  rows.value = [];
  try {
    const found = await Service.candidatesYear(year.value);
    rows.value = found.rows ?? [];
    regimes.value = found.regimes ?? 0;
    loaded.value = true;
  } catch {
    Eventy.showHideMessage("Could not load the sampling points to link.", "error", 4000);
  } finally {
    loading.value = false;
  }
};

const onLink = async () => {
  const selected = gridApi.value?.getSelectedRows() ?? [];
  const links = (selected.length > 0 ? selected : rows.value).map((r) => ({
    assessment_regime_id: r.assessment_regime_id,
    sampling_point_id: r.sampling_point_id,
    assessmenttype: r.assessmenttype || "fixed"
  }));
  if (links.length === 0) return;

  saving.value = true;
  try {
    Eventy.showMessage(`Linking ${links.length} sampling point(s)...`, "loading");
    const result = await Service.insertMany(links);
    Eventy.hideMessage();
    Eventy.showHideMessage(result.msg, "success", 5000);
    linked.value += result.ids?.length ?? 0;
    emit("linked");
    await load();
  } catch {
    Eventy.hideMessage();
    // Request already surfaced the server message.
  } finally {
    saving.value = false;
  }
};

const back = () => {
  emit("close");
  router.push({ name: "AssessmentRegimes", query: { wizard: 1, year: year.value } });
};
const next = () => {
  emit("close");
  router.push({ name: "ComplianceAssessmentMethod", query: { wizard: 1, year: year.value } });
};
</script>

<template>
  <popup :show="show" title="Link sampling points by zone — step 2 of 3" class="w-[78rem] max-w-[95%] h-[85vh]"
         body-class="flex-1 min-h-0 flex flex-col" @on-close="emit('close')">
    <p class="text-xs text-nord3 mb-3 shrink-0">
      For each assessment regime of the year, the reporting sampling points that measure its pollutant and
      whose station lies <strong>inside the regime's zone</strong>, not linked yet. Select rows to link only
      those; with nothing selected, all listed are linked. Models have no location — link them per regime
      from <em>Assessment regimes → Linked sampling points / models</em>.
    </p>

    <div class="flex gap-3 items-end mb-3 shrink-0">
      <div>
        <div class="font-bold text-sm">Classification Year</div>
        <select class="select w-32" v-model="year" :disabled="loading || saving" @change="load">
          <option v-for="y in years" :key="y" :value="y">{{ y }}</option>
        </select>
      </div>
      <button class="button" @click="load" :disabled="loading || saving">
        {{ loading ? "Loading..." : "Refresh" }}
      </button>
    </div>

    <div class="text-xs text-nord3 mb-1 shrink-0">
      <template v-if="!loaded">Loading...</template>
      <template v-else-if="regimes === 0">
        No assessment regimes for {{ year }} yet —
        <a class="text-nord10 hover:underline cursor-pointer" @click="back">generate them first (step 1)</a>.
      </template>
      <template v-else-if="rows.length">
        {{ rows.length }} link(s) missing across {{ regimes }} regime(s) of {{ year }}.
      </template>
      <template v-else>Every sampling point inside the zones is linked for {{ year }}.</template>
    </div>

    <div class="flex-1 min-h-0 text-xs">
      <DataTable :data="rows" :columns="columns" :filter="true" :floating-filter="false"
                 :get-row-id="getRowId" selection-mode="multiRow" @grid-ready="onGridReady" />
    </div>

    <div class="border-t border-gray-300 mt-3 shrink-0"></div>
    <div class="flex justify-end pt-2 gap-4 shrink-0">
      <button class="button mr-auto" @click="back">← Step 1: regimes</button>
      <button class="button" :disabled="!canLink" @click="onLink">
        {{ saving ? "Linking..." : "Link" }}
      </button>
      <button class="button" :class="linked ? 'bg-nord14/30' : ''" @click="next"
              title="Recalculate ComplianceAssessmentMethod for the year">
        Next: calculate compliance →
      </button>
      <button class="button" @click="emit('close')">Close</button>
    </div>
  </popup>
</template>
