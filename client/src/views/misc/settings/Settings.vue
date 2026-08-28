<script setup>
import { onMounted, ref } from "vue";
import CommonLayout from "../../../components/CommonLayout.vue";
import ToolBar from "../../../components/ToolBar.vue";
import Container from "../../../components/Container.vue";
import Service from "./service";
import LogFilterRules from "./LogFilterRules.vue";
import Eventy from "../../../helpers/eventy";

const settings = ref({
  country_code_id: "",
  timezone_id: "",
  observation_log_config: {}
});

const lookups = ref({
  countries: [],
  timezones: []
});

onMounted(async () => {
  // Load lookups
  lookups.value = await Service.lookups();

  // Load current settings. Assign the two known fields rather than the whole
  // row: the endpoint does `SELECT s.*`, so a database still on the pre-v4
  // settings shape returns namespace/uom_m/... and replacing the object
  // wholesale would blank country_code_id and leave Save permanently disabled.
  const data = await Service.get();
  if (data && data.length > 0) {
    settings.value = {
      country_code_id: data[0].country_code_id ?? "",
      timezone_id: data[0].timezone_id ?? "",
      observation_log_config: data[0].observation_log_config ?? {}
    };
  }
});

const onSave = async () => {
  Eventy.showMessage("Saving settings...", "loading");
  await Service.save({
    country_code_id: settings.value.country_code_id,
    timezone_id: settings.value.timezone_id,
    observation_log_config: settings.value.observation_log_config
  });
  Eventy.showHideMessage("Settings saved successfully", "success", 3000);
};
</script>

<template>
  <common-layout>
    <tool-bar title="Settings" :show-column-picker="false" :show-add="false" :show-download="false" :show-filter="false" />

    <container class="p-4!">
      <div class="flex gap-4 items-end">
        <div class="flex-1">
          <label class="font-bold">
            Country
            <span class="text-nord11">*</span>
          </label>
          <select class="select w-full" v-model="settings.country_code_id">
            <option value="">Select country</option>
            <option v-for="c in lookups.countries" :key="c.value" :value="c.value">{{ c.label }}</option>
          </select>
        </div>

        <div class="flex-1">
          <label class="font-bold">
            Timezone
            <span class="text-nord11">*</span>
          </label>
          <select class="select w-full" v-model="settings.timezone_id">
            <option value="">Select timezone</option>
            <option v-for="t in lookups.timezones" :key="t.value" :value="t.value">{{ t.label }}</option>
          </select>
        </div>

        <div>
          <button class="button" :disabled="!settings.country_code_id || !settings.timezone_id" @click="onSave">Save Settings</button>
        </div>
      </div>

      <div class="border-t border-nord4 mt-6 pt-4">
        <log-filter-rules v-model="settings.observation_log_config" />
      </div>
    </container>
  </common-layout>
</template>
