<script setup>
import { computed, ref, watch } from "vue";
import { useRoute } from "vue-router";
import { useMediaQuery } from "@vueuse/core";

import ProgressBar from "./components/ProgressBar.vue";
import NotifyBar from "./components/NotifyBar.vue";
import TopBar from "./components/TopBar.vue";
import MenuBar from "./components/MenuBar.vue";
import NavPalette from "./components/NavPalette.vue";

const route = useRoute();

const isLogin = computed(() => {
  if (!route.name) return false;
  return route.name.toLowerCase() == "login";
});

// Below lg the sidebar becomes an off-canvas drawer.
const desktop = useMediaQuery("(min-width: 1024px)");
const mobile = computed(() => !desktop.value);
const mobileOpen = ref(false);
watch(mobile, () => (mobileOpen.value = false));

const COLLAPSE_KEY = "raven_nav_collapsed";
// Collapsed (icon rail) by default; only an explicit "0" — the user expanded it — opens it.
const readCollapsed = () => {
  try {
    return localStorage.getItem(COLLAPSE_KEY) !== "0";
  } catch {
    return true;
  }
};
const collapsed = ref(readCollapsed());
const toggleCollapse = () => {
  collapsed.value = !collapsed.value;
  try {
    localStorage.setItem(COLLAPSE_KEY, collapsed.value ? "1" : "0");
  } catch {
    /* storage unavailable */
  }
  // ag-grid, charts and maps size themselves on window resize.
  setTimeout(() => window.dispatchEvent(new Event("resize")), 320);
};

const paletteOpen = ref(false);
</script>

<template>
  <ProgressBar />
  <NotifyBar />
  <div class="h-full flex overflow-hidden">
    <MenuBar :show="!isLogin" :collapsed="collapsed" :mobile="mobile" :mobile-open="mobileOpen" @close="mobileOpen = false" @toggle-collapse="toggleCollapse" />
    <div class="flex-1 min-w-0 flex flex-col overflow-hidden">
      <TopBar v-if="!isLogin" :mobile="mobile" @on-click="mobileOpen = true" @open-palette="paletteOpen = true" />
      <main class="flex-1 min-h-0 overflow-auto relative">
        <router-view></router-view>
      </main>
    </div>
  </div>
  <NavPalette v-model:open="paletteOpen" :enabled="!isLogin" />
</template>
