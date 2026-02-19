<script setup>
import { computed } from "vue";
const props = defineProps({
  show: Boolean
});

const cls = computed(() => {
  return props.show ? "translate-x-0 duration-200" : "translate-x-full duration-800 ";
});
</script>

<template>
  <div class="transform transition ease-in-out absolute right-0 top-0 h-full w-full z-[999] flex" :class="cls">
    <div class="w-full h-full select-none bg-nord6/50"></div>
    <div class="bg-white border border-nord4 shadow-lg h-full">
      <slot />
    </div>
  </div>
</template>
