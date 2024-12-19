<script setup>
import { onClickOutside } from "@vueuse/core";
const props = defineProps({
  show: Boolean
});
const emit = defineEmits(["click-outside", "on-generate"]);

const year = ref(String(new Date().getFullYear() - 1));
const deleteExistingAttainments = ref(true);

const ctxm = ref(null);
onClickOutside(ctxm, (event) => {
  // console.log("e", event);
  emit("click-outside");
});

const years = () => {
  const start = 2013;
  const y = new Date().getFullYear();
  year.value = String(y - 1);
  return Array.from({ length: y - start + 1 }, (_, i) => i + start)
    .reverse()
    .map((p) => String(p));
};
</script>

<template>
  <div class="rounded border border-nord4 bg-white absolute shadow select-none z-50 left-96 top-20 flex flex-col p-2 gap-1" v-if="show" ref="ctxm">
    <div class="font-bold">Generate attainments</div>

    <div class="mb-2 flex cursor-pointer hover:bg-gray-50 gap-2 text-sm">
      <div class="self-center">Year:</div>
      <n-select class="!w-40" v-model="year">
        <n-option v-for="opt in years()" :value="opt" :label="opt" />
      </n-select>
    </div>

    <div class="mb-2 flex cursor-pointer hover:bg-gray-50 gap-2 text-sm">
      <div class="self-center flex-1" @click="deleteExistingAttainments = !deleteExistingAttainments">Delete existing attainments:</div>
      <n-checkbox v-model="deleteExistingAttainments" class="self-center" />
    </div>

    <button class="n-button" @click="emit('on-generate', { year, deleteExistingAttainments })">Generate</button>
  </div>
</template>

<style></style>
