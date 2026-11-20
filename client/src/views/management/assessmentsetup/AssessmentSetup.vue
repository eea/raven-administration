<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import CommonLayout from "../../../components/CommonLayout.vue";
import DataTable from "../../../components/DataTable.vue";
import ComplianceFeedback from "../../../components/ComplianceFeedback.vue";
import Eventy from "../../../helpers/eventy";
import GenerateRegimes from "../assessmentregimes/GenerateRegimes.vue";
import LinkedMethods from "../assessmentregimes/LinkedMethods.vue";
import GenerateAssessmentData from "../assessmentdata/GenerateAssessmentData.vue";
import RegimesService from "../assessmentregimes/service";
import LinksService from "../assessmentdata/service";
import ComplianceService from "../complianceassessmentmethod/service";
import IconLinks from "~icons/material-symbols/link";
import IconOpen from "~icons/material-symbols/open-in-new";
import AssessmentRegimes from "../assessmentregimes/AssessmentRegimes.vue";
import AssessmentData from "../assessmentdata/AssessmentData.vue";
import ComplianceAssessmentMethod from "../complianceassessmentmethod/ComplianceAssessmentMethod.vue";

// The assessment setup for one year, in three steps on one page:
//   1 Regimes          which zone x objective combinations are assessed (AQR3 ARZ)
//   2 Sampling points  which methods assess them (Assessment data, the CAM junction)
//   3 Compliance       ComplianceAssessmentMethod, derived from the two
//
// It shows what a user needs to get a year ready and leaves the AQR3 technicalities
// (ARE_/ATT_ ids, aggregation processes, attainment index, SRS, hand-kept CAM figures)
// to the raw tables, one more view in each step's switch, mounted (and so fetched) only
// when first picked. The steps reuse the wizard components
// those pages open as popups, embedded here; all three stay mounted, so each tab's
// badge is known without opening it.

const route = useRoute();
const router = useRouter();

const now = new Date().getFullYear();
const years = Array.from({ length: 6 }, (_, i) => now - i);
const year = ref(Number(route.query.year) || now - 1);
// ?step= (and ?view=table) from the standalone pages' wizard and back buttons.
const step = ref([1, 2, 3].includes(Number(route.query.step)) ? Number(route.query.step) : 1);

// Each step's view switch. "table" is the raw AQR3 table, mounted on first pick and
// then only hidden, so its filters and scroll survive switching away.
const view = ref({ 1: "missing", 2: "missing", 3: "summary" });
const tableMounted = ref(new Set());
const showView = (n, v) => {
  view.value[n] = v;
  if (v === "table") tableMounted.value.add(n);
};
if (route.query.view === "table") showView(step.value, "table");
const segClass = (n, v) => (view.value[n] === v ? "bg-nord10 text-white" : "text-nord1 hover:bg-nord6");

// The raw tables as pages of their own; they show a way back here (Manager, ?from=setup).
const FULL_PAGES = { 1: "AssessmentRegimes", 2: "AssessmentData", 3: "ComplianceAssessmentMethod" };
const openFullPage = (n) => router.push({ name: FULL_PAGES[n], query: { year: year.value, step: n, from: "setup" } });

// -- Step 1 ---------------------------------------------------------------------
const regimeLookups = ref({});
const regimes = ref([]);           // the year's existing regimes
const linkCounts = ref({});        // regime id -> number of linked methods
const missingRegimes = ref(null);  // from GenerateRegimes, null until it has loaded
const linksRegime = ref(null);

const regimeColumns = [
  { field: "zone", headerName: "Zone", sortable: true, filter: true, minWidth: 150, flex: 1.5 },
  { field: "pollutant", headerName: "Pollutant", sortable: true, filter: true, minWidth: 100, flex: 1 },
  { field: "objective", headerName: "Objective", sortable: true, filter: true, minWidth: 130, flex: 1,
    valueGetter: (p) => [p.data?.objective_type, p.data?.protection_target, p.data?.reporting_metric].filter(Boolean).join(" / ") },
  { field: "assessment_threshold_exceedance", headerName: "Classification", sortable: true, filter: true, minWidth: 120, flex: 1,
    valueFormatter: (p) => p.value || "—" },
  { field: "methods", headerName: "Linked methods", sortable: true, filter: true, minWidth: 110, flex: 0.8,
    valueGetter: (p) => linkCounts.value[p.data?.id] ?? 0,
    cellClass: (p) => (p.value ? "" : "text-nord11 font-bold"),
    headerTooltip: "Sampling points and models assessing the regime. A regime with none reports no compliance." }
];

const loadRegimes = async () => {
  try {
    const [all, links] = await Promise.all([RegimesService.get(), LinksService.get()]);
    regimes.value = (all ?? []).filter((r) => Number(r.classification_year) === year.value);
    const counts = {};
    for (const l of links ?? []) counts[l.assessment_regime_id] = (counts[l.assessment_regime_id] ?? 0) + 1;
    linkCounts.value = counts;
  } catch {
    Eventy.showHideMessage("Could not load the assessment regimes.", "error", 4000);
  }
};

const onRegimesCounted = (n) => {
  missingRegimes.value = n;
  // Open on whatever needs attention: the missing ones, else the list.
  if (n === 0 && view.value[1] === "missing") view.value[1] = "existing";
};

const onRegimeMenu = ({ action, data }) => {
  if (action === "linked_methods") linksRegime.value = data?.row ?? null;
};

const unlinkedRegimes = computed(() => regimes.value.filter((r) => !linkCounts.value[r.id]).length);

// -- Step 2 ---------------------------------------------------------------------
const missingLinks = ref(null);
// Remount step 2 when step 1 changed the regimes, so it reloads its candidates.
const linksVersion = ref(0);

const onLinksCounted = ({ missing }) => (missingLinks.value = missing);
// Remount the raw tables when a step itself wrote rows, so they show them. Not after an
// edit made in a raw table -- that one already shows it, and would lose its state.
const rawVersion = ref(0);

const onGenerated = async () => {
  await loadRegimes();
  linksVersion.value++;
  rawVersion.value++;
};
const onLinked = async () => {
  await loadRegimes();
  rawVersion.value++;
};
const onLinksPopupClosed = async () => {
  linksRegime.value = null;
  await loadRegimes();
  linksVersion.value++;
  rawVersion.value++;
};
// An edit in the regimes or links table changes what steps 1 and 2 count.
const onRawRegimesOrLinksChanged = async () => {
  await loadRegimes();
  linksVersion.value++;
};

const linkedTotal = computed(() => regimes.value.reduce((n, r) => n + (linkCounts.value[r.id] ?? 0), 0));

// -- Step 3 ---------------------------------------------------------------------
const camYears = ref([]);
const camRows = ref([]);
const recalc = ref(null);
const running = ref(false);
const camLoading = ref(false);

const calculated = computed(() => camYears.value.includes(year.value));
const activeCam = computed(() => camRows.value.filter((r) => !r.deletion));
const incomplete = computed(() => activeCam.value.filter((r) => r.pollution_level === null || r.pollution_level === undefined).length);
const exceeding = computed(() => activeCam.value.filter((r) => r.is_exceedance === true).length);

const yesNo = (v) => (v === null || v === undefined ? "—" : v ? "Yes" : "No");
const camColumns = [
  { field: "zone_name", headerName: "Zone", sortable: true, filter: true, minWidth: 140, flex: 1.3 },
  { field: "pollutant", headerName: "Pollutant", sortable: true, filter: true, minWidth: 90, flex: 0.8 },
  { field: "objective", headerName: "Objective", sortable: true, filter: true, minWidth: 110, flex: 0.9,
    valueGetter: (p) => [p.data?.objective_type, p.data?.reporting_metric].filter(Boolean).join(" / ") },
  { field: "assessment_method", headerName: "Assessed by", sortable: true, filter: true, minWidth: 170, flex: 1.5,
    valueGetter: (p) => p.data?.assessment_method ?? p.data?.assessment_method_id },
  { field: "assessment_type", headerName: "Type", sortable: true, filter: true, minWidth: 90, flex: 0.7 },
  { field: "is_exceedance", headerName: "Exceeds", sortable: true, filter: true, minWidth: 80, flex: 0.6,
    valueFormatter: (p) => yesNo(p.value),
    cellClass: (p) => (p.value === true ? "text-nord11 font-bold" : "") },
  { field: "pollution_level", headerName: "Level", sortable: true, filter: true, minWidth: 80, flex: 0.6,
    valueFormatter: (p) => (p.value === null || p.value === undefined ? "missing" : p.value),
    cellClass: (p) => (p.value === null || p.value === undefined ? "text-nord11" : ""),
    headerTooltip: "AQR3 requires a pollution level on every row" },
  { field: "data_coverage", headerName: "Coverage %", sortable: true, filter: true, minWidth: 90, flex: 0.6,
    valueFormatter: (p) => p.value ?? "—" },
  { field: "preliminary_reason", headerName: "Preliminary", sortable: true, filter: true, minWidth: 100, flex: 0.8,
    valueFormatter: (p) => p.value || "" }
];
const camRowStyle = (p) => (p.data?.deletion ? { opacity: 0.5, textDecoration: "line-through" } : null);

const loadCompliance = async () => {
  camLoading.value = true;
  try {
    const lookups = await ComplianceService.lookups();
    camYears.value = lookups?.years ?? [];
    camRows.value = calculated.value ? (await ComplianceService.get(year.value)) ?? [] : [];
  } catch {
    Eventy.showHideMessage("Could not load compliance.", "error", 4000);
  } finally {
    camLoading.value = false;
  }
};

const recalculate = async () => {
  running.value = true;
  Eventy.showMessage(`Calculating compliance for ${year.value}...`, "loading");
  try {
    recalc.value = await ComplianceService.recalculate(year.value);
    Eventy.hideMessage();
    await loadCompliance();
    rawVersion.value++;
  } catch {
    Eventy.hideMessage();
    // Request already surfaced the server message.
  } finally {
    running.value = false;
  }
};


// -- Tabs -----------------------------------------------------------------------
// state: "done" | "todo" | "blocked" | "loading"
const tabs = computed(() => {
  const r = regimes.value.length;
  const one = missingRegimes.value === null
    ? { state: "loading", note: "…" }
    : missingRegimes.value > 0
      ? { state: "todo", note: `${missingRegimes.value} to generate` }
      : r > 0 ? { state: "done", note: `${r} regime(s)` } : { state: "blocked", note: "nothing to assess" };

  const two = r === 0
    ? { state: "blocked", note: "needs regimes" }
    : missingLinks.value === null
      ? { state: "loading", note: "…" }
      : missingLinks.value > 0
        ? { state: "todo", note: `${missingLinks.value} to link` }
        : unlinkedRegimes.value > 0
          ? { state: "todo", note: `${unlinkedRegimes.value} regime(s) without a method` }
          : { state: "done", note: `${linkedTotal.value} linked` };

  const three = linkedTotal.value === 0
    ? { state: "blocked", note: "needs links" }
    : !calculated.value
      ? { state: "todo", note: "not calculated" }
      : incomplete.value > 0
        ? { state: "todo", note: `${incomplete.value} without a level` }
        : { state: "done", note: `${activeCam.value.length} row(s)` };

  return [
    { n: 1, label: "Regimes", ...one },
    { n: 2, label: "Sampling points", ...two },
    { n: 3, label: "Compliance", ...three }
  ];
});

const mark = { done: "✓", todo: "⚠", blocked: "–", loading: "" };
const markClass = { done: "text-nord14", todo: "text-nord12", blocked: "text-nord3", loading: "text-nord3" };

// -- Year -----------------------------------------------------------------------
const loadYear = () => {
  missingRegimes.value = null;
  missingLinks.value = null;
  recalc.value = null;
  if (view.value[1] === "existing") view.value[1] = "missing";
  loadRegimes();
  loadCompliance();
};

watch(year, (y) => {
  router.replace({ query: { ...route.query, year: y } });
  loadYear();
});

onMounted(async () => {
  try {
    regimeLookups.value = (await RegimesService.lookups()) ?? {};
  } catch {
    // The document picker stays empty; generating still works.
  }
  loadYear();
});
</script>

<template>
  <common-layout>
    <linked-methods :show="!!linksRegime" :regime="linksRegime" @close="onLinksPopupClosed" />

    <div class="flex flex-wrap items-center gap-3 mb-2">
      <h1 class="font-display font-bold text-xl text-nord0">Assessment setup</h1>
      <select v-model="year" class="select w-28 text-sm" title="Classification and reporting year">
        <option v-for="y in years" :key="y" :value="y">{{ y }}</option>
      </select>
    </div>

    <div class="flex flex-wrap gap-2 mb-3">
      <button v-for="t in tabs" :key="t.n"
              class="px-3 py-2 rounded-lg border text-left flex items-center gap-2 min-w-48 transition-colors"
              :class="step === t.n ? 'border-nord10 bg-nord10/10' : 'border-gray-300 hover:bg-nord6'"
              @click="step = t.n">
        <span class="grid place-items-center size-6 rounded-full text-xs font-bold"
              :class="step === t.n ? 'bg-nord10 text-white' : 'bg-nord4 text-nord1'">{{ t.n }}</span>
        <span class="flex flex-col leading-tight">
          <span class="font-bold text-sm text-nord0">{{ t.label }}</span>
          <span class="text-xs" :class="markClass[t.state]">{{ mark[t.state] }} {{ t.note }}</span>
        </span>
      </button>
    </div>

    <!-- 1 Regimes -->
    <div v-show="step === 1" class="flex-1 min-h-[32rem] flex flex-col">
      <div class="flex items-center gap-1 mb-2 text-sm">
        <button class="px-2 py-1 rounded" :class="segClass(1, 'missing')" @click="showView(1, 'missing')">To generate ({{ missingRegimes ?? "…" }})</button>
        <button class="px-2 py-1 rounded" :class="segClass(1, 'existing')" @click="showView(1, 'existing')">Existing regimes ({{ regimes.length }})</button>
        <button class="px-2 py-1 rounded" :class="segClass(1, 'table')" @click="showView(1, 'table')"
                title="Every year's regimes: edit, delete, import, ids and population">All regimes — table</button>
        <span class="flex-1"></span>
        <button v-if="view[1] === 'table'" class="text-xs text-nord10 hover:underline flex items-center gap-1" @click="openFullPage(1)">
          Open as full page <icon-open class="text-sm" />
        </button>
      </div>

      <generate-regimes v-show="view[1] === 'missing'" embedded :initial-year="year" :lookups="regimeLookups"
                        @counted="onRegimesCounted" @generated="onGenerated" @next="step = 2" />

      <div v-show="view[1] === 'existing'" class="flex-1 min-h-0 flex flex-col">
        <p class="text-xs text-nord3 mb-2">
          The regimes of {{ year }}. Right-click or double-click one to see and change the sampling points and
          models assessing it — the only place a model is linked.
          <span v-if="unlinkedRegimes" class="text-nord11">{{ unlinkedRegimes }} regime(s) have no method and will report no compliance.</span>
        </p>
        <div class="flex-1 min-h-0 text-xs">
          <DataTable :data="regimes" :columns="regimeColumns" :filter="true" :floating-filter="false"
                     @on-double-click="(row) => (linksRegime = row)" @context-menu-action="onRegimeMenu">
            <template #context-menu-items="{ handleAction }">
              <div class="pl-2 pr-4 py-1.5 flex cursor-pointer hover:bg-nord6" @click="handleAction('linked_methods')">
                <icon-links class="text-nord10 text-base self-center" />
                <div class="self-center ml-1">Linked sampling points / models</div>
              </div>
            </template>
          </DataTable>
        </div>
      </div>

      <div v-if="tableMounted.has(1)" v-show="view[1] === 'table'" class="flex-1 min-h-0 flex flex-col">
        <assessment-regimes :key="`regimes-${rawVersion}`" embedded @changed="onRawRegimesOrLinksChanged" />
      </div>
    </div>

    <!-- 2 Sampling points -->
    <div v-show="step === 2" class="flex-1 min-h-[32rem] flex flex-col">
      <div class="flex items-center gap-1 mb-2 text-sm">
        <button class="px-2 py-1 rounded" :class="segClass(2, 'missing')" @click="showView(2, 'missing')">To link ({{ missingLinks ?? "…" }})</button>
        <button class="px-2 py-1 rounded" :class="segClass(2, 'table')" @click="showView(2, 'table')"
                title="Every link: edit, set Valid To, delete, import">All links — table</button>
        <span class="flex-1"></span>
        <button v-if="view[2] === 'table'" class="text-xs text-nord10 hover:underline flex items-center gap-1" @click="openFullPage(2)">
          Open as full page <icon-open class="text-sm" />
        </button>
      </div>

      <generate-assessment-data v-show="view[2] === 'missing'" :key="`links-${linksVersion}`" embedded :initial-year="year"
                                @counted="onLinksCounted" @linked="onLinked" @back="step = 1" @next="step = 3" />

      <div v-if="tableMounted.has(2)" v-show="view[2] === 'table'" class="flex-1 min-h-0 flex flex-col">
        <assessment-data :key="`links-raw-${rawVersion}`" embedded @changed="onRawRegimesOrLinksChanged" />
      </div>
    </div>

    <!-- 3 Compliance -->
    <div v-show="step === 3" class="flex-1 min-h-[32rem] flex flex-col">
      <div class="flex items-center gap-1 mb-2 text-sm">
        <button class="px-2 py-1 rounded" :class="segClass(3, 'summary')" @click="showView(3, 'summary')">Summary</button>
        <button class="px-2 py-1 rounded" :class="segClass(3, 'table')" @click="showView(3, 'table')"
                title="Enter pollution levels, MQI and uncertainty; retract rows">Edit table</button>
        <span class="flex-1"></span>
        <button v-if="view[3] === 'table'" class="text-xs text-nord10 hover:underline flex items-center gap-1" @click="openFullPage(3)">
          Open as full page <icon-open class="text-sm" />
        </button>
        <button v-else class="button" :disabled="running || linkedTotal === 0" @click="recalculate">
          {{ running ? "Calculating..." : calculated ? `Recalculate ${year}` : `Calculate ${year}` }}
        </button>
      </div>

      <div v-show="view[3] === 'summary'" class="flex-1 min-h-0 flex flex-col">
        <p class="text-xs text-nord3 mb-2">
          Compliance per regime and method, derived from steps 1 and 2 and the measured data. Calculate again after
          changing regimes or links. Values entered in <em>Edit table</em> are kept.
        </p>

        <ComplianceFeedback v-if="recalc" :summary="recalc" @dismiss="recalc = null" />

        <div class="text-xs text-nord3 mb-1">
          <template v-if="camLoading">Loading...</template>
          <template v-else-if="!calculated">Not calculated for {{ year }} yet.</template>
          <template v-else>
            {{ activeCam.length }} row(s) for {{ year }}; {{ exceeding }} exceed<template v-if="incomplete">,
            <a class="text-nord11 hover:underline cursor-pointer" @click="showView(3, 'table')">{{ incomplete }} have no pollution level</a>
            (AQR3 requires one)</template>.
          </template>
        </div>
        <div class="flex-1 min-h-0 text-xs">
          <DataTable :data="camRows" :columns="camColumns" :filter="true" :floating-filter="false"
                     :get-row-style="camRowStyle" />
        </div>
      </div>

      <div v-if="tableMounted.has(3)" v-show="view[3] === 'table'" class="flex-1 min-h-0 flex flex-col">
        <compliance-assessment-method :key="`cam-${year}-${rawVersion}`" embedded :year="year"
                                      @changed="loadCompliance" />
      </div>
    </div>
  </common-layout>
</template>
