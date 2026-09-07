<script setup>
import { computed, onMounted, ref } from "vue";
import Eventy from "../../../helpers/eventy";
import Service from "./service";
import IconEdit from "~icons/material-symbols/edit-outline";

// Its own page rather than the generic Manager: the primary key is four columns
// (reporting_year, assessment_regime_id, data_aggregation_process_id,
// assessment_method_id), and Manager addresses rows by a single `id`.
//
// There is no add or delete button on purpose. The row set is derived from the
// assessment regimes and the sampling points linked to them, and is rebuilt by
// Recalculate compliance on the Dataflow page. AQR3's way to retract a row is the
// Deletion flag, which is one of the editable fields.

const rows = ref([]);
const lookups = ref({ reasons: [], years: [] });
const year = ref(null);
const loading = ref(false);
const saving = ref(false);

// null = form closed; otherwise the key of the row being edited.
const editing = ref(null);
const form = ref({});

const KEY = ["reporting_year", "assessment_regime_id", "data_aggregation_process_id",
             "assessment_method_id"];
const VALUES = ["is_exceedance", "data_coverage", "pollution_level",
                "pollution_level_adjusted", "relative_uncertainty_limit",
                "assessment_mqi", "correction_flag", "preliminary_reason_id", "deletion"];

const typedCount = computed(
  () => rows.value.filter((r) => r.pollution_level !== null).length
);

const num = (v) => (v === null || v === undefined || v === "" ? null : Number(v));

const load = async () => {
  if (!year.value) return;
  loading.value = true;
  try {
    rows.value = await Service.get(year.value);
  } catch {
    Eventy.showHideMessage("Failed to load compliance rows.", "error", 4000);
  } finally {
    loading.value = false;
  }
};

const init = async () => {
  try {
    lookups.value = await Service.lookups();
  } catch {
    Eventy.showHideMessage("Failed to load lookups.", "error", 4000);
    return;
  }
  year.value = lookups.value.years?.[0] ?? null;
  await load();
};

const openEdit = (row) => {
  form.value = Object.fromEntries(VALUES.map((k) => [k, row[k] ?? null]));
  editing.value = Object.fromEntries(KEY.map((k) => [k, row[k]]));
  editing.value._label = `${row.assessment_regime_id} · ${row.assessment_method_id}`;
};

const onSave = async () => {
  saving.value = true;
  try {
    const values = { ...form.value };
    for (const k of ["data_coverage", "pollution_level", "pollution_level_adjusted",
                     "relative_uncertainty_limit", "assessment_mqi"]) {
      values[k] = num(values[k]);
    }
    const key = Object.fromEntries(KEY.map((k) => [k, editing.value[k]]));
    await Service.update(key, values);
    editing.value = null;
    await load();
    Eventy.showHideMessage("Compliance row saved.", "success", 3000);
  } catch {
    // Request already surfaced the server message.
  } finally {
    saving.value = false;
  }
};

onMounted(init);
</script>

<template>
  <div class="p-4">
    <div class="flex items-center gap-3 mb-2">
      <h1 class="text-lg font-semibold">Compliance assessment method</h1>
      <select v-if="lookups.years?.length" v-model="year" class="input text-sm"
              @change="load">
        <option v-for="y in lookups.years" :key="y" :value="y">{{ y }}</option>
      </select>
      <span v-if="rows.length" class="text-xs text-nord3">
        {{ rows.length }} rows · {{ typedCount }} with a pollution level
      </span>
    </div>

    <p class="text-xs text-nord3 mb-2 max-w-4xl">
      The yearly compliance situation per assessment regime and assessment method (AQR3 CAM).
      Rows are <strong>derived</strong>: <em>Recalculate compliance</em> on the Dataflow page
      builds them from the assessment regimes and the sampling points linked to them, so they
      cannot be added or deleted here.
    </p>
    <p class="text-xs text-nord3 mb-4 max-w-4xl">
      What is editable is the part the calculation does not produce yet — the measured figures.
      A recalculation keeps whatever is entered here <strong>only while it has no value of its
      own</strong>: once the exceedance evaluation computes a figure, the computed one wins.
      AQR3 requires a pollution level for every assessment method, so a blank column is an
      incomplete submission.
    </p>

    <div v-if="editing" class="mb-4 p-3 border border-nord4 rounded bg-white max-w-4xl">
      <p class="text-xs font-semibold text-nord3 mb-1">
        Editing {{ editing._label }} ({{ editing.data_aggregation_process_id }},
        {{ editing.reporting_year }})
      </p>
      <p class="text-[11px] text-nord3 mb-3">
        The four key columns identify this row and are not editable — they describe which
        compliance situation this is.
      </p>
      <div class="grid grid-cols-3 gap-3 mb-3">
        <div>
          <label class="block text-xs font-semibold text-nord3 mb-1">
            Is exceedance <span class="text-nord3 font-normal">(CAM_08)</span>
          </label>
          <select v-model="form.is_exceedance" class="input w-full text-sm">
            <option :value="null">— unknown —</option>
            <option :value="true">Yes</option>
            <option :value="false">No</option>
          </select>
        </div>
        <div>
          <label class="block text-xs font-semibold text-nord3 mb-1">
            Data coverage % <span class="text-nord3 font-normal">(CAM_09)</span>
          </label>
          <input v-model="form.data_coverage" type="number" step="0.01" min="0" max="100"
                 class="input w-full text-sm" placeholder="e.g. 85.78" />
        </div>
        <div>
          <label class="block text-xs font-semibold text-nord3 mb-1">
            Pollution level <span class="text-nord3 font-normal">(CAM_10)</span>
          </label>
          <input v-model="form.pollution_level" type="number" step="0.001"
                 class="input w-full text-sm" placeholder="required by AQR3" />
        </div>
        <div>
          <label class="block text-xs font-semibold text-nord3 mb-1">
            Pollution level adjusted <span class="text-nord3 font-normal">(CAM_11)</span>
          </label>
          <input v-model="form.pollution_level_adjusted" type="number" step="0.001"
                 class="input w-full text-sm" />
          <p class="text-[11px] text-nord3 mt-0.5">After the ADJ deductions</p>
        </div>
        <div>
          <label class="block text-xs font-semibold text-nord3 mb-1">
            Relative uncertainty % <span class="text-nord3 font-normal">(CAM_12)</span>
          </label>
          <input v-model="form.relative_uncertainty_limit" type="number" step="0.01"
                 class="input w-full text-sm" />
          <p class="text-[11px] text-nord3 mt-0.5">Required for sampling-point methods</p>
        </div>
        <div>
          <label class="block text-xs font-semibold text-nord3 mb-1">
            Assessment MQI <span class="text-nord3 font-normal">(CAM_13)</span>
          </label>
          <input v-model="form.assessment_mqi" type="number" step="0.01"
                 class="input w-full text-sm" />
          <p class="text-[11px] text-nord3 mt-0.5">Modelling quality indicator, models only</p>
        </div>
        <div>
          <label class="block text-xs font-semibold text-nord3 mb-1">
            Preliminary reason <span class="text-nord3 font-normal">(CAM_17)</span>
          </label>
          <select v-model="form.preliminary_reason_id" class="input w-full text-sm">
            <option :value="null">— none —</option>
            <option v-for="o in lookups.reasons" :key="o.value" :value="o.value">
              {{ o.label }}
            </option>
          </select>
        </div>
        <div class="flex flex-col justify-center gap-2 pt-4">
          <label class="flex items-center gap-2 text-xs text-nord3">
            <input v-model="form.correction_flag" type="checkbox" />
            Correction applied (CAM_14)
          </label>
          <label class="flex items-center gap-2 text-xs text-nord11">
            <input v-model="form.deletion" type="checkbox" />
            Deletion — retract this row (CAM_18)
          </label>
        </div>
      </div>
      <div class="flex justify-end pt-2 gap-4">
        <button class="button" :disabled="saving" @click="onSave">
          {{ saving ? "Saving…" : "Save" }}
        </button>
        <button class="button" @click="editing = null">Cancel</button>
      </div>
    </div>

    <div v-if="loading" class="text-nord3 text-sm py-4">Loading…</div>
    <div v-else-if="!lookups.years?.length" class="text-nord3 text-sm py-4">
      No compliance has been calculated yet. Use <em>Recalculate compliance</em> on the
      Dataflow page first.
    </div>
    <div v-else-if="rows.length === 0" class="text-nord3 text-sm py-4">
      No compliance rows for {{ year }}.
    </div>
    <div v-else class="overflow-x-auto">
      <table class="table w-full text-sm">
        <thead>
          <tr>
            <th colspan="6" class="text-left text-xs font-normal text-nord3">
              Derived — rebuilt by Recalculate compliance
            </th>
            <th colspan="7" class="text-left text-xs font-normal text-nord10">
              Entered here
            </th>
            <th></th>
          </tr>
          <tr>
            <th>Zone</th>
            <th>Regime</th>
            <th>Method</th>
            <th>Aggregation</th>
            <th>Pollutant</th>
            <th>Type</th>
            <th>Exceed.</th>
            <th>Coverage</th>
            <th>Level</th>
            <th>Adjusted</th>
            <th>Uncert.</th>
            <th>MQI</th>
            <th>Reason</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in rows"
              :key="`${r.reporting_year}|${r.assessment_regime_id}|${r.data_aggregation_process_id}|${r.assessment_method_id}`"
              :class="r.deletion ? 'opacity-50 line-through' : ''">
            <td class="text-xs">{{ r.zone_name ?? r.zone_id ?? "—" }}</td>
            <td class="font-mono text-[11px]">{{ r.assessment_regime_id }}</td>
            <td class="font-mono text-xs">{{ r.assessment_method_id }}</td>
            <td class="text-xs">{{ r.data_aggregation_process ?? r.data_aggregation_process_id }}</td>
            <td class="text-xs">{{ r.pollutant ?? r.pollutant_id }}</td>
            <td class="text-xs">{{ r.assessment_type ?? "—" }}</td>
            <td class="text-xs">
              {{ r.is_exceedance === null ? "—" : r.is_exceedance ? "Yes" : "No" }}
            </td>
            <td class="text-xs">{{ r.data_coverage ?? "—" }}</td>
            <td class="text-xs" :class="r.pollution_level === null ? 'text-nord11' : ''">
              {{ r.pollution_level ?? "missing" }}
            </td>
            <td class="text-xs">{{ r.pollution_level_adjusted ?? "—" }}</td>
            <td class="text-xs">{{ r.relative_uncertainty_limit ?? "—" }}</td>
            <td class="text-xs">{{ r.assessment_mqi ?? "—" }}</td>
            <td class="text-xs">{{ r.preliminary_reason ?? "—" }}</td>
            <td class="whitespace-nowrap">
              <button class="text-nord10 hover:text-nord9" title="Edit" @click="openEdit(r)">
                <icon-edit class="text-base" />
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
