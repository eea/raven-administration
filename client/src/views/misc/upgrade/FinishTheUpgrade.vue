<script setup>
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import CommonLayout from "../../../components/CommonLayout.vue";
import ToolBar from "../../../components/ToolBar.vue";
import Container from "../../../components/Container.vue";
import Service from "./service";
import Eventy from "../../../helpers/eventy";

// What is left to do before this database can be submitted to Reportnet 3.
//
// The list is derived from the database every time it is opened, not stored, so
// an item disappears as soon as the operator actually fixes it. That is the whole
// point of the page: a migration report is a snapshot of one afternoon, and goes
// stale the moment someone starts working through it.

const tasks = ref([]);
const loading = ref(true);
const repairing = ref("");

// Which page each task sends you to. Kept here rather than in the API so the
// backend does not have to know what the client's routes are called.
const ROUTES = {
  "regime-identifiers": "AssessmentRegimes",
  "regime-no-zone": "AssessmentRegimes",
  "classification-document-missing": "Documents",
  "settings-incomplete": "Settings",
  "stations-no-eoi": "Stations",
  "authorities-no-email": "Authorities",
  "compliance-not-calculated": "Dataflow",
  "sampling-points-no-regime": "AssessmentRegimes",
  "no-sampling-point-locations": "SamplingPoints"
};

const router = useRouter();
const blockers = computed(() => tasks.value.filter((t) => t.severity === "blocker").length);

const load = async () => {
  loading.value = true;
  try {
    const data = await Service.tasks();
    tasks.value = data?.tasks ?? [];
  } finally {
    loading.value = false;
  }
};

onMounted(load);

const goto = (task) => {
  const name = ROUTES[task.id];
  if (name) router.push({ name });
};

// The one task this page can complete on your behalf. Everything else is a
// decision or a piece of missing information, and belongs to a person.
const repair = async (task) => {
  const ids = task.examples ?? [];
  if (!ids.length) return;
  repairing.value = task.id;
  Eventy.showMessage(`Rebuilding ${ids.length} identifier(s)...`, "loading");
  let done = 0;
  const failed = [];
  for (const id of ids) {
    try {
      const r = await Service.repairRegimeId(id);
      if (r?.changed) done += 1;
    } catch (e) {
      failed.push(id);
    }
  }
  repairing.value = "";
  if (failed.length) {
    Eventy.showHideMessage(
      `${done} rebuilt. ${failed.length} could not be — open Assessment Regime Zones and ` +
        `fill in what they are missing first.`,
      "warning",
      6000
    );
  } else {
    Eventy.showHideMessage(`${done} identifier(s) rebuilt`, "success", 4000);
  }
  await load();
};
</script>

<template>
  <common-layout>
    <tool-bar title="Finish the upgrade" :show-add="false" :show-download="false" :show-filter="false" />

    <container class="p-4!">
      <div v-if="loading" class="text-nord3">Checking…</div>

      <div v-else-if="!tasks.length" class="p-4 rounded border border-nord14 bg-nord14/10">
        <div class="font-bold">Nothing outstanding</div>
        <div class="text-nord3 text-sm mt-1">
          Everything this check knows how to look for is in place. Build the export on the
          Dataflow page to confirm Reportnet 3 accepts it.
        </div>
      </div>

      <template v-else>
        <p class="text-sm text-nord3 mb-4">
          {{ tasks.length }} thing{{ tasks.length === 1 ? "" : "s" }} to finish before this
          database can be submitted<span v-if="blockers">, {{ blockers }} of which Reportnet 3
          will reject the submission over</span>. This list is rebuilt every time you open the
          page, so an item disappears once it is actually done.
        </p>

        <div
          v-for="t in tasks"
          :key="t.id"
          class="mb-3 p-3 rounded border"
          :class="t.severity === 'blocker' ? 'border-nord11 bg-nord11/5' : 'border-nord13 bg-nord13/10'"
        >
          <div class="flex items-baseline gap-2">
            <span
              class="text-xs font-bold uppercase tracking-wide px-2 py-0.5 rounded"
              :class="t.severity === 'blocker' ? 'bg-nord11/20 text-nord11' : 'bg-nord13/20 text-nord3'"
            >
              {{ t.severity === "blocker" ? "Must fix" : "Should fix" }}
            </span>
            <span class="font-bold">{{ t.title }}</span>
          </div>

          <p class="text-sm text-nord3 mt-2">{{ t.why }}</p>

          <ol class="text-sm text-nord3 mt-2 ml-5 list-decimal">
            <li v-for="(step, i) in t.how" :key="i">{{ step }}</li>
          </ol>

          <div v-if="t.examples?.length" class="font-mono text-xs text-nord3 mt-2 break-all">
            {{ t.examples.join(", ") }}
            <span v-if="t.count > t.examples.length"> and {{ t.count - t.examples.length }} more</span>
          </div>

          <div class="mt-3 flex gap-2">
            <button v-if="ROUTES[t.id]" class="button" @click="goto(t)">
              Go to {{ t.where }}
            </button>
            <button
              v-if="t.id === 'regime-identifiers'"
              class="button"
              :disabled="repairing === t.id"
              @click="repair(t)"
            >
              Rebuild {{ t.examples?.length }} identifier(s) now
            </button>
          </div>
        </div>
      </template>
    </container>
  </common-layout>
</template>
