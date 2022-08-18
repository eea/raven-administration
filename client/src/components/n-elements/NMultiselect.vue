<script setup>
import EventListener from "./EventListener.vue";

var p = defineProps({
  modelValue: {
    type: Array,
    default: [],
  },
  searchable: {
    type: Boolean,
    default: false,
  },
});
const id = "id" + Math.random().toString(16).slice(2);

const emit = defineEmits(["update:modelValue"]);

const expand = ref(false);
const options = ref(null);
const q = ref("");
const disabledOptions = ref([]);
const labels = ref([]);

onMounted(() => {
  setSelectedOnOptions();
});

watch(
  () => p.modelValue,
  (nv) => {
    setSelectedOnOptions();
  }
);

// bug in multiselect. if options are not yet drawn, v-model is not showing as selected
// watch(
//   () => options.children,
//   (nv) => {
//     console.log("WATCH2", options.value);
//     setSelectedOnOptions();
//   },
//   { deep: true }
// );

watch(q, (nv) => {
  disabledOptions.value = [];
  for (let i = 0; i < options.value.children.length; i++) {
    var l = options.value.children[i].getAttribute("label");
    if (l != null) {
      if (!l.toLowerCase().includes(q.value.toLowerCase())) disabledOptions.value.push(options.value.children[i].getAttribute("value"));
    }
  }

  setSelectedOnOptions();
});

const onSelectionClick = (o) => {
  const f = p.modelValue.filter((m) => m != o);
  emit("update:modelValue", removeDuplicates(f.map((p) => p)));
};

const onOptionClick = (o) => {
  const values = p.modelValue.map((m) => m);
  if (!values.includes(o)) {
    values.push(o);
    emit("update:modelValue", removeDuplicates(values.map((p) => p)));
  } else {
    onSelectionClick(o);
  }
};

const setSelectedOnOptions = () => {
  labels.value = [];
  for (let i = 0; i < options.value.children.length; i++) {
    var v = options.value.children[i].getAttribute("value");
    var values = p.modelValue.map((p) => p);
    if (values.includes(v)) {
      options.value.children[i].setAttribute("selected", true);
      labels.value[v] = options.value.children[i].getAttribute("label");
    } else options.value.children[i].removeAttribute("selected");
    if (disabledOptions.value.includes(v)) options.value.children[i].setAttribute("disabled", true);
    else options.value.children[i].removeAttribute("disabled");
  }
};

const onFocusOut = (e) => {
  const rel = e.relatedTarget == null ? null : e.relatedTarget.getAttribute("n-id");
  const tar = e.target.getAttribute("n-id");

  if (rel == null) {
    return closeOptions();
  } else if (rel != id && tar == "n-search-option") {
    return closeOptions();
  } else if (rel != "n-search-option" && tar == id) {
    return closeOptions();
  }
};

const removeDuplicates = (arr) => {
  return arr.filter((value, index, self) => index === self.findIndex((t) => t === value));
};

const closeOptions = () => {
  q.value = "";
  expand.value = false;
  return;
};
</script>
<script>
export default {
  inheritAttrs: false,
};
</script>

<template>
  <div class="n-multiselect" tabindex="0" @focusout="onFocusOut" :n-id="id">
    <div class="select" v-bind="$attrs" @click="expand = !expand">
      <div class="selections">
        <div v-if="labels.length == 0">&nbsp;</div>
        <div class="selected-box" v-for="(o, i) in modelValue" @click.stop.prevent="onSelectionClick(o, $event)">{{ labels[o] }}</div>
      </div>
      <svg class="caret" preserveAspectRatio="xMidYMid meet" viewBox="0 0 256 256">
        <path fill="currentColor" d="M128 188a12.2 12.2 0 0 1-8.5-3.5l-80-80a12 12 0 0 1 17-17L128 159l71.5-71.5a12 12 0 0 1 17 17l-80 80a12.2 12.2 0 0 1-8.5 3.5Z"></path>
      </svg>
    </div>

    <div>
      <div class="options" v-show="expand" ref="options" v-bind="$attrs">
        <div v-if="searchable">
          <input n-id="n-search-option" placeholder="Search" type="search" class="n-input n-search-option" v-model="q" />
        </div>
        <event-listener @slot-click="onOptionClick">
          <slot />
        </event-listener>
      </div>
    </div>
  </div>
</template>
