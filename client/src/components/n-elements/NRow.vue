<script setup>

</script>
<template>
    <tr @click="$parent.$emit('slot-click', $event.target.parentElement, $event.shiftKey, $event.ctrlKey,false,$event.target.parentElement.getAttribute('selected'))" @contextmenu.prevent="$parent.$emit('slot-contextmenu', $event.target.parentElement, $event.shiftKey, $event.ctrlKey,true, $event.target.parentElement.getAttribute('selected'))">
        <slot />
    </tr>
</template>