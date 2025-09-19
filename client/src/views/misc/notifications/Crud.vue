<script setup>
import { ref, watch, computed } from "vue";
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

const onSelect = (mv) => {
  mv.selected = selectAll.value ? mv.selected : !mv.selected;
  selectAll.value = false;
  // Add or remove from obj.value.sampling_points based on mv.selected
  if (!obj.value.sampling_points) obj.value.sampling_points = [];
  if (mv.selected) {
    // add
    if (!obj.value.sampling_points.includes(mv.spo)) obj.value.sampling_points.push(mv.spo);
  } else {
    // remove
    obj.value.sampling_points = obj.value.sampling_points.filter((sp) => sp !== mv.spo);
  }
};

const onSelectAll = () => {
  selectAll.value = !selectAll.value;
  obj.value.sampling_points = [];
};
</script>

<template>
  <popup :title="title" :show="show" @on-close="$emit('on-close', false)" class="w-[95%] h-[95%]">
    <div class="flex flex-col gap-4 h-full">
      <div class="flex gap-2 text-sm mt-4">
        <div class="w-1/6">
          <label class="font-bold">Name</label>
          <br />
          <input class="n-input w-full" type="text" v-model="obj.name" />
        </div>
        <div class="w-4/6">
          <label class="font-bold">Emails (semicolon-separated)</label>
          <br />
          <input class="n-input w-full" type="text" v-model="obj.emails" />
        </div>
        <div class="w-1/6">
          <label class="font-bold">Enabled</label>
          <br />
          <n-checkbox class="scale-[1.4] mt-2 ml-1" v-model="obj.enabled" />
        </div>
      </div>

      <div class="flex-1 flex-col overflow-auto mt-4">
        <table class="n-table w-full">
          <thead>
            <tr>
              <th @click="onSelectAll" class="!cursor-pointer"><n-checkbox class=" " v-model="selectAll" :disabled="true" /></th>
              <th>SPO</th>
              <th>Station</th>
              <th>Pollutant</th>
              <th>Concentration</th>
              <th>Timestep</th>
              <th>Type</th>
            </tr>
          </thead>
          <tr v-for="mv in cmp_samplingpoints" :key="mv.id" @click="onSelect(mv)">
            <td><n-checkbox class="align-middle" v-model="mv.selected" :disabled="true" /></td>
            <td>{{ mv.spo }}</td>
            <td>{{ mv.station }}</td>
            <td>{{ mv.pollutant }}</td>
            <td>{{ mv.concentration }}</td>
            <td>{{ mv.timestep }}</td>
            <td>{{ mv.type }}</td>
          </tr>
        </table>
      </div>

      <!-- BUTTONS -->
      <div class="flex justify-end gap-2 h-20">
        <div><button class="n-button" @click="$emit('on-close', false)">Cancel</button></div>
        <div><button class="n-button" :disabled="!obj.name || !obj.emails" @click="onSave">Save</button></div>
      </div>
    </div>
  </popup>
</template>
