<script setup>
import IconAdd from "~icons/ic/baseline-add";
import IconDownload from "~icons/ic/round-file-download";
import IconRemoveRedEye from "~icons/ic/baseline-remove-red-eye";

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

const ev = ref({});
const showColumnPicker = ref(false);
const emit = defineEmits(["update:modelValue", "add-click", "download-click"]);

const onContextMenu = (e) => {
  ev.value = e;
  showColumnPicker.value = !showColumnPicker.value;
};
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
          <circle-hover class="ml-1 self-center" @click="onContextMenu($event)" v-if="showAdd" @contextmenu.prevent="onContextMenu($event)">
            <icon-remove-red-eye class="text-nord14 text-lg self-center" />
          </circle-hover>
        </div>
      </div>
    </div>
    <contextmenu :evt="ev" :show="showColumnPicker" @click-outside="showColumnPicker = false">
      <div v-for="(column, key) in columnPicker" class="pl-2 pr-4 py-2 flex cursor-pointer hover:bg-gray-100">
        <input class="n-checkbox" type="checkbox" :id="key" :value="column" @input="$emit('columns-changed', key)" :checked="columnsPicked?.includes(key)" />
        <label :for="key">
          {{ column }}
        </label>
      </div>
    </contextmenu>
    <!-- <div v-for="(column, key) in columnPicker">
        <input class="n-checkbox" type="checkbox" :id="key" :value="column" @input="$emit('columns-changed', key)" :checked="columnsPicked?.includes(key)" />
        <label :for="key">
          {{ column }}
        </label>
      </div> -->
  </div>
</template>

<style>
input.n-checkbox + label {
  margin-left: 0.5rem;
  vertical-align: text-bottom;
  cursor: pointer;
}
</style>
