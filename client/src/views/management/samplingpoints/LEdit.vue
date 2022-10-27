<script setup>
const props = defineProps({
  show: Boolean,
  samplingpoint: Object,
  media: Array,
  networks: Array,
  measurement_regimes: Array,
  stations: Array,
  pollutants: Array,
  timesteps: Array,
  assessmentTypes: Array,
  stationClassifications: Array,
  concentrations: Array
});

const obj = ref({});

watch(
  () => props.samplingpoint,
  () => (obj.value = Object.assign({}, props.samplingpoint))
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
            <div class="font-bold">Station:</div>
            <n-select v-model="obj.station_id" class="w-64">
              <n-option v-for="s in stations" :key="s.value" :value="s.value" :label="s.label" />
            </n-select>
          </div>
          <div class="mb-2">
            <div class="font-bold">Station Classification:</div>
            <n-select v-model="obj.station_classification" class="w-64">
              <n-option v-for="s in stationClassifications" :key="s.value" :value="s.value" :label="s.label" />
            </n-select>
          </div>
          <div class="mb-2">
            <div class="font-bold">Pollutant:</div>
            <n-select v-model="obj.pollutant" class="w-64">
              <n-option v-for="p in pollutants" :key="p.value" :value="p.value" :label="p.label" />
            </n-select>
          </div>
          <div class="mb-2">
            <div class="font-bold">Concentration:</div>
            <n-select v-model="obj.concentration" class="w-64">
              <n-option v-for="c in concentrations" :key="c.value" :value="c.value" :label="c.label" />
            </n-select>
          </div>
          <div class="mb-2">
            <div class="font-bold">Timestep:</div>
            <n-select v-model="obj.timestep" class="w-64">
              <n-option v-for="t in timesteps" :key="t.value" :value="t.value" :label="t.label" />
            </n-select>
          </div>
          <div class="mb-2">
            <div class="font-bold">Media:</div>
            <n-select v-model="obj.media_monitored" class="w-64">
              <n-option v-for="a in media" :key="a.value" :value="a.value" :label="a.label" />
            </n-select>
          </div>
          <div class="mb-2">
            <div class="font-bold">Begin Position:</div>
            <input type="text" class="n-input w-64" v-model="obj.begin_position" placeholder="date: YYYY-MM-DDTHH:mm:ss+hh:00" />
          </div>

          <div class="mb-2">
            <div class="font-bold">Assessment Type:</div>
            <n-select v-model="obj.assessment_type" class="w-64">
              <n-option v-for="t in assessmentTypes" :key="t.value" :value="t.value" :label="t.label" />
            </n-select>
          </div>

          <div class="mb-2">
            <div class="font-bold">Measurement Regime:</div>
            <n-select v-model="obj.measurement_regime" class="w-64">
              <n-option v-for="a in measurement_regimes" :key="a.value" :value="a.value" :label="a.label" />
            </n-select>
          </div>

          <div class="mt-2 mb-2 flex cursor-pointer hover:bg-gray-50 p-1">
            <div class="font-bold self-center flex-1" @click="obj.mobile = !obj.mobile">Mobile:</div>
            <n-checkbox v-model="obj.mobile" class="self-center" />
          </div>

          <div class="mt-2 mb-2 flex cursor-pointer hover:bg-gray-50 p-1">
            <div class="font-bold self-center flex-1" @click="obj.used_aqd = !obj.used_aqd">Used Aqd:</div>
            <n-checkbox v-model="obj.used_aqd" class="self-center" />
          </div>
        </div>
      </div>
      <div class="flex w-1/2">
        <div class="h-full w-64">
          <div class="mb-4 font-bold text-base border-b">Optional</div>
          <div class="mb-2">
            <div class="font-bold">Logger Id:</div>
            <input type="text" class="n-input w-64" v-model="obj.logger_id" placeholder="str: Logger Id (if using push logger functionality)" />
          </div>
          <div class="mb-2">
            <div class="font-bold">Main Emission Sources:</div>
            <input type="text" class="n-input w-64" v-model="obj.main_emission_sources" placeholder="str: Main Emission Sources" />
          </div>
          <div class="mb-2">
            <div class="font-bold">Traffic Emissions:</div>
            <input type="text" class="n-input w-64" v-model="obj.traffic_emissions" placeholder="str: Traffic Emissions" />
          </div>
          <div class="mb-2">
            <div class="font-bold">Heating Emissions:</div>
            <input type="text" class="n-input w-64" v-model="obj.heating_emissions" placeholder="str: Heating Emissions" />
          </div>
          <div class="mb-2">
            <div class="font-bold">Industrial Emissions:</div>
            <input type="text" class="n-input w-64" v-model="obj.industrial_emissions" placeholder="str: Industrial Emissions" />
          </div>
          <div class="mb-2">
            <div class="font-bold">Distance Source:</div>
            <input type="text" class="n-input w-64" v-model="obj.distance_source" placeholder="str: Distance Source" />
          </div>
          <div class="mb-2">
            <div class="font-bold">Change Aei Stations:</div>
            <input type="text" class="n-input w-64" v-model="obj.change_aei_stations" placeholder="str: Change Aei Stations" />
          </div>
          <div class="mb-2">
            <div class="font-bold">End Position:</div>
            <input type="text" class="n-input w-64" v-model="obj.end_position" placeholder="d: YYYY-MM-DDTHH:mm:ss+hh:00" />
          </div>
        </div>
      </div>
    </div>
  </side-bar-crud>
</template>
<style></style>
