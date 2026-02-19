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
  return props.isEdit ? "Edit User" : "Add User";
});

watch(
  () => props.show,
  () => {
    if (!props.selectedValue) {
      obj.value = { name: "", username: "", password: "", groups: [] };
    } else {
      obj.value = { ...props.selectedValue, password: "" };
    }
  }
);

const onSave = () => {
  const o = {
    ...obj.value,
    groups: [...obj.value.groups]
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
        <div>
          <label class="font-bold">Name</label>
          <br />
          <input class="input w-full" v-model="obj.name" placeholder="The fullname of the user" />
        </div>

        <div>
          <label class="font-bold">Username</label>
          <br />
          <input class="input w-full" v-model="obj.username" placeholder="A unique username" />
        </div>

        <div>
          <label class="font-bold">Password</label>
          <br />
          <input type="password" class="input w-full" v-model="obj.password" :placeholder="obj.id ? 'Leave empty to keep current password' : 'A password'" autocomplete="new-password" />
        </div>

        <div>
          <label class="font-bold">Groups</label>
          <br />
          <select class="input w-full" v-model="obj.groups" multiple size="5">
            <option v-for="g in options?.lookups?.groups" :key="g.value" :value="g.value">{{ g.label }}</option>
          </select>
        </div>
      </div>

      <!-- BUTTONS -->
      <div class="flex justify-end gap-2 h-20">
        <div><button class="button" @click="onClose">Cancel</button></div>
        <div><button class="button" :disabled="!obj.name || !obj.username" @click="onSave">Save</button></div>
      </div>
    </div>
  </popup>
</template>
