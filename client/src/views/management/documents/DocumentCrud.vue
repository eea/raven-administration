<script setup>
import { computed, ref, watch } from "vue";
import Popup from "../../../components/Popup.vue";
import FieldLabel from "../../../components/n-manager/FieldLabel.vue";
import { ID_HELP } from "./pageOptions";

// Create/edit dialog for documents, in place of the generic n-manager Crud:
// it builds the DocumentId's first part from Data table and Type, and takes an
// optional PDF that Documents.vue uploads once the row is saved.

const props = defineProps({
  show: Boolean,
  isEdit: Boolean,
  options: Object,
  selectedValue: { type: Object, default: null },
  duplicateSource: { type: Object, default: null },
});

const emit = defineEmits(["close", "save"]);

const ID_MAX = 255; // documents.id
const REST_PATTERN = /^[A-Za-z0-9_.-]+$/; // the guide's separators: _ - .

const obj = ref({});
const rest = ref("");
const fileInput = ref(null);
const file = ref(null);

watch(
  () => props.show,
  (visible) => {
    if (!visible) return;
    const source = props.selectedValue ?? props.duplicateSource;
    obj.value = source
      ? { ...source }
      : { id: null, datatable_id: null, documentobject_id: null, documentattachment: null, document_original_url: null };
    if (!props.isEdit) obj.value.id = null;
    rest.value = "";
    file.value = null;
    if (fileInput.value) fileInput.value.value = "";
  }
);

const shortOf = (lookup, value) =>
  (props.options?.lookups?.[lookup] ?? []).find((l) => l.value === value)?.short ?? "";

// DOC_<type>_<table>_ -- the order most of the guide's examples use
// (DOC_DQ_SPP_DU0005_1). Only DOC_ until both dropdowns are chosen.
const prefix = computed(() => {
  const type = shortOf("documentobjects", obj.value.documentobject_id);
  const table = shortOf("datatables", obj.value.datatable_id);
  return type && table ? `DOC_${type}_${table}_` : "DOC_";
});

const fullId = computed(() => (props.isEdit ? obj.value.id : prefix.value + rest.value));

const idError = computed(() => {
  if (props.isEdit) return null;
  if (!rest.value) return null;
  if (!REST_PATTERN.test(rest.value)) return "Use letters, digits and _ - . only.";
  if (fullId.value.length > ID_MAX) return `At most ${ID_MAX} characters in all (now ${fullId.value.length}).`;
  return null;
});

const isFormValid = computed(
  () =>
    !!obj.value.datatable_id &&
    !!obj.value.documentobject_id &&
    (props.isEdit || (prefix.value !== "DOC_" && !!rest.value && !idError.value))
);

const onFile = (e) => {
  file.value = e.target.files?.[0] ?? null;
};

const handleSave = () => {
  emit("save", { ...obj.value, id: fullId.value, _file: file.value });
};

const title = computed(() => (props.isEdit ? "Edit Document" : "Create Document"));
</script>

<template>
  <popup :show="show" :title="title" @on-close="emit('close')" class="max-w-3xl w-full">
    <div class="overflow-y-auto pr-2 max-h-[65vh]">
      <div class="mb-4 font-bold text-lg border-b border-nord4">Required</div>

      <div class="mb-2">
        <FieldLabel class="font-bold" label="Data Table" />
        <select v-model="obj.datatable_id" class="select w-full">
          <option v-for="l in options.lookups?.datatables ?? []" :key="l.value" :value="l.value">{{ l.label }}</option>
        </select>
      </div>

      <div class="mb-2">
        <FieldLabel class="font-bold" label="Type" />
        <select v-model="obj.documentobject_id" class="select w-full">
          <option v-for="l in options.lookups?.documentobjects ?? []" :key="l.value" :value="l.value">{{ l.label }}</option>
        </select>
      </div>

      <div class="mb-2">
        <FieldLabel class="font-bold" label="Id" :help="ID_HELP" />
        <input v-if="isEdit" class="input w-full" :value="obj.id" disabled />
        <template v-else>
          <div class="flex items-stretch">
            <span class="px-2 flex items-center rounded-l border border-r-0 border-nord4 bg-nord6 font-mono text-sm whitespace-nowrap"
                  :title="prefix === 'DOC_' ? 'Choose Data Table and Type first' : 'Built from Type and Data Table'">{{ prefix }}</span>
            <input class="input w-full rounded-l-none font-mono" v-model.trim="rest"
                   :disabled="prefix === 'DOC_'"
                   placeholder="e.g. station or zone code + index, like NO0042A_1" />
          </div>
          <div v-if="idError" class="text-xs text-red-600 mt-1">{{ idError }}</div>
          <div v-else-if="rest" class="text-xs text-nord3 mt-1">Id: <span class="font-mono">{{ fullId }}</span></div>
        </template>
      </div>

      <div class="mb-4 mt-6 font-bold text-lg border-b border-nord4">Optional</div>

      <div class="mb-2">
        <FieldLabel class="font-bold" label="PDF" />
        <input ref="fileInput" type="file" accept=".pdf,application/pdf" class="input w-full text-sm" @change="onFile" />
        <div class="text-xs text-nord3 mt-1">
          Uploaded to Raven after saving; its permanent public URL replaces the Attachment.
        </div>
      </div>

      <div class="mb-2">
        <FieldLabel class="font-bold" label="Attachment" />
        <input class="input w-full" v-model="obj.documentattachment" :disabled="!!file"
               placeholder="str: PDF filename or URL (max 100 chars)" />
      </div>

      <div class="mb-2">
        <FieldLabel class="font-bold" label="Original URL" />
        <input class="input w-full" v-model="obj.document_original_url"
               placeholder="str: where the document is published (max 100 chars)" />
      </div>
    </div>

    <div class="border-t border-gray-300 mt-4"></div>
    <div class="flex justify-end pt-2 gap-4">
      <button class="button" @click="handleSave" :disabled="!isFormValid">Save</button>
      <button class="button" @click="emit('close')">Cancel</button>
    </div>
  </popup>
</template>
