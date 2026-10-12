<script setup>
import { computed, ref, watch } from "vue";
import { format } from "date-fns";
import Popup from "../../../components/Popup.vue";
import DatetimePicker from "../../../components/DatetimePicker.vue";
import FieldLabel from "../../../components/n-manager/FieldLabel.vue";
import { fits, methodKind, methodLabel, modelMatches } from "./methodKind";

// The generic n-manager Crud shows Sampling Point and Model / OBE side by side and any
// assessment type with either. But the type decides the method: a measurement type is
// assessed by a sampling point, Modelling by a MOD_ model, Objective estimation by an
// OBE_ one (methodKind.js; the API refuses anything else). So the type is chosen first
// and there is one method field, whose label and list follow it.

const props = defineProps({
  show: Boolean,
  isEdit: Boolean,
  options: Object,
  selectedValue: { type: Object, default: null },
  duplicateSource: { type: Object, default: null }
});

const emit = defineEmits(["close", "save"]);

const obj = ref({});
// The one method field: a sampling_points.id or a models.id, by the type.
const method = ref(null);
// Why the row as loaded breaks the rule -- written before it was enforced.
const loadedMismatch = ref(null);

const lookups = computed(() => props.options?.lookups ?? {});
const kind = computed(() => methodKind(obj.value.assessmenttype));

const methodOptions = computed(() => {
  if (kind.value === "sampling_point") return lookups.value.sampling_points ?? [];
  if (kind.value) return (lookups.value.models ?? []).filter((m) => modelMatches(kind.value, m.value));
  return [];
});

const asLink = (type, id) =>
  methodKind(type) === "sampling_point"
    ? { sampling_point_id: id, model_id: null }
    : { sampling_point_id: null, model_id: id };

watch(
  () => props.show,
  () => {
    const source = props.duplicateSource ?? props.selectedValue;
    if (!source) {
      obj.value = props.options.properties.reduce((a, v) => ({ ...a, [v.prop]: v.default }), {});
    } else {
      obj.value = { ...source };
      if (props.duplicateSource) obj.value.id = null;
      ["from_time", "to_time"].forEach((p) => {
        if (obj.value[p] && typeof obj.value[p] === "string") obj.value[p] = new Date(obj.value[p]);
      });
    }
    loadedMismatch.value = props.isEdit ? (props.selectedValue?.method_mismatch ?? null) : null;
    // A method that no longer fits its type starts empty, so the save cannot carry it.
    const id = obj.value.sampling_point_id || obj.value.model_id || null;
    method.value = id && fits(obj.value.assessmenttype, obj.value) ? id : null;
  }
);

// A new type keeps the chosen method if it still fits, and clears it otherwise.
watch(
  () => obj.value.assessmenttype,
  (type) => {
    if (method.value && !fits(type, asLink(type, method.value))) method.value = null;
  }
);

const title = computed(() => (props.isEdit ? "Edit Assessment Data" : "Create Assessment Data"));

const isFormValid = computed(
  () =>
    !!obj.value.assessment_regime_id &&
    !!obj.value.assessmenttype &&
    !!method.value &&
    fits(obj.value.assessmenttype, asLink(obj.value.assessmenttype, method.value))
);

const toApi = (v) => (v instanceof Date ? format(v, "yyyy-MM-dd HH:00") : v || null);

const handleSave = () => {
  const o = obj.value;
  emit("save", {
    id: o.id || null,
    assessment_regime_id: o.assessment_regime_id,
    assessmenttype: o.assessmenttype,
    ...asLink(o.assessmenttype, method.value),
    assessmentmethodedescription: o.assessmentmethodedescription || null,
    from_time: toApi(o.from_time),
    to_time: toApi(o.to_time)
  });
};
</script>

<template>
  <popup :show="show" :title="title" @on-close="emit('close')" class="max-w-6xl w-full">
    <div class="overflow-y-auto pr-2 max-h-[60vh]">
      <div v-if="loadedMismatch" class="mb-3 p-2 text-sm bg-yellow-50 border border-yellow-300 text-yellow-900">
        {{ loadedMismatch }}. Choose a method that fits the assessment type, or change the type.
      </div>

      <div class="flex flex-row gap-6">
        <div class="flex-1">
          <div class="mb-4 font-bold text-lg border-b border-nord4">Required</div>

          <div class="mb-2">
            <FieldLabel class="font-bold" label="Assessment Regime" />
            <select v-model="obj.assessment_regime_id" class="select w-full">
              <option v-for="r in lookups.regimes ?? []" :key="r.value" :value="r.value">{{ r.label }}</option>
            </select>
          </div>

          <div class="mb-2">
            <FieldLabel class="font-bold" label="Assessment Type" />
            <select v-model="obj.assessmenttype" class="select w-full">
              <option v-for="t in lookups.assessment_types ?? []" :key="t.value" :value="t.value">{{ t.label }}</option>
            </select>
            <div class="text-xs text-nord3 mt-1">
              AQR3 CAM_07. Decides the method below: a measurement type takes a sampling point, Modelling a MOD_
              model, Objective estimation an OBE_ one.
            </div>
          </div>

          <div class="mb-2">
            <FieldLabel class="font-bold" :label="methodLabel(obj.assessmenttype)" />
            <select v-model="method" class="select w-full" :disabled="!kind">
              <option v-for="m in methodOptions" :key="m.value" :value="m.value">{{ m.label }}</option>
            </select>
            <div class="text-xs text-nord3 mt-1">
              <template v-if="!kind">Choose an assessment type first.</template>
              <template v-else-if="methodOptions.length === 0">
                No {{ kind === "sampling_point" ? "reported sampling points" : `${kind === "model" ? "MOD_" : "OBE_"} models` }}
                exist yet.
              </template>
              <template v-else>AQR3 CAM_05 AssessmentMethodId.</template>
            </div>
          </div>
        </div>

        <div class="flex-1">
          <div class="mb-4 font-bold text-lg border-b border-nord4">Optional</div>

          <div class="mb-2">
            <FieldLabel class="font-bold" label="Valid From" />
            <DatetimePicker v-model="obj.from_time" />
          </div>
          <div class="mb-2">
            <FieldLabel class="font-bold" label="Valid To" />
            <DatetimePicker v-model="obj.to_time" />
            <div class="text-xs text-nord3 mt-1">When it stopped — set this rather than deleting the row.</div>
          </div>
          <div class="mb-2">
            <FieldLabel class="font-bold" label="Description" />
            <textarea class="input w-full" v-model="obj.assessmentmethodedescription" rows="3"
                      placeholder="free text, for anything the codes cannot say"></textarea>
          </div>
        </div>
      </div>
    </div>

    <div class="border-t border-gray-300 mt-4"></div>
    <div class="flex justify-end pt-2 gap-4">
      <button class="button" @click="handleSave" :disabled="!isFormValid">Save</button>
      <button class="button" @click="emit('close')">Cancel</button>
    </div>
  </popup>
</template>
