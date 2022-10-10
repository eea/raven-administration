<script setup>
const props = defineProps({
  show: Boolean,
  sample: Object
});

const obj = ref({});

watch(
  () => props.sample,
  () => (obj.value = Object.assign({}, props.sample))
);
</script>

<template>
  <side-bar-crud :show="show" @cancel="$emit('close')" @commit="$emit('save', Object.assign({}, obj))">
    <div class="flex w-fit" style="width: 500px">
      <div class="flex w-1/2">
        <div class="h-full w-64">
          <div class="mb-4 font-bold text-base border-b">Required</div>
          <div class="mb-2">
            <div class="font-bold">Id:</div>
            <input type="text" class="n-input w-64" v-model="obj.id" placeholder="str: Id" />
          </div>

          <div class="mb-2">
            <div class="font-bold">Inlet Height:</div>
            <input type="number" class="n-input w-64" v-model="obj.inlet_height" placeholder="int: Inlet Height" />
          </div>
        </div>
      </div>
      <div class="flex w-1/2">
        <div class="h-full w-64">
          <div class="mb-4 font-bold text-base border-b">Optional</div>
          <div class="mb-2">
            <div class="font-bold">Building Distance:</div>
            <input type="number" class="n-input w-64" v-model="obj.building_distance" placeholder="int: Building Distance" />
          </div>
          <div class="mb-2">
            <div class="font-bold">Kerb Distance:</div>
            <input type="number" class="n-input w-64" v-model="obj.kerb_distance" placeholder="int: Kerb Distance" />
          </div>
        </div>
      </div>
    </div>
  </side-bar-crud>
</template>
<style></style>
