<script setup>
const props = defineProps({
  show: Boolean,
  isEdit: Boolean,
  options: Object,
  selectedValue: {
    type: Object,
    default: null
  }
});

const obj = ref({});

watch(
  () => props.show,
  () => {
    if (!props.selectedValue) {
      obj.value = props.options.properties.reduce((a, v) => ({ ...a, [v.prop]: v.default }), {});
    } else {
      obj.value = Object.assign({}, props.selectedValue);
    }
  }
);

const cmp_required_properties = computed(() => {
  if (!props.options.properties) return [];
  return props.options.properties.filter((p) => !!p.required);
});

const cmp_optional_properties = computed(() => {
  if (!props.options.properties) return [];
  return props.options.properties.filter((p) => !p.required);
});
</script>

<template>
  <side-bar-crud :show="show" @cancel="$emit('close')" @commit="$emit('save', Object.assign({}, obj))">
    <div class="flex gap-6" :class="options.showRequiredAndoptionalSideBySideInCrud ? 'flex-row' : 'flex-col'">
      <div>
        <div class="mb-4 font-bold text-base border-b">Required</div>

        <div class="mb-2" v-for="p in cmp_required_properties">
          <div v-if="!p.enableInEdit && p.type != 'gridOnly'">
            <div class="font-bold">{{ p.label }}:</div>
            <input class="n-input w-72" v-model="obj[p.prop]" :disabled="true" />
          </div>

          <div v-else>
            <div v-if="p.type == 'text' || p.type == 'number'">
              <div class="font-bold">{{ p.label }}:</div>
              <input :type="p.type" class="n-input w-72" v-model="obj[p.prop]" :placeholder="p.placeholder" />
            </div>
            <div v-else-if="p.type == 'checkbox'" class="mb-2 flex cursor-pointer hover:bg-gray-50 p-1">
              <div class="font-bold self-center flex-1" @click="obj[p.prop] = !obj[p.prop]">{{ p.label }}:</div>
              <n-checkbox v-model="obj[p.prop]" class="self-center" />
            </div>
            <div v-else-if="p.type == 'lookup'">
              <div class="font-bold">{{ p.label }}:</div>
              <n-select v-model="obj[p.prop_id]" class="!w-72">
                <n-option v-for="p in options.lookups[p.lookup]" :key="p.value" :value="p.value" :label="p.label" />
              </n-select>
            </div>
            <div v-else-if="p.type == 'eeaDatetime'">
              <div class="font-bold">{{ p.label }}:</div>
              <n-eea-datetime v-model="obj[p.prop]" class="!w-72" />
            </div>
          </div>
        </div>
      </div>

      <div>
        <div class="mb-4 font-bold text-base border-b" v-if="cmp_optional_properties.length > 0">Optional</div>

        <div class="mb-2" v-for="p in cmp_optional_properties">
          <div v-if="!p.enableInEdit && p.type != 'gridOnly'">
            <div class="font-bold">{{ p.label }}:</div>
            <input class="n-input w-72" v-model="obj[p.prop]" :disabled="true" />
          </div>

          <div v-else>
            <div v-if="p.type == 'text' || p.type == 'number'">
              <div class="font-bold">{{ p.label }}:</div>
              <input :type="p.type" class="n-input w-72" v-model="obj[p.prop]" :placeholder="p.placeholder" />
            </div>
            <div v-else-if="p.type == 'checkbox'" class="mb-2 flex cursor-pointer hover:bg-gray-50 p-1">
              <div class="font-bold self-center flex-1" @click="obj[p.prop] = !obj[p.prop]">{{ p.label }}:</div>
              <n-checkbox v-model="obj[p.prop]" class="self-center" />
            </div>
            <div v-else-if="p.type == 'lookup'">
              <div class="font-bold">{{ p.label }}:</div>
              <n-select v-model="obj[p.prop_id]" class="!w-72">
                <n-option v-for="p in options.lookups[p.lookup]" :key="p.value" :value="p.value" :label="p.label" />
              </n-select>
            </div>
            <div v-else-if="p.type == 'eeaDatetime'">
              <div class="font-bold">{{ p.label }}:</div>
              <n-eea-datetime v-model="obj[p.prop]" class="!w-72" />
            </div>
          </div>
        </div>
      </div>
    </div>
  </side-bar-crud>
</template>

<style></style>
