<script setup>
import { compare } from "../../helpers/utils";

const props = defineProps({
  id: String,
  properties: Array,
  values: Array,
  selected: Object,
  ev: Object
});

const emit = defineEmits(["update:selected", "update:ev", "on-right-click"]);

const cls_rowClass = (row) => {
  if (compare(props.selected, row)) return " selected";
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
</script>

<template>
  <div>
    <table :id="id" class="n-table">
      <th v-for="header in properties" v-show="header.showInGrid">{{ header.label }}</th>
      <tr v-for="row in values" :class="cls_rowClass(row)" @contextmenu.prevent="onRightClick(row, $event)" @click="onClick()">
        <td v-for="header in properties" v-show="header.showInGrid">
          <n-checkbox v-if="header.type == 'checkbox'" class="align-middle" v-model="row[header.prop]" :disabled="true" />
          <span v-else>{{ row[header.prop] }}</span>
        </td>
      </tr>
    </table>
  </div>
</template>

<style></style>
