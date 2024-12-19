<template>
  <div class="rounded border border-nord4 bg-white absolute shadow select-none z-50" :style="cls" v-if="show" ref="ctxm">
    <div class="flex flex-col py-2">
      <slot></slot>
    </div>
  </div>
</template>

<script setup>
import { onClickOutside } from "@vueuse/core";

const p = defineProps({
  show: Boolean,
  evt: Object
});
const emit = defineEmits(["click-outside"]);

const ctxm = ref(null);
onClickOutside(ctxm, (event) => {
  // console.log("e", event);
  emit("click-outside");
});

const cls = computed(() => {
  if (ctxm.value) {
    var h = window.innerHeight - ctxm.value.offsetHeight - 30;
    var w = window.innerWidth - ctxm.value.offsetWidth - 50;
    var ow = p.evt.x - p.evt.layerX;
    var oh = p.evt.y - p.evt.layerY;

    var top = p.evt.y + 5;
    var left = p.evt.x + 5;
    if (top > h) top = h;
    if (left > w) left = w;

    console.log({
      b: top > h,
      top: top - oh + "px",
      left: left - ow + "px"
    });

    return {
      top: top - oh + "px",
      left: left - ow + "px"
    };
  }
});
</script>
