<script setup>
const props = defineProps({
  show: Boolean,
  process: Object,
  measurement_types: Array,
  measurement_methods: Array,
  measurement_equipment: Array,
  equiv_demonstrations: Array,
  concentrations: Array,
  timesteps: Array,
  responsible_authorities: Array
});

const obj = ref({});

watch(
  () => props.process,
  () => (obj.value = Object.assign({}, props.process))
);
</script>

<!-- id: str
    measurement_type: str
    measurement_type_name: str
    measurement_method: str
    measurement_method_name: str
    other_measurement_method: str
    sampling_method: str
    other_sampling_method: str
    analytical_tech: str
    other_analytical_tech: str
    sampling_equipment: str
    measurement_equipment: str
    measurement_equipment_name: str
    equiv_demonstration: str
    equiv_demonstration_name: str
    equiv_demonstration_report: str
    detection_limit: str
    detection_limit_uom: str
    detection_limit_uom_name: str
    uncertainty_estimate: str
    documentation: str
    qa_report: str
    duration_number: str
    duration_unit: str
    duration_unit_name: str
    cadence_number: str
    cadence_unit: str
    cadence_unit_name: str
    responsible_authority_id: str
    responsible_authority: str
    other_measurement_equipment: str
    other_sampling_equipment: str -->

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
            <div class="font-bold">Measurement Type:</div>
            <n-select v-model="obj.measurement_type" class="w-64">
              <n-option v-for="t in measurement_types" :key="t.value" :value="t.value" :label="t.label" />
            </n-select>
          </div>
          <div class="mb-2">
            <div class="font-bold">Measurement Method:</div>
            <n-select v-model="obj.measurement_method" class="w-64">
              <n-option v-for="t in measurement_methods" :key="t.value" :value="t.value" :label="t.label" />
            </n-select>
          </div>
          <div class="mb-2">
            <div class="font-bold">Sampling Method:</div>
            <input type="text" class="n-input w-64" v-model="obj.sampling_method" placeholder="str: Sampling Method" />
          </div>
          <div class="mb-2">
            <div class="font-bold">Analytical Tech:</div>
            <input type="text" class="n-input w-64" v-model="obj.analytical_tech" placeholder="str: Analytical Tech" />
          </div>
          <div class="mb-2">
            <div class="font-bold">Measurement Equipment:</div>
            <n-select v-model="obj.measurement_equipment" class="w-64">
              <n-option v-for="t in measurement_equipment" :key="t.value" :value="t.value" :label="t.label" />
            </n-select>
          </div>
          <div class="mb-2">
            <div class="font-bold">Equiv Demonstration:</div>
            <n-select v-model="obj.equiv_demonstration" class="w-64">
              <n-option v-for="t in equiv_demonstrations" :key="t.value" :value="t.value" :label="t.label" />
            </n-select>
          </div>
          <div class="mb-2">
            <div class="font-bold">Detection Limit:</div>
            <input type="text" class="n-input w-64" v-model="obj.detection_limit" placeholder="str: Detection Limit" />
          </div>
          <div class="mb-2">
            <div class="font-bold">Detection Limit Uom:</div>
            <n-select v-model="obj.detection_limit_uom" class="w-64">
              <n-option v-for="t in concentrations" :key="t.value" :value="t.value" :label="t.label" />
            </n-select>
          </div>
          <div class="mb-2">
            <div class="font-bold">Uncertainty Estimate:</div>
            <input type="text" class="n-input w-64" v-model="obj.uncertainty_estimate" placeholder="str: Uncertainty Estimate" />
          </div>
          <div class="mb-2">
            <div class="font-bold">Documentation:</div>
            <input type="text" class="n-input w-64" v-model="obj.documentation" placeholder="str: Documentation" />
          </div>
          <div class="mb-2">
            <div class="font-bold">Qa Report:</div>
            <input type="text" class="n-input w-64" v-model="obj.qa_report" placeholder="str: Qa Report" />
          </div>
          <div class="mb-2">
            <div class="font-bold">Duration Number:</div>
            <input type="text" class="n-input w-64" v-model="obj.duration_number" placeholder="int: Duration Number" />
          </div>
          <div class="mb-2">
            <div class="font-bold">Duration Unit:</div>
            <n-select v-model="obj.duration_unit" class="w-64">
              <n-option v-for="t in timesteps" :key="t.value" :value="t.value" :label="t.label" />
            </n-select>
          </div>
          <div class="mb-2">
            <div class="font-bold">Cadence Number:</div>
            <input type="text" class="n-input w-64" v-model="obj.cadence_number" placeholder="int: Cadence Number" />
          </div>
          <div class="mb-2">
            <div class="font-bold">Cadence Unit:</div>
            <n-select v-model="obj.cadence_unit" class="w-64">
              <n-option v-for="t in timesteps" :key="t.value" :value="t.value" :label="t.label" />
            </n-select>
          </div>
        </div>
      </div>
      <div class="flex w-1/2">
        <div class="h-full w-64">
          <div class="mb-4 font-bold text-base border-b">Optional</div>
          <div class="mb-2">
            <div class="font-bold">Sampling Equipment:</div>
            <input type="text" class="n-input w-64" v-model="obj.sampling_equipment" placeholder="str: Sampling Equipment" />
          </div>
          <div class="mb-2">
            <div class="font-bold">Other Analytical Tech:</div>
            <input type="text" class="n-input w-64" v-model="obj.other_analytical_tech" placeholder="str: Other Analytical Tech" />
          </div>
          <div class="mb-2">
            <div class="font-bold">Other Measurement Equipment:</div>
            <input type="text" class="n-input w-64" v-model="obj.other_measurement_equipment" placeholder="str: Other Measurement Equipment" />
          </div>
          <div class="mb-2">
            <div class="font-bold">Other Sampling Equipment:</div>
            <input type="text" class="n-input w-64" v-model="obj.other_sampling_equipment" placeholder="str: Other Sampling Equipment" />
          </div>
        </div>
      </div>
    </div>
  </side-bar-crud>
</template>
<style></style>
