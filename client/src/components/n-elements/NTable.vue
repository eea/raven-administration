<script setup>
import { ref, watch, onMounted } from 'vue'
import EventListener from './EventListener.vue';

var p = defineProps({
    modelValue: {
        type: [Array, Object],
        default: [[], {}]
    },
    multiselect: {
        type: Boolean,
        default: false
    },
    "return-as-object": {
        type: Boolean,
        default: true
    }
})


const emit = defineEmits(["update:modelValue", "right-click"]);


const tbl = ref("");

watch(() => p.modelValue, (nv) => {
    setSelectedOnRows();
});

const onRowClick = (el, shiftKey, ctrlKey, rightClick, isSelected) => {
    var row = cellsToObject(el);
    
    if (!p.multiselect)  emit('update:modelValue', row);

    else if (p.multiselect) {
        var arr = p.modelValue.map(o => Object.assign(p.returnAsObject ? {} : [], o));
        
        if(rightClick && isSelected) emit('update:modelValue', arr);
        else if (!shiftKey && !ctrlKey) emit('update:modelValue', [row]);
        else {
            if(shiftKey) {
                var selectedRows = [];
                var rows = [...tbl.value.children].map(o=>cellsToObject(o));
                var last = rows.findIndex(o=>compare(p.modelValue[p.modelValue.length-1],o));                
                var current = rows.findIndex(o=>compare(row,o));

                var selectedRows = rows.slice(Math.min(last,current),Math.max(last,current)+1);
                var all = arr.concat(selectedRows);
                // Show only one if duplicate
                all = all.filter((value, index, self) => index == self.findIndex(o => compare(o,value)));
                emit('update:modelValue', all)
            } 
            else if(ctrlKey) {
                var arr2 = [];
                var found = false;
                arr.forEach(o => {
                    var isSame = compare(row, o);
                    if (!isSame) arr2.push(o)
                    if (!found && isSame) found = true;
                });

                if (!found) arr2.push(row)
                emit('update:modelValue', arr2)
            }
        }
    }
    if(rightClick)  emit('right-click', row)
}

const setSelectedOnRows = () => {
    var found = false;
    for (let i = 0; i < tbl.value.children.length; i++) {
        var o = cellsToObject(tbl.value.children[i]);

        var isSame = false;
        if (!p.multiselect) {
            if (!found) { // if not multiselect and true is found then remove att for rest
                isSame = compare(o, p.modelValue);
                found = isSame;
            }
            else tbl.value.children[i].removeAttribute("selected")
        }

        if (p.multiselect) {
            isSame = !!p.modelValue.find(p => compare(o, p));
        }
        if (isSame) tbl.value.children[i].setAttribute("selected", true);
        else tbl.value.children[i].removeAttribute("selected")
    }
}

const cellsToObject = (el) => {
    let values = [...el.cells].map(p => p.innerText);
    if (p.returnAsObject) {
        const keys = [...el.parentElement.rows[0].cells].map(p => p.innerText.toLowerCase().replace(/\s+/g, ''));
        values = Object.assign.apply({}, keys.map((v, i) => ({ [v]: values[i] })));
    }
    return values;
}

const compare = (object1, object2) => {
    if (!object1 || !object2) return false;
    const keys1 = Object.keys(object1);
    const keys2 = Object.keys(object2);
    if (keys1.length !== keys2.length) {
        return false;
    }
    for (let key of keys1) {
        if (object1[key] !== object2[key]) {
            return false;
        }
    }
    return true;
}

</script>
<template>
    <table class="n-elements n-table" ref="tbl">
        <event-listener @slot-click="onRowClick" @slot-contextmenu="onRowClick">
            <slot />
        </event-listener>
    </table>
</template>