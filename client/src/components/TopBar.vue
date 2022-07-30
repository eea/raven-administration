<script setup>
const msg = ref("HEY HO")
</script>

<template>
  <div class="p-1 flex bg-polar-b text-snow-a justify-between select-none overflow-hidden">
    <div>
      <div class="rounded-full h-7 w-7 flex justify-center hover:bg-polar-d hover:border-2 hover:border-aurora-d hover:cursor-pointer" @click="showMenu = !showMenu" v-if="!isLogin">
        <div i-fa6-solid-bars class="text-base self-center" />
      </div>
    </div>
    <div class="self-center text-lg flex gap-1 mr-1">
      <LogoRaven class="h-8 fill-aurora-e self-center" />
      <div class="self-center">Raven3</div>
    </div>
  </div>

</template>

<style>
</style>