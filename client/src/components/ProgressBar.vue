<script setup>
import { computed, onMounted, ref } from "vue";
import Eventy from "../helpers/eventy";

const show = ref(false);
const fail = ref(false);

onMounted(async () => {
  Eventy.listen("showProgress", (s) => {
    show.value = true;
    fail.value = false;
  });
  Eventy.listen("hideProgress", (s) => {
    show.value = false;
    fail.value = false;
  });
  Eventy.listen("failProgress", (s) => {
    show.value = true;
    fail.value = true;
  });
});

const cls = computed(() => {
  var s = show.value ? "!top-0" : "!-top-10";
  s = s + (fail.value ? " bg-nord11" : " progress-shimmer");
  return s;
});
</script>

<template>
  <div class="transition-position duration-500 ease-in-out absolute left-0 right-0 h-[3px] z-[999]" :class="cls"></div>
</template>

<style scoped>
.progress-shimmer {
  background: linear-gradient(90deg, var(--color-nord10), var(--color-nord9), var(--color-nord7), var(--color-nord10));
  background-size: 300% 100%;
  animation: shimmer 1.4s linear infinite;
}
@keyframes shimmer {
  from { background-position: 100% 0; }
  to { background-position: -200% 0; }
}
</style>
