<script setup>
import { useRoute } from "vue-router";

const route = useRoute();

var showMenu = ref(true);
const isLogin = computed(() => {
  if (!route.name) return false;
  return route.name.toLowerCase() == "login";
});
</script>

<template>
  <progress-bar />
  <notify-bar />
  <div class="h-full flex flex-col overflow-hidden">
    <top-bar @on-click="showMenu = !showMenu" :hide-menu-button="isLogin" />
    <div class="flex overflow-hidden flex-1">
      <menu-bar v-if="showMenu && !isLogin" />
      <div class="flex-1 overflow-auto">
        <router-view></router-view>
      </div>
    </div>
  </div>
</template>

<style>
html,
body {
  @apply h-full w-full text-[13px] md:text-[14px];
}

body {
  @apply h-full font-sans text-sm text-nord3 antialiased tracking-tighter m-0;
  background-color: #ededeb;
}

#app {
  @apply flex flex-col min-h-full items-stretch relative flex-1 w-full h-full;
}
</style>
