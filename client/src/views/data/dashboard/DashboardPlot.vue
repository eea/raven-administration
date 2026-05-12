<script setup>
import { ref, watch, onMounted, onBeforeUnmount } from "vue";
import { useRouter } from "vue-router";
import { format, sub } from "date-fns";
import Chart from "chart.js/auto";
import "chartjs-adapter-luxon";
import zoomPlugin from "chartjs-plugin-zoom";
import Plot, { palette, hexToRgba } from "../historical/plot";
import { groupBy } from "../../../helpers/utils";
import Service from "./service";
import Eventy from "../../../helpers/eventy";
import IconRefresh  from "~icons/material-symbols/refresh";
import IconTune     from "~icons/material-symbols/tune";
import IconDelete   from "~icons/material-symbols/delete-outline";
import IconHistory  from "~icons/material-symbols/bar-chart";
import IconValidate from "~icons/material-symbols/fact-check";
import IconScale    from "~icons/uil/process";

Chart.register(zoomPlugin);

const router = useRouter();

const props = defineProps({
  plot:          { type: Object,  required: true },
  allTimeseries: { type: Array,   default: () => [] },
});

const emit = defineEmits(["update", "remove", "edit"]);

const PRESETS = [
  { key: "6h",  label: "6h",  hours: 6,   meantype: 0 },
  { key: "12h", label: "12h", hours: 12,  meantype: 0 },
  { key: "24h", label: "24h", hours: 24,  meantype: 0 },
  { key: "3d",  label: "3d",  hours: 72,  meantype: 0 },
  { key: "7d",  label: "7d",  hours: 168, meantype: 0 },
  { key: "14d", label: "14d", hours: 336, meantype: 0 },
];

const loading         = ref(false);
const hasData         = ref(null); // null = never loaded, true/false after load
const legendItems     = ref([]);
const hoveredIdx      = ref(-1);
const canvasRef       = ref(null);
let chart             = null;

// SP picker — shared by validate and scale (both take a single SP)
const pickerTarget  = ref(null); // "Validate" | "Scale" | null
const pickerRef     = ref(null);

const pickerItems = () =>
  legendItems.value.length
    ? legendItems.value
    : props.allTimeseries
        .filter(sp => props.plot.seriesIds?.includes(sp.sampling_point_id))
        .map(sp => ({ sampling_point_id: sp.sampling_point_id, label: [sp.station, sp.pollutant].filter(Boolean).join(" — "), color: null }));

const openPicker = (routeName) => {
  if (props.plot.seriesIds?.length <= 1) {
    navigateWithSp(routeName, props.plot.seriesIds[0]);
  } else {
    pickerTarget.value = pickerTarget.value === routeName ? null : routeName;
  }
};

const navigateWithSp = (routeName, spId) => {
  pickerTarget.value = null;
  const { from_dt, to_dt } = getDateRange(props.plot.timePreset);
  if (routeName === "Validate") {
    router.push({ name: "Validate", query: { ids: spId, from: from_dt, to: to_dt } });
  } else if (routeName === "Scale") {
    router.push({ name: "Scale", query: { id: spId } });
  }
};

const onPickerClickOutside = (e) => {
  if (pickerRef.value && !pickerRef.value.contains(e.target)) {
    pickerTarget.value = null;
  }
};

const getDateRange = (presetKey) => {
  const p  = PRESETS.find(x => x.key === presetKey) ?? PRESETS[2];
  const to = new Date();
  const from = sub(to, { hours: p.hours });
  return { from_dt: format(from, "yyyy-MM-dd HH:00"), to_dt: format(to, "yyyy-MM-dd HH:00"), meantype: p.meantype };
};

const getAxes = (data) => groupBy(data, r => r.unit).map(e => e[0]);

const getFinestTimestepSeconds = () => {
  if (!props.allTimeseries?.length || !props.plot.seriesIds?.length) return null;
  const selected = props.allTimeseries.filter(sp => props.plot.seriesIds.includes(sp.sampling_point_id));
  const seconds = selected.map(sp => sp.timestep_seconds).filter(s => s > 0);
  return seconds.length ? Math.min(...seconds) : null;
};

const buildChart = (data) => {
  if (chart) { chart.destroy(); chart = null; }
  if (!canvasRef.value) return;

  const axes   = getAxes(data);
  // Start y-axis at 0 per unit, unless that unit has negative values
  const negativeAxes = new Set(data.filter(o => o.value < 0).map(o => o.unit));
  const beginAtZero  = Object.fromEntries(axes.map(a => [a, !negativeAxes.has(a)]));
  const config = Plot.config(axes, beginAtZero, props.plot.plotType ?? "line", getFinestTimestepSeconds());
  chart        = new Chart(canvasRef.value, config);

  const grouped       = groupBy(data, r => r.sampling_point_id);
  const allTimestamps = [...new Set(data.map(o => o.datetime))].sort();
  legendItems.value   = [];

  const datasets = grouped.map((entry, i) => {
    const [spId, values] = entry;
    const color    = palette[i % palette.length];
    const byDt     = new Map(values.map(o => [o.datetime, o]));
    const pts      = allTimestamps.map(ts => ({ x: ts.replace(" ", "T"), y: byDt.get(ts)?.value ?? null }));
    const axis     = axes.find(a => a === values[0].unit);
    const first    = values[0];
    const eq       = [first.equipment, first.equipment_identifier].filter(Boolean).join(" / ");
    const label    = [first.station, first.component, first.unit, eq].filter(Boolean).join(" - ");
    legendItems.value.push({ color, label, hidden: false, sampling_point_id: spId });
    return Plot.dataset(label, pts, color, props.plot.plotType ?? "line", axis);
  });

  chart.data = { datasets };
  chart.update();
};

const loadData = async (presetKey) => {
  const key = presetKey ?? props.plot.timePreset;
  if (!props.plot.seriesIds?.length) return;
  loading.value = true;
  hasData.value = null;
  try {
    const { from_dt, to_dt, meantype } = getDateRange(key);
    const data = await Service.get({ sampling_point_ids: props.plot.seriesIds, from_dt, to_dt, meantype, coverage: 75 });
    hasData.value = data.length > 0;
    if (data.length) buildChart(data);
  } catch {
    Eventy.showHideMessage("Failed to load chart data.", "error", 4000);
  } finally {
    loading.value = false;
  }
};

const setPreset = (key) => {
  emit("update", { ...props.plot, timePreset: key });
  loadData(key);
};

const resetZoom = () => { if (chart) chart.resetZoom(); };

const goToHistorical = () => {
  const { from_dt, to_dt } = getDateRange(props.plot.timePreset);
  router.push({ name: "Historical", query: { ids: props.plot.seriesIds.join(";"), from: from_dt, to: to_dt } });
};

const toggleSeries = (i) => {
  if (!chart) return;
  const visible = chart.isDatasetVisible(i);
  chart.setDatasetVisibility(i, !visible);
  chart.update();
  legendItems.value[i].hidden = visible;
};

const onLegendHover = (i) => {
  if (!chart || legendItems.value[i].hidden) return;
  hoveredIdx.value = i;
  chart.data.datasets.forEach((ds, idx) => {
    const c = legendItems.value[idx].color;
    const f = hexToRgba(c, 0.2);
    Object.assign(ds, idx === i
      ? { borderColor: c, backgroundColor: c, borderWidth: 3, pointRadius: 1, pointHoverRadius: 3 }
      : { borderColor: f, backgroundColor: f, borderWidth: 1, pointRadius: 0,  pointHoverRadius: 0 });
  });
  chart.update();
};

const onLegendLeave = () => {
  if (!chart) return;
  hoveredIdx.value = -1;
  chart.data.datasets.forEach((ds, idx) => {
    const c = legendItems.value[idx].color;
    Object.assign(ds, { borderColor: c, backgroundColor: c, borderWidth: 2, pointRadius: 1, pointHoverRadius: 3 });
  });
  chart.update();
};

// Reload when series list changes (after edit)
watch(() => props.plot.seriesIds, () => { if (props.plot.seriesIds?.length) loadData(); }, { deep: true });

onMounted(() => {
  if (props.plot.seriesIds?.length) loadData();
  document.addEventListener("click", onPickerClickOutside);
});
onBeforeUnmount(() => {
  if (chart) { chart.destroy(); chart = null; }
  document.removeEventListener("click", onPickerClickOutside);
});
</script>

<template>
  <div class="border border-nord4 bg-gray-50 flex flex-col h-96">

    <!-- Header -->
    <div class="flex items-center gap-2 px-3 py-2 border-b border-nord4 bg-white shrink-0">
      <span class="font-bold text-sm truncate min-w-0 cursor-default" :title="plot.title || 'Untitled'">{{ plot.title || "Untitled" }}</span>
      <button class="text-nord3 hover:text-nord10 p-1 rounded shrink-0" @click="goToHistorical" title="Open in Historical">
        <icon-history class="text-base" />
      </button>

      <!-- SP picker: shared by Validate + Scale -->
      <div class="relative shrink-0 flex gap-0.5" ref="pickerRef">
        <button class="text-nord3 hover:text-nord10 p-1 rounded" :class="{ 'text-nord10': pickerTarget === 'Validate' }" @click.stop="openPicker('Validate')" title="Open in Validate">
          <icon-validate class="text-base" />
        </button>
        <button class="text-nord3 hover:text-nord10 p-1 rounded" :class="{ 'text-nord10': pickerTarget === 'Scale' }" @click.stop="openPicker('Scale')" title="Open in Scale">
          <icon-scale class="text-base" />
        </button>
        <div v-if="pickerTarget"
             class="absolute left-0 top-full mt-1 z-50 bg-white border border-nord4 rounded shadow-lg py-1 min-w-40 max-w-64">
          <div class="px-3 py-1 text-[10px] font-bold uppercase tracking-wide text-nord3 border-b border-nord6">
            {{ pickerTarget === 'Validate' ? 'Validate' : 'Scale' }}
          </div>
          <button
            v-for="item in pickerItems()" :key="item.sampling_point_id"
            class="w-full text-left px-3 py-1.5 text-xs text-nord1 hover:bg-nord6 flex items-center gap-2 cursor-pointer"
            :title="item.label"
            @click="navigateWithSp(pickerTarget, item.sampling_point_id)">
            <div class="w-2 h-2 rounded-full shrink-0" :style="{ background: item.color ?? '#ccc' }"></div>
            <span class="truncate">{{ item.label }}</span>
          </button>
        </div>
      </div>

      <span class="flex-1"></span>

      <span class="text-xs font-mono text-nord3 shrink-0">{{ plot.timePreset }}</span>

      <button class="text-nord3 hover:text-nord10 p-1 rounded" :class="{ 'animate-spin': loading }" @click="loadData()" title="Refresh">
        <icon-refresh class="text-base" />
      </button>
      <button class="text-nord3 hover:text-nord10 p-1 rounded" @click="emit('edit', plot)" title="Configure">
        <icon-tune class="text-base" />
      </button>
      <button class="text-nord3 hover:text-nord11 p-1 rounded" @click="emit('remove', plot.id)" title="Remove">
        <icon-delete class="text-base" />
      </button>
    </div>

    <!-- Chart area -->
    <div class="relative flex-1 min-h-0 p-2">
      <div v-if="!plot.seriesIds?.length"
           class="absolute inset-0 flex flex-col items-center justify-center text-nord4 select-none gap-1">
        <icon-tune class="text-3xl" />
        <span class="text-sm">Click configure to add series</span>
      </div>
      <div v-else-if="loading"
           class="absolute inset-0 flex items-center justify-center text-nord3 text-sm select-none">
        Loading…
      </div>
      <div v-else-if="hasData === false"
           class="absolute inset-0 flex items-center justify-center text-nord3 text-sm select-none">
        No data for this period
      </div>
      <canvas ref="canvasRef" v-show="hasData" @dblclick="resetZoom" style="cursor: crosshair; width:100%; height:100%;" />
    </div>

    <!-- Legend -->
    <div v-if="legendItems.length" class="flex flex-wrap gap-x-4 gap-y-1 px-3 pb-2 pt-1 border-t border-nord4 max-h-16 overflow-y-auto shrink-0">
      <div
        v-for="(item, i) in legendItems" :key="item.label"
        class="flex items-center gap-1.5 cursor-pointer select-none text-xs text-nord3"
        :style="{ opacity: item.hidden ? 0.35 : (hoveredIdx === -1 || hoveredIdx === i ? 1 : 0.35) }"
        @click="toggleSeries(i)" @mouseenter="onLegendHover(i)" @mouseleave="onLegendLeave">
        <div class="w-2 h-2 rounded-full shrink-0" :style="{ background: item.color }"></div>
        <span>{{ item.label }}</span>
      </div>
    </div>

  </div>
</template>
