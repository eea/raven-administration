<script setup>
import { ref, computed } from "vue"
import IconCaretDown from "~icons/ph/caret-down-bold";
import IconClose from "~icons/ic/sharp-close";
import { onClickOutside } from '@vueuse/core'

const p = defineProps({
    "modelValue": Array,
    "options": Array,
    "searchable": Boolean,
    "multiselect": Boolean
});

const emit = defineEmits(["update:modelValue"])

//emit('update:modelValue', removeDuplicates(p.modelValue.map(p => Object.assign({}, p))))

const ctxm = ref(null);
const showOptions = ref(false)
const q = ref("")

const onOptionClick = (o) => {
    const values = p.modelValue.map(m => m.value);
    if (p.multiselect) {
        if (!values.includes(o.value)) {
            p.modelValue.push(o)
            emit('update:modelValue', removeDuplicates(p.modelValue.map(p => Object.assign({}, p))))
        }
        else {
            const f = p.modelValue.filter(m => m.value != o.value);
            emit('update:modelValue', removeDuplicates(f.map(p => Object.assign({}, p))))
        }
    }
}

onClickOutside(ctxm, (event) => {
    showOptions.value = false;
});

const removeDuplicates = (arr) => {
    return arr.filter((value, index, self) =>
        index === self.findIndex((t) => (
            t.value === value.value
        ))
    )
}

const cls = (o) => {
    const values = p.modelValue.map(m => m.value);
    if (values.includes(o.value)) return "bg-nord14/20";
    return ""
}

const cmp_options = computed(() => {
    var t = p.options.filter((p) => {
        return !q.value || p.label.toLowerCase().includes(q.value.toLowerCase());
    });
    return t;
});

</script>

<template>
    <div class="w-full flex flex-col gap-1  h-full w-full select-none relative " ref="ctxm">
        <div class="w-full border rounded px-2 py-1 flex justify-between" @click="showOptions = !showOptions">
            <div class="flex flex-wrap gap-1 ">
                <div v-if="!modelValue.length" class=" px-1">&nbsp;</div>
                <div v-for="v in modelValue" :key="v.value" class="text-3xs bg-nord14/20 rounded p-1 flex justify-between">
                    <div>{{ v.label }}</div>
                    <icon-close @click="onOptionClick(v)" class="hover:text-nord14" />
                </div>
            </div>
            <div>
                <icon-caret-down class="" />
            </div>
        </div>
        <div class="">
            <div class="w-full h-auto max-h-64 rounded border flex flex-col z-10  shadow bg-white absolute" v-show="showOptions">
                <div v-if="searchable" class="p-2 border-b bg-gray-50"><input type="search" class="w-full inp" placeholder="Search" v-model="q" /></div>
                <div class="flex flex-col overflow-y-auto ">
                    <div class="px-2 py-1 hover:bg-gray-100" :class="cls(o)" v-for="o in cmp_options" :key="o.value" @click="onOptionClick(o)">{{ o.label }}</div>
                </div>
            </div>
        </div>
    </div>
</template>