<script setup>
import IconAdd from "~icons/ic/baseline-add";
import IconDownload from "~icons/ic/round-file-download";
import IconUpload from "~icons/ic/round-file-upload";
import IconColumnPicker from "~icons/ic/twotone-grid-view";

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
  "show-upload": {
    type: Boolean,
    default: false
  },
  "show-filter": {
    type: Boolean,
    default: true
  },
  "show-column-picker": {
    type: Boolean,
    default: true
  },
  "filter-text": {
    type: String,
    default: "Type to filter"
  },
  q: {
    type: String,
    default: ""
  }
});

const ev = ref({});
const emit = defineEmits(["update:q", "add-click", "download-click", "upload-click", "column-picker-click"]);
</script>

<template>
  <div>
    <div class="flex justify-between p-1">
      <div class="flex">
        <div class="font-bold text-lg self-center">{{ title }}</div>
        <circle-hover class="ml-1 self-center" @click="$emit('add-click', $event)" v-if="showAdd">
          <icon-add class="text-nord14 text-lg self-center" />
        </circle-hover>
        <circle-hover class="ml-1 self-center" @click="$emit('upload-click', $event)" v-if="showUpload">
          <icon-upload class="text-nord9 text-base self-center" />
        </circle-hover>
        <circle-hover class="ml-1 self-center" @click="$emit('download-click', $event)" v-if="showDownload">
          <icon-download class="text-nord11 text-base self-center" />
        </circle-hover>
        <circle-hover class="ml-1 self-center" @click="$emit('column-picker-click', $event)" v-if="showColumnPicker">
          <icon-column-picker class="text-nord15 text-sm self-center" />
        </circle-hover>
      </div>
      <div v-if="showFilter" class="flex">
        <input :placeholder="filterText" class="n-input" type="search" :value="q" @input="$emit('update:q', $event.target.value)" v-bind="$attrs" />
      </div>
    </div>
  </div>
</template>
