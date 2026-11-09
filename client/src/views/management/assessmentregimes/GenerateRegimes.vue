<script setup>
import { computed, ref, watch } from "vue";
import { useRouter } from "vue-router";
import Popup from "../../../components/Popup.vue";
import DataTable from "../../../components/DataTable.vue";
import Eventy from "../../../helpers/eventy";
import Service from "./service";

// Step 1 of the assessment setup wizard: regimes -> assessment data -> compliance.
//
// Lists zone x environmental objective combinations (the EEA environmentalobjective
// vocabulary, split into pollutant, objective type, protection target and reporting
// metric) that have no regime yet for the classification year. By default only what
// the zone actually assesses: a pollutant measured by a sampling point whose station
// lies inside the zone, or modelled. Generating creates real ARZ rows with ARZ_02
// derived server-side.
//
// Each row carries a proposed AssessmentThresholdExceedance, computed from the five
// previous years measured in the zone against the directive's assessment thresholds
// (core/eea/assessment_threshold.py). It is editable, limited to what the objective
// allows; the reasoning is in the row's tooltip.

const props = defineProps({
  show: Boolean,
  lookups: { type: Object, default: () => ({}) },
  initialYear: { type: Number, default: null }
});

const emit = defineEmits(["close", "generated"]);
const router = useRouter();

const now = new Date().getFullYear();
const years = Array.from({ length: 6 }, (_, i) => now - i);

const year = ref(now - 1);
const measuredOnly = ref(true);
const rows = ref([]);
const loading = ref(false);
const saving = ref(false);
const loaded = ref(false);
const generated = ref(0);
const gridApi = ref(null);

const document = ref("");

const classificationColumn = {
  field: "chosen_threshold",
  headerName: "Classification",
  minWidth: 130,
  flex: 1,
  editable: (params) => (params.data?.allowed_thresholds ?? []).length > 0,
  singleClickEdit: true,
  cellEditor: "agSelectCellEditor",
  cellEditorParams: (params) => ({ values: ["", ...(params.data?.allowed_thresholds ?? [])] }),
  tooltipValueGetter: (params) => params.data?.proposal_basis || null,
  cellClass: (params) => (params.value && params.value === params.data?.proposed_threshold_exceedance
    ? "text-nord14" : params.value ? "" : "text-nord3"),
  valueFormatter: (params) => params.value || "—"
};

const columns = [
  { field: "zone_national_code", headerName: "Zone Code", sortable: true, filter: true, minWidth: 110, flex: 1 },
  { field: "zone_name", headerName: "Zone", sortable: true, filter: true, minWidth: 150, flex: 1.5 },
  { field: "pollutant", headerName: "Pollutant", sortable: true, filter: true, minWidth: 110, flex: 1 },
  { field: "objective_type", headerName: "Objective Type", sortable: true, filter: true, minWidth: 110, flex: 1 },
  { field: "protection_target", headerName: "Protection Target", sortable: true, filter: true, minWidth: 100, flex: 0.8 },
  { field: "reporting_metric", headerName: "Reporting Metric", sortable: true, filter: true, minWidth: 120, flex: 1 },
  { field: "n_points", headerName: "Points in zone", sortable: true, filter: true, minWidth: 90, flex: 0.7,
    headerTooltip: "Reporting sampling points measuring the pollutant whose station lies inside the zone" },
  classificationColumn
];

const getRowId = (params) => `${params.data.zone_id}|${params.data.environmental_objective_id}`;
const onGridReady = (api) => (gridApi.value = api);

const canGenerate = computed(() => !saving.value && rows.value.length > 0);
const proposed = computed(() => rows.value.filter((r) => r.proposed_threshold_exceedance).length);

const reset = () => {
  rows.value = [];
  loaded.value = false;
  generated.value = 0;
  document.value = "";
};

watch(() => props.show, (open) => {
  if (!open) return reset();
  if (props.initialYear) year.value = props.initialYear;
});

const load = async () => {
  loading.value = true;
  loaded.value = false;
  rows.value = [];
  try {
    const found = await Service.candidates(year.value, measuredOnly.value ? "measured" : "all");
    rows.value = found.map((r) => ({ ...r, chosen_threshold: r.proposed_threshold_exceedance ?? "" }));
    loaded.value = true;
    if (rows.value.length === 0) {
      Eventy.showHideMessage(`Every combination already has a regime for ${year.value}`, "success", 4000);
    }
  } catch {
    Eventy.showHideMessage("Could not load candidate combinations.", "error", 4000);
  } finally {
    loading.value = false;
  }
};

const onGenerate = async () => {
  gridApi.value?.stopEditing();
  const selected = gridApi.value?.getSelectedRows() ?? [];
  const combinations = (selected.length > 0 ? selected : rows.value).map((r) => ({
    zone_id: r.zone_id,
    environmental_objective_id: r.environmental_objective_id,
    assessment_threshold_exceedance_id: r.chosen_threshold || null
  }));
  if (combinations.length === 0) return;

  saving.value = true;
  try {
    Eventy.showMessage(`Creating ${combinations.length} assessment regimes...`, "loading");
    const result = await Service.generate({
      year: year.value,
      combinations,
      classification_document_id: document.value || null
    });
    Eventy.hideMessage();
    Eventy.showHideMessage(result.msg, "success", 5000);
    generated.value += result.created?.length ?? 0;
    emit("generated");
    await load();
  } catch {
    Eventy.hideMessage();
    // Request already surfaced the server message.
  } finally {
    saving.value = false;
  }
};

const next = () => {
  emit("close");
  router.push({ name: "AssessmentData", query: { wizard: 1, year: year.value } });
};
</script>

<template>
  <popup :show="show" title="Generate assessment regimes — step 1 of 3" class="w-[78rem] max-w-[95%] h-[85vh]"
         body-class="flex-1 min-h-0 flex flex-col" @on-close="emit('close')">
    <p class="text-xs text-nord3 mb-3 shrink-0">
      Zone x environmental objective combinations (EEA vocabulary) that have <strong>no regime yet</strong>
      for the classification year. The AssessmentRegimeId is derived server-side. The classification is
      proposed from the five previous years measured inside the zone against the directive's assessment
      thresholds — hover it for the reasoning, click it to change it. Select rows to generate only those;
      with nothing selected, all listed combinations are generated.
    </p>

    <div class="flex gap-3 items-end mb-3 shrink-0">
      <div>
        <div class="font-bold text-sm">Classification Year</div>
        <select class="select w-32" v-model="year" :disabled="loading || saving">
          <option v-for="y in years" :key="y" :value="y">{{ y }}</option>
        </select>
      </div>
      <label class="flex items-center gap-1 text-sm self-center mt-4 cursor-pointer"
             title="A pollutant counts when a reporting sampling point measuring it has its station inside the zone, or a model exists for it">
        <input type="checkbox" v-model="measuredOnly" :disabled="loading || saving" />
        Only pollutants measured in the zone
      </label>
      <button class="button" @click="load" :disabled="loading || saving">
        {{ loading ? "Loading..." : "Find missing" }}
      </button>

      <div class="flex-1"></div>

      <div>
        <div class="font-bold text-sm">Classification Document</div>
        <select class="select w-64" v-model="document" :disabled="saving">
          <option value="">— leave empty —</option>
          <option v-for="d in lookups.documents ?? []" :key="d.value" :value="d.value">
            {{ d.label }}
          </option>
        </select>
      </div>
    </div>

    <div v-if="loaded && rows.length > 0" class="text-xs text-nord3 mb-1 shrink-0">
      {{ rows.length }} combination(s) without a regime for {{ year }};
      a classification is proposed for {{ proposed }}.
    </div>
    <div v-else-if="loaded" class="text-xs text-nord3 mb-1 shrink-0">
      Nothing missing for {{ year }}.
    </div>
    <div v-else class="text-xs text-nord3 mb-1 shrink-0">
      Pick a year and choose <em>Find missing</em>.
    </div>

    <div class="flex-1 min-h-0 text-xs">
      <DataTable :data="rows" :columns="columns" :filter="true" :floating-filter="false"
                 :get-row-id="getRowId" selection-mode="multiRow" :enable-click-selection="false"
                 @grid-ready="onGridReady" />
    </div>

    <div class="border-t border-gray-300 mt-3 shrink-0"></div>
    <div class="flex justify-end pt-2 gap-4 shrink-0">
      <button class="button" :disabled="!canGenerate" @click="onGenerate">
        {{ saving ? "Generating..." : "Generate" }}
      </button>
      <button class="button" :class="generated ? 'bg-nord14/30' : ''" @click="next"
              title="Link the sampling points inside each regime's zone">
        Next: link sampling points →
      </button>
      <button class="button" @click="emit('close')">Close</button>
    </div>
  </popup>
</template>
