<script setup>
import { computed, watchEffect } from "vue";
import { useRoute } from "vue-router";
import IconMenu from "~icons/tabler/menu-2";
import IconSlash from "~icons/tabler/chevron-right";
import IconCommand from "~icons/tabler/command";
import IconSearch from "~icons/tabler/search";
import { branding } from "../helpers/branding";
import { useNavigation } from "../composables/useNavigation";

const props = defineProps({
  "hide-menu-button": { type: Boolean, default: false },
  mobile: { type: Boolean, default: false }
});
const emit = defineEmits(["on-click", "open-palette"]);

const route = useRoute();
const { findByRoute } = useNavigation();
const crumb = computed(() => findByRoute(route.name));
const isMac = typeof navigator !== "undefined" && /Mac|iPhone|iPad/.test(navigator.platform);

watchEffect(() => {
  document.title = crumb.value ? `${crumb.value.item.name} · ${branding.tabTitle}` : branding.tabTitle;
});
</script>

<template>
  <header class="h-14 shrink-0 flex items-center gap-3 px-3 sm:px-5 bg-white/80 backdrop-blur-md border-b border-nord4/80 select-none z-[400]">
    <button v-if="mobile && !hideMenuButton" class="grid place-items-center size-9 -ml-1 rounded-lg text-nord2 hover:bg-nord6" aria-label="Open menu" @click="emit('on-click')">
      <IconMenu class="text-xl" />
    </button>

    <!-- Breadcrumb -->
    <div class="flex items-center gap-2 min-w-0 text-sm">
      <template v-if="crumb">
        <span class="hidden sm:inline-flex items-center gap-1.5 text-muted">
          <component :is="crumb.group.icon" class="text-base" />
          {{ crumb.group.group }}
        </span>
        <IconSlash class="hidden sm:block text-nord4 shrink-0" />
        <span class="flex items-center gap-2 font-semibold text-nord0 truncate">
          <span class="grid place-items-center size-7 rounded-lg bg-brand-soft text-nord10 shrink-0"><component :is="crumb.item.icon" class="text-[1.05rem]" /></span>
          <span class="truncate font-display text-[0.98rem]">{{ crumb.item.name }}</span>
        </span>
      </template>
      <template v-else-if="mobile || hideMenuButton">
        <span class="font-display font-bold text-nord0">{{ branding.appName }}</span>
        <span class="text-muted">{{ branding.subtitle }}</span>
      </template>
    </div>

    <div class="ml-auto flex items-center gap-2">
      <button v-if="!hideMenuButton" class="hidden md:flex items-center gap-2 h-9 pl-3 pr-1.5 w-64 rounded-lg border border-nord4 bg-nord6/60 text-sm text-muted hover:border-nord10/40 hover:bg-white transition" @click="emit('open-palette')">
        <IconSearch class="shrink-0" />
        <span class="flex-1 text-left">Go to page…</span>
        <kbd><IconCommand v-if="isMac" class="text-[0.7rem]" /><span v-else>Ctrl</span></kbd>
        <kbd>/</kbd>
      </button>
      <button v-if="!hideMenuButton" class="md:hidden grid place-items-center size-9 rounded-lg text-nord2 hover:bg-nord6" aria-label="Go to page" @click="emit('open-palette')">
        <IconSearch class="text-lg" />
      </button>
    </div>
  </header>
</template>
