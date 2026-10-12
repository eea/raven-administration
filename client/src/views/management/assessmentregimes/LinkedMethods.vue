<script setup>
import { computed, ref, watch } from "vue";
import { format } from "date-fns";
import Popup from "../../../components/Popup.vue";
import Confirm from "../../../components/Confirm.vue";
import DatetimePicker from "../../../components/DatetimePicker.vue";
import Eventy from "../../../helpers/eventy";
import Service from "./service";

// The sampling points and models assessing one regime -- AQR3 CAM_05, one CAM row per
// link per year. v3 edited these as a ticked list inside the regime popup; this brings
// that back, but each link stays its own row: adding inserts, editing updates that row,
// deleting deletes that row. v3 saved by deleting every link and re-inserting the ticked
// ones, which cascaded away the exceedingmethods rows hanging off them.
//
// The same rows are on Management -> Assessment data, which lists every regime's links.

const props = defineProps({
  show: Boolean,
  regime: { type: Object, default: null }
});

const emit = defineEmits(["close"]);

const links = ref([]);
const assessmentTypes = ref([]);
const loading = ref(false);

// Inline edit of one link: its id, and a working copy.
const editingId = ref(null);
const draft = ref({});

const confirmDelete = ref(null);

// Multi-add
const adding = ref(false);
const candidates = ref({ sampling_points: [], models: [] });
const ticked = ref(new Set());
const search = ref("");
const spType = ref("fixed");
const modelType = ref("model");
const addFrom = ref(null);
const addTo = ref(null);
const addDescription = ref("");
const saving = ref(false);

const regimeId = computed(() => props.regime?.id);

const title = computed(() => {
  const r = props.regime;
  if (!r) return "Linked sampling points / models";
  const what = [r.zone, r.pollutant, `${r.objective_type ?? "?"}/${r.reporting_metric ?? "?"}`]
    .filter(Boolean).join(" · ");
  return `Linked sampling points / models — ${what}`;
});

// Flask serialises timestamps as RFC 1123 strings; the API takes "yyyy-MM-dd HH:00".
const asDate = (v) => (v ? (v instanceof Date ? v : new Date(v)) : null);
const showDate = (v) => (v ? format(asDate(v), "yyyy-MM-dd HH:mm") : "—");
const toApi = (v) => {
  if (!v) return null;
  if (typeof v === "string" && /^\d{4}-\d{2}-\d{2}/.test(v)) return v;
  return format(asDate(v), "yyyy-MM-dd HH:00");
};

const loadLinks = async () => {
  if (!regimeId.value) return;
  loading.value = true;
  try {
    links.value = await Service.links(regimeId.value);
  } finally {
    loading.value = false;
  }
};

const loadCandidates = async () => {
  candidates.value = await Service.linkCandidates(regimeId.value);
  ticked.value = new Set();
};

const reset = () => {
  links.value = [];
  editingId.value = null;
  adding.value = false;
  search.value = "";
  addFrom.value = null;
  addTo.value = null;
  addDescription.value = "";
};

watch(
  () => props.show,
  async (open) => {
    reset();
    if (!open || !regimeId.value) return;
    if (assessmentTypes.value.length === 0) {
      const lookups = await Service.linkLookups();
      assessmentTypes.value = lookups.assessment_types ?? [];
    }
    await loadLinks();
  }
);

// -- Edit / delete one link ------------------------------------------------------

const startEdit = (link) => {
  editingId.value = link.id;
  draft.value = {
    ...link,
    from_time: asDate(link.from_time),
    to_time: asDate(link.to_time)
  };
};

const saveEdit = async () => {
  const d = draft.value;
  Eventy.showMessage("Saving link, please wait!", "loading");
  await Service.updateLink({
    id: d.id,
    assessment_regime_id: d.assessment_regime_id,
    sampling_point_id: d.sampling_point_id || null,
    model_id: d.model_id || null,
    assessmenttype: d.assessmenttype,
    assessmentmethodedescription: d.assessmentmethodedescription || null,
    from_time: toApi(d.from_time),
    to_time: toApi(d.to_time)
  });
  editingId.value = null;
  await loadLinks();
  Eventy.showHideMessage("Link saved", "success", 3000);
};

const doDelete = async () => {
  const link = confirmDelete.value;
  confirmDelete.value = null;
  if (!link) return;
  Eventy.showMessage("Deleting link, please wait!", "loading");
  await Service.deleteLink(link.id);
  await loadLinks();
  Eventy.showHideMessage("Link deleted", "success", 3000);
};

// -- Multi-add -------------------------------------------------------------------

const candidateRows = computed(() => {
  const rows = [
    ...(candidates.value.sampling_points ?? []).map((sp) => ({
      key: `sp:${sp.id}`, id: sp.id, kind: "Sampling point",
      label: sp.station_name ?? "?", detail: sp.sampling_point_reference_id,
      to_time: sp.to_time
    })),
    ...(candidates.value.models ?? []).map((m) => ({
      key: `mod:${m.id}`, id: m.id, kind: "Model / OBE",
      label: m.assessment_method_name ?? m.id, detail: null, to_time: null
    }))
  ];
  const q = search.value.trim().toLowerCase();
  if (!q) return rows;
  return rows.filter((r) => `${r.id} ${r.label} ${r.detail ?? ""}`.toLowerCase().includes(q));
});

const anySpTicked = computed(() => [...ticked.value].some((k) => k.startsWith("sp:")));
const anyModelTicked = computed(() => [...ticked.value].some((k) => k.startsWith("mod:")));
const allVisibleTicked = computed(
  () => candidateRows.value.length > 0 && candidateRows.value.every((r) => ticked.value.has(r.key))
);

const toggle = (key) => {
  const next = new Set(ticked.value);
  next.has(key) ? next.delete(key) : next.add(key);
  ticked.value = next;
};

const toggleAll = () => {
  const next = new Set(ticked.value);
  if (allVisibleTicked.value) candidateRows.value.forEach((r) => next.delete(r.key));
  else candidateRows.value.forEach((r) => next.add(r.key));
  ticked.value = next;
};

const openAdd = async () => {
  adding.value = true;
  spType.value = "fixed";
  modelType.value = "model";
  await loadCandidates();
};

const linkTicked = async () => {
  if (ticked.value.size === 0) return;
  // Every ticked key, not only the visible ones: a search narrows the list, it does
  // not untick what was ticked before it.
  const all = [
    ...(candidates.value.sampling_points ?? []).filter((sp) => ticked.value.has(`sp:${sp.id}`))
      .map((sp) => ({ sampling_point_id: sp.id, assessmenttype: spType.value })),
    ...(candidates.value.models ?? []).filter((m) => ticked.value.has(`mod:${m.id}`))
      .map((m) => ({ model_id: m.id, assessmenttype: modelType.value }))
  ];
  const rows = all.map((r) => ({
    ...r,
    assessment_regime_id: regimeId.value,
    assessmentmethodedescription: addDescription.value || null,
    from_time: toApi(addFrom.value),
    to_time: toApi(addTo.value)
  }));

  saving.value = true;
  try {
    Eventy.showMessage(`Linking ${rows.length} assessment method(s)...`, "loading");
    const result = await Service.linkMany(rows);
    Eventy.hideMessage();
    Eventy.showHideMessage(result.msg, "success", 4000);
    adding.value = false;
    await loadLinks();
  } catch {
    Eventy.hideMessage();
    // Request already surfaced the server message, naming the method that failed.
  } finally {
    saving.value = false;
  }
};
</script>

<template>
  <confirm :show="!!confirmDelete" title="Delete link"
           text="Deleting a link says it never happened, and the next compliance recalculation drops its CAM rows for every year — including years already submitted. If this method has stopped assessing the regime, edit the link and set Valid To instead. Delete anyway?"
           @close="confirmDelete = null" @ok="doDelete" />

  <popup :show="show" :title="title" class="w-[72rem] max-w-[95%] h-[80vh]"
         body-class="flex-1 min-h-0 flex flex-col" @on-close="emit('close')">
    <p class="text-xs text-nord3 mb-3 shrink-0">
      Each link is one AssessmentMethodId (CAM_05) for <span class="font-mono">{{ regimeId }}</span>, reported as one
      ComplianceAssessmentMethod row per year. When a method stops assessing this regime, set
      <em>Valid To</em> rather than deleting the link.
    </p>

    <!-- Linked methods ---------------------------------------------------------- -->
    <div v-if="!adding" class="flex-1 min-h-0 flex flex-col">
      <div class="flex items-center mb-2 shrink-0">
        <div class="font-bold">{{ links.length }} linked</div>
        <div class="flex-1"></div>
        <button class="button" @click="openAdd">Add sampling points / models…</button>
      </div>

      <div class="flex-1 min-h-0 overflow-auto text-xs border border-nord4">
        <table class="w-full">
          <thead class="bg-nord6 sticky top-0">
            <tr class="text-left">
              <th class="p-1.5">Assessment method</th>
              <th class="p-1.5">Kind</th>
              <th class="p-1.5">Assessment type</th>
              <th class="p-1.5">Valid from</th>
              <th class="p-1.5">Valid to</th>
              <th class="p-1.5">Description</th>
              <th class="p-1.5 w-28"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="!loading && links.length === 0">
              <td colspan="7" class="p-3 text-nord3">
                Nothing assesses this regime yet, so it produces no CAM rows — and AQR3 flags an ARZ row without CAM rows
                for deletion.
              </td>
            </tr>
            <tr v-for="link in links" :key="link.id" class="border-t border-nord5 align-top">
              <template v-if="editingId === link.id">
                <td class="p-1.5">
                  <div>{{ link.assessment_method }}</div>
                  <div class="font-mono text-nord3">{{ link.assessmentlocal_id }}</div>
                </td>
                <td class="p-1.5">{{ link.assessment_method_kind }}</td>
                <td class="p-1.5">
                  <select class="select w-full" v-model="draft.assessmenttype">
                    <option v-for="t in assessmentTypes" :key="t.value" :value="t.value">{{ t.label }}</option>
                  </select>
                </td>
                <td class="p-1.5 w-44"><DatetimePicker v-model="draft.from_time" /></td>
                <td class="p-1.5 w-44"><DatetimePicker v-model="draft.to_time" /></td>
                <td class="p-1.5"><input class="input w-full" v-model="draft.assessmentmethodedescription" /></td>
                <td class="p-1.5 whitespace-nowrap">
                  <button class="button" @click="saveEdit" :disabled="!draft.assessmenttype">Save</button>
                  <button class="button ml-1" @click="editingId = null">Cancel</button>
                </td>
              </template>
              <template v-else>
                <td class="p-1.5">
                  <div>{{ link.assessment_method }}</div>
                  <div class="font-mono text-nord3">{{ link.assessmentlocal_id }}</div>
                </td>
                <td class="p-1.5">{{ link.assessment_method_kind }}</td>
                <td class="p-1.5">{{ link.assessment_type ?? link.assessmenttype }}</td>
                <td class="p-1.5 whitespace-nowrap">{{ showDate(link.from_time) }}</td>
                <td class="p-1.5 whitespace-nowrap">{{ showDate(link.to_time) }}</td>
                <td class="p-1.5">{{ link.assessmentmethodedescription }}</td>
                <td class="p-1.5 whitespace-nowrap">
                  <button class="button" @click="startEdit(link)" :disabled="editingId !== null">Edit</button>
                  <button class="button ml-1" @click="confirmDelete = link" :disabled="editingId !== null">Delete</button>
                </td>
              </template>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Multi-add --------------------------------------------------------------- -->
    <div v-else class="flex-1 min-h-0 flex flex-col">
      <div class="text-xs text-nord3 mb-2 shrink-0">
        Sampling points and models measuring <strong>{{ candidates.regime?.pollutant ?? "the regime's pollutant" }}</strong>
        that are not already linked with an open-ended period. Tick as many as apply; one link is created for each.
      </div>

      <div class="flex gap-3 items-end mb-2 shrink-0 flex-wrap">
        <div>
          <div class="font-bold text-sm">Search</div>
          <input class="input w-56" v-model="search" placeholder="station, id or reference" />
        </div>
        <div v-if="anySpTicked">
          <div class="font-bold text-sm">Type for sampling points</div>
          <select class="select w-48" v-model="spType">
            <option v-for="t in assessmentTypes" :key="t.value" :value="t.value">{{ t.label }}</option>
          </select>
        </div>
        <div v-if="anyModelTicked">
          <div class="font-bold text-sm">Type for models</div>
          <select class="select w-48" v-model="modelType">
            <option v-for="t in assessmentTypes" :key="t.value" :value="t.value">{{ t.label }}</option>
          </select>
        </div>
        <div class="w-44">
          <div class="font-bold text-sm">Valid from</div>
          <DatetimePicker v-model="addFrom" />
        </div>
        <div class="w-44">
          <div class="font-bold text-sm">Valid to</div>
          <DatetimePicker v-model="addTo" />
        </div>
        <div class="flex-1 min-w-48">
          <div class="font-bold text-sm">Description</div>
          <input class="input w-full" v-model="addDescription" placeholder="optional, applied to every new link" />
        </div>
      </div>

      <div class="flex-1 min-h-0 overflow-auto text-xs border border-nord4">
        <table class="w-full">
          <thead class="bg-nord6 sticky top-0">
            <tr class="text-left">
              <th class="p-1.5 w-8">
                <input type="checkbox" :checked="allVisibleTicked" @change="toggleAll" title="Tick every listed row" />
              </th>
              <th class="p-1.5">Station / model</th>
              <th class="p-1.5">Id</th>
              <th class="p-1.5">Reference</th>
              <th class="p-1.5">Kind</th>
              <th class="p-1.5">Sampling point ended</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="candidateRows.length === 0">
              <td colspan="6" class="p-3 text-nord3">Nothing left to link.</td>
            </tr>
            <tr v-for="r in candidateRows" :key="r.key" class="border-t border-nord5 cursor-pointer hover:bg-nord6"
                @click="toggle(r.key)">
              <td class="p-1.5"><input type="checkbox" :checked="ticked.has(r.key)" @click.stop="toggle(r.key)" /></td>
              <td class="p-1.5">{{ r.label }}</td>
              <td class="p-1.5 font-mono">{{ r.id }}</td>
              <td class="p-1.5 font-mono">{{ r.detail ?? "" }}</td>
              <td class="p-1.5">{{ r.kind }}</td>
              <td class="p-1.5 whitespace-nowrap">{{ r.to_time ? showDate(r.to_time) : "" }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="border-t border-gray-300 mt-3 shrink-0"></div>
    <div class="flex justify-end pt-2 gap-4 shrink-0">
      <template v-if="adding">
        <button class="button" :disabled="saving || ticked.size === 0" @click="linkTicked">
          {{ saving ? "Linking..." : `Link ${ticked.size} selected` }}
        </button>
        <button class="button" @click="adding = false">Back</button>
      </template>
      <button v-else class="button" @click="emit('close')">Close</button>
    </div>
  </popup>
</template>
