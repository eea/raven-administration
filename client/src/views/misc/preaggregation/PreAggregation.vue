<script setup>
import { onMounted, onUnmounted, ref } from "vue";
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

// The refresh runs in the background on the server: it outlived the HTTP request, so
// the page reported a failure while the database went on and finished. Poll its status
// instead, and pick up a refresh already running (started here earlier, or by the cron).
const running = ref(false);
let timer = null;

const poll = async () => {
  let still = true;
  try {
    ({ running: still } = await Service.status());
  } catch {
    // A failed poll is not a finished refresh; try again on the next tick.
  }
  if (still) {
    timer = setTimeout(poll, 5000);
    return;
  }
  running.value = false;
  timer = null;
  await loadData();
  Eventy.hideMessage();
  Eventy.showHideMessage("Aggregation finished", "success", 4000);
};

const watchRefresh = () => {
  running.value = true;
  Eventy.showMessage("Aggregating data. This may take several minutes -- you can leave this page.", "loading");
  timer = setTimeout(poll, 5000);
};

onMounted(async () => {
  await loadData();
  const { running: busy } = await Service.status();
  if (busy) watchRefresh();
});

onUnmounted(() => {
  if (timer) clearTimeout(timer);
  if (running.value) Eventy.hideMessage();
});

const loadData = async () => {
  data.value = await Service.get();
};

const update = async () => {
  if (running.value) return;
  await Service.update();
  watchRefresh();
};
</script>

<template>
  <common-layout>
    <tool-bar title="Pre aggregation" :show-add="false" :show-download="false" :show-filter="false" />

    <container>
      <div class="font-bold">Pre aggregating the data may take a while, depending on the amount of data stored in the database</div>
      <div><button class="button" :disabled="running" @click="update">{{ running ? "Aggregating..." : "Manually aggregate data" }}</button></div>
    </container>
    <div class="flex-1 mt-4 min-h-0">
      <DataTable :data="data" :columns="columns" :filter="true" :floating-filter="false" :responsive="true" />
    </div>
  </common-layout>
</template>
