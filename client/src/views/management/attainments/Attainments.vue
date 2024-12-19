<script setup>
import GenerateAtt from "./GenerateAtt.vue";
import Service from "./service";
import pageOptions from "./pageOptions";
import Eventy from "../../../helpers/eventy";
import IconGenerate from "~icons/mingcute/lightning-fill";
import { ref } from "vue";
import { useRoute } from "vue-router";

const options = ref({});
const showGenerate = ref(false);
const manager_ref = ref(null);
const show_experimental = ref(false);

const route = useRoute();

onMounted(async () => {
  if (route.query.experimental) show_experimental.value = true;
  Eventy.showMessage("Loading metadata", "loading");
  const assessment_regimes = await Service.assessment_regimes();
  Eventy.hideMessage();
  options.value = pageOptions({ assessment_regimes });
});

const generateAttainment = async (o) => {
  showGenerate.value = false;
  Eventy.showMessage("Generating attainments", "loading");
  await Service.generate(o);
  await manager_ref.value.loadData();
  Eventy.showHideMessage(`Attainments generated`, "success", 5000);
  console.log(o);
};

const showGenerateAttainment = (e) => {
  showGenerate.value = true;
};

const close = () => {
  showGenerate.value = false;
};
</script>

<template>
  <generate-att :show="showGenerate" @click-outside="close" @on-generate="generateAttainment" />

  <manager name="Attainments" :options="options" :service="Service" ref="manager_ref">
    <template #custom-toolbar v-if="show_experimental">
      <circle-hover class="ml-1 self-center" @click="showGenerateAttainment($event)">
        <icon-generate class="text-nord12 text-sm self-center" />
      </circle-hover>
    </template>
  </manager>
</template>
