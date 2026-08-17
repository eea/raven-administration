<script setup>
import { computed, onMounted, ref } from "vue";
import Eventy from "../../../helpers/eventy";
import Service from "./service";
import IconAdd from "~icons/material-symbols/add";
import IconEdit from "~icons/material-symbols/edit-outline";
import IconDelete from "~icons/material-symbols/delete-outline";

// Its own page rather than the generic Manager: the primary key is
// (attainment_id, adjustment_source_id), and Manager's delete addresses rows by a
// single `id`.

const rows = ref([]);
const lookups = ref({ adjustment_sources: [], attainments: [], methods: [], documents: [] });
const loading = ref(false);
const saving = ref(false);

// null = form closed; {} = adding; otherwise the key being edited.
const editing = ref(null);
const form = ref({});

const BLANK = {
  attainment_id: null,
  adjustment_source_id: null,
  adjustment_assessment_method_id: null,
  adjustment_document_id: null,
};

const isNew = computed(() => editing.value !== null && !editing.value.attainment_id);
const canSave = computed(() => !!form.value.attainment_id && !!form.value.adjustment_source_id);

const load = async () => {
  loading.value = true;
  try {
    const [data, lk] = await Promise.all([Service.get(), Service.lookups()]);
    rows.value = data;
    lookups.value = lk;
  } catch {
    Eventy.showHideMessage("Failed to load adjustments.", "error", 4000);
  } finally {
    loading.value = false;
  }
};

const openAdd = () => {
  form.value = { ...BLANK };
  editing.value = {};
};

const openEdit = (row) => {
  form.value = {
    attainment_id: row.attainment_id,
    adjustment_source_id: row.adjustment_source_id,
    adjustment_assessment_method_id: row.adjustment_assessment_method_id,
    adjustment_document_id: row.adjustment_document_id,
  };
  editing.value = {
    attainment_id: row.attainment_id,
    adjustment_source_id: row.adjustment_source_id,
  };
};

const onSave = async () => {
  if (!canSave.value) return;
  saving.value = true;
  try {
    if (isNew.value) {
      await Service.insert(form.value);
    } else {
      await Service.update(editing.value, form.value);
    }
    editing.value = null;
    await load();
    Eventy.showHideMessage("Adjustment saved.", "success", 3000);
  } catch {
    // Request already surfaced the server message (duplicate method, FK, key clash).
  } finally {
    saving.value = false;
  }
};

const onDelete = async (row) => {
  if (!confirm(`Delete the ${row.adjustment_source_id} adjustment for ${row.attainment_id}?`)) {
    return;
  }
  try {
    await Service.delete({
      attainment_id: row.attainment_id,
      adjustment_source_id: row.adjustment_source_id,
    });
    await load();
    Eventy.showHideMessage("Adjustment deleted.", "success", 3000);
  } catch {
    /* message already shown */
  }
};

onMounted(load);
</script>

<template>
  <div class="p-4">
    <div class="flex items-center justify-between mb-2">
      <h1 class="text-lg font-semibold">Pollution level adjustments</h1>
      <button v-if="!editing" class="button" @click="openAdd">
        <span class="flex items-center gap-1.5"><icon-add class="text-base" /> Add adjustment</span>
      </button>
    </div>

    <p class="text-xs text-nord3 mb-4 max-w-3xl">
      Deductions from measured pollution levels for causes outside a country's control —
      natural sources and winter salting or sanding (AQR3 ADJ). A deduction can change whether
      a zone passes or fails, so each row records the attainment it applies to, the cause, the
      model that quantified it and the report that justifies it. AQR3 requires a different
      assessment method for each adjustment source, so the deduction for each can be reported
      separately in the MOEResult tables.
    </p>

    <div v-if="editing" class="mb-4 p-3 border border-nord4 rounded bg-white max-w-3xl">
      <div class="grid grid-cols-2 gap-3 mb-3">
        <div>
          <label class="block text-xs font-semibold text-nord3 mb-1">
            Attainment <span class="text-nord11">*</span>
          </label>
          <select v-model="form.attainment_id" class="input w-full text-sm">
            <option :value="null">— select —</option>
            <option v-for="o in lookups.attainments" :key="o.value" :value="o.value">
              {{ o.label }}
            </option>
          </select>
          <p v-if="!lookups.attainments.length" class="text-[11px] text-nord11 mt-0.5">
            No attainments yet — run the compliance calculation on the Dataflow page first.
          </p>
        </div>
        <div>
          <label class="block text-xs font-semibold text-nord3 mb-1">
            Adjustment source <span class="text-nord11">*</span>
          </label>
          <select v-model="form.adjustment_source_id" class="input w-full text-sm">
            <option :value="null">— select —</option>
            <option v-for="o in lookups.adjustment_sources" :key="o.value" :value="o.value">
              {{ o.label }}
            </option>
          </select>
        </div>
        <div>
          <label class="block text-xs font-semibold text-nord3 mb-1">Assessment method</label>
          <select v-model="form.adjustment_assessment_method_id" class="input w-full text-sm">
            <option :value="null">— none —</option>
            <option v-for="o in lookups.methods" :key="o.value" :value="o.value">{{ o.label }}</option>
          </select>
          <p class="text-[11px] text-nord3 mt-0.5">The model/OBE that quantified the deduction</p>
        </div>
        <div>
          <label class="block text-xs font-semibold text-nord3 mb-1">Justifying document</label>
          <select v-model="form.adjustment_document_id" class="input w-full text-sm">
            <option :value="null">— none —</option>
            <option v-for="o in lookups.documents" :key="o.value" :value="o.value">{{ o.label }}</option>
          </select>
        </div>
      </div>
      <div class="flex justify-end pt-2 gap-4">
        <button class="button" :disabled="saving || !canSave" @click="onSave">
          {{ saving ? "Saving…" : "Save" }}
        </button>
        <button class="button" @click="editing = null">Cancel</button>
      </div>
    </div>

    <div v-if="loading" class="text-nord3 text-sm py-4">Loading…</div>
    <div v-else-if="rows.length === 0" class="text-nord3 text-sm py-4">
      No adjustments recorded.
    </div>
    <div v-else class="overflow-x-auto">
      <table class="table w-full text-sm">
        <thead>
          <tr>
            <th>Attainment</th>
            <th>Adjustment source</th>
            <th>Assessment method</th>
            <th>Document</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in rows" :key="`${r.attainment_id}|${r.adjustment_source_id}`">
            <td class="font-mono text-xs">{{ r.attainment_id }}</td>
            <td>{{ r.adjustment_source_label ?? r.adjustment_source ?? r.adjustment_source_id }}</td>
            <td class="font-mono text-xs">{{ r.adjustment_assessment_method_id ?? "—" }}</td>
            <td class="font-mono text-xs">{{ r.adjustment_document_id ?? "—" }}</td>
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
  </div>
</template>
