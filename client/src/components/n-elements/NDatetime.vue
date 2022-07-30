<script setup>
import { ref, onMounted, computed } from 'vue'
import NInput from './NInput.vue'
import NSelect from './NSelect.vue'
import NOption from './NOption.vue'
import Datepicker from 'vanillajs-datepicker/Datepicker';

const id = "id" + Math.random().toString(16).slice(2);

var p = defineProps({
    modelValue: {
        type: String,
        validator: (value) => {
            if (!value || value == "") return true;
            var re = /[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1]) (2[0-3]|[01][0-9]):[0-5][0-9]/;
            var matches = value.match(re);
            return !!matches;
        }
    }
});
const emit = defineEmits(["update:modelValue"]);

const date = computed({
    get() {
        if (!validate(p.modelValue)) {
            var n = new Date();
            var o = [
                n.getFullYear(),
                ('0' + (n.getMonth() + 1)).slice(-2),
                ('0' + n.getDate()).slice(-2)
            ].join('-');
            date.value = o;
            return o;
        }
        var t = p.modelValue.split(" ")[0]
        return t;
    },
    set(value) {
        emit("update:modelValue", `${value} ${time.value.value}`);
    }
});
const time = computed({
    get() {
        if (!validate(p.modelValue)) {
            var o = { value: "00:00", label: "00:00" }
            time.value = o;
            return o;
        }
        var t = p.modelValue.split(" ")[1]
        return { label: t, value: t };
    },
    set(value) {
        emit("update:modelValue", `${date.value} ${value.value}`);
    }
});

const validate = (dt) => {
    if (!dt || dt == "") return false;
    var re = /[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1]) (2[0-3]|[01][0-9]):[0-5][0-9]/;
    var matches = dt.match(re);
    return !!matches;
}

onMounted(async () => {
    const elem = document.querySelector('input[id=' + id + ']');
    const datepicker = new Datepicker(elem, {
        format: "yyyy-mm-dd",
        autohide: true
    });
    elem.addEventListener('changeDate', (e) => date.value = e.target.value);
});

</script>
<script  >
export default {
    inheritAttrs: false,
}
</script>

<template>
    <div class="n-elements n-datetime" v-bind="$attrs">
        <div style="flex:1">
            <n-input v-model="date" class="date" :id="id" />
        </div>
        <div style="width:fit-content">
            <n-select v-model="time" class="time">
                <n-option v-for="i in 24" :key="i" :value="((i - 1) < 10 ? '0' + (i - 1) : (i - 1)) + ':00'" :label="((i - 1) < 10 ? '0' + (i - 1) : (i - 1)) + ':00'" />
            </n-select>
        </div>
    </div>
</template>
