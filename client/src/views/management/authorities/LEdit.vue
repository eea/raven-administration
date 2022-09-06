<script setup>
const p = defineProps({
  show: Boolean,
  authority: Object
});

const obj = ref({});
watch(
  () => p.authority,
  () => (obj.value = Object.assign({}, p.authority))
);
</script>

<template>
  <side-bar-crud :show="show" @cancel="$emit('close')" @commit="$emit('save', Object.assign({}, obj))">
    <div class="mb-4 font-bold text-base border-b">Required</div>
    <div class="mb-2">
      <div class="font-bold">Name:</div>
      <input type="text" class="n-input w-64" v-model="obj.name" />
    </div>
    <div class="mb-2">
      <div class="font-bold">Organisation:</div>
      <input type="text" class="n-input w-64" v-model="obj.organisation" />
    </div>
    <div class="mb-2">
      <div class="font-bold">Locator:</div>
      <input type="text" class="n-input w-64" v-model="obj.locator" />
    </div>
    <div class="mb-2">
      <div class="font-bold">Poscode:</div>
      <input type="text" class="n-input w-64" v-model="obj.postcode" />
    </div>
    <div class="mb-2">
      <div class="font-bold">Email:</div>
      <input type="text" class="n-input w-64" v-model="obj.email" />
    </div>
    <div class="mb-2">
      <div class="font-bold">Address:</div>
      <input type="text" class="n-input w-64" v-model="obj.address" />
    </div>
    <div class="mb-2">
      <div class="font-bold">Phone:</div>
      <input type="text" class="n-input w-64" v-model="obj.phone" />
    </div>
    <div class="mb-2">
      <div class="font-bold">Website:</div>
      <input type="text" class="n-input w-64" v-model="obj.website" />
    </div>
  </side-bar-crud>
</template>
<style></style>
