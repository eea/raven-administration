<script setup>
import { computed, ref, watch, shallowRef } from "vue";
import Popup from "../../../components/Popup.vue";
import DataTable from "../../../components/DataTable.vue";
import { sortBy } from "../../../helpers/utils";

const props = defineProps({
  show: Boolean,
  isEdit: Boolean,
  options: Object,
  selectedValue: {
    type: Object,
    default: null
  }
});

const emit = defineEmits(["save", "close"]);
const obj = ref({});
const gridData = shallowRef([]);
const samplingPointColumns = shallowRef([]);
const gridApi = ref(null);
const selectedSamplingPointIds = ref(new Set());

// Initialize columns when options change
watch(
  () => props.options?.lookups?.assessment_types,
  (assessmentTypes) => {
    if (!assessmentTypes) return;

    samplingPointColumns.value = [
      {
        field: "details",
        headerName: "Details",
        flex: 1.5,
        valueGetter: (params) => {
          return `${params.data.station || ""} ${params.data.pollutant || ""} ${params.data.timestep || ""} ${params.data.concentration || ""} (ID: ${params.data.sampling_point_id || ""})`;
        }
      },
      {
        field: "assessment_type_id",
        headerName: "Assessment Type",
        flex: 1,
        editable: true,
        cellEditor: "agSelectCellEditor",
        cellEditorParams: {
          values: assessmentTypes.map((at) => at.label)
        },
        valueGetter: (params) => {
          // Convert ID to label for display
          if (!params.data.assessment_type_id) return "";
          const type = assessmentTypes.find((at) => at.value === params.data.assessment_type_id);
          return type ? type.label : "";
        },
        valueSetter: (params) => {
          // Convert label back to ID when saving
          const type = assessmentTypes.find((at) => at.label === params.newValue);
          if (type) {
            params.data.assessment_type_id = type.value;
            return true;
          }
          return false;
        }
      },
      {
        field: "description",
        headerName: "Description",
        flex: 1,
        editable: true
      }
    ];
  },
  { immediate: true }
);

watch(
  () => props.show,
  () => {
    if (!props.selectedValue) {
      obj.value = props.options.properties.reduce((a, v) => ({ ...a, [v.prop]: v.default }), {});
      gridData.value = [];
      selectedSamplingPointIds.value = new Set();
    } else {
      obj.value = { ...props.selectedValue };
      const data = props.selectedValue.data || [];
      gridData.value = [...data];
      selectedSamplingPointIds.value = new Set(data.map((d) => d.sampling_point_id));
    }
    if (props.show) {
      onPollutantChange();
      setTimeout(() => updateGridSelection(), 150);
    }
  }
);

const onSave = () => {
  const selectedRows = gridApi.value?.getSelectedRows() || [];
  const data = selectedRows.map((row) => ({
    ...row,
    assessment_regime_id: obj.value.id
  }));

  emit("save", { ...obj.value, data });
};

const onPollutantChange = () => {
  if (!props.options?.lookups || !obj.value.pollutant_id) return;

  const newData = props.options.lookups["sampling_points"].filter((p) => p.pollutant_id == obj.value.pollutant_id);
  const currentData = gridData.value || [];

  newData.forEach((d) => {
    d.assessment_regime_id = obj.value.id;
    const existing = currentData.find((o) => o.sampling_point_id == d.sampling_point_id);
    d.assessment_type_id = existing?.assessment_type_id || null;
    d.description = existing?.description || null;
  });

  gridData.value = newData;
  setTimeout(() => updateGridSelection(), 100);
};

const updateGridSelection = () => {
  if (!gridApi.value) return;

  setTimeout(() => {
    gridApi.value.deselectAll();
    if (selectedSamplingPointIds.value.size > 0) {
      gridApi.value.forEachNode((node) => {
        if (selectedSamplingPointIds.value.has(node.data.sampling_point_id)) {
          node.setSelected(true);
        }
      });
    }
  }, 0);
};

const onSelectionChanged = (rows) => {
  selectedSamplingPointIds.value = new Set(rows.map((row) => row.sampling_point_id));
};

const onGridReady = (api) => {
  gridApi.value = api;
  updateGridSelection();
};

const getRowId = (params) => params.data.sampling_point_id;

const sortedGridData = computed(() => {
  if (!gridData.value) return [];

  const mappedData = gridData.value.map((sp) => ({
    ...sp,
    sortOrder: selectedSamplingPointIds.value.has(sp.sampling_point_id) ? 0 : 1
  }));

  return sortBy(mappedData, ["sortOrder", "station", "pollutant"]);
});

const title = computed(() => {
  const entityName = props.options?.entityName || "Assessment Regime";
  return props.isEdit ? `Edit ${entityName}` : `Create ${entityName}`;
});
</script>

<template>
  <popup :show="show" :title="title" @on-close="emit('close')" class="w-[90%]! h-[90%]">
    <div class="flex flex-col h-full">
      <!-- Required Fields Section -->
      <div class="p-4 border-b border-gray-300">
        <div class="mb-2 font-bold text-lg">Required</div>
        <div class="grid grid-cols-2 gap-4">
          <template v-for="p in props.options.properties">
            <div v-if="p.type != 'custom' && p.type != 'gridOnly'">
              <div v-if="!p.enableInEdit && isEdit">
                <div class="font-bold">{{ p.label }}:</div>
                <input class="input w-full" v-model="obj[p.prop]" :disabled="true" />
              </div>
              <div v-else>
                <div v-if="p.type == 'text' || p.type == 'number'">
                  <div class="font-bold">{{ p.label }}:</div>
                  <input :type="p.type" class="input w-full" v-model="obj[p.prop]" :placeholder="p.placeholder" />
                </div>
                <div v-else-if="p.type == 'checkbox'" class="flex cursor-pointer hover:bg-gray-50 p-1">
                  <div class="font-bold self-center flex-1" @click="obj[p.prop] = !obj[p.prop]">{{ p.label }}:</div>
                  <input type="checkbox" v-model="obj[p.prop]" class="self-center" />
                </div>
                <div v-else-if="p.type == 'lookup'">
                  <div class="font-bold">{{ p.label }}:</div>
                  <select v-model="obj[p.prop_id]" class="select w-full" :disabled="p.prop_id === 'pollutant_id' && selectedSamplingPointIds.size > 0" @change="p.prop_id === 'pollutant_id' && onPollutantChange()">
                    <option v-if="p.prop_id == 'zone_id'" value="" label="No zone">No zone</option>
                    <option v-for="p in options.lookups[p.lookup]" :key="p.value" :value="p.value">{{ p.label }}</option>
                  </select>
                </div>
                <div v-else-if="p.type == 'eeaDatetime'">
                  <div class="font-bold">{{ p.label }}:</div>
                  <input type="datetime-local" v-model="obj[p.prop]" class="input w-full" />
                </div>
              </div>
            </div>
          </template>
        </div>
      </div>

      <!-- Sampling Points Section -->
      <div class="flex-1 flex flex-col border-b border-gray-300 min-h-0">
        <div class="p-4 pb-2">
          <div class="font-bold text-lg">{{ props.options.properties.find((p) => p.type === "custom")?.label || "Sampling Points" }}</div>
        </div>
        <div class="flex-1 px-4 pb-4 min-h-0">
          <DataTable :data="sortedGridData" :columns="samplingPointColumns" :filter="true" :floating-filter="false" :responsive="true" selection-mode="multiRow" :get-row-id="getRowId" @selection-changed="onSelectionChanged" @grid-ready="onGridReady" />
        </div>
      </div>

      <!-- Buttons Section -->
      <div class="pt-4">
        <div class="flex justify-end gap-4">
          <button class="button" @click="onSave">Save</button>
          <button class="button" @click="emit('close')">Cancel</button>
        </div>
      </div>
    </div>
  </popup>
</template>
