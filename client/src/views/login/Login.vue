<script setup>
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";

import Auth from "../../helpers/auth";
import Container from "../../components/Container.vue";

const router = useRouter();
const canCreateAdmin = ref(false);
const username = ref("");
const password = ref("");
const message = ref("");

onMounted(async () => {
  canCreateAdmin.value = await Auth.canCreateAdmin();
});

const canLogin = computed(() => {
  return username.value.length > 0 && password.value.length > 0;
});

const canCreate = computed(() => {
  return password.value.length;
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

const create = async () => {
  if (!canCreate.value) return;
  try {
    message.value = "";
    await Auth.create(password.value);
    reset();
    canCreateAdmin.value = await Auth.canCreateAdmin();
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
  <div class="flex justify-center mt-10 w-full">
    <Container class="m-auto w-80! gap-0!" v-if="!canCreateAdmin">
      <div class="p-2 flex flex-col">
        <div class="mb-1">Username:</div>
        <input type="text" placeholder="Username" class="input w-full" v-model="username" @keyup.enter="login" />
      </div>
      <div class="p-2 flex flex-col">
        <div class="mb-1">Password:</div>
        <input type="password" placeholder="Password" class="input w-full" v-model="password" @keyup.enter="login" />
      </div>
      <div class="p-2">
        <button :disabled="!canLogin" class="button w-full" @click="login">Log in</button>
      </div>
      <div class="text-nord11 text-center flex-wrap wrap-break-word">{{ message }}</div>
    </Container>
    <Container class="m-auto w-80! gap-0!" v-if="canCreateAdmin">
      <div class="p-4 bg-nord14/50 text-nord0 font-bold text-center rounded-t">Create First Admin User</div>
      <div class="p-2 flex flex-col">
        <div class="mb-1">Username:</div>
        <input type="text" class="input w-full" placeholder="admin" value="admin" :disabled="true" />
      </div>
      <div class="p-2 flex flex-col">
        <div class="mb-1">Password:</div>
        <input type="password" placeholder="Password" class="input w-full" v-model="password" @keyup.enter="create" />
      </div>
      <div class="p-2">
        <button :disabled="!canCreate" class="button w-full" @click="create">Create admin user</button>
      </div>
      <div class="text-nord11 text-center flex-wrap wrap-break-word">{{ message }}</div>
    </Container>
  </div>
</template>
