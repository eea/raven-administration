<script setup>
import { onMounted, ref } from "vue";
import Manager from "../../../components/n-manager/Manager.vue";
import Service from "./service";
import pageOptions from "./pageOptions";
import DocumentFile from "./DocumentFile.vue";
import DocumentCrud from "./DocumentCrud.vue";
import IconUpload from "~icons/material-symbols/upload-file-outline";

const options = ref({});

// DocumentCrud hands over a chosen PDF as `_file`. The row is saved first --
// the file needs a document to belong to -- and the PDF uploaded after it. If
// the upload fails the document stays, without the file; Request() shows the
// API's message and "Upload PDF" in the row menu can retry.
const withFile = (save) => async (o) => {
  const { _file, ...row } = o;
  const result = await save(row);
  if (_file) {
    const data = new FormData();
    data.append("file", _file);
    await Service.uploadFile(row.id, data);
  }
  return result;
};
const service = { ...Service, insert: withFile(Service.insert), update: withFile(Service.update) };

const showFile = ref(false);
const fileDocument = ref(null);
// Bumped after an upload: remounting the manager reloads the grid, which shows
// the new Attachment URL.
const managerKey = ref(0);

const onContextMenuAction = ({ action, data }) => {
  if (action === "upload_file") {
    fileDocument.value = data?.row ?? null;
    showFile.value = true;
  }
};

onMounted(async () => {
  const lookups = await Service.lookups();
  options.value = pageOptions(lookups);
});
</script>

<template>
  <document-file :show="showFile" :document="fileDocument" @close="showFile = false" @uploaded="managerKey++" />

  <Manager :key="managerKey" name="Documents" :options="options" :service="service"
           :crud-component="DocumentCrud" @context-menu-action="onContextMenuAction">
    <template #extra-context-menu-items="{ handleAction }">
      <div class="pl-2 pr-4 py-1.5 flex cursor-pointer hover:bg-nord6" @click="handleAction('upload_file')">
        <icon-upload class="text-nord10 text-base self-center" />
        <div class="self-center ml-1">Upload PDF</div>
      </div>
    </template>
  </Manager>
</template>
