
<script setup>
import Auth from "../../helpers/auth";
import { useRouter } from "vue-router";

const router = useRouter();

const username = ref("");
const password = ref("");
const message = ref("");

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

<template>
  <div class="flex justify-center mt-10">
    <div class="m-auto border rounded-lg bg-gray-50 p-4">
      <div class="p-2 flex flex-col">
        <div class="mb-1">Username:</div>
        <input type="text" placeholder="Username" class="n-input w-64" v-model="username" @keyup.enter="login" />
      </div>
      <div class="p-2 flex flex-col">
        <div class="mb-1">Password:</div>
        <input type="password" placeholder="Password" class="n-input w-64" v-model="password" @keyup.enter="login" />
      </div>
      <div class="p-2">
        <button :disabled="!canLogin" class="n-button w-full" @click="login">Log in</button>
      </div>
      <div class="text-nord11 text-center">{{ message }}</div>
    </div>
  </div>
</template>
