<script setup>
const props = defineProps({
  show: Boolean,
  assessmentregime: Object,
  zones: Array,
  pollutants: Array,
  assessmentTypes: Array,
  exceedances: Array,
  edit: Boolean
});

const obj = ref({});

watch(
  () => props.assessmentregime,
  () => (obj.value = Object.assign({}, props.assessmentregime))
);
</script>

<template>
  <!--     id: str
    name: str
    objecttype: str
    reportingmetric: str
    protectiontarget: str
    assessmentthresholdexceedance: str
    include: bool
    thresholdclassificationyear: str
    thresholdclassificationreport: str
    zoneid: str
    zone_name: str
    pollutant: str
    pollutant_name: str
    data: list -->
  <side-bar-crud :show="show" @cancel="$emit('close')" @commit="$emit('save', Object.assign({}, obj))">
    <div class="" style="min-width: 600px">
      <div class="flex flex-col w-full">
        <div class="mb-4 font-bold text-base border-b">Required</div>
      </div>
      <div class="grid grid-cols-2 gap-1">
        <div class="flex flex-col w-1/2">
          <div class="mb-2">
            <div class="font-bold">Id:</div>
            <input :disabled="edit == true" type="text" class="n-input w-64" v-model="obj.id" placeholder="str: Id" />
          </div>
          <div class="mb-2">
            <div class="font-bold">Name:</div>
            <input type="text" class="n-input w-64" v-model="obj.name" placeholder="str: Name" />
          </div>
          <div class="mb-2">
            <div class="font-bold">Object Type:</div>
            <input :disabled="edit == true" type="text" class="n-input w-64" v-model="obj.objecttype" placeholder="str: Object Type" />
          </div>
          <div class="mb-2">
            <div class="font-bold">Reporting Metric:</div>
            <input :disabled="edit == true" type="text" class="n-input w-64" v-model="obj.reportingmetric" placeholder="str: Reporting Metric" />
          </div>
          <div class="mb-2">
            <div class="font-bold">Protection Target:</div>
            <input type="text" :disabled="edit == true" class="n-input w-64" v-model="obj.protectiontarget" placeholder="str: Protection Target" />
          </div>
        </div>
        <div class="flex flex-col w-1/2">
          <div class="mb-2">
            <div class="font-bold">Exceedances:</div>
            <n-select v-model="obj.assessmentthresholdexceedance" style="width: 224px">
              <n-option v-for="t in exceedances" :key="t.value" :value="t.value" :label="t.label" />
            </n-select>
          </div>
          <!-- <div class="mb-2">
            <div class="font-bold">Include:</div>
            <input type="text" class="n-input w-64" v-model="obj.include" placeholder="bool: Include" />
          </div> -->
          <div class="mb-2">
            <div class="font-bold">Year:</div>
            <input type="text" class="n-input w-64" v-model="obj.thresholdclassificationyear" placeholder="str: Year" />
          </div>
          <div class="mb-2">
            <div class="font-bold">Report:</div>
            <input type="text" class="n-input w-64" v-model="obj.thresholdclassificationreport" placeholder="str: Threshold Classification Report" />
          </div>

          <div class="mb-2">
            <div class="font-bold">Pollutant:</div>
            <input v-if="edit == true" disabled="true" type="text" class="n-input w-64" v-model="obj.pollutant" />
            <n-select v-if="edit == false" :disabled="edit == true" v-model="obj.pollutant" class="w-64" style="width: 224px">
              <n-option v-for="t in pollutants" :key="t.value" :value="t.value" :label="t.label" />
            </n-select>
          </div>
          <div class="mb-2">
            <div class="font-bold">Zone:</div>
            <input v-if="edit == true" disabled="true" type="text" class="n-input w-64" v-model="obj.zoneid" />
            <n-select v-if="edit == false" v-model="obj.zoneid" style="width: 224px">
              <n-option v-for="t in zones" :key="t.value" :value="t.value" :label="t.label" />
            </n-select>
          </div>
        </div>
      </div>
      <div class="grid grid-cols-1 w-fit mt-6">
        <div class="flex flex-row mb-4 font-bold text-base border-b">Optional</div>
        <div class="flex flex-row">
          <table id="assessmentRegimesId" class="n-table">
            <tr v-for="row in obj.data" :key="row.samplingpoint_id">
              <td>{{ row.station_name }} {{ row.samplingpoint_id }}</td>
              <td>
                <n-select v-model="row.assessmenttype" class="n-input">
                  <n-option v-for="t in assessmentTypes" :key="t.value" :value="t.value" :label="t.label" />
                </n-select>
              </td>
              <td>
                <input type="text" class="n-input w-64" v-model="obj.thresholdclassificationreport" placeholder="str: Threshold Classification Report" />
              </td>
            </tr>
          </table>
        </div>
      </div>
    </div>
  </side-bar-crud>
</template>
<style></style>
