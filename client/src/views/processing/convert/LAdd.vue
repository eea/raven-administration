<script setup>
const props = defineProps({
  show: Boolean,
  timeseries: Array,
  units: Array
});

const obj = ref({});
const emit = defineEmits(["close", "save"]);

watch(
  () => props.show,
  (nv) => {
    obj.value = {};
  }
);

const close = () => {
  obj.value = {};
  emit("close");
};

const save = () => {
  emit("save", Object.assign({}, obj.value));
};
</script>

<template>
  <side-bar :show="show" @close="close">
    <div class="flex flex-col px-6 py-4 justify-between h-full">
      <div class="flex flex-col">
        <div class="mb-4 font-bold text-base border-b">Required</div>
        <div class="mb-2">
          <div class="font-bold">Timeserie:</div>
          <n-select v-model="obj.sampling_point_id" class="!w-64" :searchable="true">
            <n-option v-for="a in timeseries" :key="a.value" :value="a.value" :label="a.label" />
          </n-select>
        </div>
        <div class="mb-2">
          <div class="font-bold">From unit:</div>
          <n-select v-model="obj.source_id" class="!w-64" :searchable="true">
            <n-option v-for="a in units" :key="a.value" :value="a.value" :label="a.label" />
          </n-select>
        </div>
        <div class="mb-2">
          <div class="font-bold">To unit:</div>
          <n-select v-model="obj.target_id" class="!w-64" :searchable="true">
            <n-option v-for="a in units" :key="a.value" :value="a.value" :label="a.label" />
          </n-select>
        </div>

        <div class="mb-2">
          <div class="font-bold">Factor:</div>
          <input type="number" class="n-input w-64" v-model="obj.factor" placeholder="float: Factor to convert unit" />
        </div>
      </div>
      <div class="flex justify-between">
        <button class="n-button outline outline-2 outline-nord14" @click="save">Add</button>
        <button class="n-button outline outline-2 outline-nord11" @click="close">Cancel</button>
      </div>
    </div>
  </side-bar>
</template>
<style></style>
