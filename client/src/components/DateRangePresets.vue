<script setup>
import { ref } from "vue";
import { sub, startOfWeek } from "date-fns";
import CMenu from "./CMenu.vue";
import IconCalendar from "~icons/ic/round-access-time";

// Calendar-relative range presets for a From/To DatetimePicker pair. Each resolver
// returns [from, to] as Date objects — DatetimePicker normalizes Dates to its own
// string model type, so hosts can assign them straight to their date refs.
const PRESETS = [
  {
    label: "This week",
    accent: "border-nord14",
    resolve: (d) => [startOfWeek(d, { weekStartsOn: 1 }), d]
  },
  {
    label: "Last week",
    accent: "border-nord14",
    resolve: (d) => [sub(startOfWeek(d, { weekStartsOn: 1 }), { days: 7 }), startOfWeek(d, { weekStartsOn: 1 })]
  },
  {
    label: "This month",
    accent: "border-nord11",
    resolve: (d) => [new Date(d.getFullYear(), d.getMonth(), 1), d]
  },
  {
    label: "Last month",
    accent: "border-nord11",
    // to = day 0 of this month, i.e. the last day of the previous month at 00:00
    resolve: (d) => [new Date(d.getFullYear(), d.getMonth() - 1, 1), new Date(d.getFullYear(), d.getMonth(), 0)]
  },
  {
    label: "This year",
    accent: "border-nord15",
    resolve: (d) => [new Date(d.getFullYear(), 0, 1), d]
  },
  {
    label: "Last year",
    accent: "border-nord15",
    resolve: (d) => [new Date(d.getFullYear() - 1, 0, 1), new Date(d.getFullYear(), 0, 1)]
  }
];

const emit = defineEmits(["select"]);

const menuRef = ref();

const onPresetClick = (e) => {
  // CMenu.handleAction bails on falsy menu data, so pass {} rather than null
  menuRef.value?.showMenu({}, e);
};

const onMenuClick = ({ action }) => {
  const preset = PRESETS.find((p) => p.label === action);
  if (!preset) return;
  const [from, to] = preset.resolve(new Date());
  emit("select", { from, to, label: preset.label });
};
</script>

<template>
  <div>
    <c-menu ref="menuRef" @on-click="onMenuClick">
      <template #default="{ handleAction }">
        <div class="px-2 font-bold">Presets:</div>
        <div v-for="p in PRESETS" :key="p.label" class="border-l-2 pl-2 pr-4 py-1.5 cursor-pointer hover:bg-nord6" :class="p.accent" @click="handleAction(p.label)">{{ p.label }}</div>
      </template>
    </c-menu>

    <button class="button flex gap-2" @click="onPresetClick">
      <icon-calendar class="self-center text-nord10 text-lg p-0!" />
      <div class="self-center">Presets</div>
    </button>
  </div>
</template>
