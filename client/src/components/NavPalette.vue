<script setup>
/**
 * Quick-jump to any page the user may open. Ctrl+/ (⌘/ on macOS) or the header button.
 * Ctrl+K stays with CmdK.vue, the per-page grid filter.
 */
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from "vue";
import { useRouter } from "vue-router";
import { useNavigation } from "../composables/useNavigation";
import IconSearch from "~icons/tabler/search";
import IconEnter from "~icons/tabler/corner-down-left";

const props = defineProps({ open: Boolean, enabled: { type: Boolean, default: true } });
const emit = defineEmits(["update:open"]);

const router = useRouter();
const { visibleGroups } = useNavigation();
const q = ref("");
const idx = ref(0);
const input = ref(null);
const list = ref(null);

const flat = computed(() => visibleGroups.value.flatMap((g) => g.items.map((i) => ({ ...i, group: g.group }))));
const results = computed(() => {
  const t = q.value.trim().toLowerCase();
  if (!t) return flat.value;
  const score = (i) => {
    const n = i.name.toLowerCase();
    if (n.startsWith(t)) return 0;
    if (n.split(/\s+/).some((w) => w.startsWith(t))) return 1;
    if (n.includes(t)) return 2;
    if (i.group.toLowerCase().includes(t)) return 3;
    return 9;
  };
  return flat.value
    .map((i) => ({ i, s: score(i) }))
    .filter((x) => x.s < 9)
    .sort((a, b) => a.s - b.s)
    .map((x) => x.i);
});

watch(q, () => (idx.value = 0));
watch(
  () => props.open,
  async (o) => {
    if (!o) return;
    q.value = "";
    idx.value = 0;
    await nextTick();
    input.value?.focus();
  }
);

const close = () => emit("update:open", false);
const go = (item) => {
  if (!item) return;
  close();
  router.push({ name: item.comp });
};
const move = async (d) => {
  const n = results.value.length;
  if (!n) return;
  idx.value = (idx.value + d + n) % n;
  await nextTick();
  list.value?.querySelector(`[data-i="${idx.value}"]`)?.scrollIntoView({ block: "nearest" });
};

const onGlobalKey = (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === "/" && props.enabled) {
    e.preventDefault();
    emit("update:open", !props.open);
  }
};
onMounted(() => window.addEventListener("keydown", onGlobalKey));
onUnmounted(() => window.removeEventListener("keydown", onGlobalKey));
</script>

<template>
  <Teleport to="body">
    <Transition name="pal">
      <div v-if="open" class="fixed inset-0 z-[700] flex justify-center px-4 bg-nord0/35 backdrop-blur-[3px]" style="padding-top: 14vh" @click.self="close">
        <div class="w-full max-w-xl h-fit rounded-2xl bg-white shadow-pop ring-1 ring-nord0/5 overflow-hidden">
          <div class="flex items-center gap-3 px-4 h-14 border-b border-nord5">
            <IconSearch class="text-xl text-nord10 shrink-0" />
            <input
              ref="input"
              v-model="q"
              placeholder="Go to page…"
              class="flex-1 bg-transparent outline-none focus-visible:outline-none text-[1.05rem] text-nord0 placeholder:text-[#9aa6ba]"
              @keydown.down.prevent="move(1)"
              @keydown.up.prevent="move(-1)"
              @keydown.enter.prevent="go(results[idx])"
              @keydown.esc.prevent="close"
            />
            <kbd>Esc</kbd>
          </div>
          <ul ref="list" class="max-h-[52vh] overflow-y-auto p-2">
            <li v-for="(r, n) in results" :key="r.group + r.comp" :data-i="n">
              <button
                class="w-full flex items-center gap-3 px-3 h-11 rounded-xl text-left transition-colors"
                :class="n === idx ? 'bg-brand-soft text-nord0' : 'text-nord2 hover:bg-nord6'"
                @mousemove="idx = n"
                @click="go(r)"
              >
                <span class="grid place-items-center size-8 rounded-lg shrink-0" :class="n === idx ? 'bg-nord10 text-white' : 'bg-nord6 text-nord3'">
                  <component :is="r.icon" class="text-[1.05rem]" />
                </span>
                <span class="flex-1 min-w-0 truncate font-medium">{{ r.name }}</span>
                <span class="text-xs text-muted">{{ r.group }}</span>
                <IconEnter v-if="n === idx" class="text-nord10" />
              </button>
            </li>
            <li v-if="!results.length" class="px-3 py-8 text-center text-muted">Nothing matches “{{ q }}”.</li>
          </ul>
          <div class="flex items-center gap-4 px-4 h-10 border-t border-nord5 bg-nord6/60 text-xs text-muted">
            <span class="flex items-center gap-1"><kbd>↑</kbd><kbd>↓</kbd> navigate</span>
            <span class="flex items-center gap-1"><kbd>Enter</kbd> open</span>
            <span class="ml-auto">Ctrl K filters the current page</span>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.pal-enter-active,
.pal-leave-active {
  transition: opacity 0.16s ease;
}
.pal-enter-active > div,
.pal-leave-active > div {
  transition: transform 0.16s ease;
}
.pal-enter-from,
.pal-leave-to {
  opacity: 0;
}
.pal-enter-from > div,
.pal-leave-to > div {
  transform: translateY(-8px) scale(0.98);
}
</style>
