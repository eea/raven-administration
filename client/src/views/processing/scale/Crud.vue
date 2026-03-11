<script setup>
import { ref, watch, computed } from "vue";
import Popup from "../../../components/Popup.vue";
import DatetimePicker from "../../../components/DatetimePicker.vue";

const props = defineProps({
  show: Boolean,
  obj: Object,
  isEdit: Boolean
});

const emit = defineEmits(["save", "close"]);
const _obj = ref({});

watch(
  () => props.show,
  () => {
    _obj.value = Object.assign({}, props.obj);

    // Default to today at midnight when adding new scaling point
    if (!props.isEdit && !_obj.value.timestamp) {
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      const year = today.getFullYear();
      const month = String(today.getMonth() + 1).padStart(2, "0");
      const day = String(today.getDate()).padStart(2, "0");
      _obj.value.timestamp = `${year}-${month}-${day} 00:00:00`;
    }
  }
);

const onSave = () => {
  if (props.isEdit) {
    _obj.value.current_timestamp = props.obj.timestamp;
  }
  emit("save", Object.assign({}, _obj.value));
};

const isEmpty = (val) => val === null || val === undefined || val === "";

const isFormValid = computed(() => {
  const hasRequired = !isEmpty(_obj.value.zero_point) && !isEmpty(_obj.value.span_value) && !isEmpty(_obj.value.gas_concentration) && !!_obj.value.timestamp;
  const spanNotEqualZero = Number(_obj.value.zero_point) !== Number(_obj.value.span_value);
  return hasRequired && spanNotEqualZero;
});

const showSpanError = computed(() => {
  return !isEmpty(_obj.value.zero_point) && !isEmpty(_obj.value.span_value) && Number(_obj.value.zero_point) === Number(_obj.value.span_value);
});
</script>

<template>
  <popup :show="show" :title="isEdit ? 'Edit Scaling Point' : 'Add Scaling Point'" @on-close="$emit('close')" class="">
    <div class="mb-4 font-bold text-base border-b">Required</div>
    <div class="mb-2">
      <div class="font-bold">Zero point:</div>
      <input type="number" class="input w-full" v-model="_obj.zero_point" placeholder="float: Zero point value" />
    </div>
    <div class="mb-2">
      <div class="font-bold">Span value:</div>
      <input type="number" class="input w-full" :class="{ 'border-red-500': showSpanError }" v-model="_obj.span_value" placeholder="float: Span value" />
      <div v-if="showSpanError" class="text-red-500 text-sm mt-1">Span value cannot equal zero point</div>
    </div>
    <div class="mb-2">
      <div class="font-bold">Gas concentration:</div>
      <input type="number" class="input w-full" v-model="_obj.gas_concentration" placeholder="float: Gas concentration" />
    </div>
    <div class="mb-2">
      <div class="font-bold">Timestamp:</div>
      <DatetimePicker v-model="_obj.timestamp" class="w-full" />
    </div>

    <!-- BUTTONS -->
    <div class="flex justify-end gap-4 mt-4">
      <button class="button" :disabled="!isFormValid" @click="onSave">Save</button>
      <button class="button" @click="$emit('close')">Cancel</button>
    </div>
  </popup>
</template>
<style></style>
