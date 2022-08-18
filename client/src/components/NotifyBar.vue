<script setup>
import Eventy from "../helpers/eventy";
import IconError from "~icons/ic/baseline-error-outline";
import IconSuccess from "~icons/clarity/success-standard-line";
import IconClose from "~icons/ic/sharp-close";

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
  var s = show.value ? " left-4 duration-500 " : "-left-full duration-500";
  s = s + (notify.value.type == "error" ? "border-nord11/75" : "border-nord14");
  return s;
});

const cls2 = computed(() => {
  var s = notify.value.type == "error" ? "bg-nord11/50" : "bg-nord14/50";
  return s;
});
</script>
<template>
  <div class="transition-position ease-in-out absolute bottom-4 border rounded shadow z-[9999] bg-white flex" :class="cls">
    <div class="flex p-1" :class="cls2">
      <icon-error v-if="notify.type == 'error'" class="text-base self-center" />
      <icon-success v-else class="text-base self-center" />
    </div>
    <div class="px-4 py-2">{{ notify.msg }}</div>
    <div class="pr-1 pt-1">
      <icon-close class="text-sm self-center cursor-pointer hover:text-nord14" @click="close()" />
    </div>
  </div>
</template>
