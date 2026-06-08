<script setup>
import { ref, watch } from "vue";
import Popup from "../../../components/Popup.vue";
import Service from "./service";

const props = defineProps({
  show: Boolean,
  row: { type: Object, default: null }
});

const emit = defineEmits(["close"]);

const VERIFICATION_LABELS = { 1: "Verified", 2: "Pre-verified", 3: "Not verified" };
const VALIDITY_LABELS = { 1: "Valid", 2: "Below detection", 3: "Below+sub.", 4: "Ozone CCQM", "-1": "Not valid", "-99": "Maintenance" };
const SOURCE_COLORS = {
  qc_verify: "bg-nord8/20 text-nord10",
  qc_validate: "bg-nord9/20 text-nord10",
  scaling: "bg-nord13/20 text-nord12",
  adacs_import: "bg-nord4/30 text-nord3",
  aqtvl_migration: "bg-nord15/20 text-nord15"
};

const logRows = ref([]);
const hasMore = ref(false);
const offset = ref(0);
const loading = ref(false);

watch(
  () => props.show,
  async (val) => {
    if (val && props.row) {
      logRows.value = [];
      offset.value = 0;
      hasMore.value = false;
      await loadMore();
    }
  }
);

const loadMore = async () => {
  if (loading.value || !props.row) return;
  loading.value = true;
  try {
    const result = await Service.log(
      props.row.sampling_point_id,
      props.row.fromtime,
      props.row.totime,
      offset.value
    );
    logRows.value.push(...result.rows);
    hasMore.value = result.has_more;
    offset.value += result.rows.length;
  } finally {
    loading.value = false;
  }
};

const verLabel = (v) => (v != null ? VERIFICATION_LABELS[v] ?? `#${v}` : "—");
const valLabel = (v) => (v != null ? VALIDITY_LABELS[String(v)] ?? `#${v}` : "—");
const srcColor = (src) => SOURCE_COLORS[src] ?? "bg-nord4/20 text-nord3";
</script>

<template>
  <popup :show="show" title="Observation Change History" @on-close="emit('close')" class="max-w-5xl w-full">
    <div v-if="logRows.length === 0 && !loading" class="text-nord3 text-sm py-4 text-center">
      No history entries found.
    </div>
    <div v-else class="overflow-x-auto">
      <table class="table w-full text-sm">
        <thead>
          <tr>
            <th class="whitespace-nowrap">Changed at</th>
            <th>By</th>
            <th>Source</th>
            <th class="whitespace-nowrap">Period from</th>
            <th class="whitespace-nowrap">Period to</th>
            <th class="whitespace-nowrap">Verif. old→new</th>
            <th class="whitespace-nowrap">Validity old→new</th>
            <th class="whitespace-nowrap">Value old→new</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in logRows" :key="r.id">
            <td class="whitespace-nowrap font-mono text-xs">{{ r.changed_at }}</td>
            <td>{{ r.changed_by ?? "—" }}</td>
            <td>
              <span class="px-1.5 py-0.5 rounded text-xs font-medium" :class="srcColor(r.change_source)">
                {{ r.change_source }}
              </span>
            </td>
            <td class="whitespace-nowrap font-mono text-xs">{{ r.period_from }}</td>
            <td class="whitespace-nowrap font-mono text-xs">{{ r.period_to }}</td>
            <td class="whitespace-nowrap">
              <span v-if="r.old_verification != null || r.new_verification != null">
                <span class="text-nord11">{{ verLabel(r.old_verification) }}</span>
                <span class="text-nord3 mx-1">→</span>
                <span class="text-nord14">{{ verLabel(r.new_verification) }}</span>
              </span>
              <span v-else class="text-nord3">—</span>
            </td>
            <td class="whitespace-nowrap">
              <span v-if="r.old_validity != null || r.new_validity != null">
                <span class="text-nord11">{{ valLabel(r.old_validity) }}</span>
                <span class="text-nord3 mx-1">→</span>
                <span class="text-nord14">{{ valLabel(r.new_validity) }}</span>
              </span>
              <span v-else class="text-nord3">—</span>
            </td>
            <td class="whitespace-nowrap font-mono text-xs">
              <span v-if="r.old_value != null || r.new_value != null">
                {{ r.old_value ?? "—" }} → {{ r.new_value ?? "—" }}
              </span>
              <span v-else class="text-nord3">—</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div class="mt-3 flex justify-center" v-if="hasMore">
      <button class="button" :disabled="loading" @click="loadMore">
        {{ loading ? "Loading…" : "Load more" }}
      </button>
    </div>
    <div v-if="loading && logRows.length === 0" class="text-nord3 text-sm py-4 text-center">Loading…</div>
  </popup>
</template>
