<script setup>
const props = defineProps({
  show: Boolean,
  validation: Object,
  pollutants: Array
});

const emit = defineEmits(["close", "save"]);

const obj = ref({});

watch(
  () => props.validation,
  (nv) => {
    obj.value = Object.assign({}, props.validation);
  }
);

const close = () => {
  emit("close");
};

const save = () => {
  emit("save", obj.value);
};
</script>

<template>
  <side-bar :show="show" @close="close">
    <div class="flex flex-col px-6 py-4 justify-between h-full">
      <div class="flex flex-col">
        <div class="mb-4 font-bold text-base border-b">Required</div>
        <div class="mb-2">
          <div class="font-bold">Pollutant:</div>
          <input type="text" class="n-input w-64" v-model="obj.pollutant" :disabled="true" />
        </div>
        <div class="mb-2">
          <div class="font-bold">Minimum:</div>
          <input type="number" class="n-input w-64" v-model="obj.min" placeholder="float: Minimum valid value" />
        </div>
        <div class="mb-2">
          <div class="font-bold">Maximum:</div>
          <input type="number" class="n-input w-64" v-model="obj.max" placeholder="float: Maximum valid value" />
        </div>
        <div class="mb-2">
          <div class="font-bold">Repeat:</div>
          <input type="number" class="n-input w-64" v-model="obj.rep" placeholder="int: Maximum number of repeats" />
        </div>
      </div>
      <div class="flex justify-between">
        <button class="n-button outline outline-2 outline-nord14" @click="save">Update</button>
        <button class="n-button outline outline-2 outline-nord11" @click="close">Cancel</button>
      </div>
    </div>
  </side-bar>
</template>
<style></style>
