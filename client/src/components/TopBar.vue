<script setup>
import { watchEffect } from "vue";
import IconMenu from "~icons/fa-solid/bars";
import { branding } from "../helpers/branding";

const props = defineProps({
  "hide-menu-button": {
    type: Boolean,
    default: false
  }
});
const emit = defineEmits(["on-click"]);

watchEffect(() => {
  document.title = branding.tabTitle;
});
</script>

<template>
  <div class="px-1 py-1 flex bg-nord1 text-nord4 justify-between select-none overflow-hidden">
    <div>
      <div class="rounded-full h-7 w-7 flex justify-center hover:bg-nord3 hover:border-2 hover:border-nord14 hover:cursor-pointer" @click="$emit('on-click')" v-if="!hideMenuButton">
        <icon-menu class="text-xs self-center" />
      </div>
    </div>
    <div class="self-center flex gap-1 mr-1 text-base">
      <div class="self-center">{{ branding.appName }}</div>
      <div class="self-center text-nord15">{{ branding.subtitle }}</div>
    </div>
  </div>
</template>

<style></style>
