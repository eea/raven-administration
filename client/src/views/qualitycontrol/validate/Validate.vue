<script setup>
import IconValid from "~icons/prime/check-circle";
import IconNotValid from "~icons/prime/times-circle";

import { useRoute } from "vue-router";
import { format, sub, isAfter, isBefore } from "date-fns";
import { tblToCsv, compare } from "../../../helpers/utils";
import { multiRowClick } from "../../../helpers/table";
import Eventy from "../../../helpers/eventy";
import Service from "./service";

const timeseries = ref([]);

const fromtime = ref("");
const totime = ref("");
const selectedId = ref();

const timevalues = ref([]);
const ev = ref({});
const showContextmenu = ref(false);
const selectedRows = ref([]);

const route = useRoute();

onMounted(async () => {
  timeseries.value = await Service.timeseries();
  fromtime.value = format(sub(new Date(), { days: 14 }), "yyy-MM-dd 00:00");

  if (route.query.ids) selectedId.value = route.query.ids.split(";")[0];
  if (route.query.from) fromtime.value = route.query.from;
  if (route.query.to) totime.value = route.query.to;
  if (route.query.ids || route.query.from || route.query.to) showData();
});

const cmp_timeseries = computed(() => {
  return timeseries.value.filter((t) => {
    if (!t.fromtime && !t.totime) return true;
    return isAfter(new Date(t.totime), new Date(fromtime.value)) && isBefore(new Date(t.fromtime), new Date(totime.value));
  });
});

const showData = async () => {
  Eventy.showMessage("Retrieving data. Please wait", "loading");
  timevalues.value = [];
  await load();
  Eventy.hideMessage();
};

const load = async () => {
  timevalues.value = await Service.get({
    sampling_point_id: selectedId.value,
    from_dt: fromtime.value,
    to_dt: totime.value,
  });
};

const onDownload = () => {
  const o = timeseries.value.find((p) => p.value == selectedId.value);
  if (o) {
    const name = o.label.replaceAll(", ", "-");
    tblToCsv("validationId", name);
  }
};

const cls_rowClass = (row) => {
  var classes = "";
  if (row.validation_flag < 1) classes = " bg-nord11/10";
  if (selectedRows.value.find((p) => compare(p, row))) classes = classes + " selected";
  // if (row.pollutant == "O3") return "bg-nord14/20"
  // if (row.pollutant == "NO") return "bg-nord13/20"
  return classes;
};

const onValidate = async (flag) => {
  Eventy.showMessage("Setting validation flag. Please wait", "loading");
  const ids = selectedRows.value.map((p) => p.id);
  close();
  await Service.validate({ flag, ids });
  await load();
  Eventy.hideMessage();
};

const onRowClick = (row, e, rightClick) => {
  const { shiftKey, ctrlKey } = e;
  var r = Object.assign({}, row);
  var model = selectedRows.value.map((o) => Object.assign({}, o));
  var rows = timevalues.value.map((o) => Object.assign({}, o));
  var isSelected = e.target.parentElement.classList.contains("selected");
  var arr = multiRowClick(model, r, rows, shiftKey, ctrlKey, rightClick, isSelected);
  selectedRows.value = arr;

  if (rightClick) {
    ev.value = e;
    showContextmenu.value = true;
  }
};

const close = () => {
  showContextmenu.value = false;
  selectedRows.value = [];
};
</script>

<template>
  <common-layout>
    <contextmenu :evt="ev" @click-outside="close" :show="showContextmenu">
      <div class="px-2 font-bold">Set validation to:</div>
      <div class="pl-2 pr-4 py-2 flex cursor-pointer hover:bg-gray-100" @click="onValidate(-99)">
        <icon-not-valid class="text-nord11 text-lg self-center" />
        <div class="self-center ml-1">Not valid due to station maintenance or calibration (-99)</div>
      </div>
      <div class="pl-2 pr-4 py-2 flex cursor-pointer hover:bg-gray-100" @click="onValidate(-1)">
        <icon-not-valid class="text-nord11 text-lg self-center" />
        <div class="self-center ml-1">Not valid (-1)</div>
      </div>
      <div class="pl-2 pr-4 py-2 flex cursor-pointer hover:bg-gray-100" @click="onValidate(1)">
        <icon-valid class="text-nord14 text-lg self-center" />
        <div class="self-center ml-1">Valid (1)</div>
      </div>
      <div class="pl-2 pr-4 py-2 flex cursor-pointer hover:bg-gray-100" @click="onValidate(2)">
        <icon-valid class="text-nord14 text-lg self-center" />
        <div class="self-center ml-1">Valid, but below detection limit measurement value given (2)</div>
      </div>
      <div class="pl-2 pr-4 py-2 flex cursor-pointer hover:bg-gray-100" @click="onValidate(3)">
        <icon-valid class="text-nord14 text-lg self-center" />
        <div class="self-center ml-1">Valid, but below detection limit and number replaced by 0.5*detection limit (3)</div>
      </div>
    </contextmenu>

    <tool-bar title="Validate" :show-filter="false" :show-add="false" :show-download="true" @download-click="onDownload" />

    <div class="border border-nord4 bg-gray-50 p-2 flex flex-col gap-3">
      <div class="flex gap-2">
        <div>
          <div class="font-bold">From</div>
          <n-datetime v-model="fromtime" class="" />
        </div>
        <div>
          <div class="font-bold">To</div>
          <n-datetime v-model="totime" class="" />
        </div>
      </div>

      <div>
        <div class="font-bold">Timeseries</div>
        <n-select class="!w-full" v-model="selectedId" :searchable="cmp_timeseries.length > 0">
          <n-option v-for="t in cmp_timeseries" :key="t.value" :value="t.value" :label="t.label" />
          <n-option v-if="cmp_timeseries.length == 0" :value="0" label="No timeseries found for time period" class="!pointer-events-none" />
        </n-select>
      </div>

      <div class="mt-2">
        <button class="n-button" @click="showData" :disabled="!selectedId">Show data</button>
      </div>
    </div>

    <div class="mt-4">
      <table id="validationId" class="n-table">
        <tr>
          <th>From</th>
          <th>To</th>
          <th>Value</th>
          <th>Validation</th>
          <th>Verification</th>
        </tr>
        <tr v-for="row in timevalues" :key="row.id" :class="cls_rowClass(row)" @contextmenu.prevent="onRowClick(row, $event, true)" @click="onRowClick(row, $event, false)">
          <td>{{ row.fromtime }}</td>
          <td>{{ row.totime }}</td>
          <td>{{ row.value }}</td>
          <td>{{ row.validation_flag }}</td>
          <td>{{ row.verification_flag }}</td>
        </tr>
      </table>
    </div>
  </common-layout>
</template>

<style></style>
