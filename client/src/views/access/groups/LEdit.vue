<script setup>
const props = defineProps({
  show: Boolean,
  networks: Array,
  group: Object
});

const emit = defineEmits(["save", "close"]);

const obj = ref({});

watch(
  () => props.group,
  () => (obj.value = Object.assign({}, props.group))
);

const onSave = () => {
  const o = Object.assign({}, obj.value);
  o.networks = Object.assign([], o.networks);
  emit("save", o);
};
</script>

<template>
  <side-bar-crud :show="show" @cancel="$emit('close')" @commit="onSave">
    <div class="mb-4 font-bold text-base border-b">Required</div>
    <div class="mb-2">
      <div class="font-bold">Name:</div>
      <input class="n-input w-64" v-model="obj.name" placeholder="str: A unique group name" />
    </div>
    <div class="mt-2 flex cursor-pointer hover:bg-gray-50 p-1 select-none">
      <div class="font-bold self-center flex-1" @click="obj.management = !obj.management">Management:</div>
      <n-checkbox v-model="obj.management" class="self-center" />
    </div>
    <div class="flex cursor-pointer hover:bg-gray-50 p-1 select-none">
      <div class="font-bold self-center flex-1" @click="obj.data = !obj.data">Data:</div>
      <n-checkbox v-model="obj.data" class="self-center" />
    </div>
    <div class="flex cursor-pointer hover:bg-gray-50 p-1 select-none">
      <div class="font-bold self-center flex-1" @click="obj.exporting = !obj.exporting">EEA dataflow:</div>
      <n-checkbox v-model="obj.exporting" class="self-center" />
    </div>
    <div class="flex cursor-pointer hover:bg-gray-50 p-1 select-none">
      <div class="font-bold self-center flex-1" @click="obj.processing = !obj.processing">Processing:</div>
      <n-checkbox v-model="obj.processing" class="self-center" />
    </div>
    <div class="flex cursor-pointer hover:bg-gray-50 p-1 select-none">
      <div class="font-bold self-center flex-1" @click="obj.qualitycontrol = !obj.qualitycontrol">Quality control:</div>
      <n-checkbox v-model="obj.qualitycontrol" class="self-center" />
    </div>
    <div class="flex cursor-pointer hover:bg-gray-50 p-1 select-none">
      <div class="font-bold self-center flex-1" @click="obj.users = !obj.users">Users:</div>
      <n-checkbox v-model="obj.users" class="self-center" />
    </div>
    <div class="mt-3 mb-1 flex cursor-pointer hover:bg-gray-50 p-1 select-none">
      <div class="font-bold self-center flex-1" @click="obj.allnetworks = !obj.allnetworks">All networks:</div>
      <n-checkbox v-model="obj.allnetworks" class="self-center" />
    </div>
    <div v-if="!obj.allnetworks" class=" ">
      <n-multiselect class="!w-full" v-model="obj.networks" :searchable="true">
        <n-option v-for="t in networks" :key="t.value" :value="t.value" :label="t.label" />
      </n-multiselect>
    </div>
  </side-bar-crud>
</template>
<style></style>
