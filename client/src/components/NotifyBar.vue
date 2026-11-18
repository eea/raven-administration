<script setup>
import { computed, ref } from "vue";
import Eventy from "../helpers/eventy";
import IconError from "~icons/tabler/alert-circle";
import IconSuccess from "~icons/tabler/circle-check";
import IconLoading from "~icons/tabler/loader-2";
import IconClose from "~icons/tabler/x";

var notify = ref({});
var show = ref(false);
Eventy.listen("showMessage", (s) => {
  notify.value = s;
  show.value = true;
});

Eventy.listen("hideMessage", () => {
  close();
});

const close = () => {
  show.value = false;
  notify.value = { type: "none", msg: "" };
};

const cls = computed(() => {
  return show.value ? "left-4 sm:left-6 opacity-100 duration-500" : "-left-full opacity-0 duration-500";
});

const tone = computed(() => {
  if (notify.value.type == "error") return { icon: "bg-nord11/12 text-nord11", bar: "bg-nord11" };
  if (notify.value.type == "warning") return { icon: "bg-nord13/15 text-[#b7791f]", bar: "bg-nord13" };
  if (notify.value.type == "loading") return { icon: "bg-nord10/10 text-nord10", bar: "bg-nord10" };
  return { icon: "bg-nord14/12 text-nord14", bar: "bg-nord14" };
});
</script>
<template>
  <div class="transition-all ease-[cubic-bezier(.2,.8,.2,1)] fixed bottom-5 max-w-[calc(100vw-2rem)] rounded-xl shadow-pop ring-1 ring-nord0/8 z-[9999] bg-white flex items-center gap-3 pl-3 pr-2 py-2.5 overflow-hidden" :class="cls">
    <div class="absolute left-0 top-0 bottom-0 w-1" :class="tone.bar"></div>
    <div class="grid place-items-center size-8 rounded-full shrink-0 ml-1" :class="tone.icon">
      <icon-error v-if="notify.type == 'error' || notify.type == 'warning'" class="text-lg" />
      <icon-loading v-else-if="notify.type == 'loading'" class="text-lg animate-spin" />
      <icon-success v-else class="text-lg" />
    </div>
    <div class="pr-2 text-[0.95rem] text-nord1 font-medium">{{ notify.msg }}</div>
    <button class="grid place-items-center size-7 rounded-md text-nord3 hover:bg-nord6 hover:text-nord0 shrink-0" aria-label="Dismiss" @click="close()">
      <icon-close class="text-sm" />
    </button>
  </div>
</template>
