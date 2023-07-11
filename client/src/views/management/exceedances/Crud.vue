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
const emit = defineEmits(["save", "close"]);
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

const onSave = () => {
  const o = Object.assign({}, obj.value);
  var data = [];
  emit("save", o);
};

const cmp_data = computed(() => {
  if (!props.options.lookups) return [];
  return props.options.lookups["sampling_points"].filter((p) => p.attainment_id == obj.value.attainment_id);
});

const cmp_required_properties = computed(() => {
  if (!props.options.properties) return [];
  return props.options.properties.filter((p) => !!p.required && p.type != "gridOnly");
});

const cmp_optional_properties = computed(() => {
  if (!props.options.properties) return [];
  return props.options.properties.filter((p) => !p.required && p.type != "gridOnly");
});
</script>

<template>
  <side-bar-crud :show="show" @cancel="$emit('close')" @commit="onSave">
    <div class="flex gap-6" :class="options.showRequiredAndoptionalSideBySideInCrud ? 'flex-row' : 'flex-col'">
      <div>
        <div class="mb-4 font-bold text-base border-b">Required</div>

        <div class="mb-2" v-for="p in cmp_required_properties">
          <div v-if="!p.enableInEdit && p.type != 'gridOnly' && isEdit">
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
          <div v-if="!p.enableInEdit && p.type != 'gridOnly' && isEdit">
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
    <div class="mt-4">
      <div class="font-bold">Sampling points:</div>
      <table class="n-table !bg-gray-50">
        <tr v-for="s in cmp_data" @click="s.selected = !s.selected">
          <td>
            <div class="flex gap-2">
              <div class="flex flex-col">
                <div>{{ s.station }}</div>
                <div class="text-xs">{{ s.pollutant }} {{ s.timestep }} {{ s.concentration }} {{ s.sampling_point_id }}</div>
              </div>
            </div>
          </td>
          <td>{{ s.assessment_regime }}</td>
        </tr>
      </table>
    </div>
  </side-bar-crud>
</template>

<style></style>
