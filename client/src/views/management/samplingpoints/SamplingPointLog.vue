<script setup>
import { ref, watch } from "vue";
import Popup from "../../../components/Popup.vue";
import Eventy from "../../../helpers/eventy";
import Service from "./service";
import IconLog from "~icons/material-symbols/assignment-outline";

const props = defineProps({
  show: Boolean,
  samplingPoint: { type: Object, default: null },
  defaultType: { type: String, default: "manual" },
  typeFilter: { type: String, default: null }, // when set: filter list, read-only, change title
});

const emit = defineEmits(["close"]);

const rows = ref([]);
const loading = ref(false);
const showAddForm = ref(false);
const saving = ref(false);

const form = ref({ comment: "", period_from: "", period_to: "" });

const TYPE_LABELS = { manual: "Manual", daily_check: "Daily check", migration: "Migration" };
const TYPE_COLORS = {
  manual: "bg-nord8/20 text-nord10",
  daily_check: "bg-nord14/20 text-nord14",
  migration: "bg-nord4/30 text-nord3",
};
const typeLabel = (t) => TYPE_LABELS[t] ?? t;
const typeColor = (t) => TYPE_COLORS[t] ?? "bg-nord4/20 text-nord3";

const load = async () => {
  if (!props.samplingPoint?.id) return;
  loading.value = true;
  try {
    rows.value = await Service.logList(props.samplingPoint.id, props.typeFilter || null);
  } catch {
    Eventy.showHideMessage("Failed to load log entries.", "error", 4000);
  } finally {
    loading.value = false;
  }
};

const onSave = async () => {
  const { comment, period_from, period_to } = form.value;
  if (!comment.trim() || !period_from || !period_to) return;
  saving.value = true;
  try {
    await Service.logInsert({
      sampling_point_id: props.samplingPoint.id,
      type: props.defaultType,
      comment: comment.trim(),
      period_from,
      period_to,
    });
    form.value = { comment: "", period_from: "", period_to: "" };
    showAddForm.value = false;
    await load();
    Eventy.showHideMessage("Log entry saved.", "success", 3000);
  } catch {
    Eventy.showHideMessage("Failed to save log entry.", "error", 4000);
  } finally {
    saving.value = false;
  }
};

watch(() => props.show, (v) => {
  if (v) {
    showAddForm.value = false;
    form.value = { comment: "", period_from: "", period_to: "" };
    load();
  }
});
</script>

<template>
  <popup :show="show" :title="typeFilter === 'daily_check' ? `Daily check log — ${samplingPoint?.id ?? ''}` : `Sampling point log — ${samplingPoint?.id ?? ''}`" @on-close="emit('close')" class="max-w-3xl w-full">

    <!-- Add entry toggle (hidden in read-only/filtered mode) -->
    <div v-if="!typeFilter" class="flex justify-end mb-3">
      <button
        class="flex items-center gap-1.5 px-3 py-1.5 text-sm rounded border border-nord10 text-nord10 hover:bg-nord10/10"
        @click="showAddForm = !showAddForm">
        <icon-log class="text-base" />
        {{ showAddForm ? "Cancel" : "Add entry" }}
      </button>
    </div>

    <!-- Add entry form (hidden in read-only/filtered mode) -->
    <div v-if="showAddForm && !typeFilter" class="mb-4 p-3 border border-nord4 rounded bg-white">
      <div class="grid grid-cols-2 gap-3 mb-3">
        <div>
          <label class="block text-xs font-semibold text-nord3 mb-1">Period from <span class="text-nord11">*</span></label>
          <input type="datetime-local" v-model="form.period_from" class="input w-full text-sm" />
        </div>
        <div>
          <label class="block text-xs font-semibold text-nord3 mb-1">Period to <span class="text-nord11">*</span></label>
          <input type="datetime-local" v-model="form.period_to" class="input w-full text-sm" />
        </div>
      </div>
      <div class="mb-3">
        <label class="block text-xs font-semibold text-nord3 mb-1">Comment <span class="text-nord11">*</span></label>
        <textarea v-model="form.comment" rows="3" class="input w-full text-sm resize-none" placeholder="Enter log comment..." />
      </div>
      <div class="flex justify-end gap-2">
        <button class="btn btn-primary text-sm" :disabled="saving || !form.comment.trim() || !form.period_from || !form.period_to" @click="onSave">
          {{ saving ? "Saving…" : "Save" }}
        </button>
      </div>
    </div>

    <!-- Log entries table -->
    <div v-if="loading" class="text-nord3 text-sm py-4 text-center">Loading…</div>
    <div v-else-if="rows.length === 0" class="text-nord3 text-sm py-4 text-center">No log entries found.</div>
    <div v-else class="overflow-x-auto">
      <table class="table w-full text-sm">
        <thead>
          <tr>
            <th class="whitespace-nowrap">Created</th>
            <th>By</th>
            <th>Type</th>
            <th class="whitespace-nowrap">Period from</th>
            <th class="whitespace-nowrap">Period to</th>
            <th>Comment</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in rows" :key="r.id">
            <td class="whitespace-nowrap font-mono text-xs">{{ r.created_at }}</td>
            <td class="whitespace-nowrap">{{ r.created_by ?? "—" }}</td>
            <td>
              <span class="px-1.5 py-0.5 rounded text-xs font-medium" :class="typeColor(r.type)">
                {{ typeLabel(r.type) }}
              </span>
            </td>
            <td class="whitespace-nowrap font-mono text-xs">{{ r.period_from }}</td>
            <td class="whitespace-nowrap font-mono text-xs">{{ r.period_to }}</td>
            <td class="max-w-xs break-words">{{ r.comment }}</td>
          </tr>
        </tbody>
      </table>
    </div>

  </popup>
</template>
