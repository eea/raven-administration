<script setup>
import IconAlert from "~icons/tabler/alert-triangle";

const props = defineProps({
  show: Boolean,
  title: String,
  text: String
});

const emit = defineEmits(["ok", "close"]);

const close = () => {
  emit("close");
};

const ok = () => {
  emit("ok");
};
</script>

<template>
  <div class="absolute inset-0 z-998 bg-nord0/30 backdrop-blur-[2px] grid place-items-center p-4" v-if="show" @keydown.esc="close">
    <div class="z-999 w-full max-w-sm p-5 bg-white rounded-2xl shadow-pop ring-1 ring-nord0/5 flex flex-col gap-4 animate-fade-in">
      <div class="flex gap-3">
        <div class="grid place-items-center size-10 rounded-full bg-nord11/10 text-nord11 shrink-0"><IconAlert class="text-xl" /></div>
        <div class="min-w-0">
          <div class="font-display font-bold text-lg text-nord0">{{ title }}</div>
          <div class="mt-1 text-nord3" v-html="text"></div>
        </div>
      </div>
      <div class="flex justify-end gap-2">
        <button class="button" @click="close">Cancel</button>
        <button class="button button-primary" @click="ok">Ok</button>
      </div>
    </div>
  </div>
</template>
