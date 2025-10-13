<script setup>
import { onMounted, computed, watch } from "vue";

const props = defineProps({
  show: Boolean,
  ev: Object,
  properties: Array,
  name: String
});

const cmp_properties = computed(() => {
  // This computed will re-run when properties change or when showInGrid values change
  return props.properties.filter((p) => !p.hideInPicker);
});

onMounted(() => {
  // Load state immediately when component mounts
  loadColumnState();
});

// Watch for changes in properties array and reload state
watch(
  () => props.properties,
  () => {
    if (props.properties && props.properties.length > 0) {
      loadColumnState();
    }
  },
  { immediate: true }
);

const loadColumnState = () => {
  if (!props.name) return;

  const storageKey = `column-picker-${props.name.toLowerCase().replace(/\s+/g, "-")}`;
  const savedState = localStorage.getItem(storageKey);

  if (savedState) {
    try {
      const columnState = JSON.parse(savedState);
      props.properties.forEach((p) => {
        if (columnState.hasOwnProperty(p.label)) {
          p.showInGrid = columnState[p.label];
        }
      });
    } catch (e) {
      console.warn("Failed to parse column state from localStorage:", e);
    }
  }
};

const saveColumnState = () => {
  if (!props.name) return;

  const storageKey = `column-picker-${props.name.toLowerCase().replace(/\s+/g, "-")}`;
  const columnState = {};

  props.properties.forEach((p) => {
    columnState[p.label] = p.showInGrid;
  });

  localStorage.setItem(storageKey, JSON.stringify(columnState));
};

const onClick = (p) => {
  p.showInGrid = !p.showInGrid;
  console.log(props.name + " column " + p.label + " set to " + p.showInGrid);
  saveColumnState();
};
</script>

<template>
  <contextmenu :evt="ev" :show="show" @click-outside="$emit('click-outside')" class="">
    <table class="n-table border-none bg-white">
      <tr v-for="p in cmp_properties" @click="onClick(p)" class="bg-white flex justify-between">
        <td class="!px-3 !p-1">{{ p.label }}</td>
        <td class="!px-3 !p-1 self-center flex"><n-checkbox v-model="p.showInGrid"></n-checkbox></td>
      </tr>
    </table>
  </contextmenu>
</template>

<style></style>
