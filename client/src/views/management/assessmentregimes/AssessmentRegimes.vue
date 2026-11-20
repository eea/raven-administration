<script setup>
import { onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import Manager from "../../../components/n-manager/Manager.vue";
import GenerateRegimes from "./GenerateRegimes.vue";
import LinkedMethods from "./LinkedMethods.vue";
import CircleHover from "../../../components/CircleHover.vue";
import Service from "./service";
import pageOptions from "./pageOptions";
import IconGenerate from "~icons/material-symbols/wand-stars";
import IconLinks from "~icons/material-symbols/link";

// AQR3 calls this table AssessmentRegimeZone (ARZ), which is why the page is titled
// that way while the module keeps the shorter name. A second, unrelated table
// `assessmentregime_zones` used to hold this menu slot; it could not express ARZ and
// nothing exported it, so migration 020 dropped it. Its bulk fill lives on in
// GenerateRegimes.vue, writing real regimes.

// embedded: shown inside Management -> Assessment setup, which has the generator
// itself -- so no wand here, and edits are reported up so its summaries follow.
const props = defineProps({ embedded: { type: Boolean, default: false } });
const emit = defineEmits(["changed"]);

const options = ref({});
const showGenerate = ref(false);
// ?wizard=1&year= opens the generate step directly (the wizard's entry point).
const route = useRoute();
const wizardYear = ref(Number(route.query.year) || null);
// Remount Manager after a generate so its row set reloads.
const dataVersion = ref(0);

// The regime whose sampling points / models are being edited. Opened from the row's
// context menu, so it exists only for a regime that has been saved.
const linksRegime = ref(null);

const onContextMenuAction = ({ action, data }) => {
  if (action === "linked_methods") linksRegime.value = data?.row ?? null;
};

onMounted(async () => {
  const lookups = await Service.lookups();
  options.value = pageOptions(lookups);
  if (route.query.wizard && !props.embedded) showGenerate.value = true;
});
</script>

<template>
  <generate-regimes v-if="!embedded" :show="showGenerate" :lookups="options.lookups ?? {}" :initial-year="wizardYear"
                    @close="showGenerate = false" @generated="dataVersion++" />

  <linked-methods :show="!!linksRegime" :regime="linksRegime" @close="linksRegime = null; emit('changed')" />

  <Manager :key="dataVersion" name="Assessment regime zones" :options="options" :service="Service"
           :show-download-button="false" :embedded="embedded"
           @context-menu-action="onContextMenuAction" @changed="emit('changed')">
    <template v-if="!embedded" #toolbar>
      <CircleHover class="ml-1 self-center" title="Generate regimes for a year (also on Management → Assessment setup)"
                   @click="showGenerate = true">
        <icon-generate class="text-nord10 text-base self-center" />
      </CircleHover>
    </template>
    <template #extra-context-menu-items="{ handleAction }">
      <div class="pl-2 pr-4 py-1.5 flex cursor-pointer hover:bg-nord6"
           @click="handleAction('linked_methods')">
        <icon-links class="text-nord10 text-base self-center" />
        <div class="self-center ml-1">Linked sampling points / models</div>
      </div>
    </template>
  </Manager>
</template>
