<script setup>
/**
 * The compact funnel for the Observation Change History.
 *
 * One icon and one panel with two sections (Columns, Filters) rather than two
 * separate controls, to keep the popup header uncluttered.
 *
 * Structure is FavoritesPicker's: a `relative inline-block` root with an `absolute`
 * panel, dismissed by a document mousedown guarded on root.contains(). It is NOT
 * CMenu, even though CMenu is the codebase's general floating menu, because this
 * lives inside Popup.vue whose container carries -translate-x-1/2. A transform
 * establishes the containing block for position:fixed descendants, so CMenu would
 * anchor to the modal box instead of the viewport and its clamping would be wrong.
 * Anchoring in the popup header — outside the overflow-y-auto body — is what keeps
 * an absolute panel from being clipped.
 */
import { ref, computed, onMounted, onUnmounted } from "vue";
import IconFilter from "~icons/mdi/filter-variant";
import CircleHover from "../CircleHover.vue";

const props = defineProps({
  columns: { type: Array, default: () => [] },   // [{key, label}] core + plugin
  hiddenColumns: { type: Set, default: () => new Set() },
  rules: { type: Array, default: () => [] },
  isUnavailable: { type: Function, default: () => false },
  isSuspended: { type: Boolean, default: false },
});

const emit = defineEmits(["toggle-column", "toggle-rule", "resume-all"]);

const open = ref(false);
const root = ref(null);

const activeCount = computed(() => props.rules.filter((r) => r.enabled).length);
const hiddenCount = computed(() => props.hiddenColumns.size);
// The badge is what stops an instance-wide "hide ADACS" default from reading as a
// bug: rows are missing, and the icon says why.
const badge = computed(() => activeCount.value + hiddenCount.value);

const onDocumentClick = (e) => {
  if (root.value && !root.value.contains(e.target)) open.value = false;
};
onMounted(() => document.addEventListener("mousedown", onDocumentClick));
onUnmounted(() => document.removeEventListener("mousedown", onDocumentClick));

/** Plain-English summary of a rule, so the list is readable without opening Settings. */
const OP_TEXT = {
  eq: "is", ne: "is not", in: "is one of", not_in: "is not one of",
  contains: "contains", not_contains: "does not contain",
  empty: "is empty", not_empty: "is not empty", between: "is between",
};
const describe = (rule) => {
  const parts = (rule.conditions ?? []).map((c) => {
    const op = OP_TEXT[c.op] ?? c.op;
    if (c.op === "empty" || c.op === "not_empty") return `${c.field} ${op}`;
    if (c.op === "between") return `${c.field} ${op} ${c.from} and ${c.to}`;
    return `${c.field} ${op} ${Array.isArray(c.value) ? c.value.join(", ") : c.value}`;
  });
  return parts.join(rule.match === "any" ? " or " : " and ");
};
</script>

<template>
  <div ref="root" class="relative inline-block">
    <circle-hover title="Columns and filters" @click="open = !open">
      <icon-filter class="text-nord10 text-sm self-center" />
    </circle-hover>
    <span
      v-if="badge"
      class="absolute -top-1 -right-1 bg-nord10 text-white rounded-full text-[10px] leading-none px-1 py-0.5 pointer-events-none select-none"
    >
      {{ badge }}
    </span>

    <div
      v-if="open"
      class="absolute right-0 top-7 z-120 bg-white border border-nord4 rounded shadow-xl min-w-72 max-h-96 overflow-y-auto py-1 font-normal"
    >
      <div class="px-3 py-1 text-xs font-bold text-nord3 select-none">Columns</div>
      <label
        v-for="col in columns"
        :key="col.key"
        class="flex items-center gap-2 px-3 py-1 hover:bg-nord6 cursor-pointer text-sm whitespace-nowrap"
      >
        <input type="checkbox" :checked="!hiddenColumns.has(col.key)" @change="emit('toggle-column', col.key)" />
        {{ col.label }}
      </label>

      <div class="border-t border-nord4 my-1"></div>
      <div class="px-3 py-1 text-xs font-bold text-nord3 select-none">Filters</div>

      <div v-if="!rules.length" class="px-3 py-2 text-sm text-nord3 select-none">
        None configured — add them under Settings.
      </div>

      <template v-else>
        <div
          v-for="rule in rules"
          :key="rule.id"
          class="px-3 py-1 hover:bg-nord6 text-sm"
          :class="isUnavailable(rule) ? 'opacity-50' : 'cursor-pointer'"
        >
          <label class="flex items-start gap-2" :class="isUnavailable(rule) ? 'cursor-not-allowed' : 'cursor-pointer'">
            <input
              type="checkbox"
              class="mt-1"
              :checked="rule.enabled"
              :disabled="isUnavailable(rule)"
              @change="emit('toggle-rule', rule)"
            />
            <span class="min-w-0">
              <span class="block truncate">
                {{ rule.label || rule.id }}
                <span class="text-xs" :class="rule.action === 'keep' ? 'text-nord14' : 'text-nord11'">
                  ({{ rule.action === "keep" ? "show only" : "hide" }})
                </span>
              </span>
              <span class="block text-xs text-nord3 truncate">{{ describe(rule) }}</span>
              <span v-if="isUnavailable(rule)" class="block text-xs text-nord12">
                unavailable — plugin not installed
              </span>
            </span>
          </label>
        </div>
      </template>

      <template v-if="isSuspended">
        <div class="border-t border-nord4 my-1"></div>
        <div
          class="px-3 py-2 text-sm text-nord10 hover:bg-nord6 cursor-pointer select-none"
          @click="emit('resume-all'); open = false"
        >
          Re-apply filters
        </div>
      </template>
    </div>
  </div>
</template>
