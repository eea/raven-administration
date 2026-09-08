<script setup>
import { computed, ref, watch } from "vue";
import { klona } from "klona";
import DataTable from "../DataTable.vue";

const props = defineProps({
  properties: Array,
  values: Array,
  selected: Array,
  getRowStyle: {
    type: Function,
    default: null
  }
});

const emit = defineEmits(["update:selected", "on-dbl-click", "context-menu-action"]);

// Properties that the user can toggle on/off (showInGrid or defaultHidden)
const toggleableProps = computed(() =>
  props.properties.filter((p) => p.showInGrid || p.defaultHidden)
);

const colStorageKey = `raven-cols-${window.location.pathname}`;

function savedHiddenCols() {
  try {
    const saved = localStorage.getItem(colStorageKey);
    if (saved) return new Set(JSON.parse(saved));
  } catch {}
  return null;
}

// Default: hide props that declare defaultHidden: true
const defaultHiddenCols = (properties) =>
  new Set((properties ?? []).filter((p) => p.defaultHidden).map((p) => p.prop));

function loadHiddenCols() {
  return savedHiddenCols() ?? defaultHiddenCols(props.properties);
}

const hiddenCols = ref(loadHiddenCols());
const showColumnToggle = ref(false);

// Manager renders this component before the page's onMounted has fetched its lookups
// and assigned `options`, so `properties` is [] on the first pass and the seed above
// has nothing to read -- which is why every defaultHidden declaration used to be
// inert. Seed again the first time a real list arrives.
//
// Once only, and never over a stored choice: a plugin can contribute columns later
// via usePluginPageExtension, and re-seeding then would un-show a column the viewer
// had ticked. A defaultHidden column added after a viewer already has a preference
// stored does show for them, being absent from their hidden set -- that is how the
// picker has always treated a new column, and hiding it on their behalf would
// silently overrule a choice they made.
let seeded = (props.properties?.length ?? 0) > 0;
watch(
  () => props.properties,
  (properties) => {
    if (seeded || !properties?.length) return;
    seeded = true;
    if (!savedHiddenCols()) hiddenCols.value = defaultHiddenCols(properties);
  }
);

function toggleCol(prop) {
  const next = new Set(hiddenCols.value);
  if (next.has(prop)) next.delete(prop);
  else next.add(prop);
  hiddenCols.value = next;
  try { localStorage.setItem(colStorageKey, JSON.stringify([...next])); } catch {}
}

// Map properties to DataTable column format, respecting hidden state
const columns = computed(() => {
  return props.properties
    .filter((p) => (p.showInGrid || p.defaultHidden) && !hiddenCols.value.has(p.prop))
    .map((prop) => {
      const col = {
        field: prop.prop,
        headerName: prop.label,
        // Columns are flex: 1 by default, so a long header ellipsis-truncates.
        // DataTable already sets tooltipShowMode="whenTruncated", so this makes
        // the full label appear on hover only when it has actually been cut off.
        headerTooltip: prop.label,
        sortable: true
      };

      if (prop.width) col.width = prop.width;
      if (prop.flex) col.flex = prop.flex;

      if (prop.type === "checkbox") {
        col.cellRenderer = (params) => {
          const checked = params.value ? "checked" : "";
          return `<input type="checkbox" ${checked} disabled />`;
        };
      }

      // Any property may render through val_func, not just gridOnly: a lookup whose
      // stored value is not what the grid should show -- a tri-state boolean, an id
      // with no display column beside it -- needs the same hook.
      if (prop.val_func) {
        col.valueGetter = (params) => prop.val_func(klona(params.data));
      }

      if (prop.cls_func) {
        col.cellClass = (params) => prop.cls_func(klona(params.data));
      }
      return col;
    });
});

const onContextMenuAction = ({ action, data }) => {
  if (data?.row) emit("update:selected", [klona(data.row)]);
  emit("context-menu-action", { action, data });
};

const onDoubleClick = (data, event, gridEvent) => {
  emit("update:selected", [klona(data)]);
  emit("on-dbl-click");
};
</script>

<template>
  <div class="flex flex-col h-full">
    <!-- Column toggle: only shown when there are toggleable properties -->
    <div v-if="toggleableProps.length > 0" class="flex justify-end relative shrink-0 mb-1">
      <div v-if="showColumnToggle" class="fixed inset-0 z-10" @click="showColumnToggle = false" />
      <button
        class="text-xs px-2 py-0.5 rounded border border-nord4 bg-white hover:bg-nord6 z-20 relative select-none"
        @click="showColumnToggle = !showColumnToggle"
      >
        ⊞ Columns
      </button>
      <div
        v-if="showColumnToggle"
        class="absolute top-7 right-0 bg-white border border-nord4 rounded shadow-lg p-1 z-20 min-w-max"
      >
        <label
          v-for="p in toggleableProps"
          :key="p.prop"
          class="flex items-center gap-2 px-2 py-1 hover:bg-nord6 cursor-pointer text-sm whitespace-nowrap"
        >
          <input
            type="checkbox"
            :checked="!hiddenCols.has(p.prop)"
            @change="toggleCol(p.prop)"
          />
          {{ p.label }}
        </label>
      </div>
    </div>

    <div class="flex-1 min-h-0">
      <DataTable
        :data="values"
        :columns="columns"
        :filter="true"
        :floating-filter="false"
        :responsive="true"
        :get-row-style="getRowStyle"
        :show-copy-options="true"
        @context-menu-action="onContextMenuAction"
        @on-double-click="onDoubleClick"
      >
        <template #context-menu-items="slotProps">
          <slot name="context-menu-items" v-bind="slotProps" />
        </template>
      </DataTable>
    </div>
  </div>
</template>

<style scoped></style>
