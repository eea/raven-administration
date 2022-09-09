<script setup>
import Service from "./service";

const year = ref();
const timezoneId = ref();
const description = ref("update");
const timezones = ref();

onMounted(async () => {
  timezones.value = await Service.timezones();
  if (timezones.value.length) timezoneId.value = timezones.value[0].value;
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
            <n-option v-for="opt in timezones" :value="opt.value" :label="opt.label" />
          </n-select>
        </div>
        <div>
          <div class="font-bold">Description</div>
          <input class="n-input !w-56" v-model="description" />
        </div>
      </div>
      <div class="flex gap-4">
        <button class="n-button" @click="showDatasets" :disabled="false">Dataflow B</button>
        <button class="n-button" @click="showDatasets" :disabled="false">Dataflow C</button>
        <button class="n-button" @click="showDatasets" :disabled="false">Dataflow D</button>
        <button class="n-button" @click="showDatasets" :disabled="false">Dataflow E1A</button>
        <button class="n-button" @click="showDatasets" :disabled="false">Dataflow G</button>
      </div>
    </div>
  </common-layout>
</template>

<style></style>
