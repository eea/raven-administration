<script setup>
const props = defineProps({
  show: Boolean,
  groups: Array,
  user: Object
});

const emit = defineEmits(["save", "close"]);

const obj = ref({});

watch(
  () => props.user,
  () => (obj.value = Object.assign({}, props.user))
);

const onSave = () => {
  const o = Object.assign({}, obj.value);
  o.groups = Object.assign([], o.groups);
  emit("save", o);
};
</script>

<template>
  <side-bar-crud :show="show" @cancel="$emit('close')" @commit="onSave">
    <div class="mb-4 font-bold text-base border-b">Required</div>
    <div class="mb-2">
      <div class="font-bold">Name:</div>
      <input class="n-input w-64" v-model="obj.name" placeholder="str: The fullname of the user" />
    </div>
    <div class="mb-2">
      <div class="font-bold">Username:</div>
      <input class="n-input w-64" v-model="obj.username" placeholder="str: A unique username" />
    </div>
    <div class="mb-2">
      <div class="font-bold">Password:</div>
      <input type="password" class="n-input w-64" v-model="obj.password" placeholder="str: Set a new password" autocomplete="new-password" />
    </div>
    <div class="mb-2">
      <div class="font-bold">Groups:</div>
      <n-multiselect class="!w-full" v-model="obj.groups" :searchable="true">
        <n-option v-for="t in groups" :key="t.id" :value="t.id" :label="t.name" />
      </n-multiselect>
    </div>
  </side-bar-crud>
</template>
<style></style>
