<script setup>
import { onMounted, ref } from "vue";
import Manager from "../../../components/n-manager/Manager.vue";
import Crud from "./Crud.vue";
import Service from "./service";
import pageOptions from "./pageOptions";

const options = ref({});

onMounted(async () => {
  const groups = await Service.groups();
  const groupsLookup = groups.map((g) => ({ value: g.id, label: g.name }));
  options.value = pageOptions({ groups: groupsLookup });
});
</script>

<template>
  <Manager name="Users" :options="options" :service="Service" :crud-component="Crud" />
</template>

<style></style>
