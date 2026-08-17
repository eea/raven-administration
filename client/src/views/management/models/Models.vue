<script setup>
import { onMounted, ref } from "vue";
import Manager from "../../../components/n-manager/Manager.vue";
import Service from "./service";
import pageOptions from "./pageOptions";
import ModelResultsUpload from "./ModelResultsUpload.vue";
import IconUpload from "~icons/material-symbols/upload-file-outline";

const options = ref({});
const lookups = ref({});

const showUpload = ref(false);
const uploadModel = ref(null);

const onContextMenuAction = ({ action, data }) => {
  if (action === "upload_results") {
    uploadModel.value = data?.row ?? null;
    showUpload.value = true;
  }
};

onMounted(async () => {
  lookups.value = await Service.lookups();
  options.value = pageOptions(lookups.value);
});
</script>

<template>
  <model-results-upload :show="showUpload" :model="uploadModel" :lookups="lookups"
                        @close="showUpload = false" />

  <Manager name="Models / objective estimation" :options="options" :service="Service"
           :show-add-button="true" @context-menu-action="onContextMenuAction">
    <template #extra-context-menu-items="{ handleAction }">
      <div class="pl-2 pr-4 py-1.5 flex cursor-pointer hover:bg-nord6"
           @click="handleAction('upload_results')">
        <icon-upload class="text-nord10 text-base self-center" />
        <div class="self-center ml-1">Upload gridded results</div>
      </div>
    </template>
  </Manager>
</template>
