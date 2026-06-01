<script setup>
import { onMounted, ref } from "vue";
import Manager from "../../../components/n-manager/Manager.vue";
import Service from "./service";
import pageOptions from "./pageOptions";
import usePluginPageExtension from "../../../composables/usePluginPageExtension";
import SamplingPointLog from "./SamplingPointLog.vue";
import IconLog from "~icons/material-symbols/assignment-outline";

const { extendOptions, extendService } = usePluginPageExtension('samplingpoints');
const service = extendService(Service);
const options = ref({});

const showLog = ref(false);
const logSamplingPoint = ref(null);

const onContextMenuAction = ({ action, data }) => {
  if (action === "view_log") {
    logSamplingPoint.value = data?.row ?? null;
    showLog.value = true;
  }
};

onMounted(async () => {
  const lookups = await service.lookups();
  options.value = extendOptions(pageOptions(lookups));
});
</script>

<template>
  <sampling-point-log :show="showLog" :sampling-point="logSamplingPoint" @close="showLog = false" />

  <manager name="Sampling points" :options="options" :service="service" @context-menu-action="onContextMenuAction">
    <template #extra-context-menu-items="{ handleAction }">
      <div class="pl-2 pr-4 py-1.5 flex cursor-pointer hover:bg-nord6" @click="handleAction('view_log')">
        <icon-log class="text-nord10 text-base self-center" />
        <div class="self-center ml-1">View log</div>
      </div>
    </template>
  </manager>
</template>
