<script setup>
import { ref, watch, nextTick, onMounted, onUnmounted } from "vue";
import IconSearch from "~icons/ic/round-search";
import IconClose from "~icons/uil/times";

const props = defineProps({
  modelValue: {
    type: String,
    default: ""
  },
  resultCount: {
    type: Number,
    default: null
  }
});

const emit = defineEmits(["update:modelValue"]);

const open = ref(false);
const inputRef = ref(null);
const localQ = ref(props.modelValue);

watch(
  () => props.modelValue,
  (v) => (localQ.value = v)
);

const onInput = (e) => {
  localQ.value = e.target.value;
  emit("update:modelValue", e.target.value);
};

const show = async () => {
  open.value = true;
  await nextTick();
  inputRef.value?.select();
};

const hide = () => {
  open.value = false;
};

const clear = () => {
  localQ.value = "";
  emit("update:modelValue", "");
  inputRef.value?.focus();
};

const onKeydown = (e) => {
  if (e.ctrlKey && e.key === "k") {
    e.preventDefault();
    open.value ? hide() : show();
  }
  if ((e.key === "Escape" || e.key === "Enter") && open.value) {
    hide();
  }
};

onMounted(() => window.addEventListener("keydown", onKeydown));
onUnmounted(() => window.removeEventListener("keydown", onKeydown));
</script>

<template>
  <Teleport to="body">
    <Transition name="cmdk">
      <div v-if="open" class="fixed inset-0 z-200 flex justify-center px-4 bg-nord0/25 backdrop-blur-[2px]" style="padding-top: 16vh" @click.self="hide">
        <div class="bg-white ring-1 ring-nord0/5 rounded-2xl shadow-pop w-full max-w-lg h-fit overflow-hidden">
          <!-- Input row -->
          <div class="flex items-center gap-3 px-4 h-14 border-b border-nord5">
            <IconSearch class="text-nord10 text-xl shrink-0" />
            <input
              ref="inputRef"
              type="text"
              :value="localQ"
              @input="onInput"
              placeholder="Filter this page…"
              class="flex-1 outline-none focus-visible:outline-none bg-transparent text-[1.05rem] text-nord0 placeholder:text-[#9aa6ba]"
            />
            <button v-if="localQ" @click="clear" class="text-nord3 hover:text-nord0 transition-colors">
              <IconClose class="text-base" />
            </button>
            <kbd class="hidden sm:inline-flex shrink-0">Enter</kbd>
          </div>

          <!-- Footer -->
          <div class="px-4 h-10 items-center bg-nord6/60 text-xs text-muted flex justify-between">
            <span v-if="localQ && resultCount !== null">
              <span class="font-semibold text-nord0">{{ resultCount }}</span> result{{ resultCount !== 1 ? "s" : "" }}
            </span>
            <span v-else class="italic">Start typing to filter</span>
            <span class="font-mono">Enter / Esc to close</span>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.cmdk-enter-active,
.cmdk-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}
.cmdk-enter-from,
.cmdk-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
