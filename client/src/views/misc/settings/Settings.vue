<script setup>
import { onMounted, ref } from "vue";
import CommonLayout from "../../../components/CommonLayout.vue";
import ToolBar from "../../../components/ToolBar.vue";
import Container from "../../../components/Container.vue";
import Service from "./service";
import Eventy from "../../../helpers/eventy";

const settings = ref({
  country_code_id: "",
  timezone_id: ""
});

const lookups = ref({
  countries: [],
  timezones: []
});

onMounted(async () => {
  // Load lookups
  lookups.value = await Service.lookups();

  // Load current settings
  const data = await Service.get();
  if (data && data.length > 0) {
    settings.value = data[0];
  }
});

const onSave = async () => {
  Eventy.showMessage("Saving settings...", "loading");
  await Service.save(settings.value);
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
    </container>
  </common-layout>
</template>
