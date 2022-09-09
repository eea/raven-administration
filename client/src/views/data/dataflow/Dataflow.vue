<script setup>
import Service from "./service";
import FileDownload from "js-file-download";
import Eventy from "../../../helpers/eventy";

const year = ref();
const timezoneId = ref();
const description = ref("update");

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
</script>

<template>
  <common-layout>
    <tool-bar title="Dataflow" :show-filter="false" :show-add="false" :show-download="false" />

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
  </common-layout>
</template>

<style></style>
