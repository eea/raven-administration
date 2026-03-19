<script setup>
import { computed, ref, watch } from "vue";
import { format } from "date-fns";
import Popup from "../Popup.vue";
import DatetimePicker from "../DatetimePicker.vue";

const props = defineProps({
  show: Boolean,
  isEdit: Boolean,
  options: Object,
  selectedValue: {
    type: Object,
    default: null
  }
});

const emit = defineEmits(["close", "save"]);

const obj = ref({});

watch(
  () => props.show,
  () => {
    if (!props.selectedValue) {
      obj.value = props.options.properties.reduce((a, v) => ({ ...a, [v.prop]: v.default }), {});
    } else {
      obj.value = Object.assign({}, props.selectedValue);

      // Convert string datetime values to Date objects for DatetimePicker
      props.options.properties
        .filter((p) => p.type === "eeaDatetime")
        .forEach((p) => {
          if (obj.value[p.prop] && typeof obj.value[p.prop] === "string") {
            obj.value[p.prop] = new Date(obj.value[p.prop]);
          }
        });
    }
  }
);

const cmp_required_properties = computed(() => {
  if (!props.options.properties) return [];
  return props.options.properties.filter((p) => !!p.required && p.type != "gridOnly");
});

const cmp_optional_properties = computed(() => {
  if (!props.options.properties) return [];
  return props.options.properties.filter((p) => !p.required && p.type != "gridOnly");
});

const handleSave = () => {
  const saveData = Object.assign({}, obj.value);

  // Convert Date objects back to strings for API
  props.options.properties
    .filter((p) => p.type === "eeaDatetime")
    .forEach((p) => {
      if (saveData[p.prop] instanceof Date) {
        saveData[p.prop] = format(saveData[p.prop], "yyyy-MM-dd HH:00");
      }
    });

  emit("save", saveData);
};

const handleClose = () => {
  emit("close");
};

const title = computed(() => {
  const entityName = props.options?.entityName || "Item";
  return props.isEdit ? `Edit ${entityName}` : `Create ${entityName}`;
});

const isFormValid = computed(() => {
  return cmp_required_properties.value.every((p) => {
    const value = obj.value[p.prop] ?? obj.value[p.prop_id];

    // For checkboxes, undefined/false/true are all valid (undefined = unchecked)
    if (p.type === "checkbox") {
      return true;
    }

    // For numbers, 0 is valid (check string "0" too since input returns string)
    if (p.type === "number") {
      return value !== null && value !== undefined && value !== "";
    }

    // For other types, check if not empty
    return value !== null && value !== undefined && value !== "";
  });
});
</script>

<template>
  <popup :show="show" :title="title" @on-close="handleClose" class="max-w-6xl w-full">
    <!-- Content Section with Scrollbar -->
    <div class="overflow-y-auto pr-2 max-h-[60vh]">
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
                <DatetimePicker v-model="obj[p.prop]" />
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
                <DatetimePicker v-model="obj[p.prop]" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer Section (Always Visible) -->
    <div class="border-t border-gray-300 mt-4"></div>
    <div class="flex justify-end pt-2 gap-4">
      <button class="button" @click="handleSave" :disabled="!isFormValid">Save</button>
      <button class="button" @click="handleClose">Cancel</button>
    </div>
  </popup>
</template>

<style></style>
