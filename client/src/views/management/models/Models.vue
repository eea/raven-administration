<script setup>
import { onMounted, ref } from "vue";
import Manager from "../../../components/n-manager/Manager.vue";
import Service from "./service";
import pageOptions from "./pageOptions";
import ModelResultsUpload from "./ModelResultsUpload.vue";
import ModelResultsExternal from "./ModelResultsExternal.vue";
import IconUpload from "~icons/material-symbols/upload-file-outline";
import IconExternal from "~icons/material-symbols/table-rows-outline";

const options = ref({});
const lookups = ref({});

const showUpload = ref(false);
const showExternal = ref(false);
const activeModel = ref(null);

const onContextMenuAction = ({ action, data }) => {
  if (action === "upload_results") {
    activeModel.value = data?.row ?? null;
    showUpload.value = true;
  }
  if (action === "external_results") {
    activeModel.value = data?.row ?? null;
    showExternal.value = true;
  }
};

const reload = async () => {
  // The grid shows external_result_count, so it goes stale when rows change.
  options.value = pageOptions(lookups.value);
};

onMounted(async () => {
  lookups.value = await Service.lookups();
  options.value = pageOptions(lookups.value);
});
</script>

<template>
  <model-results-upload :show="showUpload" :model="activeModel" :lookups="lookups"
                        @close="showUpload = false" />
  <model-results-external :show="showExternal" :model="activeModel" :lookups="lookups"
                          @close="showExternal = false" @changed="reload" />

  <Manager name="Models / objective estimation" :options="options" :service="Service"
           :show-add-button="true" @context-menu-action="onContextMenuAction">
    <template #extra-context-menu-items="{ handleAction }">
      <div class="pl-2 pr-4 py-1.5 flex cursor-pointer hover:bg-nord6"
           @click="handleAction('upload_results')">
        <icon-upload class="text-nord10 text-base self-center" />
        <div class="self-center ml-1">Upload gridded results</div>
      </div>
      <div class="pl-2 pr-4 py-1.5 flex cursor-pointer hover:bg-nord6"
           @click="handleAction('external_results')">
        <icon-external class="text-nord10 text-base self-center" />
        <div class="self-center ml-1">External gridded results</div>
      </div>
    </template>
  </Manager>
</template>
