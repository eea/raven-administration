<script setup>
import { ref, watch, computed } from "vue";
import Popup from "../../../components/Popup.vue";
import DataTable from "../../../components/DataTable.vue";

import Service from "./service";
import Eventy from "../../../helpers/eventy";
import { sortBy } from "../../../helpers/utils";

const props = defineProps({
  show: Boolean,
  data: {},
  samplingPoints: Array
});
const $emit = defineEmits(["on-close"]);

const title = ref("Add/Edit Notifications");
const obj = ref(null);
const selectAll = ref(false);
const gridApi = ref(null);

const cmp_samplingpoints = computed(() => {
  // list all props.samplingpoints, but add a "selected" field based on whether it's in obj.value.samplingpoints
  if (!props.samplingPoints || !obj.value) return [];

  // Convert sampling_points to Set for O(1) lookup instead of O(n) includes()
  const selectedPoints = obj.value.sampling_points ? new Set(obj.value.sampling_points) : new Set();

  const mappedData = props.samplingPoints.map((sp) => ({
    ...sp,
    selected: selectAll.value || selectedPoints.has(sp.spo),
    // Add a sort helper for selection (0 for selected, 1 for unselected)
    sortOrder: selectAll.value || selectedPoints.has(sp.spo) ? 0 : 1
  }));

  // Use sortBy utility to sort by selection status, then station, then pollutant
  return sortBy(mappedData, ["sortOrder", "station", "pollutant"]);
});

watch(
  () => props.show,
  () => {
    if (!props.data) {
      obj.value = null;
      selectAll.value = false;
    } else {
      obj.value = JSON.parse(JSON.stringify(props.data));
      obj.value.originalname = props.data.name;
      if (obj.value.sampling_points && obj.value.sampling_points.length === 0) selectAll.value = true;
      // console.log(obj.value);
    }
    // Update grid selection when dialog opens
    setTimeout(() => updateGridSelection(), 150);
  }
);

const onSave = async () => {
  var o = {
    originalname: obj.value.originalname ?? null,
    name: obj.value.name,
    emails: obj.value.emails,
    enabled: obj.value.enabled || false,
    sampling_points: selectAll.value ? [] : JSON.parse(JSON.stringify(obj.value.sampling_points || []))
  };
  console.log(o);

  Eventy.showMessage("Saving data, Please wait!", "loading");
  await Service.save(o);
  Eventy.showHideMessage(`Notification saved`, "success", 5000);
  $emit("on-close", true);
};

const onSelectionChanged = (rows) => {
  if (!obj.value) return;

  // If all rows are selected, store empty array (means "all current and future sampling points")
  if (rows.length === props.samplingPoints.length) {
    selectAll.value = true;
    obj.value.sampling_points = [];
  } else {
    // Otherwise, store the specific selected spo values
    selectAll.value = false;
    obj.value.sampling_points = rows.map((row) => row.spo);
  }
};

const updateGridSelection = () => {
  if (!gridApi.value || !obj.value) return;

  setTimeout(() => {
    if (!gridApi.value) return;

    gridApi.value.deselectAll();

    if (selectAll.value) {
      gridApi.value.selectAll();
    } else if (obj.value.sampling_points && obj.value.sampling_points.length > 0) {
      gridApi.value.forEachNode((node) => {
        if (obj.value.sampling_points.includes(node.data.spo)) {
          node.setSelected(true);
        }
      });
    }
  }, 0);
};

const onGridReady = (api) => {
  gridApi.value = api;
  updateGridSelection();
};

const getRowId = (params) => params.data.spo;
const samplingPointColumns = [
  { field: "spo", headerName: "SPO", flex: 1 },
  { field: "station", headerName: "Station", flex: 1 },
  { field: "pollutant", headerName: "Pollutant", flex: 1 },
  { field: "concentration", headerName: "Concentration", flex: 0.7 },
  { field: "timestep", headerName: "Timestep", flex: 0.7 },
  { field: "type", headerName: "Type", flex: 1 }
];
</script>

<template>
  <popup :title="title" :show="show" @on-close="$emit('on-close', false)" class="w-[95%] h-[95%]">
    <div class="flex flex-col gap-4 h-full">
      <div class="flex gap-2 text-sm mt-4">
        <div class="w-1/6">
          <label class="font-bold">Name</label>
          <br />
          <input class="input w-full" type="text" v-model="obj.name" />
        </div>
        <div class="w-4/6">
          <label class="font-bold">Emails (semicolon-separated)</label>
          <br />
          <input class="input w-full" type="text" v-model="obj.emails" />
        </div>
        <div class="w-1/6">
          <label class="font-bold">Enabled</label>
          <br />
          <input type="checkbox" class="mt-2 ml-1" v-model="obj.enabled" />
        </div>
      </div>

      <div class="flex-1 flex flex-col mt-4 min-h-0">
        <DataTable :data="cmp_samplingpoints" :columns="samplingPointColumns" :filter="true" :floating-filter="false" :responsive="true" selection-mode="multiRow" :get-row-id="getRowId" @selection-changed="onSelectionChanged" @grid-ready="onGridReady" />
      </div>

      <!-- BUTTONS -->
      <div class="flex justify-end gap-2 h-20">
        <div><button class="button" @click="$emit('on-close', false)">Cancel</button></div>
        <div><button class="button" :disabled="!obj.name || !obj.emails" @click="onSave">Save</button></div>
      </div>
    </div>
  </popup>
</template>
