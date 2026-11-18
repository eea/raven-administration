<script setup>
import { computed } from "vue";
const props = defineProps({
  show: Boolean
});

const cls = computed(() => {
  return props.show ? "translate-x-0 duration-300" : "translate-x-full duration-300 pointer-events-none";
});
</script>

<template>
  <div class="transform transition ease-[cubic-bezier(.2,.8,.2,1)] absolute right-0 top-0 h-full w-full z-[999] flex" :class="cls">
    <div class="flex-1 h-full select-none bg-nord0/25 backdrop-blur-[2px] transition-opacity duration-300" :class="show ? 'opacity-100' : 'opacity-0'"></div>
    <div class="bg-white border-l border-nord4 shadow-pop h-full max-w-full">
      <slot />
    </div>
  </div>
</template>
