<script setup>
import { ref, watch, computed } from "vue";
import Popup from "../../../components/Popup.vue";
import DatetimePicker from "../../../components/DatetimePicker.vue";

const props = defineProps({
  show: Boolean,
  obj: Object,
  isEdit: Boolean,
  groupMembers: { type: Array, default: () => [] },
  primaryPollutant: { type: String, default: "" }
});

const emit = defineEmits(["save", "close"]);
const _obj = ref({});
const _members = ref([]);  // [{id, pollutant, zero_point, span_value, gas_concentration}]

watch(
  () => props.show,
  () => {
    _obj.value = Object.assign({}, props.obj);

    if (!props.isEdit && !_obj.value.timestamp) {
      const now = new Date();
      now.setMinutes(0, 0, 0);
      const year = now.getFullYear();
      const month = String(now.getMonth() + 1).padStart(2, "0");
      const day = String(now.getDate()).padStart(2, "0");
      const hour = String(now.getHours()).padStart(2, "0");
      _obj.value.timestamp = `${year}-${month}-${day} ${hour}:00:00`;
    }

    _members.value = props.groupMembers.map((m) => ({
      id: m.id,
      pollutant: m.pollutant,
      scaling_point_id: m.scaling_point_id ?? null,
      zero_point: m.zero_point ?? null,
      span_value: m.span_value ?? null,
      gas_concentration: m.gas_concentration ?? (props.obj?.gas_concentration ?? null)
    }));
  }
);

const isEmpty = (val) => val === null || val === undefined || val === "";

const memberValid = (m) =>
  !isEmpty(m.zero_point) && !isEmpty(m.span_value) && !isEmpty(m.gas_concentration) &&
  Number(m.zero_point) !== Number(m.span_value);

const isFormValid = computed(() =>
  !!_obj.value.timestamp && memberValid(_obj.value) && _members.value.every(memberValid)
);

const showSpanError = (zero, span) =>
  !isEmpty(zero) && !isEmpty(span) && Number(zero) === Number(span);

const memberPayload = (m, timestamp) => ({
  sampling_point_id: m.id,
  timestamp,
  zero_point: m.zero_point,
  span_value: m.span_value,
  gas_concentration: m.gas_concentration
});

const onSave = () => {
  const ts = _obj.value.timestamp;
  const primary = Object.assign({}, _obj.value);

  if (props.isEdit) {
    primary.current_timestamp = props.obj.timestamp;
    const members = _members.value.map((m) => ({
      ...memberPayload(m, ts),
      id: m.scaling_point_id ?? null,
      current_timestamp: props.obj.timestamp
    }));
    emit("save", [primary, ...members]);
  } else {
    emit("save", [primary, ..._members.value.map((m) => memberPayload(m, ts))]);
  }
};
</script>

<template>
  <popup :show="show" :title="isEdit ? 'Edit Scaling Point' : 'Add Scaling Point'" @on-close="$emit('close')" class="w-[560px]">
    <div class="mb-4">
      <div class="font-bold">Timestamp:</div>
      <DatetimePicker v-model="_obj.timestamp" class="w-full" />
    </div>

    <!-- Primary SP -->
    <div v-if="primaryPollutant || _members.length" class="text-sm font-semibold text-nord3 mb-1">{{ primaryPollutant }}</div>
    <div class="grid grid-cols-3 gap-3 mb-4">
      <div>
        <div class="font-bold">Zero point:</div>
        <input type="number" class="input w-full" v-model="_obj.zero_point" placeholder="Zero point" />
      </div>
      <div>
        <div class="font-bold">Span value:</div>
        <input type="number" class="input w-full" :class="{ 'border-red-500': showSpanError(_obj.zero_point, _obj.span_value) }" v-model="_obj.span_value" placeholder="Span value" />
        <div v-if="showSpanError(_obj.zero_point, _obj.span_value)" class="text-red-500 text-sm mt-1">Cannot equal zero point</div>
      </div>
      <div>
        <div class="font-bold">Gas concentration:</div>
        <input type="number" class="input w-full" v-model="_obj.gas_concentration" placeholder="Gas concentration" />
      </div>
    </div>

    <!-- Group members (add, edit, and duplicate) -->
    <template v-if="_members.length">
      <div v-for="m in _members" :key="m.id" class="mb-4">
        <div class="text-sm font-semibold text-nord3 mb-1">{{ m.pollutant }}</div>
        <div class="grid grid-cols-3 gap-3">
          <div>
            <div class="font-bold">Zero point:</div>
            <input type="number" class="input w-full" v-model="m.zero_point" placeholder="Zero point" />
          </div>
          <div>
            <div class="font-bold">Span value:</div>
            <input type="number" class="input w-full" :class="{ 'border-red-500': showSpanError(m.zero_point, m.span_value) }" v-model="m.span_value" placeholder="Span value" />
            <div v-if="showSpanError(m.zero_point, m.span_value)" class="text-red-500 text-sm mt-1">Cannot equal zero point</div>
          </div>
          <div>
            <div class="font-bold">Gas concentration:</div>
            <input type="number" class="input w-full" v-model="m.gas_concentration" placeholder="Gas concentration" />
          </div>
        </div>
      </div>
    </template>

    <div class="flex justify-end gap-4 mt-4">
      <button class="button" :disabled="!isFormValid" @click="onSave">Save</button>
      <button class="button" @click="$emit('close')">Cancel</button>
    </div>
  </popup>
</template>
<style></style>
