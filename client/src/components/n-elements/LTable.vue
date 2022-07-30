<template>
    <table class="bg-gray-50 min-w-full divide-y divide-gray-200 border text-2xs tbl select-none" ref="headline">
        <tr>
            <th v-for="(c, i) in cols">{{ c }} </th>
        </tr>
        <tr :class="[isSelected(r), onRowClass(r)]" v-for="r in rows" :key="r.id" @click="onRowClick($event, r)" @contextmenu.prevent="onContextMenu($event, r)">
            <slot :row="r" />
        </tr>
    </table>
</template>

<script setup>
const p = defineProps({
    "modelValue": Array,
    "rows": Array,
    "cols": Array,
    "disable-multi-select": Boolean,
    "row-class": Function
});


const emit = defineEmits(["update:modelValue", "right-click", "row-click"])

const onContextMenu = (e, row) => {
    if (p.modelValue && p.modelValue.length < 2) onRowClick(e, row, false, true);
    emit("right-click", row, e)
}

const onRowClick = (e, row, emitClick = true, isRightClick = false) => {
    if (p.modelValue) {
        const ids = p.modelValue.map(m => m.id);
        row = Object.assign({}, row);
        if (e.shiftKey && p.modelValue.length > 0 && !p.disableMultiSelect) {
            var last_selection_idx = p.rows.findIndex(i => i.id == ids[ids.length - 1]);
            var curr_selection_idx = p.rows.findIndex(i => i.id == row.id);
            var f = [];
            if (last_selection_idx < curr_selection_idx) f = p.rows.filter(p => p.id > last_selection_idx && p.id <= curr_selection_idx).map(p => Object.assign({}, p))
            if (last_selection_idx > curr_selection_idx) f = p.rows.filter(p => p.id < last_selection_idx && p.id >= curr_selection_idx).map(p => Object.assign({}, p))
            emit('update:modelValue', removeDuplicates(f.concat(p.modelValue.map(p => Object.assign({}, p)))));
        }
        else {
            if (e.ctrlKey && !p.disableMultiSelect) {
                if (!ids.includes(row.id)) {
                    p.modelValue.push(row)
                    emit('update:modelValue', removeDuplicates(p.modelValue.map(p => Object.assign({}, p))))
                }
                else {
                    const f = p.modelValue.filter(m => m.id != row.id);
                    emit('update:modelValue', removeDuplicates(f.map(p => Object.assign({}, p))))
                }
            }
            else {
                if (isRightClick || !ids.includes(row.id)) emit('update:modelValue', [row]);
                else emit('update:modelValue', []);
            }
        }
    }
    if (emitClick) emit("row-click", row)
};

const isSelected = (row) => {
    if (p.modelValue) {
        var ids = p.modelValue.map(m => m.id);
        if (ids.includes(row.id)) return "selected";
    }
    return ""
}

const onRowClass = (row) => {
    if (!p.rowClass) return "";
    return p.rowClass(Object.assign({}, row));
}

const removeDuplicates = (arr) => {
    return arr.filter((value, index, self) =>
        index === self.findIndex((t) => (
            t.id === value.id
        ))
    )
}


</script>

<style>
.tbl td,
.tbl th {
    @apply p-2;
}

.tbl tr:hover {
    @apply bg-gray-100 cursor-pointer;
}

.tbl th:hover {
    @apply cursor-auto;
}

.tbl th {
    @apply bg-gray-100;
}

.tbl td:first-child {
    width: 1%;
    white-space: nowrap;
}


.tbl .selected {
    @apply bg-nord14/20;
}

.tbl .selected:hover {
    @apply bg-nord14/20;
}
</style>
