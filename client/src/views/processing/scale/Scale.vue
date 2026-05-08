<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute } from "vue-router";

import CommonLayout from "../../../components/CommonLayout.vue";
import ToolBar from "../../../components/ToolBar.vue";
import Container from "../../../components/Container.vue";
import Confirm from "../../../components/Confirm.vue";
import DataTable from "../../../components/DataTable.vue";
import CMenuItems from "../../../components/CMenuItems.vue";

import Chart from "chart.js/auto";
import "chartjs-adapter-luxon";
import Plot from "./plot";
import { palette as SP_COLORS } from "../../data/historical/plot";
import Service from "./service";
import Eventy from "../../../helpers/eventy";
import Crud from "./Crud.vue";

import IconDuplicate from "~icons/ic/twotone-content-copy";

const timeserieId = ref("");
const timeseries = ref([]);
const scalingpoints = ref([]);
const showPlotAndTable = ref(false);
const showCrud = ref(false);
const isEdit = ref(false);
const selected = ref({});
const showConfirm = ref(false);

// Map sampling_point_id → color, built from loaded scalingpoints
const spColorMap = computed(() => {
  const map = new Map();
  let i = 0;
  for (const row of scalingpoints.value) {
    if (!map.has(row.sampling_point_id)) {
      map.set(row.sampling_point_id, SP_COLORS[i % SP_COLORS.length]);
      i++;
    }
  }
  return map;
});

const scalingpointsColumns = computed(() => [
  {
    headerName: "",
    width: 40,
    sortable: false,
    filter: false,
    valueGetter: (p) => p.data?.sampling_point_id,
    cellRenderer: (p) => {
      const color = spColorMap.value.get(p.data?.sampling_point_id) || "#ccc";
      return `<span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:${color};margin-top:4px"></span>`;
    }
  },
  { field: "pollutant", headerName: "Pollutant", flex: 1, filter: true },
  { field: "timestamp", headerName: "Timestamp", flex: 1, filter: true },
  { field: "zero_point", headerName: "0-point", flex: 1, filter: true },
  { field: "span_value", headerName: "Span", flex: 1, filter: true },
  { field: "gas_concentration", headerName: "Gas concentration", flex: 1, filter: true }
]);

var chart1;
var chart2;

const route = useRoute();

onMounted(async () => {
  await loadData();
  if (route.query.id) {
    timeserieId.value = route.query.id;
    onShowScalingpoints();
  }
});

const loadData = async () => {
  timeseries.value = await Service.timeseries();
};

const onShowScalingpoints = async () => {
  showPlotAndTable.value = true;
  scalingpoints.value = await Service.scalingpoints({ sampling_point_id: timeserieId.value });

  const config1 = Plot.config();
  const config2 = Plot.config();
  if (!chart1) chart1 = new Chart("chart1", config1);
  if (!chart2) chart2 = new Chart("chart2", config2);

  const groups = groupBySp(scalingpoints.value);
  chart1.data = formatValues1(groups);
  chart1.update();
  chart2.data = formatValues2(groups);
  chart2.update();
};

const groupBySp = (rows) => {
  const map = new Map();
  for (const r of rows) {
    if (!map.has(r.sampling_point_id)) map.set(r.sampling_point_id, { pollutant: r.pollutant, rows: [] });
    map.get(r.sampling_point_id).rows.push(r);
  }
  return [...map.entries()];
};

const formatValues1 = (groups) => {
  const datasets = groups.map(([spId, g]) => {
    const color = spColorMap.value.get(spId) || "#ccc";
    const data = g.rows.slice(-10).map((o) => ({ x: o.timestamp.replace(" ", "T"), y: o.zero_point }));
    return Plot.dataset(`${g.pollutant} 0-point`, data, color);
  });
  return { datasets };
};

const formatValues2 = (groups) => {
  const datasets = [];
  groups.forEach(([spId, g]) => {
    const color = spColorMap.value.get(spId) || "#ccc";
    const span = g.rows.slice(-10).map((o) => ({ x: o.timestamp.replace(" ", "T"), y: o.span_value }));
    const gas = g.rows.map((o) => ({ x: o.timestamp.replace(" ", "T"), y: o.gas_concentration }));
    datasets.push(Plot.dataset(`${g.pollutant} Span`, span, color));
    datasets.push(Plot.dataset(`${g.pollutant} Gas`, gas, color + "88"));
  });
  return { datasets };
};

const lastRow = computed(() => scalingpoints.value.at(-1) ?? null);

const groupMembers = ref([]);
const primaryPollutant = ref("");

const resolvePollutant = (spId) => {
  const ts = timeseries.value.find((t) => t.value === spId);
  return ts ? ts.label.split(", ")[1] : spId;
};

const buildGroupMembersWithValues = async (spId, timestamp) => {
  const members = await Service.groupMembers(spId);
  return members.map((m) => {
    const sibling = scalingpoints.value.find((r) => r.sampling_point_id === m.id && r.timestamp === timestamp);
    return {
      ...m,
      zero_point: sibling?.zero_point ?? null,
      span_value: sibling?.span_value ?? null,
      gas_concentration: sibling?.gas_concentration ?? null,
      scaling_point_id: sibling?.id ?? null
    };
  });
};

const openCrud = async (row, edit) => {
  groupMembers.value = await buildGroupMembersWithValues(row.sampling_point_id, row.timestamp);
  primaryPollutant.value = resolvePollutant(row.sampling_point_id);
  selected.value = row;
  isEdit.value = edit;
  showCrud.value = true;
};

const onShowAdd = () =>
  openCrud({ sampling_point_id: timeserieId.value, gas_concentration: lastRow.value?.gas_concentration ?? null }, false);

const onSaveCrud = async (items) => {
  const list = Array.isArray(items) ? items : [items];
  if (isEdit.value) {
    Eventy.showMessage("Updating scaling point. Please wait", "loading");
    for (const item of list) {
      if (item.id) {
        await Service.update(item);
      } else {
        const { id, current_timestamp, scaling_point_id, ...insertData } = item;
        await Service.insert(insertData);
      }
    }
    Eventy.showHideMessage("Scaling point changed", "success", 5000);
  } else {
    Eventy.showMessage("Inserting scaling point(s). Please wait", "loading");
    for (const item of list) await Service.insert(item);
    Eventy.showHideMessage("Scaling point(s) added", "success", 5000);
  }
  await onShowScalingpoints();
  close();
};

const onSaveDelete = async () => {
  Eventy.showMessage("Deleting scaling point. Please wait", "loading");
  showConfirm.value = false;
  await Service.delete(selected.value);
  await onShowScalingpoints();
  Eventy.showHideMessage("Scaling point deleted", "success", 5000);
  close();
};

const close = () => {
  showCrud.value = false;
  selected.value = {};
  showConfirm.value = false;
};

const onRowDoubleClick = (row) => openCrud(row, true);

const onContextMenuAction = ({ action, data }) => {
  if (action === "edit") {
    openCrud(data.row, true);
  } else if (action === "delete") {
    selected.value = data.row;
    showConfirm.value = true;
  } else if (action === "duplicate") {
    openCrud(data.row, false);
  }
};

const cmp_scalingpoints = computed(() => [...scalingpoints.value].reverse());
</script>

<template>
  <common-layout>
    <confirm :show="showConfirm" title="Delete" text="Are you sure you want to delete the scaling point?" @close="close" @ok="onSaveDelete" />
    <tool-bar title="Scale" :show-filter="false" @add-click="onShowAdd" :show-download="false" :show-column-picker="false" />
    <Crud :show="showCrud" :obj="selected" :is-edit="isEdit" :group-members="groupMembers" :primary-pollutant="primaryPollutant" @close="close" @save="onSaveCrud" />

    <container>
      <div class="flex gap-3">
        <div class="flex-1">
          <div class="font-bold">Sampling point</div>
          <select class="select w-full" v-model="timeserieId">
            <option value="">Select sampling point</option>
            <option v-for="opt in timeseries" :key="opt.value" :value="opt.value" :class="opt.hasscalingpoint ? 'border-l-2 border-nord7' : ''">{{ opt.label }}</option>
          </select>
        </div>
        <div>
          <div>&nbsp;</div>
          <button class="button" :disabled="timeserieId.length == 0" @click="onShowScalingpoints">Show scaling points</button>
        </div>
      </div>
    </container>

    <div class="flex gap-2 mt-4 w-full" v-show="showPlotAndTable">
      <container class="w-1/2 h-72 min-w-0"><canvas id="chart1"></canvas></container>
      <container class="w-1/2 h-72 min-w-0"><canvas id="chart2"></canvas></container>
    </div>

    <div class="mt-4 min-h-96 flex-1" v-if="showPlotAndTable">
      <DataTable :columns="scalingpointsColumns" :data="cmp_scalingpoints" :filter="false" :floating-filter="false" :responsive="true" @context-menu-action="onContextMenuAction" @on-double-click="onRowDoubleClick">
        <template #context-menu-items="{ handleAction }">
          <CMenuItems @edit="handleAction('edit')" @delete="handleAction('delete')" />
          <div class="pl-2 pr-4 py-1.5 flex cursor-pointer hover:bg-nord6" @click="handleAction('duplicate')">
            <icon-duplicate class="text-nord12 text-base self-center" />
            <div class="self-center ml-1">Duplicate</div>
          </div>
        </template>
      </DataTable>
    </div>
  </common-layout>
</template>

<style></style>
