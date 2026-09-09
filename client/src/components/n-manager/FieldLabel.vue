<script setup>
// The label half of every control in Crud.vue.
//
// It used to be `<div class="font-bold">{{ p.label }}:</div>` copied twelve times
// -- once per property type, in each of the required and the optional block, which
// are duplicates of one another. Guidance attached to a field therefore had twelve
// places to be forgotten in, and the two blocks could drift apart silently.
//
// Attributes fall through to the root div, which is how the checkbox branch keeps
// its own `self-center flex-1` and its @click-to-toggle. HelpTip stops the click
// so the icon does not toggle the checkbox it is documenting.
import HelpTip from "../HelpTip.vue";

defineProps({
  label: { type: String, required: true },
  help: { type: String, default: null },
  // Only for a help string that cites something worth opening -- a directive, say.
  helpHref: { type: String, default: null }
});
</script>

<template>
  <div>
    {{ label }}:
    <HelpTip v-if="help" :href="helpHref">{{ help }}</HelpTip>
  </div>
</template>
