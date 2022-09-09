<script setup>
import { onMounted } from "vue";

const props = defineProps({
  show: Boolean
});

const obj = ref({});

watch(
  () => props.show,
  () => {
    obj.value = {};
    obj.value.is_responsible_reporter = "false";
  }
);
</script>

<template>
  <side-bar-crud :show="show" @cancel="$emit('close')" @commit="$emit('save', Object.assign({}, obj))">
    <div class="mb-4 font-bold text-base border-b">Required</div>
    <div class="mb-2">
      <div class="font-bold">Id:</div>
      <input type="text" class="n-input w-64" v-model="obj.id" placeholder="str: A unique id" />
    </div>
    <div class="mb-2">
      <div class="font-bold">Name:</div>
      <input type="text" class="n-input w-64" v-model="obj.name" placeholder="str: Name of authority" />
    </div>
    <div class="mb-2">
      <div class="font-bold">Organisation:</div>
      <input type="text" class="n-input w-64" v-model="obj.organisation" placeholder="str: Name of organisation" />
    </div>
    <div class="mb-2">
      <div class="font-bold">Locator:</div>
      <input type="text" class="n-input w-64" v-model="obj.locator" placeholder="str: Location of authority" />
    </div>
    <div class="mb-2">
      <div class="font-bold">Postcode:</div>
      <input type="number" class="n-input w-64" v-model="obj.postcode" placeholder="int: Postal code of authority" />
    </div>
    <div class="mb-2">
      <div class="font-bold">Email:</div>
      <input type="text" class="n-input w-64" v-model="obj.email" placeholder="str: Email of authority" />
    </div>
    <div class="mb-2">
      <div class="font-bold">Address:</div>
      <input type="text" class="n-input w-64" v-model="obj.address" placeholder="str: Address of authority" />
    </div>
    <div class="mb-2">
      <div class="font-bold">Phone:</div>
      <input type="text" class="n-input w-64" v-model="obj.phone" placeholder="str: Phone of authority" />
    </div>
    <div class="mb-2">
      <div class="font-bold">Website:</div>
      <input type="text" class="n-input w-64" v-model="obj.website" placeholder="str: Website of authority" />
    </div>
    <div class="mb-2">
      <div class="font-bold">Is the main authority:</div>
      <n-select v-model="obj.is_responsible_reporter" class="!w-64">
        <n-option value="true" label="true" />
        <n-option value="false" label="false" />
      </n-select>
    </div>
  </side-bar-crud>
</template>

<style></style>
