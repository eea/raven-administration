<script setup>
import NSelect from "./NSelect.vue";
import NOption from "./NOption.vue";
import Datepicker from "vanillajs-datepicker/Datepicker";

const id = "id" + Math.random().toString(16).slice(2);
let datepicker = null;

var p = defineProps({
  modelValue: {
    type: String,
    validator: (value) => {
      if (!value || value == "") return true;
      var re = /^([\+-]?\d{4}(?!\d{2}\b))((-?)((0[1-9]|1[0-2])(\3([12]\d|0[1-9]|3[01]))?|W([0-4]\d|5[0-2])(-?[1-7])?|(00[1-9]|0[1-9]\d|[12]\d{2}|3([0-5]\d|6[1-6])))([T\s]((([01]\d|2[0-3])((:?)[0-5]\d)?|24\:?00)([\.,]\d+(?!:))?)?(\17[0-5]\d([\.,]\d+)?)?([zZ]|([\+-])([01]\d|2[0-3]):?([0-5]\d)?)?)?)?$/;
      var matches = value.match(re);
      return !!matches;
    }
  }
});
const emit = defineEmits(["update:modelValue"]);

const date = computed({
  get() {
    if (!validate(p.modelValue)) {
      date.value = null;
      return null;
    } else {
      var t = p.modelValue.split("T")[0];
      if (datepicker) datepicker.setDate(t);
      return t;
    }
  },
  set(value) {
    const v = !value ? null : `${value}T${time.value}:00${utc.value}`;
    emit("update:modelValue", v);
  }
});
const time = computed({
  get() {
    if (!validate(p.modelValue)) {
      time.value = "00:00";
      return "00:00";
    }
    var t = p.modelValue.split("T")[1];
    return t.substring(0, 5);
  },
  set(value) {
    const v = !date.value ? null : `${date.value}T${value}:00${utc.value}`;
    emit("update:modelValue", v);
  }
});

const utc = computed({
  get() {
    if (!validate(p.modelValue)) {
      utc.value = "+00:00";
      return "+00:00";
    }

    var t = p.modelValue.split("T")[1];
    if (t.toLocaleLowerCase().endsWith("z")) return "+00:00";
    return t.slice(-6);
  },
  set(value) {
    const v = !date.value ? null : `${date.value}T${time.value}:00${value}`;
    emit("update:modelValue", v);
  }
});

const validate = (dt) => {
  if (!dt || dt == "") return false;
  var re = /^([\+-]?\d{4}(?!\d{2}\b))((-?)((0[1-9]|1[0-2])(\3([12]\d|0[1-9]|3[01]))?|W([0-4]\d|5[0-2])(-?[1-7])?|(00[1-9]|0[1-9]\d|[12]\d{2}|3([0-5]\d|6[1-6])))([T\s]((([01]\d|2[0-3])((:?)[0-5]\d)?|24\:?00)([\.,]\d+(?!:))?)?(\17[0-5]\d([\.,]\d+)?)?([zZ]|([\+-])([01]\d|2[0-3]):?([0-5]\d)?)?)?)?$/;
  var matches = dt.match(re);
  return !!matches;
};

onMounted(async () => {
  const elem = document.querySelector("input[id=" + id + "]");
  datepicker = new Datepicker(elem, {
    format: "yyyy-mm-dd",
    autohide: true
  });
  elem.addEventListener("changeDate", (e) => (date.value = e.target.value));
});
</script>
<script>
export default {
  inheritAttrs: false
};
</script>

<template>
  <div class="n-eea-datetime" v-bind="$attrs">
    <div class="w-1/3">
      <input v-model="date" class="n-input date" :id="id" />
    </div>
    <div class="w-1/3">
      <n-select v-model="time" class="time" :disabled="!date">
        <n-option v-for="i in 24" :key="i" :value="(i - 1 < 10 ? '0' + (i - 1) : i - 1) + ':00'" :label="(i - 1 < 10 ? '0' + (i - 1) : i - 1) + ':00'" />
      </n-select>
    </div>
    <div class="w-1/3">
      <n-select v-model="utc" class="utc" :disabled="!date">
        <n-option value="-06:00" label="-06:00" />
        <n-option value="-05:00" label="-05:00" />
        <n-option value="-04:00" label="-04:00" />
        <n-option value="-03:00" label="-03:00" />
        <n-option value="-02:00" label="-02:00" />
        <n-option value="-01:00" label="-01:00" />
        <n-option value="+00:00" label="+00:00" />
        <n-option value="+01:00" label="+01:00" />
        <n-option value="+02:00" label="+02:00" />
        <n-option value="+03:00" label="+03:00" />
        <n-option value="+04:00" label="+04:00" />
        <n-option value="+05:00" label="+05:00" />
        <n-option value="+06:00" label="+06:00" />
      </n-select>
    </div>
  </div>
</template>
