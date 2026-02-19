<script setup>
import SideBar from "./SideBar.vue";

const props = defineProps({
  show: Boolean,
  saveText: {
    type: String,
    default: "Save"
  },
  cancelText: {
    type: String,
    default: "Cancel"
  }
});
</script>

<template>
  <SideBar :show="show">
    <div class="flex flex-col gap-4 px-6 py-4 justify-between h-full">
      <div class="flex flex-col h-full overflow-y-auto">
        <slot />
      </div>
      <div class="flex justify-between">
        <button class="button" @click="$emit('commit')">{{ saveText }}</button>
        <button class="button" @click="$emit('cancel')">{{ cancelText }}</button>
      </div>
    </div>
  </SideBar>
</template>
