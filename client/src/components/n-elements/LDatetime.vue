<script setup>
import { onMounted } from "vue";
import Datepicker from 'vanillajs-datepicker/Datepicker';

const id = "id" + Math.random().toString(16).slice(2);

const p = defineProps({
    date: String,
    time: String
});
const emit = defineEmits(["update:date", "update:time"]);

onMounted(async () => {
    const elem = document.querySelector('input[id=' + id + ']');
    const datepicker = new Datepicker(elem, {
        format: "yyyy-mm-dd",
        autohide: true
    });
    elem.addEventListener('changeDate', updatedate);
});

const updatedate = (e) => {
    emit("update:date", toDateString(e.detail.date));
}

const toDateString = (dt) => {
    return [
        dt.getFullYear(),
        ('0' + (dt.getMonth() + 1)).slice(-2),
        ('0' + dt.getDate()).slice(-2)
    ].join('-');
}

</script>
<template>
    <div class="flex  text-xs">
        <input type="text" :id="id" class="inp-l" v-model="date">
        <select class="inp-r" :value="time" @input="$emit('update:time', $event.target.value)">
            <option v-for="i in 24" :key="i" :value="((i - 1) < 10 ? '0' + (i - 1) : (i - 1)) + ':00'">{{ (i - 1) < 10 ? '0' + (i - 1) : (i - 1) }}:00</option>
        </select>
    </div>
</template>

<style >
.inp-l {
    @apply border px-2 py-1 rounded-l inline-block bg-white text-xs focus: outline-none w-36;
}

.inp-r {
    @apply border-r border-t border-b px-2 py-1 rounded-r inline-block bg-white text-xs focus: outline-none w-28;
}

.datepicker {
    display: none;
    @apply text-xs;
}

.datepicker.active {
    display: block;
}

.datepicker-dropdown {
    position: absolute;
    top: 0;
    left: 0;
    z-index: 20;
    padding-top: 4px;
}

.datepicker-dropdown.datepicker-orient-top {
    padding-top: 0;
    padding-bottom: 4px;
}

.datepicker-picker {
    display: inline-block;
    border-radius: 4px;
    background-color: white;
}

.datepicker-dropdown .datepicker-picker {
    box-shadow: 0 2px 3px rgba(10, 10, 10, 0.1), 0 0 0 1px rgba(10, 10, 10, 0.1);
}

.datepicker-picker span {
    display: block;
    flex: 1;
    border: 0;
    border-radius: 4px;
    cursor: default;
    text-align: center;
    -webkit-touch-callout: none;
    -webkit-user-select: none;
    -moz-user-select: none;
    -ms-user-select: none;
    user-select: none;
}

.datepicker-main {
    padding: 2px;
}

.datepicker-footer {
    box-shadow: inset 0 1px 1px rgba(10, 10, 10, 0.1);
    background-color: whitesmoke;
}

.datepicker-grid,
.datepicker-view .days-of-week,
.datepicker-view,
.datepicker-controls {
    display: flex;
}

.datepicker-grid {
    flex-wrap: wrap;
}

.datepicker-view .days .datepicker-cell,
.datepicker-view .dow {
    flex-basis: 14.2857142857%;
}

.datepicker-view.datepicker-grid .datepicker-cell {
    flex-basis: 25%;
}

.datepicker-cell,
.datepicker-view .week {
    height: 2.25rem;
    line-height: 2.25rem;
}

.datepicker-title {
    box-shadow: inset 0 -1px 1px rgba(10, 10, 10, 0.1);
    background-color: whitesmoke;
    padding: 0.375rem 0.75rem;
    text-align: center;
    font-weight: 700;
}

.datepicker-header .datepicker-controls {
    padding: 2px 2px 0;
}

.datepicker-controls .button {
    display: inline-flex;
    position: relative;
    align-items: center;
    justify-content: center;
    margin: 0;
    border: 1px solid #dbdbdb;
    border-radius: 4px;
    box-shadow: none;
    background-color: white;
    cursor: pointer;
    padding: calc(0.375em - 1px) 0.75em;
    height: 2.25em;
    vertical-align: top;
    text-align: center;
    line-height: 1.5;
    white-space: nowrap;
    color: #363636;
    @apply text-xs;
}

.datepicker-controls .button:focus,
.datepicker-controls .button:active {
    outline: none;
}

.datepicker-controls .button:hover {
    border-color: #b5b5b5;
    color: #363636;
}

.datepicker-controls .button:focus {
    border-color: #3273dc;
    color: #363636;
}

.datepicker-controls .button:focus:not(:active) {
    box-shadow: 0 0 0 0.125em rgba(50, 115, 220, 0.25);
}

.datepicker-controls .button:active {
    border-color: #4a4a4a;
    color: #363636;
}

.datepicker-controls .button[disabled] {
    cursor: not-allowed;
}

.datepicker-header .datepicker-controls .button {
    border-color: transparent;
    font-weight: bold;
}

.datepicker-header .datepicker-controls .button:hover {
    background-color: #f9f9f9;
}

.datepicker-header .datepicker-controls .button:focus:not(:active) {
    box-shadow: 0 0 0 0.125em rgba(255, 255, 255, 0.25);
}

.datepicker-header .datepicker-controls .button:active {
    background-color: #f2f2f2;
}

.datepicker-header .datepicker-controls .button[disabled] {
    box-shadow: none;
}

.datepicker-footer .datepicker-controls .button {
    margin: calc(0.375rem - 1px) 0.375rem;
    border-radius: 2px;
    width: 100%;
    @apply text-xs;
}

.datepicker-controls .view-switch {
    flex: auto;
}

.datepicker-controls .prev-btn,
.datepicker-controls .next-btn {
    padding-right: 0.375rem;
    padding-left: 0.375rem;
    width: 2.25rem;
}

.datepicker-controls .prev-btn.disabled,
.datepicker-controls .next-btn.disabled {
    visibility: hidden;
}

.datepicker-view .dow {
    height: 1.5rem;
    line-height: 1.5rem;
    @apply text-xs;
    font-weight: 700;
}

.datepicker-view .week {
    width: 2.25rem;
    color: #b5b5b5;
    @apply text-xs;
}

@media (max-width: 22.5rem) {
    .datepicker-view .week {
        width: 1.96875rem;
    }
}

.datepicker-grid {
    width: 15.75rem;
}

@media (max-width: 22.5rem) {
    .calendar-weeks+.days .datepicker-grid {
        width: 13.78125rem;
    }
}

.datepicker-cell:not(.disabled):hover {
    background-color: #f9f9f9;
    cursor: pointer;
}

.datepicker-cell.focused:not(.selected) {
    background-color: #e8e8e8;
}

.datepicker-cell.selected,
.datepicker-cell.selected:hover {
    background-color: #3273dc;
    color: #fff;
    font-weight: 600;
}

.datepicker-cell.disabled {
    color: #dbdbdb;
}

.datepicker-cell.prev:not(.disabled),
.datepicker-cell.next:not(.disabled) {
    color: #7a7a7a;
}

.datepicker-cell.prev.selected,
.datepicker-cell.next.selected {
    color: #e6e6e6;
}

.datepicker-cell.highlighted:not(.selected):not(.range):not(.today) {
    border-radius: 0;
    background-color: whitesmoke;
}

.datepicker-cell.highlighted:not(.selected):not(.range):not(.today):not(.disabled):hover {
    background-color: #eeeeee;
}

.datepicker-cell.highlighted:not(.selected):not(.range):not(.today).focused {
    background-color: #e8e8e8;
}

.datepicker-cell.today:not(.selected) {
    background-color: #00d1b2;
}

.datepicker-cell.today:not(.selected):not(.disabled) {
    color: #fff;
}

.datepicker-cell.today.focused:not(.selected) {
    background-color: #00c4a7;
}

.datepicker-cell.range-end:not(.selected),
.datepicker-cell.range-start:not(.selected) {
    background-color: #b5b5b5;
    color: #fff;
}

.datepicker-cell.range-end.focused:not(.selected),
.datepicker-cell.range-start.focused:not(.selected) {
    background-color: #afafaf;
}

.datepicker-cell.range-start {
    border-radius: 4px 0 0 4px;
}

.datepicker-cell.range-end {
    border-radius: 0 4px 4px 0;
}

.datepicker-cell.range {
    border-radius: 0;
    background-color: #dbdbdb;
}

.datepicker-cell.range:not(.disabled):not(.focused):not(.today):hover {
    background-color: #d5d5d5;
}

.datepicker-cell.range.disabled {
    color: #c2c2c2;
}

.datepicker-cell.range.focused {
    background-color: #cfcfcf;
}

.datepicker-view.datepicker-grid .datepicker-cell {
    height: 4.5rem;
    line-height: 4.5rem;
}

.datepicker-input.in-edit {
    border-color: #2366d1;
}

.datepicker-input.in-edit:focus,
.datepicker-input.in-edit:active {
    box-shadow: 0 0 0.25em 0.25em rgba(35, 102, 209, 0.2);
}
</style>