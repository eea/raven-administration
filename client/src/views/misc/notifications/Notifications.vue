<script setup>
import { ref, onMounted } from "vue";
import CommonLayout from "../../../components/CommonLayout.vue";
import ToolBar from "../../../components/ToolBar.vue";
import Confirm from "../../../components/Confirm.vue";
import Popup from "../../../components/Popup.vue";
import DataTable from "../../../components/DataTable.vue";
import CMenuItems from "../../../components/CMenuItems.vue";
import Crud from "./Crud.vue";

import Service from "./service";
import { timeAgo } from "../../../helpers/utils";
import IconError from "~icons/material-symbols/help";

const notifications = ref([]);
const samplingPoints = ref([]);
const logs = ref([]);
const missingSamplingPoints = ref([]);
const showCrud = ref(false);
const selectedRow = ref(null);
const showConfirm = ref(false);
const errorMessage = ref("");
const showErrorPopup = ref(false);

const notificationsColumns = [
  {
    field: "enabled",
    headerName: "",
    width: 40,
    maxWidth: 40,
    cellRenderer: (params) => `<input type="checkbox" ${params.value ? "checked" : ""} disabled />`
  },
  { field: "name", headerName: "Name", flex: 1 },
  { field: "emails", headerName: "Emails", flex: 2 }
];

const missingSamplingPointsColumns = [
  { field: "spo", headerName: "SPO", flex: 2 },
  { field: "station", headerName: "Station", flex: 1 },
  { field: "pollutant", headerName: "Pollutant", flex: 1 },
  { field: "concentration", headerName: "Concentration", flex: 1 },
  { field: "timestep", headerName: "Timestep", flex: 1 },
  { field: "totime", headerName: "Last Update", flex: 2 },
  {
    field: "time_ago",
    headerName: "Time Ago",
    width: 110,
    valueGetter: (params) => timeAgo(params.data.totime)
  }
];

onMounted(async () => {
  notifications.value = await Service.get();
  samplingPoints.value = await Service.sampling_points();
  missingSamplingPoints.value = await Service.missing_values();
  logs.value = await Service.logs();
});

const onOpenCrud = (row) => {
  selectedRow.value = row || selectedRow.value;
  showCrud.value = true;
};

const onCloseCrud = async (isSaved) => {
  showCrud.value = false;
  selectedRow.value = null;
  showConfirm.value = false;

  if (isSaved) notifications.value = await Service.get();
};

const onContextMenuAction = ({ action, data }) => {
  if (data?.row) {
    selectedRow.value = data.row;
  }
  if (action === "edit") {
    showCrud.value = true;
  } else if (action === "delete") {
    showConfirm.value = true;
  }
};

const onSaveDelete = async () => {
  if (!selectedRow.value) return;
  await Service.delete({ name: selectedRow.value.name });
  await onCloseCrud(true);
};

const onCloseErrorPopup = () => {
  showErrorPopup.value = false;
  errorMessage.value = "";
};

const onOpenErrorPopup = (msg) => {
  errorMessage.value = msg;
  showErrorPopup.value = true;
};
</script>

<template>
  <common-layout>
    <popup :show="showErrorPopup" title="Notifications error" @on-close="onCloseErrorPopup">{{ errorMessage }}</popup>
    <confirm :show="showConfirm" title="Delete" text="Are you sure you want to delete the notification?" @close="onCloseCrud" @ok="onSaveDelete" />
    <Crud :data="selectedRow" :sampling-points="samplingPoints" :show="showCrud" @on-close="onCloseCrud" />
    <tool-bar title="Notifications" :show-column-picker="false" :show-add="true" :show-download="false" :show-filter="false" @add-click="onOpenCrud" />

    <div class="min-h-36">
      <DataTable :data="notifications" :columns="notificationsColumns" :filter="false" :floating-filter="false" @on-double-click="onOpenCrud" @context-menu-action="onContextMenuAction">
        <template #context-menu-items="{ handleAction }">
          <CMenuItems @edit="handleAction('edit')" @delete="handleAction('delete')" />
        </template>
      </DataTable>
    </div>

    <div class="mt-8">
      <div class="text-base font-bold self-center">Last 5 email notifications</div>
      <table class="table">
        <tr>
          <th>Email sent</th>
          <th>Missing sampling points</th>
          <th>Notifications sent</th>
          <th>Notifications failed</th>
          <th>Email server</th>
          <th>Status</th>
          <th></th>
        </tr>
        <tr v-for="p in logs" :key="p.id">
          <td>{{ p.run_timestamp }}</td>
          <td>{{ p.missing_data_count }}</td>
          <td>{{ p.notifications_sent }}</td>
          <td>{{ p.notifications_failed }}</td>
          <td>{{ p.smtp_server }}</td>
          <td>{{ p.status }}</td>
          <td>
            <IconError v-if="p.error_message" class="text-nord11 text-lg cursor-pointer" @click="onOpenErrorPopup(p.error_message || 'No error message available')" />
          </td>
        </tr>
      </table>
    </div>

    <div class="mt-8 flex-1 min-h-0 flex flex-col">
      <div class="text-base font-bold mb-2">Sampling points with data older than 3 hours</div>
      <div class="flex-1 min-h-0">
        <DataTable :data="missingSamplingPoints" :columns="missingSamplingPointsColumns" :filter="true" :floating-filter="false" :responsive="true" />
      </div>
    </div>
  </common-layout>
</template>
