<script setup>
import IconAdd from "~icons/tabler/plus";
import IconDownload from "~icons/tabler/download";
import IconUpload from "~icons/tabler/upload";
import IconSearch from "~icons/tabler/search";

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
  "filter-text": {
    type: String,
    default: "Type to filter"
  },
  q: {
    type: String,
    default: ""
  }
});

const emit = defineEmits(["update:q", "add-click", "download-click", "upload-click"]);
</script>

<template>
  <div class="flex flex-wrap items-center justify-between gap-x-4 gap-y-2 pb-2">
    <div class="flex flex-wrap items-center gap-1.5 min-w-0">
      <h1 class="font-display font-bold text-[1.35rem] leading-tight text-nord0 mr-2 truncate">{{ title }}</h1>
      <button v-if="showAdd" class="tb-btn tb-btn-primary" title="Add" @click="$emit('add-click', $event)">
        <IconAdd class="text-[1.1rem]" />
      </button>
      <button v-if="showUpload" class="tb-btn" title="Upload" @click="$emit('upload-click', $event)">
        <IconUpload class="text-[1.05rem] text-nord10" />
      </button>
      <button v-if="showDownload" class="tb-btn" title="Download" @click="$emit('download-click', $event)">
        <IconDownload class="text-[1.05rem] text-nord14" />
      </button>
      <slot />
    </div>
    <div v-if="showFilter" class="relative flex w-full sm:w-auto">
      <IconSearch class="absolute left-2.5 top-1/2 -translate-y-1/2 text-[#9aa6ba] pointer-events-none" />
      <input :placeholder="filterText" class="input w-full sm:w-64 pl-8!" type="search" :value="q" @input="$emit('update:q', $event.target.value)" v-bind="$attrs" />
    </div>
  </div>
</template>

<style scoped>
@reference "../assets/style.css";
.tb-btn {
  @apply grid place-items-center size-8 rounded-lg border border-nord4 bg-white text-nord2 shadow-card cursor-pointer
    transition-[background-color,border-color,transform] duration-150 hover:border-nord10/40 hover:bg-brand-soft active:scale-95;
}
.tb-btn-primary {
  @apply bg-nord10 border-nord10 text-white shadow-[0_2px_6px_-1px_color-mix(in_srgb,var(--color-nord10)_45%,transparent)] hover:bg-(--accent-hover) hover:border-(--accent-hover);
}
</style>
