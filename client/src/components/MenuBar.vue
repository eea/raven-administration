<script setup>
import { useRouter } from "vue-router";
import Auth from "../helpers/auth";
import IconLogout from "~icons/ic/outline-logout";
import { version } from "../helpers/utils";
const router = useRouter();

const modules = [
  {
    group: "Management",
    items: [
      { name: "Authorities", comp: "Authorities" },
      { name: "Networks", comp: "Networks" },
      { name: "Zones", comp: "Zones" },
      // { name: "Areas", comp: "management/areas" },
      { name: "Sampling Points", comp: "SamplingPoints" },
      { name: "Stations", comp: "Stations" },
      { name: "Processes", comp: "Processes" },
      { name: "Samples", comp: "Samples" },
      { name: "Observing Capabilities", comp: "ObservingCapabilities" },
      { name: "Assessment Regimes", comp: "AssessmentRegimes" }
      // { name: "Timeseries", comp: "management/timeseries" }
    ]
  },
  {
    group: "Data",
    items: [
      { name: "Latest data", comp: "Latest" },
      { name: "Historical data", comp: "Historical" },
      { name: "Dataflow", comp: "Dataflow" }
    ]
  },
  {
    group: "Import process",
    items: [
      { name: "Auto validate", comp: "AutoValidate" },
      { name: "Convert", comp: "Convert" },
      { name: "Calculate", comp: "Calculate" },
      { name: "Scale", comp: "Scale" }
    ]
  },
  {
    group: "Quality control",
    items: [
      { name: "Validate", comp: "Validate" },
      { name: "Verify", comp: "Verify" }
    ]
  },
  {
    group: "Access",
    items: [
      { name: "Users", comp: "access/users" },
      { name: "Groups", comp: "access/groups" }
    ]
  }
];
const goto = (comp) => {
  router.push({ name: comp });
};

const signout = async () => {
  Auth.signout();
  router.push({ name: "Login" });
};

const cmp_version = computed(() => version);
</script>

<template>
  <div class="border border-nord4 flex flex-col justify-between bg-gray-50 select-none">
    <div>
      <div class="mt-1 flex flex-col border-b" v-for="m in modules" :key="m.group">
        <div class="font-bold select-none px-2 mt-2 mb-1">{{ m.group }}</div>
        <div class="hover:bg-gray-100 hover:cursor-pointer" v-for="i in m.items" :key="i.name" @click="goto(i.comp)">
          <div class="py-1 px-4">{{ i.name }}</div>
        </div>
      </div>
    </div>
    <div class="">
      <div class="px-1 text-xs font-bold border-b">v.{{ cmp_version }}</div>
      <div class="flex py-2 px-2 hover:cursor-pointer hover:bg-nord8/20 hover:text-nord10" @click="signout">
        <icon-logout class="self-center" />
        <div class="self-center ml-1">Sign out</div>
      </div>
    </div>
  </div>
</template>

<style></style>
