<script setup>
const props = defineProps({
  show: Boolean,
  ev: Object,
  properties: Array
});
</script>

<template>
  <contextmenu :evt="ev" :show="show" @click-outside="$emit('click-outside')" class="">
    <table class="n-table border-none bg-white">
      <tr v-for="p in properties" @click="p.showInGrid = !p.showInGrid" class="bg-white flex justify-between">
        <td class="!px-3 !p-1">{{ p.label }}</td>
        <td class="!px-3 !p-1 self-center flex"><n-checkbox v-model="p.showInGrid"></n-checkbox></td>
      </tr>
    </table>
  </contextmenu>
</template>

<style></style>
