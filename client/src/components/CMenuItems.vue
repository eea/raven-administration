<script setup>
import IconEdit from "~icons/ic/baseline-edit";
import IconDelete from "~icons/ic/baseline-delete";
import IconDuplicate from "~icons/mingcute/transfer-3-fill";

defineProps({
  showEdit: {
    type: Boolean,
    default: true
  },
  showDelete: {
    type: Boolean,
    default: true
  },
  showDuplicate: {
    type: Boolean,
    default: false
  },
  showTitle: {
    type: Boolean,
    default: true
  }
});

const emit = defineEmits(["edit", "delete", "duplicate"]);
</script>

<template>
  <div v-if="showTitle" class="px-2 font-bold text-base text-nord3">Menu:</div>
  <div v-if="showEdit" class="pl-2 pr-4 py-1.5 flex cursor-pointer hover:bg-nord6" @click="emit('edit')">
    <IconEdit class="text-nord15 text-base self-center" />
    <div class="self-center ml-1">Edit</div>
  </div>
  <div v-if="showDuplicate" class="pl-2 pr-4 py-1.5 flex cursor-pointer hover:bg-nord6" @click="emit('duplicate')">
    <IconDuplicate class="text-nord10 text-base self-center" />
    <div class="self-center ml-1">Duplicate</div>
  </div>
  <div v-if="showDelete" class="pl-2 pr-4 py-1.5 flex cursor-pointer hover:bg-nord6" @click="emit('delete')">
    <IconDelete class="text-nord11 text-base self-center" />
    <div class="self-center ml-1">Delete</div>
  </div>
</template>
