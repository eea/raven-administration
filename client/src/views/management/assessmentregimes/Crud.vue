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
    onPollutantChange();
  }
);

const onSave = () => {
  const o = Object.assign({}, obj.value);

  var data = [];
  o.data.forEach((p) => {
    var d = Object.assign({}, p);
    if (p.selected) {
      d.assessment_regime_id = obj.value.id;
      data.push(d);
    }
  });
  o.data = data;
  emit("save", o);
};

const onPollutantChange = () => {
  if (!props.options.lookups) return;
  const data = props.options.lookups["sampling_points"].filter((p) => p.pollutant_id == obj.value.pollutant_id);
  data.forEach((d) => {
    d.assessment_regime_id = obj.value.id;
    var o = obj.value.data.find((o) => o.sampling_point_id == d.sampling_point_id);
    if (o) {
      d.selected = o.selected;
      d.assessment_type_id = o.assessment_type_id;
      d.description = o.description;
    } else {
      d.selected = false;
      d.assessment_type_id = null;
      d.description = null;
    }
  });

  obj.value.data = data;
};

const onDataClick = () => {};
</script>

<template>
  <side-bar-crud :show="show" @cancel="$emit('close')" @commit="onSave">
    <div class="flex gap-6 flex-col">
      <div>
        <div class="mb-4 font-bold text-base border-b">Required</div>

        <div class="mb-2" v-for="p in props.options.properties">
          <div v-if="!p.enableInEdit && p.type != 'gridOnly' && isEdit">
            <div class="font-bold">{{ p.label }}:</div>
            <input class="n-input w-[40rem]" v-model="obj[p.prop]" :disabled="true" />
          </div>

          <div v-else>
            <div v-if="p.type == 'text' || p.type == 'number'">
              <div class="font-bold">{{ p.label }}:</div>
              <input :type="p.type" class="n-input w-[40rem]" v-model="obj[p.prop]" :placeholder="p.placeholder" />
            </div>
            <div v-else-if="p.type == 'checkbox'" class="mb-2 flex cursor-pointer hover:bg-gray-50 p-1">
              <div class="font-bold self-center flex-1" @click="obj[p.prop] = !obj[p.prop]">{{ p.label }}:</div>
              <n-checkbox v-model="obj[p.prop]" class="self-center" />
            </div>
            <div v-else-if="p.type == 'lookup'">
              <div class="font-bold">{{ p.label }}:</div>
              <n-select v-model="obj[p.prop_id]" class="!w-[40rem]" @change="onPollutantChange">
                <n-option v-for="p in options.lookups[p.lookup]" :key="p.value" :value="p.value" :label="p.label" />
              </n-select>
            </div>
            <div v-else-if="p.type == 'eeaDatetime'">
              <div class="font-bold">{{ p.label }}:</div>
              <n-eea-datetime v-model="obj[p.prop]" class="!w-[40rem]" />
            </div>
            <div v-else-if="p.type == 'custom'" class="mt-4">
              <div class="font-bold">{{ p.label }}:</div>
              <table class="n-table !bg-gray-50 !w-[40rem]">
                <tr v-for="s in obj[p.prop]">
                  <td class="w-1/3" @click="s.selected = !s.selected">
                    <div class="flex gap-2">
                      <n-checkbox class="self-center" v-model="s.selected" />
                      <div class="flex flex-col">
                        <div>{{ s.station }}</div>
                        <div class="text-xs">{{ s.pollutant }} {{ s.timestep }} {{ s.concentration }} {{ s.sampling_point_id }}</div>
                      </div>
                    </div>
                  </td>
                  <td class="w-1/3">
                    <n-select class="" v-model="s.assessment_type_id">
                      <n-option :label="at.label" :value="at.value" v-for="at in options.lookups['assessment_types']" />
                    </n-select>
                  </td>
                  <td class="w-1/3"><input class="n-input" v-model="s.description" /></td>
                </tr>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </side-bar-crud>
</template>

<style></style>
