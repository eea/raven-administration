<script setup>
const props = defineProps({
  show: Boolean,
  ev: Object
});

const file = ref(null);
</script>

<template>
  <contextmenu :evt="ev" :show="show" @click-outside="$emit('click-outside')" class="p-2">
    <div class="font-bold">Select a file to upload:</div>
    <div class="flex gap-2">
      <input type="file" ref="file" class="n-input" />
      <button class="n-button" @click="$emit('on-upload-click', file.files[0])">Upload</button>
    </div>
  </contextmenu>
</template>

<style></style>
