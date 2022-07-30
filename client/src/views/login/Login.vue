<template>
  <div class="flex justify-center mt-10">
    <div class="m-auto border border-snow-a rounded-lg bg-gray-50 p-4">
      <div class="p-2 flex flex-col">
        <div class="mb-1">Username:</div>
        <NInput type="text" placeholder="Username" class="!w-64" v-model="username" @keyup.enter="login" />
      </div>
      <div class="p-2 flex flex-col">
        <div class="mb-1">Password:</div>
        <NInput type="password" placeholder="Password" class="!w-64" v-model="password" @keyup.enter="login" />
      </div>
      <div class="p-2">
        <NButton :disabled="!canLogin" class="!w-full" @click="login">Log in</NButton>
      </div>
      <div class="text-aurora-a text-center">{{ message }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import Auth from "../../helpers/auth";
import { useRouter } from "vue-router";

const username = ref("");
const password = ref("");
const message = ref("");
const router = useRouter();

const canLogin = computed(() => {
  return username.value.length > 0 && password.value.length > 0;
});

const login = async () => {
  if (!canLogin.value) return;
  try {
    message.value = "";
    await Auth.signin(username.value, password.value);
    reset();
    router.push({ name: "Home" });
  } catch (error) {
    message.value = error.message;
  }
};

const reset = () => {
  message.value = "";
  username.value = "";
  password.value = "";
};

</script>