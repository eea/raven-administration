<script setup>
import { computed, ref, watch } from "vue";
import Popup from "../../../components/Popup.vue";
import DataTable from "../../../components/DataTable.vue";
import Eventy from "../../../helpers/eventy";
import Service from "./service";

// Bulk fill, inherited from the retired assessmentregimezones grid. That grid listed
// zones x environmental objectives for a year and let an operator annotate them in
// bulk; the annotations went to a table nothing exported. Here the same enumeration
// produces real assessment_regimes rows, with ARZ_02 derived server-side.
//
// Only combinations that have no regime yet are listed, so re-running after a partial
// generate shows what is still missing rather than the whole grid again.

const props = defineProps({
  show: Boolean,
  lookups: { type: Object, default: () => ({}) }
});

const emit = defineEmits(["close", "generated"]);

const now = new Date().getFullYear();
const years = Array.from({ length: 6 }, (_, i) => now - i);

const year = ref(now - 1);
const rows = ref([]);
const loading = ref(false);
const saving = ref(false);
const loaded = ref(false);
const gridApi = ref(null);

const threshold = ref("");
const document = ref("");

const columns = [
  { field: "zone_national_code", headerName: "Zone Code", sortable: true, filter: true, minWidth: 110, flex: 1 },
  { field: "zone_name", headerName: "Zone", sortable: true, filter: true, minWidth: 150, flex: 1.5 },
  { field: "pollutant", headerName: "Pollutant", sortable: true, filter: true, minWidth: 110, flex: 1 },
  { field: "objective_type", headerName: "Objective Type", sortable: true, filter: true, minWidth: 120, flex: 1 },
  { field: "protection_target", headerName: "Protection Target", sortable: true, filter: true, minWidth: 130, flex: 1 },
  { field: "reporting_metric", headerName: "Reporting Metric", sortable: true, filter: true, minWidth: 130, flex: 1 }
];

const getRowId = (params) => `${params.data.zone_id}|${params.data.environmental_objective_id}`;
const onGridReady = (api) => (gridApi.value = api);

const canGenerate = computed(() => !saving.value && rows.value.length > 0);

const reset = () => {
  rows.value = [];
  loaded.value = false;
  threshold.value = "";
  document.value = "";
};

watch(() => props.show, (open) => { if (!open) reset(); });

const load = async () => {
  loading.value = true;
  loaded.value = false;
  rows.value = [];
  try {
    rows.value = await Service.candidates(year.value);
    loaded.value = true;
    if (rows.value.length === 0) {
      Eventy.showHideMessage(`Every zone x objective combination already has a regime for ${year.value}`, "success", 4000);
    }
  } catch {
    Eventy.showHideMessage("Could not load candidate combinations.", "error", 4000);
  } finally {
    loading.value = false;
  }
};

const onGenerate = async () => {
  const selected = gridApi.value?.getSelectedRows() ?? [];
  const combinations = (selected.length > 0 ? selected : rows.value).map((r) => ({
    zone_id: r.zone_id,
    environmental_objective_id: r.environmental_objective_id
  }));
  if (combinations.length === 0) return;

  saving.value = true;
  try {
    Eventy.showMessage(`Creating ${combinations.length} assessment regimes...`, "loading");
    const result = await Service.generate({
      year: year.value,
      combinations,
      assessment_threshold_exceedance_id: threshold.value || null,
      classification_document_id: document.value || null
    });
    Eventy.hideMessage();
    Eventy.showHideMessage(result.msg, "success", 5000);
    emit("generated");
    await load();
  } catch {
    Eventy.hideMessage();
    // Request already surfaced the server message.
  } finally {
    saving.value = false;
  }
};
</script>

<template>
  <popup :show="show" title="Generate assessment regimes" class="w-[70rem] max-w-[95vw] h-[80vh]"
         body-class="flex-1 min-h-0 flex flex-col" @on-close="emit('close')">
    <p class="text-xs text-nord3 mb-3 shrink-0">
      Every zone x environmental objective combination that has <strong>no regime yet</strong> for
      the chosen classification year. Generating creates real ARZ rows — the AssessmentRegimeId is
      derived server-side, so the seven-segment format is not typed by hand. Select rows to
      generate only those; with nothing selected, all listed combinations are generated.
    </p>

    <div class="flex gap-3 items-end mb-3 shrink-0">
      <div>
        <div class="font-bold text-sm">Classification Year</div>
        <select class="select w-32" v-model="year" :disabled="loading || saving">
          <option v-for="y in years" :key="y" :value="y">{{ y }}</option>
        </select>
      </div>
      <button class="button" @click="load" :disabled="loading || saving">
        {{ loading ? "Loading..." : "Find missing" }}
      </button>

      <div class="flex-1"></div>

      <div>
        <div class="font-bold text-sm">Threshold Exceedance</div>
        <select class="select w-52" v-model="threshold" :disabled="saving">
          <option value="">— leave empty —</option>
          <option v-for="o in lookups.threshold_exceedances ?? []" :key="o.value" :value="o.value">
            {{ o.label }}
          </option>
        </select>
      </div>
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
      {{ rows.length }} combination(s) without a regime for {{ year }}.
    </div>
    <div v-else-if="loaded" class="text-xs text-nord3 mb-1 shrink-0">
      Nothing missing for {{ year }}.
    </div>
    <div v-else class="text-xs text-nord3 mb-1 shrink-0">
      Pick a year and choose <em>Find missing</em>.
    </div>

    <div class="flex-1 min-h-0 text-xs">
      <DataTable :data="rows" :columns="columns" :filter="true" :floating-filter="false"
                 :get-row-id="getRowId" selection-mode="multiRow" @grid-ready="onGridReady" />
    </div>

    <div class="border-t border-gray-300 mt-3 shrink-0"></div>
    <div class="flex justify-end pt-2 gap-4 shrink-0">
      <button class="button" :disabled="!canGenerate" @click="onGenerate">
        {{ saving ? "Generating..." : "Generate" }}
      </button>
      <button class="button" @click="emit('close')">Close</button>
    </div>
  </popup>
</template>
