<script setup>
// An info icon that reveals a short explanation on hover or keyboard focus, and
// optionally links out to the source it cites.
//
// The panel teleports to <body> rather than sitting beside the icon. Two reasons,
// both discovered rather than assumed:
//
//   * Crud.vue wraps its whole form in `overflow-y-auto pr-2 max-h-[60vh]`
//     (Crud.vue:98). An absolutely positioned child of that is clipped, so a panel
//     on one of the lower fields would be cut in half.
//   * The app has a global `v-tooltip` (vue-follow-tooltip, main.js:20-26) and this
//     deliberately does not use it: its beforeUnmount never removes the element it
//     appends to <html>, so a host unmounting mid-hover leaves a tooltip following
//     the cursor forever and swallowing clicks. DashboardPlot.vue:126-133 records
//     the same decision. A dialog closing while the pointer is on the icon is
//     exactly that case. Teleport is unmounted with the component, so it cannot
//     orphan.
import { computed, ref, watch } from "vue";
import { useElementBounding, useElementHover } from "@vueuse/core";
import IconInfo from "~icons/ph/info-duotone";

defineProps({
  // When set, the icon becomes the link. Used for the directive references.
  href: { type: String, default: null }
});

// Kept in px rather than as a rem utility so the clamp below and the rendered
// width cannot disagree: the root font-size here is 14px, not 16px, so `w-80`
// would be 280px and the arithmetic would have to know that.
const PANEL_WIDTH = 280;
const GAP = 6;
const MARGIN = 8;

const anchor = ref(null);
const focused = ref(false);
const hovered = useElementHover(anchor);
const { top, left, bottom, update } = useElementBounding(anchor);

const open = computed(() => hovered.value || focused.value);

// useElementBounding tracks window scroll and resize, but the form scrolls in its
// own container, so re-measure whenever the panel is about to appear.
watch(open, (isOpen) => {
  if (isOpen) update();
});

// Below the icon, or above it when the viewport has no room. The panel is fixed, so
// "room" is measured against the viewport rather than the scroll container.
//
// maxHeight is the part that has to be right rather than merely usual: the panel's
// height depends on how long the help text is, which this cannot know without
// rendering it first. Clamping to the space actually available -- and letting a
// panel taller than that scroll inside itself -- makes staying on screen independent
// of the guess below. A fixed threshold on its own does not: the first version used
// one and put Hotspot's three-line panel 8px off the bottom of a 420px viewport.
const COMFORTABLE = 200;

const panelStyle = computed(() => {
  const spaceBelow = window.innerHeight - bottom.value - GAP - MARGIN;
  const spaceAbove = top.value - GAP - MARGIN;
  const below = spaceBelow >= COMFORTABLE || spaceBelow >= spaceAbove;
  const x = Math.min(
    Math.max(left.value - MARGIN, MARGIN),
    window.innerWidth - PANEL_WIDTH - MARGIN
  );
  return {
    width: `${PANEL_WIDTH}px`,
    maxHeight: `${Math.max(80, below ? spaceBelow : spaceAbove)}px`,
    overflowY: "auto",
    left: `${x}px`,
    top: below ? `${bottom.value + GAP}px` : "auto",
    bottom: below ? "auto" : `${window.innerHeight - top.value + GAP}px`
  };
});
</script>

<template>
  <span class="inline-block align-middle leading-none">
    <component
      :is="href ? 'a' : 'span'"
      ref="anchor"
      :href="href"
      :target="href ? '_blank' : null"
      :rel="href ? 'noopener noreferrer' : null"
      tabindex="0"
      class="inline-flex align-middle text-nord10 hover:text-nord9"
      :class="href ? 'cursor-pointer' : 'cursor-help'"
      @click.stop
      @focus="focused = true"
      @blur="focused = false"
    >
      <IconInfo class="w-4 h-4" />
    </component>

    <Teleport to="body">
      <span
        v-if="open"
        class="fixed z-9999 p-2 text-[12px] font-normal leading-snug text-nord0 bg-gray-50 border border-nord4 rounded shadow-lg whitespace-pre-line"
        :style="panelStyle"
      >
        <slot />
      </span>
    </Teleport>
  </span>
</template>
