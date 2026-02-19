<script setup>
import { ref, onMounted, onUnmounted, nextTick } from "vue";

const emit = defineEmits(["on-click", "click-outside"]);

const visible = ref(false);
const menu = ref(null);
const menuStyle = ref({ top: "0px", left: "0px" });
const menuData = ref(null);

const showMenu = async (data, event) => {
  event.preventDefault();
  event.stopPropagation(); // Prevent click from bubbling to document listener
  visible.value = true;
  menuData.value = data;

  const { clientX: x, clientY: y } = event;

  // Initially position the menu off-screen to get true dimensions without constraints
  menuStyle.value = { left: "0px", top: "0px", visibility: "hidden" };

  // Wait for menu to render
  await nextTick();

  // Get actual menu dimensions
  const menuRect = menu.value?.getBoundingClientRect();
  if (!menuRect) return;

  const menuWidth = menuRect.width;
  const menuHeight = menuRect.height;
  const viewportWidth = window.innerWidth;
  const viewportHeight = window.innerHeight;

  let posX = x;
  let posY = y;

  // Adjust horizontal position if menu would overflow right edge
  if (x + menuWidth > viewportWidth) {
    posX = viewportWidth - menuWidth - 10;
  }

  // Adjust vertical position if menu would overflow bottom edge
  if (y + menuHeight > viewportHeight) {
    posY = viewportHeight - menuHeight - 10;
  }

  // Ensure menu doesn't overflow top edge
  if (posY < 0) {
    posY = 10;
  }

  // Ensure menu doesn't overflow left edge
  if (posX < 0) {
    posX = 10;
  }

  menuStyle.value = { left: `${posX}px`, top: `${posY}px`, visibility: "visible" };
};

const hideMenu = (event) => {
  if (!menu.value || (event && menu.value.contains(event.target))) {
    return;
  }
  visible.value = false;
  emit("click-outside");
};

const handleAction = (action) => {
  if (!menuData.value) return;
  emit("on-click", { action, data: menuData.value });
  visible.value = false;
};

onMounted(() => {
  document.addEventListener("click", hideMenu);
  document.addEventListener("scroll", hideMenu, true);
});

onUnmounted(() => {
  document.removeEventListener("click", hideMenu);
  document.removeEventListener("scroll", hideMenu, true);
});

defineExpose({ showMenu, hideMenu });
</script>

<template>
  <div ref="menu" v-if="visible" class="border border-nord4 rounded shadow-lg bg-white fixed z-1000 flex flex-col py-2 text-base" :style="menuStyle">
    <slot :handleAction="handleAction" />
  </div>
</template>
