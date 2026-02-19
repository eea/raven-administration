<script setup>
import { onMounted, ref } from "vue";
import CommonLayout from "../../../components/CommonLayout.vue";
import ToolBar from "../../../components/ToolBar.vue";
import Container from "../../../components/Container.vue";
import Service from "./service";
import Eventy from "../../../helpers/eventy";

const settings = ref({
  id: "",
  namespace: "",
  observation_prefix: "",
  language_code: ""
});

onMounted(async () => {
  const data = await Service.get();
  if (data && data.length > 0) {
    settings.value = data[0];
  }
});

const onSave = async () => {
  Eventy.showMessage("Saving settings...", "loading");
  await Service.update(settings.value);
  Eventy.showHideMessage("Settings saved successfully", "success", 3000);
};
</script>

<template>
  <common-layout>
    <tool-bar title="Settings" :show-column-picker="false" :show-add="false" :show-download="false" :show-filter="false" />

    <container class="p-4!">
      <div class="flex gap-4 items-end">
        <div class="flex-1">
          <label class="font-bold">Namespace</label>
          <input class="input w-full" type="text" v-model="settings.namespace" placeholder="Namespace to be used in dataflow" />
        </div>

        <div class="flex-1">
          <label class="font-bold">Observation prefix</label>
          <input class="input w-full" type="text" v-model="settings.observation_prefix" placeholder="Dataflow prefix for observations" />
        </div>

        <div class="w-32">
          <label class="font-bold">Language code</label>
          <input class="input w-full" type="text" v-model="settings.language_code" placeholder="Language to be used in dataflow" />
        </div>

        <div>
          <button class="button" @click="onSave">Save Settings</button>
        </div>
      </div>
    </container>
  </common-layout>
</template>
