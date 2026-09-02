<script setup>
import { ref, onMounted, onUnmounted, nextTick } from "vue";

const emit = defineEmits(["on-click", "click-outside"]);

const visible = ref(false);
const menu = ref(null);
const menuStyle = ref({ top: "0px", left: "0px" });
const menuData = ref(null);

// Gap kept between the menu and the viewport edge.
const MARGIN = 8;

// A menu shorter than this is not worth scrolling — fall back to the full viewport height.
const MIN_SCROLL_HEIGHT = 160;

const showMenu = async (data, event) => {
  event.preventDefault();
  event.stopPropagation(); // Prevent click from bubbling to document listener
  visible.value = true;
  menuData.value = data;

  const { clientX: x, clientY: y } = event;

  // Initially position the menu off-screen to get true dimensions without constraints.
  // The measurement has to happen before any max-height is applied, otherwise the
  // fits-below / flip-above decision below is made against an already-clamped height.
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

  // Adjust horizontal position if menu would overflow right edge
  if (x + menuWidth > viewportWidth) {
    posX = viewportWidth - menuWidth - 10;
  }

  // Ensure menu doesn't overflow left edge
  if (posX < 0) {
    posX = 10;
  }

  // Vertical placement: choose a side by how much room it has, rather than clamping the
  // menu to an edge. A menu taller than the viewport used to be pinned to top: 10px with
  // no way to reach the items below the fold — the nilu-qa plugin contributes 36 QA flags
  // to the Validate menu, roughly 1100px, so this is the normal case on a laptop.
  const below = viewportHeight - y - MARGIN;
  const above = y - MARGIN;

  let posY;
  let maxH = null;

  if (menuHeight <= below) {
    posY = y; // fits below the cursor
  } else if (menuHeight <= above) {
    posY = y - menuHeight; // flip above the cursor
  } else if (below >= above) {
    posY = y; // scroll, opening downwards
    maxH = below;
  } else {
    posY = MARGIN; // scroll, ending at the cursor
    maxH = above;
  }

  // Cursor near the vertical middle of a short window: neither side is usable, so take
  // the whole viewport instead of offering a 40px-tall scroller.
  if (maxH !== null && maxH < MIN_SCROLL_HEIGHT) {
    posY = MARGIN;
    maxH = viewportHeight - 2 * MARGIN;
  }

  menuStyle.value = {
    left: `${posX}px`,
    top: `${posY}px`,
    visibility: "visible",
    ...(maxH === null ? {} : { maxHeight: `${maxH}px` })
  };
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

const onKeydown = (event) => {
  if (event.key !== "Escape" || !visible.value) return;
  // Deliberately not hideMenu(): its "target is inside the menu" guard exists to keep a
  // click on a menu item from closing the menu before the item handler runs, but it would
  // also swallow Escape pressed in a menu's filter input — the one place it matters most.
  visible.value = false;
  emit("click-outside");
};

onMounted(() => {
  document.addEventListener("click", hideMenu);
  document.addEventListener("scroll", hideMenu, true);
  document.addEventListener("keydown", onKeydown);
});

onUnmounted(() => {
  document.removeEventListener("click", hideMenu);
  document.removeEventListener("scroll", hideMenu, true);
  document.removeEventListener("keydown", onKeydown);
});

defineExpose({ showMenu, hideMenu });
</script>

<template>
  <!-- overflow-y-auto pairs with the maxHeight showMenu() may set. The capture-phase
       scroll -> hideMenu listener is guarded by menu.contains(target), and contains() is
       true for the node itself, so scrolling the menu does not dismiss it. -->
  <div ref="menu" v-if="visible" class="border border-nord4 rounded shadow-lg bg-white fixed z-1000 flex flex-col py-2 text-base overflow-y-auto" :style="menuStyle">
    <slot :handleAction="handleAction" />
  </div>
</template>
