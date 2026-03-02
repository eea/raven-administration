<script setup>
import { ref, watch, computed } from "vue";
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

const emit = defineEmits(["close", "save"]);

const obj = ref(null);

const title = computed(() => {
  return props.isEdit ? "Edit Group" : "Add Group";
});

watch(
  () => props.show,
  () => {
    if (!props.selectedValue) {
      obj.value = {
        name: "",
        management: false,
        data: false,
        exporting: false,
        processing: false,
        qualitycontrol: false,
        users: false,
        allnetworks: false,
        networks: []
      };
    } else {
      obj.value = { ...props.selectedValue };
    }
  }
);

const onSave = () => {
  const o = {
    ...obj.value,
    networks: [...(obj.value.networks || [])]
  };
  emit("save", o);
};

const onClose = () => {
  emit("close");
};
</script>

<template>
  <popup :title="title" :show="show" @on-close="onClose" class="w-150">
    <div class="flex flex-col gap-4 h-full" v-if="obj">
      <div class="flex flex-col gap-4 text-sm mt-4">
        <div class="mb-4 font-bold text-base border-b border-nord4">Required</div>

        <div>
          <label class="font-bold">Name</label>
          <br />
          <input class="input w-full" v-model="obj.name" placeholder="A unique group name" />
        </div>

        <div class="mt-2 flex cursor-pointer hover:bg-gray-50 p-1 select-none">
          <div class="font-bold self-center flex-1" @click="obj.management = !obj.management">Management:</div>
          <input type="checkbox" v-model="obj.management" class="self-center" />
        </div>

        <div class="flex cursor-pointer hover:bg-gray-50 p-1 select-none">
          <div class="font-bold self-center flex-1" @click="obj.data = !obj.data">Data:</div>
          <input type="checkbox" v-model="obj.data" class="self-center" />
        </div>

        <div class="flex cursor-pointer hover:bg-gray-50 p-1 select-none">
          <div class="font-bold self-center flex-1" @click="obj.exporting = !obj.exporting">EEA dataflow:</div>
          <input type="checkbox" v-model="obj.exporting" class="self-center" />
        </div>

        <div class="flex cursor-pointer hover:bg-gray-50 p-1 select-none">
          <div class="font-bold self-center flex-1" @click="obj.processing = !obj.processing">Processing:</div>
          <input type="checkbox" v-model="obj.processing" class="self-center" />
        </div>

        <div class="flex cursor-pointer hover:bg-gray-50 p-1 select-none">
          <div class="font-bold self-center flex-1" @click="obj.qualitycontrol = !obj.qualitycontrol">Quality control:</div>
          <input type="checkbox" v-model="obj.qualitycontrol" class="self-center" />
        </div>

        <div class="flex cursor-pointer hover:bg-gray-50 p-1 select-none">
          <div class="font-bold self-center flex-1" @click="obj.users = !obj.users">Users:</div>
          <input type="checkbox" v-model="obj.users" class="self-center" />
        </div>

        <div class="mt-3 mb-1 flex cursor-pointer hover:bg-gray-50 p-1 select-none">
          <div class="font-bold self-center flex-1" @click="obj.allnetworks = !obj.allnetworks">All networks:</div>
          <input type="checkbox" v-model="obj.allnetworks" class="self-center" />
        </div>

        <div>
          <label class="font-bold">Networks</label>
          <br />
          <select class="select w-full" v-model="obj.networks" multiple size="10" :disabled="obj.allnetworks">
            <option v-for="t in options?.lookups?.networks" :key="t.value" :value="t.value">{{ t.label }}</option>
          </select>
        </div>
      </div>

      <!-- BUTTONS -->
      <div class="flex justify-end gap-4">
        <button class="button" :disabled="!obj.name" @click="onSave">Save</button>
        <button class="button" @click="onClose">Cancel</button>
      </div>
    </div>
  </popup>
</template>
