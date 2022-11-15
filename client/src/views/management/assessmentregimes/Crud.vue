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
</script>

<template>
  <side-bar-crud :show="show" @cancel="$emit('close')" @commit="$emit('save', Object.assign({}, obj))">
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
              <n-select v-model="obj[p.prop_id]" class="!w-[40rem]">
                <n-option v-for="p in options.lookups[p.lookup]" :key="p.value" :value="p.value" :label="p.label" />
              </n-select>
            </div>
            <div v-else-if="p.type == 'eeaDatetime'">
              <div class="font-bold">{{ p.label }}:</div>
              <n-eea-datetime v-model="obj[p.prop]" class="!w-[40rem]" />
            </div>
            <div v-else-if="p.type == 'custom'" class="mt-4">
              <div class="font-bold">{{ p.label }}:</div>
              <div class="overflow-auto">
                <table class="n-table !bg-gray-50 !w-[40rem]">
                  <tr v-for="s in options.lookups[p.lookup]">
                    <td>
                      <div class="flex gap-2">
                        <n-checkbox class="self-center" />
                        <span>{{ s.label }}</span>
                      </div>
                    </td>
                    <td class="">
                      <n-select v-model="obj[p.prop_id]" class="">
                        <n-option label="oh" value="hey" />
                      </n-select>
                    </td>
                    <td class=""><input class="n-input" /></td>
                  </tr>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </side-bar-crud>
</template>

<style></style>
