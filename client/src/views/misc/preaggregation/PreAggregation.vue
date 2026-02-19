<script setup>
import { onMounted, ref } from "vue";
import ToolBar from "../../../components/ToolBar.vue";
import Container from "../../../components/Container.vue";
import CommonLayout from "../../../components/CommonLayout.vue";
import DataTable from "../../../components/DataTable.vue";

import Service from "./service";
import Eventy from "../../../helpers/eventy";

const data = ref([]);

const columns = [
  { field: "type", headerName: "Aggregation type", flex: 1 },
  { field: "count_val", headerName: "Values count", width: 130 },
  { field: "count_sp", headerName: "Samplingpoints count", width: 180 },
  {
    field: "avg_cov",
    headerName: "Average coverage",
    width: 160,
    valueGetter: (params) => (params.data.avg_cov ? params.data.avg_cov + "%" : "-")
  },
  {
    field: "last_time",
    headerName: "Last date",
    flex: 1,
    valueGetter: (params) => (params.data.last_time ? params.data.last_time : "-")
  },
  {
    field: "created",
    headerName: "Last updated",
    flex: 1,
    cellStyle: { fontWeight: "bold" },
    valueGetter: (params) => (params.data.created ? params.data.created : "-")
  }
];

onMounted(async () => {
  await loadData();
});

const loadData = async () => {
  data.value = await Service.get();
};

const update = async () => {
  Eventy.showMessage("Aggregating data. Please wait", "loading");
  await Service.update();
  await loadData();
  Eventy.hideMessage();
};
</script>

<template>
  <common-layout>
    <tool-bar title="Pre aggregation" :show-column-picker="false" :show-add="false" :show-download="false" :show-filter="false" />

    <container>
      <div class="font-bold">Pre aggregating the data may take a while, depending on the amount of data stored in the database</div>
      <div><button class="button" @click="update">Manually aggregate data</button></div>
    </container>
    <div class="flex-1 mt-4 min-h-0">
      <DataTable :data="data" :columns="columns" :filter="true" :floating-filter="false" :responsive="true" />
    </div>
  </common-layout>
</template>
