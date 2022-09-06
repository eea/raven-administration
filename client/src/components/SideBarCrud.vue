<script setup>
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
  <side-bar :show="show">
    <div class="flex flex-col px-6 py-4 justify-between h-full">
      <div class="flex flex-col h-full">
        <slot />
      </div>
      <div class="flex justify-between">
        <button class="n-button outline outline-2 outline-nord14" @click="$emit('commit')">{{ saveText }}</button>
        <button class="n-button outline outline-2 outline-nord11" @click="$emit('cancel')">{{ cancelText }}</button>
      </div>
    </div>
  </side-bar>
</template>
