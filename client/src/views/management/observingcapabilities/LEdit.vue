<script setup>
const props = defineProps({
  show: Boolean,
  observingcapability: Object,
  result_nature_values: Array,
  processtype_values: Array,
  samples: Array,
  processes: Array,
  samplingpoints: Array
});

const obj = ref({});

watch(
  () => props.observingcapability,
  () => (obj.value = Object.assign({}, props.observingcapability))
);
</script>

<template>
  <side-bar-crud :show="show" @cancel="$emit('close')" @commit="$emit('save', Object.assign({}, obj))">
    <div class="flex w-fit" style="width: 500px">
      <div class="flex w-1/2">
        <div class="h-full w-64">
          <div class="mb-4 font-bold text-base border-b">Required</div>
          <div class="mb-2">
            <div class="font-bold">Id:</div>
            <input type="text" class="n-input w-64" v-model="obj.id" placeholder="str: Id" />
          </div>
          <div class="mb-2">
            <div class="font-bold">Begin position:</div>
            <input type="text" class="n-input w-64" v-model="obj.begin_position" placeholder="str: Begin position" />
          </div>

          <div class="mb-2">
            <div class="font-bold">Result Nature:</div>
            <n-select v-model="obj.result_nature" class="w-64">
              <n-option v-for="t in result_nature_values" :key="t.value" :value="t.value" :label="t.label" />
            </n-select>
          </div>
          <div class="mb-2">
            <div class="font-bold">Sample Id:</div>
            <n-select v-model="obj.sample_id" class="w-64">
              <n-option v-for="t in samples" :key="t.value" :value="t.value" :label="t.label" />
            </n-select>
          </div>
          <div class="mb-2">
            <div class="font-bold">Sampling Point Id:</div>
            <n-select v-model="obj.sampling_point_id" class="w-64">
              <n-option v-for="t in samplingpoints" :key="t.value" :value="t.value" :label="t.label" />
            </n-select>
          </div>
          <div class="mb-2">
            <div class="font-bold">Process Type:</div>
            <n-select v-model="obj.process_type" class="w-64">
              <n-option v-for="t in processtype_values" :key="t.value" :value="t.value" :label="t.label" />
            </n-select>
          </div>

          <div class="mb-2">
            <div class="font-bold">Process Id:</div>
            <n-select v-model="obj.process_id" class="w-64">
              <n-option v-for="t in processes" :key="t.value" :value="t.value" :label="t.label" />
            </n-select>
          </div>
        </div>
      </div>
      <div class="flex w-1/2">
        <div class="h-full w-64">
          <div class="mb-4 font-bold text-base border-b">Optional</div>
          <div class="mb-2">
            <div class="font-bold">End position:</div>
            <input type="text" class="n-input w-64" v-model="obj.end_position" placeholder="str: End position" />
          </div>
        </div>
      </div>
    </div>
  </side-bar-crud>
</template>
<style></style>
