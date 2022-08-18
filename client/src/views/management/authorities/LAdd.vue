<script setup>
const p = defineProps({
  show: Boolean,
});

const obj = ref({});
const emit = defineEmits(["close", "save"]);

const close = () => {
  obj.value = {};
  emit("close");
};

const save = () => {
  emit("save", Object.assign({}, obj.value));
};
</script>

<template>
  <side-bar :show="show" @close="close">
    <div class="flex flex-col px-6 py-4 justify-between h-full">
      <div class="flex flex-col">
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
          <div class="font-bold">Poscode:</div>
          <input type="text" class="n-input w-64" v-model="obj.postcode" placeholder="int: Postal code of authority" />
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
      </div>
      <div class="flex justify-between">
        <button class="n-button outline outline-2 outline-nord14" @click="save">Add</button>
        <button class="n-button outline outline-2 outline-nord11" @click="close">Cancel</button>
      </div>
    </div>
  </side-bar>
</template>
<style></style>
