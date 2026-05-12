<script setup>
import { onMounted, ref, watch } from "vue";
import { useRouter } from "vue-router";
import Auth from "../helpers/auth";
import IconLogout from "~icons/ic/outline-logout";
import IconNewVersion from "~icons/material-symbols/download-for-offline-rounded";
import IconPlugin from "~icons/ic/baseline-extension";
import { jwtDecode } from "jwt-decode";
import Version from "../helpers/version";
import Eventy from "../helpers/eventy";
import { Get } from "../helpers/request";

const router = useRouter();
const modules = ref([]);
const version = ref({ current: "-", isLatest: true });
const pluginStatus = ref({});

// Plugin modules – resolved at build time. Empty when no plugins installed.
const pluginModules = import.meta.glob("../plugins/*/index.js", { eager: true });

const props = defineProps({
  show: Boolean
});

watch(
  () => props.show,
  () => (modules.value = getmodules())
);

onMounted(async () => {
  version.value = await Version.get();
  await loadPluginStatus();
  modules.value = getmodules();
  Eventy.listen("plugins-updated", loadPluginStatus);
});

const loadPluginStatus = async () => {
  if (!Auth.isAuth()) return;
  try {
    const list = await Get("/api/misc/plugins");
    // Build a lookup by plugin id: { nilu: { enabled: true, ... }, ... }
    pluginStatus.value = Object.fromEntries((list ?? []).map((p) => [p.id, p]));
  } catch {
    pluginStatus.value = {};
  }
};

const getmodules = () => {
  var token = sessionStorage.getItem("token");
  if (!token) return [];
  const jwt = jwtDecode(token);
  return [
    {
      group: "Management",
      show: jwt.management,
      items: [
        { name: "Documents", comp: "Documents", show: jwt.management && jwt.allnetworks },
        { name: "Authorities", comp: "Authorities", show: jwt.management && jwt.allnetworks },
        { name: "Zones", comp: "Zones", show: jwt.management && jwt.allnetworks },
        { name: "Networks", comp: "Networks", show: jwt.management },
        { name: "Stations", comp: "Stations", show: jwt.management },
        { name: "Sampling Points", comp: "SamplingPoints", show: jwt.management },
        { name: "Processes", comp: "Processes", show: jwt.management },
        { name: "Assessment Regime Zones", comp: "AssessmentRegimeZones", show: jwt.management && jwt.allnetworks },
        { name: "Spatial Representativeness", comp: "SpatialRepresentativeness", show: jwt.management }
      ]
    },
    {
      group: "Data",
      show: jwt.data || jwt.exporting,
      items: [
        { name: "Dashboard", comp: "Dashboard", show: jwt.data },
        { name: "Latest data", comp: "Latest", show: jwt.data },
        { name: "Historical data", comp: "Historical", show: jwt.data },
        { name: "Dataflow", comp: "Dataflow", show: jwt.exporting },
        { name: "Statistics", comp: "Statistics", show: jwt.data },
        { name: "Exceedances", comp: "DataExceedances", show: jwt.data },
        { name: "Map", comp: "Map", show: jwt.data },
        { name: "R Notebook", comp: "RNotebook", show: jwt.data }
      ]
    },
    {
      group: "Import process",
      show: jwt.processing,
      items: [
        { name: "Manual import", comp: "Import", show: jwt.processing && jwt.allnetworks },
        { name: "Auto validate", comp: "AutoValidate", show: jwt.processing },
        { name: "Convert", comp: "Convert", show: jwt.processing },
        { name: "Calculate", comp: "Calculate", show: jwt.processing },
        { name: "Scale", comp: "Scale", show: jwt.processing },
        { name: "Groups", comp: "SamplingPointGroups", show: jwt.processing }
      ]
    },
    {
      group: "Quality control",
      show: jwt.qualitycontrol,
      items: [
        { name: "Validate", comp: "Validate", show: jwt.qualitycontrol },
        { name: "Verify", comp: "Verify", show: jwt.qualitycontrol }
      ]
    },
    {
      group: "Misc",
      show: jwt.management && jwt.allnetworks,
      items: [
        { name: "Settings", comp: "Settings", show: jwt.management && jwt.allnetworks },
        { name: "Pre aggregation", comp: "PreAggregation", show: jwt.management && jwt.allnetworks },
        { name: "Local AQI", comp: "Aqi", show: jwt.management && jwt.allnetworks },
        { name: "Notifications", comp: "Notifications", show: jwt.management && jwt.allnetworks },
        { name: "Plugins", comp: "PluginManager", show: jwt.management && jwt.allnetworks }
      ]
    },
    {
      group: "Access",
      show: jwt.users,
      items: [
        { name: "Users", comp: "Users", show: jwt.users },
        { name: "Groups", comp: "Groups", show: jwt.users }
      ]
    },
    // Plugin-contributed menu groups
    ...Object.values(pluginModules).flatMap((m) => {
      const pid = m.pluginId;
      const isEnabled = pid ? (pluginStatus.value[pid]?.enabled ?? true) : true;
      return isEnabled ? (m.getMenuGroups?.(jwt) ?? m.menuGroups ?? []) : [];
    })
  ];
};

const goto_git_changelog = () => {
  // window.location.href = "https://git.nilu.no/raven/raven-administration/-/blob/master/CHANGELOG.md?ref_type=heads";
  window.open("https://github.com/eea/raven-administration/blob/master/CHANGELOG.md", "_blank");
};

const goto = (comp) => {
  router.push({ name: comp });
};

const signout = async () => {
  Auth.signout();
  router.push({ name: "Login" });
};
</script>

<template>
  <div class="border border-nord4 flex flex-col justify-between bg-gray-50 select-none" v-show="show">
    <div class="overflow-y-auto">
      <!-- RESTART REQUIRED ALERT -->
      <div v-if="Object.values(pluginStatus).some((p) => p.restart_required)" class="pt-2 px-1">
        <div class="border py-2 pl-1 pr-2 text-sm bg-nord13/20 flex gap-1 border-nord4 cursor-pointer" @click="goto('PluginManager')">
          <icon-plugin class="self-center text-nord13" />
          <div class="font-bold">Server restart required</div>
        </div>
      </div>
      <!-- NEW VERSION ALERT -->
      <div v-if="!version.isLatest" class="pt-2 px-1">
        <div class="border py-2 pl-1 pr-2 text-sm bg-nord11/10 flex gap-1 border-nord4 hover:bg-nord11/20 cursor-pointer" @click="goto_git_changelog">
          <icon-new-version class="self-center text-nord11 hover:text-nord12" />
          <div class="font-bold">New version available</div>
        </div>
      </div>
      <div class="mt-1 flex flex-col border-b border-nord4" v-for="m in modules" :key="m.group" v-show="m.show">
        <div class="font-bold select-none px-2 mt-2 mb-1">{{ m.group }}</div>
        <div class="hover:bg-gray-100 hover:cursor-pointer" v-for="i in m.items" :key="i.name" @click="goto(i.comp)" v-show="i.show">
          <div class="py-1 px-4">{{ i.name }}</div>
        </div>
      </div>
    </div>

    <div class="">
      <div class="flex px-1 text-xs font-bold border-b border-nord4 gap-1">
        <icon-new-version class="self-center text-nord11 hover:text-nord12" v-if="!version.isLatest" />
        <div class="self-center">v.{{ version.current }}</div>
      </div>
      <div class="flex py-2 px-2 hover:cursor-pointer hover:bg-nord8/20 hover:text-nord10" @click="signout">
        <icon-logout class="self-center" />
        <div class="self-center ml-1">Sign out</div>
      </div>
    </div>
  </div>
</template>

<style></style>
