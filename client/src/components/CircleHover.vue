<script setup></script>
<template>
  <!-- Icon button. Name kept for the ~30 call sites and for plugins. -->
  <div
    role="button"
    tabindex="0"
    class="grid place-items-center size-8 rounded-lg text-nord3 border border-transparent cursor-pointer transition-[background-color,border-color,box-shadow,transform] duration-150 hover:bg-white hover:border-nord4 hover:shadow-card active:scale-95"
  >
    <slot />
  </div>
</template>
