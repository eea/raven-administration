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
  <div v-if="showTitle" class="px-2.5 pt-1 pb-1.5 text-[0.7rem] font-semibold uppercase tracking-[0.12em] text-muted">Actions</div>
  <div v-if="showEdit" class="cmenu-item" @click="emit('edit')">
    <IconEdit class="text-nord15 text-[1.05rem] self-center" />
    <div class="self-center">Edit</div>
  </div>
  <div v-if="showDuplicate" class="cmenu-item" @click="emit('duplicate')">
    <IconDuplicate class="text-nord10 text-[1.05rem] self-center" />
    <div class="self-center">Duplicate</div>
  </div>
  <div v-if="showDelete" class="cmenu-item" @click="emit('delete')">
    <IconDelete class="text-nord11 text-[1.05rem] self-center" />
    <div class="self-center">Delete</div>
  </div>
</template>
