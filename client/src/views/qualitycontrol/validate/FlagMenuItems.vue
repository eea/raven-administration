<script setup>
/**
 * The Validate page's flag menu body, shared by the grid right-click menu and the
 * chart-click menu — they used to be near-identical copies of the same 40 lines of markup.
 *
 * `items` are the QA flags a plugin contributed via validateContextMenu.getItems(). When
 * empty, the built-in EEA observation-validity choices are rendered instead.
 *
 * Emits the action *strings* Validate.vue's onContextMenuAction already decodes
 * ('plugin:<id>' or one of '-99' '-1' '1' '2' '3'), so both menus keep one handler.
 */
import { ref, computed, onMounted, nextTick } from "vue";

import IconCircle from "~icons/ph/circle-duotone";
import IconChat from "~icons/ph/chat-circle-duotone";

const props = defineProps({
  items: { type: Array, default: () => [] }
});

const emit = defineEmits(["select"]);

// http://dd.eionet.europa.eu/vocabulary/aq/observationvalidity
const EEA_CHOICES = [
  { action: "-99", label: "Not valid due to maintenance (-99)", valid: false },
  { action: "-1", label: "Not valid (-1)", valid: false },
  { action: "1", label: "Valid (1)", valid: true },
  { action: "2", label: "Valid, below detection limit (2)", valid: true },
  { action: "3", label: "Valid, 0.5*detection limit (3)", valid: true }
];

// Only worth a filter box once scanning the list by eye stops being practical. The nilu-qa
// plugin contributes 36 flags; the EEA fallback is 5 and stays as it was.
const FILTER_THRESHOLD = 10;

const filter = ref("");
const filterRef = ref(null);

const showFilter = computed(() => props.items.length > FILTER_THRESHOLD);

const filtered = computed(() => {
  const q = filter.value.trim().toLowerCase();
  if (!q) return props.items;
  return props.items.filter((i) => (i.name ?? "").toLowerCase().includes(q));
});

onMounted(async () => {
  if (!showFilter.value) return;
  await nextTick();
  // CMenu measures the menu while it is still visibility:hidden, and focus() is ignored
  // inside a hidden subtree — so keep trying for a few frames until it takes.
  for (let i = 0; i < 5; i++) {
    filterRef.value?.focus();
    if (document.activeElement === filterRef.value) return;
    await new Promise((resolve) => requestAnimationFrame(resolve));
  }
});

const onFilterEnter = () => {
  // Only when the filter has narrowed to a single flag — otherwise Enter would be a guess
  // that writes a QA flag to real observations.
  if (filtered.value.length === 1) emit("select", "plugin:" + filtered.value[0].id);
};
</script>

<template>
  <!-- Plugin QA flag menu (active when nilu-qa or similar plugin is enabled) -->
  <template v-if="items.length">
    <!-- Sticky so the header and filter survive scrolling a long list. The -mt-2 pt-2 pair
         covers CMenu's own py-2, which items would otherwise scroll through. -->
    <div class="sticky top-0 z-10 bg-white -mt-2 pt-2">
      <div class="px-2 font-bold text-base text-nord3">Set QA flag:</div>
      <div v-if="showFilter" class="px-2 pt-1 pb-1">
        <input
          ref="filterRef"
          v-model="filter"
          type="text"
          placeholder="Filter flags…"
          class="input w-full text-sm"
          @keydown.enter.prevent="onFilterEnter"
          @click.stop />
        <div class="text-xs text-nord3 pt-0.5">{{ filtered.length }} of {{ items.length }} shown</div>
      </div>
    </div>
    <div
      v-for="item in filtered" :key="item.id"
      class="pl-2 pr-4 py-1.5 flex cursor-pointer hover:bg-nord6 whitespace-nowrap"
      @click="emit('select', 'plugin:' + item.id)">
      <icon-circle :class="item.flagtype === 0 ? 'text-nord14' : 'text-nord11'" class="text-base self-center" />
      <icon-chat v-if="item.isautolog" class="text-nord9 text-xs self-center ml-1" title="Requires comment" />
      <div class="self-center ml-1">{{ item.name }}</div>
    </div>
    <div v-if="!filtered.length" class="px-2 py-1.5 text-sm text-nord3 whitespace-nowrap">No matching flag</div>
  </template>

  <!-- Default EEA validity choices (used when no plugin overrides) -->
  <template v-else>
    <div class="px-2 font-bold text-base text-nord3">Set validation to:</div>
    <div
      v-for="c in EEA_CHOICES" :key="c.action"
      class="pl-2 pr-4 py-1.5 flex cursor-pointer hover:bg-nord6 whitespace-nowrap"
      @click="emit('select', c.action)">
      <icon-circle :class="c.valid ? 'text-nord14' : 'text-nord11'" class="text-base self-center" />
      <div class="self-center ml-1">{{ c.label }}</div>
    </div>
  </template>
</template>
