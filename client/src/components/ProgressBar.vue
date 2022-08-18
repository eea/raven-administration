<template>
  <div class="transition-position duration-500 ease-in-out absolute top-0 left-0 right-0 h-1 z-[999]" :class="cls"></div>
</template>

<script setup>
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
  var s = show.value ? "top-0" : "-top-10";
  s = s + (fail.value ? " bg-nord11" : " bg-nord7 animate-pulse");
  return s;
});
</script>
