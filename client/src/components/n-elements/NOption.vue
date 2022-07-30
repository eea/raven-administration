<script setup>
import { useSlots } from 'vue'
const slots = useSlots();

var p = defineProps({
    value: {
        type: [String, Number],
        default: ''
    },
    label: {
        type: String,
        default: ''
    }
})

</script>
<template>
    <div class="n-elements n-option" n-id="n-option" @click="$parent.$emit('slot-click', { value, label })" :value="value" :label="label">
        {{ label }}
    </div>
</template>
 