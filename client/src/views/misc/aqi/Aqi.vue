<script setup>
import { onMounted, computed, ref } from "vue";
import ToolBar from "../../../components/ToolBar.vue";
import Container from "../../../components/Container.vue";
import CommonLayout from "../../../components/CommonLayout.vue";

import Service from "./service";
import Aqi from "./aqi.js";
import Eventy from "../../../helpers/eventy";

const aqiData = ref([]);
const pollutants = ref([]);
const timesteps = ref([]);
const showEmptyMessage = ref(false);
const levels = ref([{ index: 1, description: "Good", color: "#026440" }]);
const pollutant_groups = ref([]);
const selectedPollutant = ref(null);
const selectedTimestep = ref(null);

onMounted(async () => {
  pollutants.value = await Service.pollutants();
  timesteps.value = await Service.timesteps();
  await load();
});

const load = async () => {
  aqiData.value = await Service.get();
  showEmptyMessage.value = aqiData.value.length === 0;

  let { levels: l, pollutant_groups: r } = Aqi.convert_to_groups(aqiData.value);
  levels.value = l;
  pollutant_groups.value = r;
};

const addLevel = () => {
  console.log("Adding new level");
  levels.value.push({ index: levels.value.length + 1, description: "", color: "#cccccc" });
  // Add a new range for each pollutant for the new level
  pollutant_groups.value.forEach((pg) => {
    var new_range = Aqi.add_range(pg, levels.value[levels.value.length - 1].index);
    pg.ranges.push(new_range);
  });
};
const addPollutantGroup = () => {
  console.log("Adding pollutant group");
  if (selectedPollutant.value && selectedTimestep.value) {
    var new_range = Aqi.add_pollutant_group(selectedPollutant.value, selectedTimestep.value, levels.value);
    pollutant_groups.value.push(new_range);
    selectedPollutant.value = null;
    selectedTimestep.value = null;
  }
};

const removeLevel = () => {
  console.log("Removing level");
  if (levels.value.length > 1) {
    levels.value.pop();
    // Remove the last range for each pollutant
    pollutant_groups.value.forEach((pg) => {
      pg.ranges.pop();
    });
  }
};

const removeAqi = () => {
  console.log("Removing local AQI configuration");
  pollutant_groups.value = [];
  levels.value = [];
  aqiData.value = [];
};

// Returns true if a range for the selected pollutant and timestep already exists
const groupExists = () => {
  return pollutant_groups.value.some((r) => r.pollutant === selectedPollutant.value.label && r.timestep === selectedTimestep.value.label);
};

// Remove a pollutant range at the given index
const removeRange = (idx) => {
  pollutant_groups.value.splice(idx, 1);
};

const save = async () => {
  console.log("Saving AQI");
  const flattened = Aqi.flatten_pollutant_groups(pollutant_groups.value, levels.value);

  console.log(flattened);
  if (flattened.length === 0) localStorage.removeItem("aqi_type");

  Eventy.showMessage("Saving AQI configuration. Please wait", "loading");
  await Service.save(flattened);
  await load();
  Eventy.showHideMessage("AQI configuration saved", "success");
};

const isSaveDisabled = computed(() => {
  if (!levels.value.every((l) => l.description && l.color)) return true;
  // Check pollutant_groups: all ranges must have from and to (not null or empty)
  for (const pg of pollutant_groups.value) {
    for (const r of pg.ranges) {
      if (r.range_from === null || r.range_from === undefined || r.range_to === null || r.range_to === undefined || r.range_from === "" || r.range_to === "") {
        return true;
      }
    }
  }
  return false;
});
</script>

<template>
  <common-layout>
    <tool-bar title="Local AQI" :show-column-picker="false" :show-add="false" :show-download="false" :show-filter="false" />

    <container v-if="showEmptyMessage">
      <div class="font-bold">Raven uses EEA methodology for air quality index calculations, but you can set up your own local AQI configuration.</div>

      <div><button class="button" @click="showEmptyMessage = false">Setup Local AQI</button></div>
    </container>

    <div v-if="!showEmptyMessage" class="flex flex-col gap-6 h-full overflow-y-hidden">
      <!-- Levels -->
      <div class="flex flex-col gap-2">
        <table class="table">
          <thead>
            <tr>
              <th>Index</th>
              <th>Description</th>
              <th>Color</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(level, idx) in levels" :key="idx">
              <td class="w-20">{{ level.index }}</td>
              <td><input v-model="level.description" placeholder="Description" class="input w-full" /></td>
              <td class="w-40"><input v-model="level.color" placeholder="Color (hex)" class="input w-full cursor-pointer" type="color" /></td>
            </tr>
          </tbody>
        </table>
        <div class="flex justify-start gap-2">
          <button class="button" @click="addLevel">Add Level</button>
          <button class="button" @click="removeLevel" :disabled="levels.length <= 1">Remove Level</button>
          <button class="button" @click="removeAqi">Delete Local AQI</button>
        </div>
      </div>

      <div class="border-t border-gray-300"></div>

      <!-- Pollutant Ranges -->
      <div class="h-full flex flex-col overflow-hidden">
        <h3 class="font-bold mb-2">Pollutant Groups</h3>
        <div class="flex gap-4">
          <select class="select" v-model="selectedPollutant">
            <option v-for="pollutant in pollutants" :key="pollutant.value" :value="pollutant">{{ pollutant.label }}</option>
          </select>
          <select class="select" v-model="selectedTimestep">
            <option v-for="timestep in timesteps" :key="timestep.value" :value="timestep">{{ timestep.label }}</option>
          </select>
          <button class="button" @click="addPollutantGroup" :disabled="!selectedPollutant || !selectedTimestep || groupExists()">Add Pollutant Group</button>
        </div>

        <div class="h-full overflow-y-auto flex flex-col mt-4">
          <container class="mt-6" v-for="(pg, idx) in pollutant_groups">
            <div class="flex justify-between">
              <div class="font-bold self-center">{{ pg.pollutant }} - {{ pg.timestep }}</div>
              <button class="button self-center" @click="removeRange(idx)">Remove</button>
            </div>
            <table class="table mt-2">
              <thead>
                <tr>
                  <th>Index</th>
                  <th>Range from</th>
                  <th>Range to</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(r, rIdx) in pg.ranges" :key="rIdx">
                  <td class="w-20">{{ r.level }}</td>
                  <td><input v-model.number="r.range_from" placeholder="From" class="input w-full" type="number" /></td>
                  <td><input v-model.number="r.range_to" placeholder="To" class="input w-full" type="number" /></td>
                </tr>
              </tbody>
            </table>
          </container>
        </div>
      </div>

      <div class="border-t border-gray-300"></div>
      <div class="flex justify-end gap-4 h-24 mb-4">
        <button class="button self-center" @click="load">Cancel</button>
        <button class="button self-center" @click="save" :disabled="isSaveDisabled">Save</button>
      </div>
    </div>
  </common-layout>
</template>
