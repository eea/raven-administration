<script setup>
import IconEdit from "~icons/ic/baseline-edit";
import IconDelete from "~icons/ic/baseline-delete";

var p = defineProps({
  ev: {
    type: Object,
    default: null,
  },
  show: {
    type: Boolean,
    default: false,
  },
});
</script>

<template>
  <contextmenu :evt="ev" @click-outside="$emit('clickOutside')" :show="show">
    <div class="px-2 font-bold">Menu:</div>
    <div class="pl-2 pr-4 py-2 flex cursor-pointer hover:bg-gray-100" @click="$emit('onEdit')">
      <icon-edit class="text-nord15 text-sm self-center" />
      <div class="self-center ml-1">Edit</div>
    </div>
    <div class="pl-2 pr-4 py-2 flex cursor-pointer hover:bg-gray-100" @click="$emit('onDelete')">
      <icon-delete class="text-nord11 text-sm self-center" />
      <div class="self-center ml-1">Delete</div>
    </div>
  </contextmenu>
</template>

<style></style>
