<script setup>
import { ref } from "vue";
import IconEdit from "~icons/ic/baseline-edit";
import IconDelete from "~icons/ic/baseline-delete";
import CMenu from "./CMenu.vue";

defineProps({
  show: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(["on-menu-click", "click-outside"]);

const menuRef = ref(null);

const showMenu = (data, event) => {
  if (menuRef.value) {
    menuRef.value.showMenu(data, event);
  }
};

const onMenuClick = (payload) => {
  emit("on-menu-click", payload);
};

defineExpose({ showMenu });
</script>

<template>
  <c-menu ref="menuRef" @click-outside="$emit('click-outside')" @on-click="onMenuClick">
    <template #default="{ handleAction }">
      <div class="px-2 font-bold">Menu:</div>
      <div class="pl-2 pr-4 py-2 flex cursor-pointer hover:bg-gray-100" @click="handleAction('edit')">
        <icon-edit class="text-nord15 text-sm self-center" />
        <div class="self-center ml-1">Edit</div>
      </div>
      <div class="pl-2 pr-4 py-2 flex cursor-pointer hover:bg-gray-100" @click="handleAction('delete')">
        <icon-delete class="text-nord11 text-sm self-center" />
        <div class="self-center ml-1">Delete</div>
      </div>
      <slot name="extra-items" :handleAction="handleAction" />
    </template>
  </c-menu>
</template>
