<script setup>
import { ref, onMounted, computed } from "vue";
import Service from "./service";
import { timeAgo } from "../../../helpers/utils";
import Crud from "./Crud.vue";
import IconError from "~icons/material-symbols/help";

const notifications = ref([]);
const samplingPoints = ref([]);
const logs = ref([]);
const missingSamplingPoints = ref([]);
const showCrud = ref(false);
const selectedRow = ref(null);
const showContextmenu = ref(false);
const ev = ref({});
const showConfirm = ref(false);
const errorMessage = ref("");
const showErrorPopup = ref(false);

onMounted(async () => {
  notifications.value = await Service.get();
  samplingPoints.value = await Service.sampling_points();
  missingSamplingPoints.value = await Service.missing_values();
  logs.value = await Service.logs();
});

const onOpenCrud = (row) => {
  selectedRow.value = row || selectedRow.value;
  showCrud.value = true;
  showContextmenu.value = false;
};

const onCloseCrud = async (isSaved) => {
  showCrud.value = false;
  selectedRow.value = null;
  showContextmenu.value = false;
  showConfirm.value = false;
  ev.value = {};

  if (isSaved) notifications.value = await Service.get();
};

const onContextMenu = (row, e) => {
  selectedRow.value = row;
  ev.value = e;
  showContextmenu.value = true;
};

const onSaveDelete = async (id) => {
  if (!selectedRow.value) return;
  await Service.delete({ name: selectedRow.value.name });
  await onCloseCrud(true);
};

const onDelete = () => {
  if (showConfirm.value) selectedRow.value = {};
  showConfirm.value = !showConfirm.value;
  showContextmenu.value = false;
};

const onCloseErrorPopup = () => {
  console.log("close error popup");

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
    <contextmenu-crud :show="showContextmenu" :ev="ev" @click-outside="onCloseCrud" @on-delete="onDelete" @on-edit="onOpenCrud" />
    <Crud :data="selectedRow" :sampling-points="samplingPoints" :show="showCrud" @on-close="onCloseCrud" />
    <tool-bar title="Notifications" :show-column-picker="false" :show-add="true" :show-download="false" :show-filter="false" @add-click="onOpenCrud" />

    <div>
      <table class="n-table">
        <tr>
          <th></th>
          <th>Name</th>
          <th>Emails</th>
        </tr>
        <tr v-for="n in notifications" :key="n.id" @dblclick="onOpenCrud(n)" @contextmenu.prevent="onContextMenu(n, $event)">
          <td class="w-4"><n-checkbox class="align-middle" v-model="n.enabled" :disabled="true" /></td>
          <td>{{ n.name }}</td>
          <td>{{ n.emails }}</td>
        </tr>
      </table>
    </div>

    <div class="mt-8">
      <div class="text-base font-bold self-center">Last 5 email notifications</div>
      <table class="n-table">
        <tr>
          <th>Email sendt</th>
          <th>Missing sampling points</th>
          <th>Notifications sent</th>
          <th>Notifications failed</th>
          <th>Email server</th>
          <!-- <th>Execution time (ms)</th> -->
          <th>Status</th>
          <th></th>
        </tr>
        <tr v-for="p in logs" :key="p.id">
          <td>{{ p.run_timestamp }}</td>
          <td>{{ p.missing_data_count }}</td>
          <td>{{ p.notifications_sent }}</td>
          <td>{{ p.notifications_failed }}</td>
          <td>{{ p.smtp_server }}</td>
          <!-- <td>{{ p.execution_time_ms }}</td> -->
          <td>{{ p.status }}</td>
          <td>
            <IconError v-if="p.error_message" class="text-nord11 text-lg" @click="onOpenErrorPopup(p.error_message || 'No error message available')" />
          </td>
        </tr>
      </table>
    </div>

    <div class="mt-8">
      <div class="text-base font-bold self-center">Sampling points with data older than 3 hours</div>
      <table class="n-table">
        <tr>
          <th>SPO</th>
          <th>Station</th>
          <th>Pollutant</th>
          <th>Concentration</th>
          <th>Timestep</th>
          <th>Last Update</th>
          <th></th>
        </tr>
        <tr v-for="mv in missingSamplingPoints" :key="mv.id">
          <td>{{ mv.spo }}</td>
          <td>{{ mv.station }}</td>
          <td>{{ mv.pollutant }}</td>
          <td>{{ mv.concentration }}</td>
          <td>{{ mv.timestep }}</td>
          <td>{{ mv.totime }}</td>
          <td>{{ timeAgo(mv.totime) }}</td>
        </tr>
      </table>
    </div>
  </common-layout>
</template>
