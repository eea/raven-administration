<script setup>
const props = defineProps({
  show: Boolean,
  authorities: Array,
  levels: Array,
  media: Array,
  timezones: Array,
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
          <input type="text" class="n-input !w-64" v-model="obj.id" placeholder="str: A unique id" />
        </div>

        <div class="mb-2">
          <div class="font-bold">Name:</div>
          <input type="text" class="n-input !w-64" v-model="obj.name" placeholder="str: Name of network" />
        </div>

        <div class="mb-2">
          <div class="font-bold">Media monitored:</div>
          <n-select v-model="obj.media_id" class="!w-64">
            <n-option v-for="a in media" :key="a.value" :value="a.value" :label="a.label" />
          </n-select>
        </div>

        <div class="mb-2">
          <div class="font-bold">Organisation level:</div>
          <n-select v-model="obj.organisationlevel_id" class="!w-64">
            <n-option v-for="a in levels" :key="a.value" :value="a.value" :label="a.label" />
          </n-select>
        </div>

        <div class="mb-2">
          <div class="font-bold">Authority:</div>
          <n-select v-model="obj.authority_id" class="!w-64">
            <n-option v-for="a in authorities" :key="a.value" :value="a.value" :label="a.label" />
          </n-select>
        </div>

        <div class="mb-2">
          <div class="font-bold">Timezone:</div>
          <n-select v-model="obj.timezone_id" class="!w-64">
            <n-option v-for="a in timezones" :key="a.value" :value="a.value" :label="a.label" />
          </n-select>
        </div>

        <div class="mb-2">
          <div class="font-bold">Begin position:</div>
          <input type="text" class="n-input !w-64" v-model="obj.begin_position" placeholder="str: YYYY-MM-DDTHH:mm:ssZ" />
        </div>

        <div class="mb-4 mt-8 font-bold text-base border-b">Optional</div>
        <div class="mb-2">
          <div class="font-bold">End position:</div>
          <input type="text" class="n-input !w-64" v-model="obj.end_position" placeholder="str: YYYY-MM-DDTHH:mm:ssZ" />
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
