<script setup>
import { ref, onMounted, onUnmounted } from "vue";
import IconStar from "~icons/mdi/star-outline";
import CircleHover from "../CircleHover.vue";
import Service from "./service";

// Discrete favorites quick-select: a star icon that opens a small dropdown of
// the current user's favorites. Stateless — emits the full favorite object and
// lets the host view decide how to apply it (grid selection, filter, form fill).
const props = defineProps({
  title: { type: String, default: "Favorites" },
  direction: { type: String, default: "down" } // "down" | "up"
});

const emit = defineEmits(["select"]);

const open = ref(false);
const loading = ref(false);
const favorites = ref([]);
const root = ref(null);

const toggle = async () => {
  open.value = !open.value;
  if (!open.value) return;
  loading.value = true;
  try {
    favorites.value = await Service.list();
  } finally {
    loading.value = false;
  }
};

const onSelect = (favorite) => {
  open.value = false;
  emit("select", favorite);
};

const onDocumentClick = (e) => {
  if (root.value && !root.value.contains(e.target)) open.value = false;
};

onMounted(() => document.addEventListener("mousedown", onDocumentClick));
onUnmounted(() => document.removeEventListener("mousedown", onDocumentClick));
</script>

<template>
  <div ref="root" class="relative inline-block">
    <CircleHover :title="title" @click="toggle">
      <icon-star class="text-nord10 text-sm self-center" />
    </CircleHover>

    <div v-if="open" class="absolute left-0 z-120 bg-white border border-nord4 rounded shadow-xl min-w-64 max-h-72 overflow-y-auto py-1" :class="direction === 'up' ? 'bottom-7' : 'top-7'">
      <div v-if="loading" class="px-4 py-2 text-sm text-nord3 select-none">Loading…</div>
      <div v-else-if="!favorites.length" class="px-4 py-2 text-sm text-nord3 select-none">No favorites yet — save one from the Dashboard</div>
      <div v-else v-for="f in favorites" :key="f.id" class="px-4 py-2 text-sm hover:bg-nord6 cursor-pointer flex justify-between gap-4" @click="onSelect(f)">
        <span class="truncate">{{ f.name }}</span>
        <span class="text-nord3 shrink-0">{{ (f.config?.seriesIds || []).length }} series</span>
      </div>
    </div>
  </div>
</template>
