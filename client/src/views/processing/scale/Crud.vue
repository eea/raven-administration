<script setup>
import { ref, watch, computed, nextTick } from "vue";
import Popup from "../../../components/Popup.vue";
import DatetimePicker from "../../../components/DatetimePicker.vue";
import Chart from "chart.js/auto";
import "chartjs-adapter-luxon";
import zoomPlugin from "chartjs-plugin-zoom";
import { palette } from "../../data/historical/plot";
import Service from "./service";

Chart.register(zoomPlugin);

const props = defineProps({
  show: Boolean,
  obj: Object,
  isEdit: Boolean,
  groupMembers: { type: Array, default: () => [] },
  primaryPollutant: { type: String, default: "" },
  scalingpoints: { type: Array, default: () => [] }
});

const emit = defineEmits(["save", "close"]);
const _obj = ref({});
const _members = ref([]);

// Preview state
const showPreview = ref(false);
const previewLoading = ref(false);
const previewData = ref([]);
const previewMessage = ref("");
const previewColorMap = ref(new Map());
const previewPollutantMap = ref(new Map());
const previewRange = ref({ min: null, max: null });
const localScalingpoints = ref([]);
const canvas1 = ref(null);
const canvas2 = ref(null);
const canvas3 = ref(null);
let pChart1 = null, pChart2 = null, pChart3 = null;

const destroyPreviewCharts = () => {
  pChart1?.destroy(); pChart1 = null;
  pChart2?.destroy(); pChart2 = null;
  pChart3?.destroy(); pChart3 = null;
};

watch(
  () => props.show,
  async () => {
    _obj.value = Object.assign({}, props.obj);

    if (!props.isEdit && !_obj.value.timestamp) {
      const now = new Date();
      now.setMinutes(0, 0, 0);
      const year = now.getFullYear();
      const month = String(now.getMonth() + 1).padStart(2, "0");
      const day = String(now.getDate()).padStart(2, "0");
      const hour = String(now.getHours()).padStart(2, "0");
      _obj.value.timestamp = `${year}-${month}-${day} ${hour}:00:00`;
    }

    _members.value = props.groupMembers.map((m) => ({
      id: m.id,
      pollutant: m.pollutant,
      scaling_point_id: m.scaling_point_id ?? null,
      zero_point: m.zero_point ?? null,
      span_value: m.span_value ?? null,
      gas_concentration: m.gas_concentration ?? (props.obj?.gas_concentration ?? null)
    }));

    // Reset preview
    showPreview.value = false;
    previewLoading.value = false;
    previewData.value = [];
    previewMessage.value = "";
    previewRange.value = { min: null, max: null };
    localScalingpoints.value = [];
    destroyPreviewCharts();

    // Load scaling points so duplicate-timestamp check and charts work without "Show scaling points" being clicked
    if (props.show && _obj.value.sampling_point_id) {
      localScalingpoints.value = await Service.scalingpoints({ sampling_point_id: _obj.value.sampling_point_id });
    }
  }
);

const isEmpty = (val) => val === null || val === undefined || val === "";

const memberValid = (m) =>
  !isEmpty(m.zero_point) && !isEmpty(m.span_value) && !isEmpty(m.gas_concentration) &&
  Number(m.zero_point) !== Number(m.span_value);

const isDuplicateTimestamp = computed(() => {
  if (props.isEdit || !_obj.value.timestamp) return false;
  const ts = _obj.value.timestamp.slice(0, 16); // YYYY-MM-DD HH:MM
  return localScalingpoints.value.some(
    (r) => r.sampling_point_id === _obj.value.sampling_point_id && r.timestamp === ts
  );
});

const isFormValid = computed(() =>
  !!_obj.value.timestamp && !isDuplicateTimestamp.value && memberValid(_obj.value) && _members.value.every(memberValid)
);

const showSpanError = (zero, span) =>
  !isEmpty(zero) && !isEmpty(span) && Number(zero) === Number(span);

const memberPayload = (m, timestamp) => ({
  sampling_point_id: m.id,
  timestamp,
  zero_point: m.zero_point,
  span_value: m.span_value,
  gas_concentration: m.gas_concentration
});

const onSave = () => {
  const ts = _obj.value.timestamp;
  const primary = Object.assign({}, _obj.value);

  if (props.isEdit) {
    primary.current_timestamp = props.obj.timestamp;
    const members = _members.value.map((m) => ({
      ...memberPayload(m, ts),
      id: m.scaling_point_id ?? null,
      current_timestamp: props.obj.timestamp
    }));
    emit("save", [primary, ...members]);
  } else {
    emit("save", [primary, ..._members.value.map((m) => memberPayload(m, ts))]);
  }
};

const groupBySp = (rows) => {
  const map = new Map();
  for (const r of rows) {
    if (!map.has(r.sampling_point_id)) map.set(r.sampling_point_id, { pollutant: r.pollutant, rows: [] });
    map.get(r.sampling_point_id).rows.push(r);
  }
  return [...map.entries()];
};

const miniChartConfig = (data, range = {}) => ({
  type: "line",
  data,
  options: {
    animation: false,
    responsive: true,
    maintainAspectRatio: false,
    interaction: { intersect: false, mode: "index", axis: "x" },
    plugins: {
      legend: { display: true, position: "bottom", labels: { boxWidth: 10, font: { size: 11 } } },
      tooltip: { backgroundColor: "#fff", borderColor: "#D8DEE9", borderWidth: 1, bodyColor: "#2E3440", titleColor: "#2E3440" }
    },
    scales: {
      x: {
        type: "time",
        adapters: { date: { zone: "UTC" } },
        time: { tooltipFormat: "yyyy-MM-dd HH", displayFormats: { hour: "MM-dd HH", day: "yyyy-MM-dd", month: "yyyy-MM" } },
        ticks: { maxTicksLimit: 8, maxRotation: 0 },
        ...(range.min ? { min: range.min } : {}),
        ...(range.max ? { max: range.max } : {})
      },
      y: { beginAtZero: false }
    }
  }
});

const renderPreviewCharts = () => {
  destroyPreviewCharts();
  const groups = groupBySp(localScalingpoints.value);

  // New point values for each SP
  const newTs = (_obj.value.timestamp || "").replace(" ", "T");
  const allSps = [
    { id: _obj.value.sampling_point_id, pollutant: props.primaryPollutant, zero: Number(_obj.value.zero_point), span: Number(_obj.value.span_value), gas: Number(_obj.value.gas_concentration) },
    ..._members.value.map((m) => ({ id: m.id, pollutant: m.pollutant, zero: Number(m.zero_point), span: Number(m.span_value), gas: Number(m.gas_concentration) }))
  ];

  // In edit mode, exclude the old version of the point being edited from historical rows (it's replaced by the new point)
  const editTs = props.isEdit ? (props.obj.timestamp || "").replace(" ", "T").slice(0, 16) : null;

  // Merge: historical rows for each SP + insert the new point in chronological order
  // Keep only ±5 surrounding points for the preview charts (just context, not full history)
  const PREVIEW_CONTEXT = 5;
  const mergedGroups = allSps.map((sp) => {
    const existing = groups.find(([spId]) => spId === sp.id);
    let histRows = existing ? existing[1].rows.map((o) => ({ x: o.timestamp.replace(" ", "T"), zero: o.zero_point, span: o.span_value, gas: o.gas_concentration })) : [];
    if (editTs) histRows = histRows.filter((r) => r.x.slice(0, 16) !== editTs);
    // Find insertion index to get surrounding context
    const insertIdx = histRows.findIndex((r) => new Date(r.x) > new Date(newTs));
    const before = insertIdx === -1 ? histRows.slice(-PREVIEW_CONTEXT) : histRows.slice(Math.max(0, insertIdx - PREVIEW_CONTEXT), insertIdx);
    const after = insertIdx === -1 ? [] : histRows.slice(insertIdx, insertIdx + PREVIEW_CONTEXT);
    const allRows = [...before, { x: newTs, zero: sp.zero, span: sp.span, gas: sp.gas, isNew: true }, ...after];
    allRows.sort((a, b) => new Date(a.x) - new Date(b.x));
    return { id: sp.id, pollutant: sp.pollutant, rows: allRows };
  });

  // Chart 1 & 2: auto-scale to data (no range constraint — avoids microsecond clipping of historical points)
  // Chart 3: use affected observation range from backend
  let chart3Range = { ...previewRange.value };
  if (!chart3Range.min && !chart3Range.max && previewData.value.length > 0) {
    const allTimes = previewData.value.flatMap((d) => d.values.map((v) => v.to_time)).filter(Boolean).sort();
    if (allTimes.length > 0) chart3Range = { min: allTimes[0], max: allTimes[allTimes.length - 1] };
  }

  // Chart 1: zero-point history (connected line ending at new point)
  pChart1 = new Chart(canvas1.value, miniChartConfig({
    datasets: mergedGroups.map((g) => {
      const color = previewColorMap.value.get(g.id) || "#ccc";
      return {
        label: `${g.pollutant} 0-point`,
        data: g.rows.map((r) => ({ x: r.x, y: r.zero })),
        borderColor: color, backgroundColor: color,
        pointRadius: g.rows.map((r) => r.isNew ? 5 : 2),
        pointStyle: g.rows.map((r) => r.isNew ? "triangle" : "circle"),
        borderWidth: 2
      };
    })
  }));

  // Chart 2: span + gas history (connected lines ending at new point)
  const c2Datasets = [];
  mergedGroups.forEach((g) => {
    const color = previewColorMap.value.get(g.id) || "#ccc";
    c2Datasets.push({
      label: `${g.pollutant} Span`,
      data: g.rows.map((r) => ({ x: r.x, y: r.span })),
      borderColor: color, backgroundColor: color,
      pointRadius: g.rows.map((r) => r.isNew ? 5 : 2),
      pointStyle: g.rows.map((r) => r.isNew ? "triangle" : "circle"),
      borderWidth: 2
    });
    c2Datasets.push({
      label: `${g.pollutant} Gas`,
      data: g.rows.map((r) => ({ x: r.x, y: r.gas })),
      borderColor: color + "88", backgroundColor: color + "88",
      pointRadius: g.rows.map((r) => r.isNew ? 5 : 2),
      pointStyle: g.rows.map((r) => r.isNew ? "triangle" : "circle"),
      borderWidth: 2, borderDash: [4, 2]
    });
  });
  pChart2 = new Chart(canvas2.value, miniChartConfig({ datasets: c2Datasets }));

  // Chart 3: raw (import_value) vs scaled
  const chart3Datasets = [];
  for (const d of previewData.value) {
    const color = previewColorMap.value.get(d.sampling_point_id) || "#ccc";
    const label = previewPollutantMap.value.get(d.sampling_point_id) || d.sampling_point_id;
    chart3Datasets.push({ label: `${label} Raw`, data: d.values.map((v) => ({ x: v.to_time, y: v.import_value })), borderColor: color + "88", backgroundColor: color + "88", pointRadius: 1, borderWidth: 1, borderDash: [4, 2] });
    chart3Datasets.push({ label: `${label} Scaled`, data: d.values.map((v) => ({ x: v.to_time, y: v.scaled_value })), borderColor: color, backgroundColor: color, pointRadius: 1, borderWidth: 2 });
  }
  const chart3Config = miniChartConfig({ datasets: chart3Datasets }, chart3Range);
  chart3Config.options.plugins.zoom = {
    zoom: { wheel: { enabled: true }, pinch: { enabled: true }, mode: "xy" },
    pan: { enabled: true, mode: "xy" }
  };
  pChart3 = new Chart(canvas3.value, chart3Config);
  canvas3.value.addEventListener("dblclick", () => pChart3?.resetZoom());
};

const onPreview = async () => {
  previewLoading.value = true;
  showPreview.value = false;
  destroyPreviewCharts();

  const allSps = [
    { id: _obj.value.sampling_point_id, pollutant: props.primaryPollutant || _obj.value.sampling_point_id },
    ..._members.value.map((m) => ({ id: m.id, pollutant: m.pollutant }))
  ];
  previewColorMap.value = new Map(allSps.map((sp, i) => [sp.id, palette[i % palette.length]]));
  previewPollutantMap.value = new Map(allSps.map((sp) => [sp.id, sp.pollutant]));

  // Load scaling points for charts 1 & 2 (existing history + new point) — may already be loaded from dialog open
  if (!localScalingpoints.value.length) {
    localScalingpoints.value = await Service.scalingpoints({ sampling_point_id: _obj.value.sampling_point_id });
  }

  const currentTs = props.isEdit ? props.obj.timestamp : null;
  const requestList = [
    { sampling_point_id: _obj.value.sampling_point_id, zero_point: _obj.value.zero_point, span_value: _obj.value.span_value, gas_concentration: _obj.value.gas_concentration, timestamp: _obj.value.timestamp, current_timestamp: currentTs },
    ..._members.value.map((m) => ({ sampling_point_id: m.id, zero_point: m.zero_point, span_value: m.span_value, gas_concentration: m.gas_concentration, timestamp: _obj.value.timestamp, current_timestamp: currentTs }))
  ];

  let previewMsg = "";
  try {
    const res = await Service.preview(requestList);
    // res.values = [{sampling_point_id, pollutant, values: [...]}, ...]
    const grouped = res.values || [];

    // Extend pollutant map with any SPs from the response (e.g. calculated results like NO)
    grouped.forEach((g) => {
      if (g.pollutant) previewPollutantMap.value.set(g.sampling_point_id, g.pollutant);
      if (!previewColorMap.value.has(g.sampling_point_id)) {
        previewColorMap.value.set(g.sampling_point_id, palette[previewColorMap.value.size % palette.length]);
      }
    });

    previewData.value = grouped.filter((g) => g.values?.length > 0);
    previewRange.value = res.range ?? { min: null, max: null };

    const noDataSps = grouped
      .filter((g) => !g.values?.length)
      .map((g) => previewPollutantMap.value.get(g.sampling_point_id) || g.sampling_point_id);
    const verifiedMsg = res.message?.includes("verified") ? res.message : "";
    const noDataMsg = noDataSps.length ? `No observations for: ${noDataSps.join(", ")}` : "";
    previewMsg = [verifiedMsg, noDataMsg].filter(Boolean).join(" | ");
  } catch (e) {
    previewMsg = e?.message || "Preview failed";
  }

  previewMessage.value = previewMsg;
  previewLoading.value = false;
  showPreview.value = true;

  await nextTick();
  renderPreviewCharts();
};
</script>

<template>
  <popup :show="show" :title="isEdit ? 'Edit Scaling Point' : 'Add Scaling Point'" @on-close="$emit('close')" class="w-[90vw] max-w-3xl">
    <div class="mb-4">
      <div class="font-bold">Timestamp:</div>
      <DatetimePicker v-model="_obj.timestamp" class="w-full" />
      <div v-if="isDuplicateTimestamp" class="mt-1 text-sm text-red-500">
        A scaling point already exists at this time. To change it, use Edit instead.
      </div>
    </div>

    <!-- Primary SP -->
    <div v-if="primaryPollutant || _members.length" class="text-sm font-semibold text-nord3 mb-1">{{ primaryPollutant }}</div>
    <div class="grid grid-cols-3 gap-3 mb-4">
      <div>
        <div class="font-bold">Zero point:</div>
        <input type="number" class="input w-full" v-model="_obj.zero_point" placeholder="Zero point" />
      </div>
      <div>
        <div class="font-bold">Span value:</div>
        <input type="number" class="input w-full" :class="{ 'border-red-500': showSpanError(_obj.zero_point, _obj.span_value) }" v-model="_obj.span_value" placeholder="Span value" />
        <div v-if="showSpanError(_obj.zero_point, _obj.span_value)" class="text-red-500 text-sm mt-1">Cannot equal zero point</div>
      </div>
      <div>
        <div class="font-bold">Gas concentration:</div>
        <input type="number" class="input w-full" v-model="_obj.gas_concentration" placeholder="Gas concentration" />
      </div>
    </div>

    <!-- Group members (add, edit, and duplicate) -->
    <template v-if="_members.length">
      <div v-for="m in _members" :key="m.id" class="mb-4">
        <div class="text-sm font-semibold text-nord3 mb-1">{{ m.pollutant }}</div>
        <div class="grid grid-cols-3 gap-3">
          <div>
            <div class="font-bold">Zero point:</div>
            <input type="number" class="input w-full" v-model="m.zero_point" placeholder="Zero point" />
          </div>
          <div>
            <div class="font-bold">Span value:</div>
            <input type="number" class="input w-full" :class="{ 'border-red-500': showSpanError(m.zero_point, m.span_value) }" v-model="m.span_value" placeholder="Span value" />
            <div v-if="showSpanError(m.zero_point, m.span_value)" class="text-red-500 text-sm mt-1">Cannot equal zero point</div>
          </div>
          <div>
            <div class="font-bold">Gas concentration:</div>
            <input type="number" class="input w-full" v-model="m.gas_concentration" placeholder="Gas concentration" />
          </div>
        </div>
      </div>
    </template>

    <div class="flex justify-end gap-4 mt-4">
      <button class="button" :disabled="!isFormValid" @click="onSave">Save</button>
      <button class="button" :disabled="!isFormValid" @click="onPreview">Preview</button>
      <button class="button" @click="$emit('close')">Cancel</button>
    </div>

    <!-- Preview section -->
    <div v-if="previewLoading" class="mt-6 text-center text-nord3 py-4">Loading preview…</div>
    <template v-if="showPreview && !previewLoading">
      <div class="border-t border-gray-200 mt-6 pt-4">
        <div v-if="previewMessage" class="mb-4 p-3 bg-amber-50 border border-amber-300 text-amber-800 rounded text-sm">
          ⚠ {{ previewMessage }}
        </div>
        <div class="text-sm font-semibold text-nord3 mb-1">Zero-point history</div>
        <div class="h-36 mb-4"><canvas ref="canvas1"></canvas></div>
        <div class="text-sm font-semibold text-nord3 mb-1">Gas / Span history</div>
        <div class="h-36 mb-4"><canvas ref="canvas2"></canvas></div>
        <template v-if="previewData.length > 0">
          <div class="text-sm font-semibold text-nord3 mb-1">Raw vs Scaled <span class="font-normal text-nord4">(scroll to zoom · drag to pan · double-click to reset)</span></div>
          <div class="h-72 mb-4"><canvas ref="canvas3"></canvas></div>
        </template>
      </div>
    </template>
  </popup>
</template>
<style></style>
