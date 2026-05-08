<script setup>
import { ref, computed, watch } from "vue";
import Popup from "../../../components/Popup.vue";

const props = defineProps({
  show: Boolean,
  isEdit: Boolean,
  selectedValue: Object,
  options: Object
});

const emit = defineEmits(["close", "save"]);

const obj = ref({});
const station = ref("");
const createGroup = ref(false);

watch(
  () => props.show,
  () => {
    if (!props.selectedValue) {
      obj.value = {};
      station.value = "";
    } else {
      obj.value = Object.assign({}, props.selectedValue);
      station.value = obj.value.station || "";
    }
    createGroup.value = false;
  }
);

const cmp_stations = computed(() => {
  if (!props.options?.timeseries) return [];
  return [...new Set(props.options.timeseries.map((p) => p.label.split(", ")[0]))];
});

const cmp_timeseries = computed(() => {
  if (!station.value || !props.options?.timeseries) return [];
  return props.options.timeseries.filter((p) => p.label.startsWith(station.value));
});

const cmp_primary_options = computed(() => {
  return cmp_timeseries.value.filter((t) => t.value !== obj.value.secondary && t.value !== obj.value.result);
});

const cmp_secondary_options = computed(() => {
  return cmp_timeseries.value.filter((t) => t.value !== obj.value.primary && t.value !== obj.value.result);
});

const cmp_result_options = computed(() => {
  return cmp_timeseries.value.filter((t) => t.value !== obj.value.primary && t.value !== obj.value.secondary);
});

// Auto-suggest group name from selected pollutant notations
const suggestedGroupName = computed(() => {
  const ts = props.options?.timeseries ?? [];
  const label = (id) => ts.find((t) => t.value === id)?.label?.split(", ")[1] ?? id;
  if (!obj.value.primary || !obj.value.secondary || !obj.value.result) return "";
  return `${label(obj.value.primary)} ${obj.value.operator ?? "+"} ${label(obj.value.secondary)} = ${label(obj.value.result)}`;
});

const onSave = () => {
  if (obj.value.primary === obj.value.secondary || obj.value.primary === obj.value.result || obj.value.secondary === obj.value.result) {
    alert("Primary, Secondary, and Result must be different sampling points");
    return;
  }

  const data = Object.assign({}, obj.value);
  if (!props.isEdit && createGroup.value) {
    data.create_group = true;
    data.group_name = suggestedGroupName.value;
  }
  emit("save", data);
};
</script>

<template>
  <popup :show="show" :title="isEdit ? 'Edit Calculation' : 'Add Calculation'" @on-close="$emit('close')" class="w-[50%]">
    <div class="mb-4 font-bold text-base border-b">Required</div>

    <div class="mb-2">
      <div class="font-bold">Station:</div>
      <select v-model="station" class="select w-full" :disabled="isEdit">
        <option value="">Select station</option>
        <option v-for="a in cmp_stations" :key="a" :value="a">{{ a }}</option>
      </select>
    </div>

    <div class="mb-2">
      <div class="font-bold">Primary:</div>
      <select v-model="obj.primary" class="select w-full">
        <option value="">Select primary</option>
        <option v-for="a in cmp_primary_options" :key="a.value" :value="a.value">{{ a.label }}</option>
      </select>
    </div>

    <div class="mb-2">
      <div class="font-bold">Operator:</div>
      <select v-model="obj.operator" class="select w-full">
        <option value="">Select operator</option>
        <option value="+">+</option>
        <option value="-">-</option>
      </select>
    </div>

    <div class="mb-2">
      <div class="font-bold">Secondary:</div>
      <select v-model="obj.secondary" class="select w-full">
        <option value="">Select secondary</option>
        <option v-for="a in cmp_secondary_options" :key="a.value" :value="a.value">{{ a.label }}</option>
      </select>
    </div>

    <div class="mb-2">
      <div class="font-bold">Result:</div>
      <select v-model="obj.result" class="select w-full">
        <option value="">Select result</option>
        <option v-for="a in cmp_result_options" :key="a.value" :value="a.value">{{ a.label }}</option>
      </select>
    </div>

    <!-- Create group option (add only) -->
    <div v-if="!isEdit" class="mt-6 border-t pt-4 pb-2 pl-1">
      <label class="flex items-center gap-2 cursor-pointer select-none">
        <input type="checkbox" v-model="createGroup" class="w-4 h-4" />
        <span class="font-bold">Also create a sampling point group</span>
      </label>
    </div>

    <!-- BUTTONS -->
    <div class="flex justify-end gap-4 mt-4">
      <button class="button" :disabled="!obj.primary || !obj.operator || !obj.secondary || !obj.result" @click="onSave">Save</button>
      <button class="button" @click="$emit('close')">Cancel</button>
    </div>
  </popup>
</template>

<style></style>
