<script setup>
var p = defineProps({
    modelValue: {
        type: [String, Number],
        default: ''
    }
})
</script>

<script  >
export default {
    inheritAttrs: false,
}
</script>

<template> 
    <input  class="n-elements n-input" :value="modelValue" @input="$emit('update:modelValue', $event.target.value)" v-bind="$attrs"> 
</template>

 
