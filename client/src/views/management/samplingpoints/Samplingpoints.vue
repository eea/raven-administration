<script setup>
import { onMounted, ref } from "vue";
import Manager from "../../../components/n-manager/Manager.vue";
import Service from "./service";
import pageOptions from "./pageOptions";
import usePluginPageExtension from "../../../composables/usePluginPageExtension";
import SamplingPointLog from "./SamplingPointLog.vue";
import SamplingPointLocations from "./SamplingPointLocations.vue";
import IconLog from "~icons/material-symbols/assignment-outline";
import IconLocation from "~icons/material-symbols/location-on-outline";

const { extendOptions, extendService } = usePluginPageExtension('samplingpoints');
const service = extendService(Service);
const options = ref({});

const showLog = ref(false);
const logSamplingPoint = ref(null);

const showLocations = ref(false);
const locationsSamplingPoint = ref(null);

const onContextMenuAction = ({ action, data }) => {
  if (action === "view_log") {
    logSamplingPoint.value = data?.row ?? null;
    showLog.value = true;
  }
  if (action === "view_locations") {
    locationsSamplingPoint.value = data?.row ?? null;
    showLocations.value = true;
  }
};

onMounted(async () => {
  const lookups = await service.lookups();
  // await: extendOptions may fetch plugin-contributed lookup lists.
  options.value = await extendOptions(pageOptions(lookups));
});
</script>

<template>
  <sampling-point-log :show="showLog" :sampling-point="logSamplingPoint" @close="showLog = false" />
  <sampling-point-locations :show="showLocations" :sampling-point="locationsSamplingPoint"
                            @close="showLocations = false" />

  <manager name="Sampling points" :options="options" :service="service" @context-menu-action="onContextMenuAction">
    <template #extra-context-menu-items="{ handleAction }">
      <div class="pl-2 pr-4 py-1.5 flex cursor-pointer hover:bg-nord6" @click="handleAction('view_log')">
        <icon-log class="text-nord10 text-base self-center" />
        <div class="self-center ml-1">View log</div>
      </div>
      <div class="pl-2 pr-4 py-1.5 flex cursor-pointer hover:bg-nord6" @click="handleAction('view_locations')">
        <icon-location class="text-nord10 text-base self-center" />
        <div class="self-center ml-1">Location history</div>
      </div>
    </template>
  </manager>
</template>
