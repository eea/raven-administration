<script setup>
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
  <div class="absolute right-0 top-0 bottom-0 w-full z-[998]" v-if="show">
    <div class="absolute z-[999] px-6 py-4 bg-white border border-nord4 rounded shadow-xl left-1/2 top-1/4 flex flex-col min-w-40 max-w-72">
      <div class="font-bold mb-1 text-lg">{{ title }}</div>
      <div class="mb-4" v-html="text"></div>
      <div class="flex justify-end">
        <button class="n-button outline outline-2 outline-nord14 mr-4" @click="ok">Ok</button>
        <button class="n-button outline outline-2 outline-nord11" @click="close">Cancel</button>
      </div>
    </div>
  </div>
</template>
