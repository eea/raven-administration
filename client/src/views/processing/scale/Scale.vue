<script setup>
import { useRoute } from "vue-router";
import Chart from "chart.js/auto";
import "chartjs-adapter-luxon";
import Plot from "./plot";
import Service from "./service";
import Eventy from "../../../helpers/eventy";
import LAdd from "./LAdd.vue";
import LEdit from "./LEdit.vue";
import IconDuplicate from "~icons/ic/twotone-content-copy";

const timeserieId = ref("");
const timeseries = ref([]);
const scalingpoints = ref([]);
const showPlotAndTable = ref(false);
const showEdit = ref(false);
const showAdd = ref(false);
const selected = ref({});
const ev = ref({});
const showContextmenu = ref(false);
const showConfirm = ref(false);

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
  console.log("scalingpoints", scalingpoints.value);

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
  showAdd.value = true;
  showContextmenu.value = false;
};

const onSaveAdd = async (o) => {
  Eventy.showMessage("Inserting scaling point. Please wait", "loading");
  await Service.insert(o);
  await onShowScalingpoints();
  Eventy.showHideMessage("Scaling point added", "success", 5000);
  close();
};

const onEdit = () => {
  if (showEdit.value) selected.value = {};
  showEdit.value = !showEdit.value;
  showContextmenu.value = false;
};

const onSaveEdit = async (o) => {
  Eventy.showMessage("Updating scaling point. Please wait", "loading");
  await Service.update(o);
  await onShowScalingpoints();
  Eventy.showHideMessage("Scaling point changed", "success", 5000);
  close();
};

const onDelete = () => {
  if (showConfirm.value) selected.value = {};
  showConfirm.value = !showConfirm.value;
  showContextmenu.value = false;
};

const onSaveDelete = async (o) => {
  Eventy.showMessage("Deleting scaling point. Please wait", "loading");
  showConfirm.value = false;
  await Service.delete(selected.value);
  await onShowScalingpoints();
  Eventy.showHideMessage("Scaling point deleted", "success", 5000);
  close();
};

const close = () => {
  showEdit.value = false;
  showAdd.value = false;
  selected.value = {};
  showContextmenu.value = false;
  showConfirm.value = false;
};

const onContextMenu = (row, e) => {
  selected.value = row;
  ev.value = e;
  showContextmenu.value = true;
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
    <contextmenu-crud :show="showContextmenu" :ev="ev" @click-outside="close" @on-edit="onEdit" @on-delete="onDelete">
      <div class="pl-2 pr-4 py-2 flex cursor-pointer hover:bg-gray-100" @click="onShowAdd">
        <icon-duplicate class="text-nord12 text-sm self-center" />
        <div class="self-center ml-1">Duplicate</div>
      </div>
    </contextmenu-crud>
    <tool-bar title="Scale" :show-filter="false" @add-click="onShowAdd" :show-download="false" />
    <l-add :show="showAdd" :obj="selected" @close="close" @save="onSaveAdd" />
    <l-edit :show="showEdit" :scalingpoint="selected" @close="close" @save="onSaveEdit" />

    <container>
      <div class="flex gap-3">
        <div class="flex-1">
          <div class="font-bold">Timeserie</div>
          <n-select class="!w-full" v-model="timeserieId" :searchable="true">
            <n-option v-for="opt in timeseries" :value="opt.value" :label="opt.label" :class="cls_timeseries(opt.hasscalingpoint)" />
          </n-select>
        </div>
        <div>
          <div>&nbsp;</div>
          <button class="n-button" :disabled="timeserieId.length == 0" @click="onShowScalingpoints">Show scaling points</button>
        </div>
      </div>
    </container>

    <div class="flex gap-2 mt-4 w-full" v-show="showPlotAndTable">
      <container class="w-1/2 h-72"><canvas id="chart1"></canvas></container>
      <container class="w-1/2 h-72"><canvas id="chart2"></canvas></container>
    </div>

    <div class="mt-4" v-if="showPlotAndTable">
      <table id="convertionsId" class="n-table">
        <tr>
          <th>Timestamp</th>
          <th>0-point</th>
          <th>Span</th>
          <th>Gas concentration</th>
        </tr>
        <tr v-for="row in cmp_scalingpoints" @contextmenu.prevent="onContextMenu(row, $event)" @click="selected = {}">
          <td class="space-x-4">{{ row.timestamp }}</td>
          <td>{{ row.zero_point }}</td>
          <td>{{ row.span_value }}</td>
          <td>{{ row.gas_concentration }}</td>
        </tr>
      </table>
    </div>
  </common-layout>
</template>

<style></style>
