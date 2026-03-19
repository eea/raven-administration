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

const scalingpointsColumns = [
  { field: "timestamp", headerName: "Timestamp", flex: 1, filter: true },
  { field: "zero_point", headerName: "0-point", flex: 1, filter: true },
  { field: "span_value", headerName: "Span", flex: 1, filter: true },
  { field: "gas_concentration", headerName: "Gas concentration", flex: 1, filter: true }
];

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

  chart1.data = formatValues1();
  chart1.update();
  chart2.data = formatValues2();
  chart2.update();
};

const formatValues1 = () => {
  const series = [];
  const values = scalingpoints.value.slice(-10);
  const data = values.map((o) => {
    return { x: o.timestamp.replace(" ", "T"), y: o.zero_point };
  });

  series.push(Plot.dataset("0-point", data, "#A3BE8C"));
  return { datasets: series };
};

const formatValues2 = () => {
  const series = [];
  const values = scalingpoints.value.slice(-10);
  const data_span = values.map((o) => {
    return { x: o.timestamp.replace(" ", "T"), y: o.span_value };
  });
  series.push(Plot.dataset("Span", data_span, "#D08770"));

  const data_gas = scalingpoints.value.map((o) => {
    return { x: o.timestamp.replace(" ", "T"), y: o.gas_concentration };
  });

  series.push(Plot.dataset("Gas", data_gas, "#B48EAD"));
  return { datasets: series };
};

const onShowAdd = () => {
  if (!selected.value.sampling_point_id) selected.value.sampling_point_id = timeserieId.value;
  isEdit.value = false;
  showCrud.value = true;
};

const onSaveCrud = async (o) => {
  if (isEdit.value) {
    Eventy.showMessage("Updating scaling point. Please wait", "loading");
    await Service.update(o);
    await onShowScalingpoints();
    Eventy.showHideMessage("Scaling point changed", "success", 5000);
  } else {
    Eventy.showMessage("Inserting scaling point. Please wait", "loading");
    await Service.insert(o);
    await onShowScalingpoints();
    Eventy.showHideMessage("Scaling point added", "success", 5000);
  }
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

const onRowDoubleClick = (row) => {
  selected.value = row;
  isEdit.value = true;
  showCrud.value = true;
};

const onContextMenuAction = ({ action, data }) => {
  if (data?.row) {
    selected.value = data.row;
  }

  if (action === "edit") {
    isEdit.value = true;
    showCrud.value = true;
  } else if (action === "delete") {
    showConfirm.value = true;
  } else if (action === "duplicate") {
    if (!selected.value.sampling_point_id) selected.value.sampling_point_id = timeserieId.value;
    isEdit.value = false;
    showCrud.value = true;
  }
};

const cmp_scalingpoints = computed(() => {
  return scalingpoints.value.reverse();
});

const cls_timeseries = (hasscalingpoint) => {
  if (hasscalingpoint) return "border-l-2 border-nord7";
  return "";
};
</script>

<template>
  <common-layout>
    <confirm :show="showConfirm" title="Delete" text="Are you sure you want to delete the scaling point?" @close="close" @ok="onSaveDelete" />
    <tool-bar title="Scale" :show-filter="false" @add-click="onShowAdd" :show-download="false" :show-column-picker="false" />
    <Crud :show="showCrud" :obj="selected" :is-edit="isEdit" @close="close" @save="onSaveCrud" />

    <container>
      <div class="flex gap-3">
        <div class="flex-1">
          <div class="font-bold">Sampling point</div>
          <select class="select w-full" v-model="timeserieId">
            <option value="">Select sampling point</option>
            <option v-for="opt in timeseries" :key="opt.value" :value="opt.value" :class="cls_timeseries(opt.hasscalingpoint)">{{ opt.label }}</option>
          </select>
        </div>
        <div>
          <div>&nbsp;</div>
          <button class="button" :disabled="timeserieId.length == 0" @click="onShowScalingpoints">Show scaling points</button>
        </div>
      </div>
    </container>

    <div class="flex gap-2 mt-4 w-full" v-show="showPlotAndTable">
      <container class="w-1/2 h-72"><canvas id="chart1"></canvas></container>
      <container class="w-1/2 h-72"><canvas id="chart2"></canvas></container>
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
