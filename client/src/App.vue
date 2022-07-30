<script setup>
import TopBar from './components/TopBar.vue';

</script>

<template>
  <div class="h-full flex flex-col overflow-hidden">
    <TopBar />
  </div>
</template>

<style>
html,
body {
  @apply h-full w-full;
}

body {
  @apply h-full font-sans text-sm text-polar-d bg-snow-d antialiased tracking-tighter m-0;
}

#app {
  @apply flex flex-col min-h-full items-stretch relative flex-1 w-full h-full;
}
</style>