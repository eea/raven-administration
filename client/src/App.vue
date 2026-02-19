<script setup>
import { computed, ref } from "vue";
import { useRoute } from "vue-router";

import ProgressBar from "./components/ProgressBar.vue";
import NotifyBar from "./components/NotifyBar.vue";
import TopBar from "./components/TopBar.vue";
import MenuBar from "./components/MenuBar.vue";

const route = useRoute();

var showMenu = ref(true);
const isLogin = computed(() => {
  if (!route.name) return false;
  return route.name.toLowerCase() == "login";
});
</script>

<template>
  <ProgressBar />
  <NotifyBar />
  <div class="h-full flex flex-col overflow-hidden">
    <TopBar @on-click="showMenu = !showMenu" :hide-menu-button="isLogin" />
    <div class="flex overflow-hidden flex-1">
      <MenuBar :show="showMenu && !isLogin" />
      <div class="flex-1 overflow-auto">
        <router-view></router-view>
      </div>
    </div>
  </div>
</template>

<style></style>
