<script setup>
// Warns before the login token expires (JWT_ACCESS_TOKEN_EXPIRES_SECONDS, default 1 h).
// "Stay signed in" swaps the token for a fresh one without leaving the page, so
// unsaved form input survives. Once expired, the page is left as it is (input can
// still be copied) and the next API call, or the button, goes to login and back.
import { computed, onMounted, onUnmounted, ref } from "vue";
import Auth from "../helpers/auth";
import IconClock from "~icons/tabler/clock-exclamation";

const WARN_MS = 2 * 60 * 1000;

const now = ref(Date.now());
const expiresAt = ref(Auth.expiresAt());
const busy = ref(false);
const failed = ref(false);
let timer = null;

const tick = () => {
  now.value = Date.now();
  // The token can change under us (refresh, sign-in in this tab), so re-read it.
  expiresAt.value = Auth.expiresAt();
};

const remaining = computed(() => (expiresAt.value ? expiresAt.value - now.value : null));
const expired = computed(() => remaining.value !== null && remaining.value <= 0);
const show = computed(() => remaining.value !== null && remaining.value <= WARN_MS);

const countdown = computed(() => {
  const s = Math.max(0, Math.ceil((remaining.value ?? 0) / 1000));
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
});

const staySignedIn = async () => {
  busy.value = true;
  failed.value = false;
  try {
    await Auth.refresh();
    tick();
  } catch {
    failed.value = true;
  } finally {
    busy.value = false;
  }
};

const signInAgain = () => {
  const url = Auth.loginUrl();
  Auth.signout();
  window.location.href = url;
};

onMounted(() => {
  tick();
  timer = setInterval(tick, 1000);
});
onUnmounted(() => clearInterval(timer));
</script>

<template>
  <div v-if="show" role="alert" class="fixed top-3 left-1/2 -translate-x-1/2 z-[9999] max-w-[calc(100vw-2rem)] rounded-xl shadow-pop ring-1 ring-nord0/8 bg-white flex flex-wrap items-center gap-3 pl-3 pr-2 py-2 overflow-hidden">
    <div class="absolute left-0 top-0 bottom-0 w-1" :class="expired ? 'bg-nord11' : 'bg-nord13'"></div>
    <div class="grid place-items-center size-8 rounded-full shrink-0 ml-1" :class="expired ? 'bg-nord11/12 text-nord11' : 'bg-nord13/15 text-[#b7791f]'">
      <icon-clock class="text-lg" />
    </div>
    <div class="text-[0.95rem] text-nord1 font-medium">
      <template v-if="expired">Your session has expired. Sign in again to continue.</template>
      <template v-else-if="failed">Could not extend the session. It expires in {{ countdown }}.</template>
      <template v-else>Your session expires in {{ countdown }}.</template>
    </div>
    <div class="flex gap-2 ml-auto">
      <button v-if="!expired" class="button button-primary" :disabled="busy" @click="staySignedIn">Stay signed in</button>
      <button class="button" @click="signInAgain">{{ expired ? "Sign in again" : "Sign out" }}</button>
    </div>
  </div>
</template>
