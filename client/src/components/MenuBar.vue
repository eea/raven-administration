<script setup>
import { useRouter } from "vue-router";
import Auth from "../helpers/auth";
import IconLogout from "~icons/ic/outline-logout";
import { version } from "../helpers/utils";
import jwt_decode from "jwt-decode";

const router = useRouter();
const modules = ref([]);

const props = defineProps({
  show: Boolean
});

watch(
  () => props.show,
  () => (modules.value = getmodules())
);

onMounted(() => {
  modules.value = getmodules();
});

const getmodules = () => {
  var token = sessionStorage.getItem("token");
  if (!token) return [];
  const jwt = jwt_decode(token);
  return [
    {
      group: "Management",
      show: jwt.management,
      items: [
        { name: "Authorities", comp: "Authorities", show: jwt.management && jwt.allnetworks },
        { name: "Zones", comp: "Zones", show: jwt.management && jwt.allnetworks },
        { name: "Networks", comp: "Networks", show: jwt.management },
        { name: "Stations", comp: "Stations", show: jwt.management },
        { name: "Sampling Points", comp: "SamplingPoints", show: jwt.management },
        { name: "Observing Capabilities", comp: "ObservingCapabilities", show: jwt.management },
        { name: "Processes", comp: "Processes", show: jwt.management },
        { name: "Samples", comp: "Samples", show: jwt.management },
        { name: "Assessment Regimes", comp: "AssessmentRegimes", show: jwt.management && jwt.allnetworks },
        { name: "Attainments", comp: "Attainments", show: jwt.management && jwt.allnetworks },
        { name: "Exceedances", comp: "Exceedances", show: jwt.management && jwt.allnetworks },
        { name: "Settings", comp: "Settings", show: jwt.management && jwt.allnetworks }
      ]
    },
    {
      group: "Data",
      show: jwt.data || jwt.exporting,
      items: [
        { name: "Latest data", comp: "Latest", show: jwt.data },
        { name: "Historical data", comp: "Historical", show: jwt.data },
        { name: "Dataflow", comp: "Dataflow", show: jwt.exporting }
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
        { name: "Scale", comp: "Scale", show: jwt.processing }
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
      group: "Access",
      show: jwt.users,
      items: [
        { name: "Users", comp: "Users", show: jwt.users },
        { name: "Groups", comp: "Groups", show: jwt.users }
      ]
    }
  ];
};

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
  <div class="border border-nord4 flex flex-col justify-between bg-gray-50 select-none" v-show="show">
    <div>
      <div class="mt-1 flex flex-col border-b" v-for="m in modules" :key="m.group" v-show="m.show">
        <div class="font-bold select-none px-2 mt-2 mb-1">{{ m.group }}</div>
        <div class="hover:bg-gray-100 hover:cursor-pointer" v-for="i in m.items" :key="i.name" @click="goto(i.comp)" v-show="i.show">
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
