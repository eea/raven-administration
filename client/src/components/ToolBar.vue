<script setup>
import IconAdd from "~icons/ic/baseline-add";
import IconDownload from "~icons/ic/round-file-download";

const props = defineProps({
  title: {
    type: String,
    default: "",
  },
  "show-add": {
    type: Boolean,
    default: true,
  },
  "show-download": {
    type: Boolean,
    default: true,
  },
  "show-filter": {
    type: Boolean,
    default: true,
  },
  "filter-text": {
    type: String,
    default: "Type to filter",
  },
  modelValue: {
    type: String,
    default: "",
  },
});

const emit = defineEmits(["update:modelValue", "add-click", "download-click"]);
</script>

<template>
  <div class="flex justify-between p-1">
    <div class="flex">
      <div class="font-bold text-lg self-center">{{ title }}</div>
      <circle-hover class="ml-1 self-center" @click="$emit('add-click')" v-if="showAdd">
        <icon-add class="text-nord14 text-lg self-center" />
      </circle-hover>
      <circle-hover class="ml-1 self-center" @click="$emit('download-click')" v-if="showDownload">
        <icon-download class="text-nord12 text-base self-center" />
      </circle-hover>
    </div>
    <div v-if="showFilter">
      <input :placeholder="filterText" class="n-input" type="search" :value="modelValue" @input="$emit('update:modelValue', $event.target.value)" v-bind="$attrs" />
    </div>
  </div>
</template>

<style></style>
