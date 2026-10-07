<script setup>
import { ref, watch } from "vue";
import Popup from "../../../components/Popup.vue";
import Eventy from "../../../helpers/eventy";
import { copyToClipboard } from "../../../helpers/utilsCopy";
import Service from "./service";

const props = defineProps({
  show: Boolean,
  document: { type: Object, default: null },
});

const emit = defineEmits(["close", "uploaded"]);

const input = ref(null);
const uploading = ref(false);
// The URL of the file just uploaded, else the document's current attachment.
const url = ref(null);

watch(() => props.show, (visible) => {
  if (visible) {
    const current = props.document?.documentattachment ?? "";
    url.value = /^https?:\/\//i.test(current) ? current : null;
    if (input.value) input.value.value = "";
  }
});

const upload = async () => {
  const file = input.value?.files?.[0];
  if (!file) {
    Eventy.showHideMessage("Choose a PDF first.", "error", 3000);
    return;
  }
  const data = new FormData();
  data.append("file", file);
  uploading.value = true;
  try {
    const result = await Service.uploadFile(props.document.id, data);
    url.value = result.url;
    Eventy.showHideMessage("PDF uploaded.", "success", 3000);
    emit("uploaded");
  } catch {
    // Request() has already shown the API's message.
  } finally {
    uploading.value = false;
  }
};

const copy = async () => {
  if (await copyToClipboard(url.value)) Eventy.showHideMessage("URL copied.", "success", 2000);
};
</script>

<template>
  <popup :show="show" :title="`Upload PDF — ${document?.id ?? ''}`" @on-close="emit('close')" class="max-w-2xl w-full">
    <p class="text-xs text-nord3 mb-3">
      Raven keeps the PDF and gives it a permanent public URL, which becomes the document's
      Attachment (AQR3 DOC_05) — Reportnet3 takes the document from there. Uploading again
      makes a new URL; the old one keeps serving the old file. Deleting the document deletes
      its files, and their URLs stop working.
    </p>

    <div class="flex gap-2 items-center mb-4">
      <input ref="input" type="file" accept=".pdf,application/pdf" class="input flex-1 text-sm" />
      <button class="button" :disabled="uploading" @click="upload">
        {{ uploading ? "Uploading…" : "Upload" }}
      </button>
    </div>

    <div v-if="url" class="text-sm">
      <div class="font-bold mb-1">Public URL</div>
      <div class="flex gap-2 items-center">
        <a :href="url" target="_blank" rel="noopener" class="text-nord10 underline break-all flex-1">{{ url }}</a>
        <button class="button" @click="copy">Copy</button>
      </div>
    </div>
  </popup>
</template>
