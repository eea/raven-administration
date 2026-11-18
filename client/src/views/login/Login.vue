<script setup>
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";

import Auth from "../../helpers/auth";
import { branding } from "../../helpers/branding";
import IconLogo from "~icons/tabler/feather";
import IconUser from "~icons/tabler/user";
import IconLock from "~icons/tabler/lock";
import IconArrow from "~icons/tabler/arrow-right";
import IconShield from "~icons/tabler/shield-check";
import IconChart from "~icons/tabler/chart-area-line";
import IconCloud from "~icons/tabler/cloud-upload";

const router = useRouter();
const canCreateAdmin = ref(false);
const username = ref("");
const password = ref("");
const passwordConfirm = ref("");
const message = ref("");

onMounted(async () => {
  canCreateAdmin.value = await Auth.canCreateAdmin();
});

const canLogin = computed(() => {
  return username.value.length > 0 && password.value.length > 0;
});

const canCreate = computed(() => {
  return password.value.length > 0 && password.value === passwordConfirm.value;
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
  passwordConfirm.value = "";
};
</script>

<template>
  <div class="min-h-full grid lg:grid-cols-[1.1fr_1fr]">
    <!-- Brand panel -->
    <section class="hero relative hidden lg:flex flex-col justify-between p-12 text-white overflow-hidden">
      <div class="flex items-center gap-3">
        <div class="logo grid place-items-center size-11 rounded-2xl shadow-lg shadow-black/30"><IconLogo class="text-xl" /></div>
        <div class="leading-tight">
          <div class="font-display font-bold text-xl">{{ branding.appName }}</div>
          <div class="text-[0.72rem] uppercase tracking-[0.16em] text-white/50">{{ branding.subtitle }}</div>
        </div>
      </div>
      <div class="relative max-w-lg">
        <h1 class="font-display text-[2.6rem] leading-[1.1] font-extrabold tracking-tight">Air quality data,<br /><span class="hero-grad text-transparent bg-clip-text">managed end to end.</span></h1>
        <p class="mt-4 text-white/60 text-[1.05rem] max-w-md">Import, validate, verify and report observations from every station in your network.</p>
        <div class="mt-8 flex flex-wrap gap-2">
          <span class="pill"><IconChart /> Monitoring</span>
          <span class="pill"><IconShield /> Quality control</span>
          <span class="pill"><IconCloud /> AQR reporting</span>
        </div>
      </div>
      <div class="text-xs text-white/35">European Environment Agency · Raven</div>
    </section>

    <!-- Form -->
    <section class="flex items-center justify-center p-6 sm:p-10">
      <div class="w-full max-w-sm animate-fade-in">
        <div class="lg:hidden flex items-center gap-3 mb-8">
          <div class="logo grid place-items-center size-10 rounded-xl text-white"><IconLogo class="text-lg" /></div>
          <div class="font-display font-bold text-xl text-nord0">{{ branding.appName }}</div>
        </div>

        <template v-if="!canCreateAdmin">
          <h2 class="font-display text-[1.7rem] font-bold text-nord0">Welcome back</h2>
          <p class="mt-1 text-muted">Sign in to continue to {{ branding.subtitle.toLowerCase() }}.</p>
          <div class="mt-7 flex flex-col gap-4">
            <label class="field">
              <span>Username</span>
              <div class="relative">
                <IconUser class="field-icon" />
                <input type="text" placeholder="Username" class="input w-full pl-9! h-11" v-model="username" autocomplete="username" @keyup.enter="login" />
              </div>
            </label>
            <label class="field">
              <span>Password</span>
              <div class="relative">
                <IconLock class="field-icon" />
                <input type="password" placeholder="Password" class="input w-full pl-9! h-11" v-model="password" autocomplete="current-password" @keyup.enter="login" />
              </div>
            </label>
            <button :disabled="!canLogin" class="button button-primary w-full h-11 mt-2 text-[0.98rem]" @click="login">Sign in <IconArrow /></button>
            <div v-if="message" class="rounded-lg bg-nord11/8 border border-nord11/20 text-nord11 text-sm px-3 py-2 wrap-break-word">{{ message }}</div>
          </div>
        </template>

        <template v-else>
          <div class="inline-flex items-center gap-2 chip bg-nord14/10! border-nord14/30! text-[#047857]! mb-4"><IconShield /> First-time setup</div>
          <h2 class="font-display text-[1.7rem] font-bold text-nord0">Create the admin user</h2>
          <p class="mt-1 text-muted">Choose a password for the built-in <span class="font-mono text-nord1">admin</span> account.</p>
          <div class="mt-7 flex flex-col gap-4">
            <label class="field">
              <span>Username</span>
              <div class="relative">
                <IconUser class="field-icon" />
                <input type="text" class="input w-full pl-9! h-11" placeholder="admin" value="admin" :disabled="true" />
              </div>
            </label>
            <label class="field">
              <span>Password</span>
              <div class="relative">
                <IconLock class="field-icon" />
                <input type="password" placeholder="Password" class="input w-full pl-9! h-11" v-model="password" autocomplete="new-password" />
              </div>
            </label>
            <label class="field">
              <span>Confirm password</span>
              <div class="relative">
                <IconLock class="field-icon" />
                <input type="password" placeholder="Confirm password" class="input w-full pl-9! h-11" v-model="passwordConfirm" autocomplete="new-password" @keyup.enter="create" />
              </div>
            </label>
            <div class="text-nord11 text-sm" v-if="password.length > 0 && passwordConfirm.length > 0 && password !== passwordConfirm">Passwords do not match</div>
            <button :disabled="!canCreate" class="button button-primary w-full h-11 mt-2 text-[0.98rem]" @click="create">Create admin user <IconArrow /></button>
            <div v-if="message" class="rounded-lg bg-nord11/8 border border-nord11/20 text-nord11 text-sm px-3 py-2 wrap-break-word">{{ message }}</div>
          </div>
        </template>
      </div>
    </section>
  </div>
</template>

<style scoped>
@reference "../../assets/style.css";
.hero {
  background: var(--hero-bg);
}
.hero-grad {
  background-image: var(--hero-grad);
}
.hero::after {
  content: "";
  position: absolute;
  inset: 0;
  background-image: radial-gradient(rgb(255 255 255 / 0.07) 1px, transparent 1px);
  background-size: 22px 22px;
  mask-image: linear-gradient(180deg, transparent, black 40%, transparent);
  pointer-events: none;
}
.logo {
  background: var(--logo-bg);
}
.pill {
  @apply inline-flex items-center gap-1.5 rounded-full px-3 py-1.5 text-sm bg-white/[0.07] ring-1 ring-white/10 text-white/80;
}
.field {
  @apply flex flex-col gap-1.5;
}
.field > span {
  @apply text-sm font-medium text-nord1;
}
.field-icon {
  @apply absolute left-3 top-1/2 -translate-y-1/2 text-[#9aa6ba] pointer-events-none;
}
</style>
