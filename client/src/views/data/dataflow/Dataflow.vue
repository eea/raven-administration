<script setup>
import Service from "./service";
import FileDownload from "js-file-download";
import Eventy from "../../../helpers/eventy";

const year = ref();
const timezoneId = ref();
const description = ref("update");
const lastRequest = ref("");

const r3_year = ref();
const r3_timezoneId = ref();
const r3_description = ref("update");

const showReportnet3 = ref(false);

onMounted(async () => {
  showReportnet3.value = await getShowReportnet3();
});

// METHODS
const years = () => {
  const start = 2013;
  const y = new Date().getFullYear();
  year.value = String(y - 1);
  return Array.from({ length: y + 1 - start + 1 }, (_, i) => i + start)
    .reverse()
    .map((p) => String(p));
};

const timezones = () => {
  const start = 0;
  timezoneId.value = String(1);
  return Array.from({ length: 6 - start + 1 }, (_, i) => i + 0).map((p) => String(p));
};

// ACTIONS
const downloadDataflow = async (type) => {
  Eventy.showMessage("Creating xml. Please wait", "loading");
  const xml = await Service.dataflow(type, year.value, parseInt(timezoneId.value), description.value);
  FileDownload(xml, `dataflow-${type.toLowerCase()}.xml`);
  Eventy.hideMessage();
};

const downloadReportnet3Dataflow = async (type) => {
  Eventy.showMessage("Creating csv. Please wait", "loading");
  const response = await Service.dataflowReportnet3(type, year.value, parseInt(timezoneId.value), description.value);
  const blob = new Blob([response], { type: "text/csv" });
  FileDownload(blob, `dataflow-${type.toLowerCase()}.zip`);
  Eventy.hideMessage();
};

const downloadDataflowE2A = async () => {
  Eventy.showMessage("Creating xml. Please wait", "loading");
  const xml = await Service.dataflowE2A(lastRequest.value);
  FileDownload(xml, `dataflow-e2a.xml`);
  Eventy.hideMessage();
};

const getShowReportnet3 = async () => {
  const json = await Service.showReportnet3();
  return json.showreportnet3;
};
</script>

<template>
  <common-layout>
    <tool-bar title="Dataflows" :show-filter="false" :show-add="false" :show-column-picker="false" :show-download="false" />

    <div class="border border-nord4 bg-gray-50 p-2 flex flex-col gap-5">
      <div class="flex gap-3">
        <div>
          <div class="font-bold">Year</div>
          <n-select class="!w-40" v-model="year">
            <n-option v-for="opt in years()" :value="opt" :label="opt" />
          </n-select>
        </div>
        <div>
          <div class="font-bold">Timezone</div>
          <n-select class="!w-40" v-model="timezoneId">
            <n-option v-for="opt in timezones()" :value="opt" :label="'UTC +0' + opt" />
          </n-select>
        </div>
        <div>
          <div class="font-bold">Description</div>
          <input class="n-input !w-56" v-model="description" />
        </div>
      </div>
      <div class="flex gap-4">
        <button class="n-button" @click="downloadDataflow('B')" :disabled="false">Dataflow B</button>
        <button class="n-button" @click="downloadDataflow('C')" :disabled="false">Dataflow C</button>
        <button class="n-button" @click="downloadDataflow('D')" :disabled="false">Dataflow D</button>
        <button class="n-button" @click="downloadDataflow('E1A')" :disabled="false">Dataflow E1A</button>
        <button class="n-button" @click="downloadDataflow('G')" :disabled="false">Dataflow G</button>
      </div>
    </div>

    <tool-bar title="Dataflow E2A (UTD)" :show-filter="false" :show-add="false" :show-download="false" :show-column-picker="false" class="mt-4" />

    <div class="border border-nord4 bg-gray-50 p-2 flex flex-col gap-5">
      <div class="flex gap-3">
        <div>
          <div class="font-bold">Get data that changed since this date</div>
          <n-datetime v-model="lastRequest" />
        </div>
        <div>
          <div>&nbsp;</div>
          <button class="n-button" @click="downloadDataflowE2A" :disabled="false">Dataflow E2A</button>
        </div>
      </div>
    </div>

    <div v-if="showReportnet3">
      <tool-bar title="Reportnet3" :show-filter="false" :show-add="false" :show-download="false" :show-column-picker="false" class="mt-4" />
      <div class="border border-nord4 bg-gray-50 p-2 flex flex-col gap-5">
        <!--   <div class="flex gap-3">
          <div>
            <div class="font-bold">Year</div>
            <n-select class="!w-40" v-model="r3_year">
              <n-option v-for="opt in years()" :key="opt" :value="opt" :label="opt" />
            </n-select>
          </div>
          <div>
            <div class="font-bold">Timezone</div>
            <n-select class="!w-40" v-model="r3_timezoneId">
              <n-option v-for="opt in timezones()" :key="opt" :value="opt" :label="'UTC +0' + opt" />
            </n-select>
          </div>
          <div>
            <div class="font-bold">Description</div>
            <input class="n-input !w-56" v-model="r3_description" />
          </div>
        </div>
         -->
        <div class="flex gap-4">
          <button class="n-button" @click="downloadReportnet3Dataflow('B')" :disabled="false">Dataflow B</button>
          <button class="n-button" disabled @click="downloadReportnet3Dataflow('C')" :disabled="false">Dataflow C</button>
          <button class="n-button" @click="downloadReportnet3Dataflow('D')" :disabled="false">Dataflow D</button>
          <button class="n-button" disabled @click="downloadReportnet3Dataflow('E1A')" :disabled="false">Dataflow E1A</button>
          <button class="n-button" disabled @click="downloadReportnet3Dataflow('G')" :disabled="false">Dataflow G</button>
        </div>
      </div>
    </div>
  </common-layout>
</template>

<style></style>
