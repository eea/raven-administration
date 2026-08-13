<script setup>
import { computed, ref } from "vue";
import Eventy from "../helpers/eventy";
import IconError from "~icons/ic/baseline-error-outline";
import IconSuccess from "~icons/clarity/success-standard-line";
import IconLoading from "~icons/uil/spinner-alt";
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
  if (notify.value.type == "error") return s + "border-nord11/75";
  if (notify.value.type == "warning") return s + "border-nord13";
  return s + "border-nord14";
});

const cls2 = computed(() => {
  if (notify.value.type == "error") return "bg-nord11/50";
  if (notify.value.type == "warning") return "bg-nord13/50";
  if (notify.value.type == "loading") return "bg-nord15/50";

  return "bg-nord14/50";
});
</script>
<template>
  <div class="transition-position ease-in-out absolute bottom-4 border rounded shadow z-[9999] bg-white flex text-xl" :class="cls">
    <div class="flex p-1" :class="cls2">
      <icon-error v-if="notify.type == 'error' || notify.type == 'warning'" class="text-lg self-center" />
      <icon-loading v-else-if="notify.type == 'loading'" class="text-lg self-center animate-spin" />
      <icon-success v-else class="text-lg self-center" />
    </div>
    <div class="px-4 py-2">{{ notify.msg }}</div>
    <div class="pr-1 pt-1">
      <icon-close class="text-sm self-center cursor-pointer hover:text-nord14" @click="close()" />
    </div>
  </div>
</template>
