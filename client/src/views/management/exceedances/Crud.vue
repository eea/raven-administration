<script setup>
import { computed, ref, watch } from "vue";
import Popup from "../../../components/Popup.vue";

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

const handleClose = () => {
  emit("close");
};

const title = computed(() => {
  const entityName = props.options?.entityName || "Exceedance";
  return props.isEdit ? `Edit ${entityName}` : `Create ${entityName}`;
});
</script>

<template>
  <popup :show="show" :title="title" @on-close="handleClose" class="max-w-6xl w-full max-h-[90vh]">
    <div class="flex flex-col gap-2 h-full">
      <div class="flex-1 overflow-y-auto pr-2">
        <div class="flex gap-6" :class="options.showRequiredAndoptionalSideBySideInCrud ? 'flex-row' : 'flex-col'">
          <div class="flex-1">
            <div class="mb-4 font-bold text-lg border-b border-nord4">Required</div>

            <div class="mb-2" v-for="p in cmp_required_properties">
              <div v-if="!p.enableInEdit && p.type != 'gridOnly' && isEdit">
                <div class="font-bold">{{ p.label }}:</div>
                <input class="input w-full" v-model="obj[p.prop]" :disabled="true" />
              </div>

              <div v-else>
                <div v-if="p.type == 'text' || p.type == 'number'">
                  <div class="font-bold">{{ p.label }}:</div>
                  <input :type="p.type" class="input w-full" v-model="obj[p.prop]" :placeholder="p.placeholder" />
                </div>
                <div v-else-if="p.type == 'checkbox'" class="mb-2 flex cursor-pointer hover:bg-gray-50 p-1">
                  <div class="font-bold self-center flex-1" @click="obj[p.prop] = !obj[p.prop]">{{ p.label }}:</div>
                  <input type="checkbox" v-model="obj[p.prop]" class="self-center" />
                </div>
                <div v-else-if="p.type == 'lookup'">
                  <div class="font-bold">{{ p.label }}:</div>
                  <select v-model="obj[p.prop_id]" class="select w-full">
                    <option v-for="p in options.lookups[p.lookup]" :key="p.value" :value="p.value">{{ p.label }}</option>
                  </select>
                </div>
                <div v-else-if="p.type == 'eeaDatetime'">
                  <div class="font-bold">{{ p.label }}:</div>
                  <input type="datetime-local" v-model="obj[p.prop]" class="input w-full" />
                </div>
              </div>
            </div>
          </div>

          <div class="flex-1">
            <div class="mb-4 font-bold text-lg border-b border-nord4" v-if="cmp_optional_properties.length > 0">Optional</div>

            <div class="mb-2" v-for="p in cmp_optional_properties">
              <div v-if="!p.enableInEdit && p.type != 'gridOnly' && isEdit">
                <div class="font-bold">{{ p.label }}:</div>
                <input class="input w-full" v-model="obj[p.prop]" :disabled="true" />
              </div>

              <div v-else>
                <div v-if="p.type == 'text' || p.type == 'number'">
                  <div class="font-bold">{{ p.label }}:</div>
                  <input :type="p.type" class="input w-full" v-model="obj[p.prop]" :placeholder="p.placeholder" />
                </div>
                <div v-else-if="p.type == 'checkbox'" class="mb-2 flex cursor-pointer hover:bg-gray-50 p-1">
                  <div class="font-bold self-center flex-1" @click="obj[p.prop] = !obj[p.prop]">{{ p.label }}:</div>
                  <input type="checkbox" v-model="obj[p.prop]" class="self-center" />
                </div>
                <div v-else-if="p.type == 'lookup'">
                  <div class="font-bold">{{ p.label }}:</div>
                  <select v-model="obj[p.prop_id]" class="select w-full">
                    <option v-for="p in options.lookups[p.lookup]" :key="p.value" :value="p.value">{{ p.label }}</option>
                  </select>
                </div>
                <div v-else-if="p.type == 'eeaDatetime'">
                  <div class="font-bold">{{ p.label }}:</div>
                  <input type="datetime-local" v-model="obj[p.prop]" class="input w-full" />
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="mt-4">
          <div class="font-bold">Sampling points:</div>
          <table class="n-table bg-gray-50!">
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
      </div>

      <div class="border-t border-gray-300"></div>
      <div class="flex justify-between pt-2">
        <button class="button" @click="onSave">Save</button>
        <button class="button" @click="handleClose">Cancel</button>
      </div>
    </div>
  </popup>
</template>

<style></style>
