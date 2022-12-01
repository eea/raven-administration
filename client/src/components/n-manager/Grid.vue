<script setup>
import { compare } from "../../helpers/utils";
import IconSort from "~icons/mdi/sort-alphabetical-ascending";

const props = defineProps({
  id: String,
  properties: Array,
  values: Array,
  selected: Object,
  ev: Object
});

const sort_header = ref();

const emit = defineEmits(["update:selected", "update:ev", "on-right-click"]);

const cls_rowClass = (row) => {
  if (compare(props.selected, row)) return "selected";
  return "";
};

const cls_cellClass = (cell, row) => {
  if (cell.cls_func) return cell.cls_func(Object.assign({}, row));
  return "";
};

const fn_cellVal = (cell, row) => {
  if (cell.val_func) return cell.val_func(Object.assign({}, row));
  return "";
};

const onRightClick = (row, e) => {
  emit("update:selected", row);
  emit("update:ev", e);
  emit("on-right-click");
};

const onClick = () => {
  emit("update:selected", {});
  emit("update:ev", {});
};

const cmp_sorted = computed(() => {
  if (!sort_header.value) return props.values;
  try {
    var s = Object.assign(
      [],
      props.values.map((o) => Object.assign({}, o))
    );
    return s.sort((x, y) => x[sort_header.value].localeCompare(y[sort_header.value]));
  } catch (error) {
    sort_header.value = undefined;
    return props.values;
  }
});
</script>

<template>
  <div>
    <table :id="id" class="n-table">
      <tr>
        <th v-for="header in properties" v-show="header.showInGrid">
          <span @click="sort_header = sort_header == header.prop ? undefined : header.prop" class="cursor-pointer">{{ header.label }}</span>
          <icon-sort class="inline ml-1 text-nord10" v-show="sort_header == header.prop" />
        </th>
      </tr>
      <tr v-for="row in cmp_sorted" :class="cls_rowClass(row)" @contextmenu.prevent="onRightClick(row, $event)" @click="onClick()">
        <td v-for="header in properties" v-show="header.showInGrid" :class="cls_cellClass(header, row)">
          <n-checkbox v-if="header.type == 'checkbox'" class="align-middle" v-model="row[header.prop]" :disabled="true" />
          <span v-else-if="header.type == 'gridOnly'">{{ fn_cellVal(header, row) }}</span>
          <span v-else>{{ row[header.prop] }}</span>
        </td>
      </tr>
    </table>
  </div>
</template>

<style></style>
