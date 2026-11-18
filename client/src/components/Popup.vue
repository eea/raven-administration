<script setup>
import { onMounted, onUnmounted } from "vue";
import IconClose from "~icons/uil/times";

const emit = defineEmits(["on-close"]);

const props = defineProps({
  show: Boolean,
  title: String,
  status: Object,
  // Classes for the body element. The default reproduces the original markup exactly,
  // so popups that do not pass this are unaffected.
  //
  // Pass "flex-1 min-h-0 flex flex-col" when the content needs to own its own
  // scrolling — a popup holding a wide table must, because a nested overflow-x-auto
  // div inside the default overflow-y-auto body is as tall as the table, which puts
  // its horizontal scrollbar below the visible area where nobody can reach it.
  bodyClass: { type: String, default: "overflow-y-auto flex-1" }
});

const onClose = () => {
  emit("on-close");
};

const handleKeydown = (event) => {
  if (event.key === "Escape") {
    emit("on-close"); // Emit the event when ESC is pressed
  }
};

onMounted(() => {
  window.addEventListener("keydown", handleKeydown);
});

onUnmounted(() => {
  window.removeEventListener("keydown", handleKeydown);
});
</script>

<script>
export default {
  inheritAttrs: false
};
</script>

<template>
  <!-- TODO: re-enable @click.self="onClose" when ready -->
  <div class="absolute top-0 bottom-0 left-0 right-0 bg-nord0/35 backdrop-blur-[2px] z-100" v-if="show">
    <div class="absolute top-1/2 left-1/2 p-5 rounded-2xl ring-1 ring-nord0/5 flex flex-col gap-3 bg-white shadow-pop z-110 -translate-x-1/2 -translate-y-1/2 min-w-[min(24rem,calc(100%-2rem))] max-w-[calc(100%-2.5rem)] text-base max-h-[90vh]" v-bind="$attrs">
      <div class="select-none font-display font-bold text-lg text-nord0 flex justify-between items-center gap-4">
        <div>{{ title }}</div>
        <div class="flex items-center gap-2">
          <!-- Header, deliberately, not the body: the body below is overflow-y-auto,
               so an absolutely-positioned dropdown opened from inside it would be
               clipped. Note also that this container carries -translate-x-1/2, and a
               transform establishes the containing block for position:fixed
               descendants — so CMenu would anchor to this box rather than the
               viewport and mis-clamp. Slotted content should use the FavoritesPicker
               pattern (relative wrapper + absolute panel) instead. -->
          <slot name="actions"></slot>
          <button class="grid place-items-center size-8 rounded-lg text-nord3 hover:bg-nord6 hover:text-nord0 transition" aria-label="Close" @click="onClose"><icon-close class="text-lg" /></button>
        </div>
      </div>
      <div class="border-t border-nord4/80 -mx-5"></div>
      <div :class="bodyClass"><slot></slot></div>
    </div>
  </div>
</template>
