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
    <div class="flex flex-col justify-between h-full">
      <div class="flex flex-col h-full overflow-y-auto px-6 py-5">
        <slot />
      </div>
      <div class="flex justify-end gap-2 px-6 py-3 border-t border-nord4 bg-nord6/60">
        <button class="button" @click="$emit('cancel')">{{ cancelText }}</button>
        <button class="button button-primary" @click="$emit('commit')">{{ saveText }}</button>
      </div>
    </div>
  </SideBar>
</template>
