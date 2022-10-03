<script setup>
import IconAdd from "~icons/ic/baseline-add";
import IconDownload from "~icons/ic/round-file-download";
import IconRemoveRedEye from "~icons/ic/baseline-remove-red-eye";
import NCheckbox from "./n-elements/NCheckbox.vue";

const props = defineProps({
  title: {
    type: String,
    default: ""
  },
  "show-add": {
    type: Boolean,
    default: true
  },
  "show-download": {
    type: Boolean,
    default: true
  },
  "show-filter": {
    type: Boolean,
    default: true
  },
  "filter-text": {
    type: String,
    default: "Type to filter"
  },
  "column-picker": {
    type: Object,
    default: null
  },
  "columns-picked": {
    type: Array,
    default: []
  },
  modelValue: {
    type: String,
    default: ""
  }
});

const showColumnPicker = ref(false);
const emit = defineEmits(["update:modelValue", "add-click", "download-click"]);
</script>

<template>
  <div>
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
      <div v-if="showFilter" class="flex">
        <input :placeholder="filterText" class="n-input" type="search" :value="modelValue" input="$emit('update:modelValue', $event.target.value)" v-bind="$attrs" />
        <div v-if="columnPicker" class="flex">
          <circle-hover class="ml-1 self-center" @click="showColumnPicker = !showColumnPicker" v-if="showAdd">
            <icon-remove-red-eye class="text-nord14 text-lg self-center" />
          </circle-hover>
        </div>
      </div>
    </div>
    <div class="p-3 mb-1 bg-gray-100 border-2" v-if="showColumnPicker">
      <div v-for="(column, key) in columnPicker">
        <input class="n-checkbox" type="checkbox" :id="key" :value="column" @input="$emit('columns-changed', key)" :checked="columnsPicked?.includes(key)" />
        <label :for="key">
          {{ column }}
        </label>
      </div>
    </div>
  </div>
</template>

<style>
input.n-checkbox + label {
  margin-left: 0.5rem;
  vertical-align: text-bottom;
  cursor: pointer;
}
</style>
