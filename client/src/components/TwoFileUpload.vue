<script setup>
const props = defineProps({
  show: Boolean,
  ev: Object
});

const file1 = ref(null);
const file2 = ref(null);
</script>

<template>
  <contextmenu :evt="ev" :show="show" @click-outside="$emit('click-outside')" class="p-2">
    <div class="font-bold">Select two files to upload:</div>
    <div class="flex gap-2 flex-col">
      <input type="file" ref="file1" class="n-input" />
      <input type="file" ref="file2" class="n-input" />
      <button class="n-button" @click="$emit('on-upload-click', { file1: file1.files[0], file2: file2.files[0] })">Upload</button>
    </div>
  </contextmenu>
</template>

<style></style>
