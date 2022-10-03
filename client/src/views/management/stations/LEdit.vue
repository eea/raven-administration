<script setup>
const props = defineProps({
  show: Boolean,
  station: Object,
  media: Array,
  networks: Array,
  measurement_regimes: Array,
  area_classifications: Array
});

const obj = ref({});

watch(
  () => props.station,
  () => (obj.value = Object.assign({}, props.station))
);
</script>

<template>
  <side-bar-crud :show="show" @cancel="$emit('close')" @commit="$emit('save', Object.assign({}, obj))">
    <div class="flex w-fit" style="width: 500px">
      <div class="flex w-1/2">
        <div class="h-full w-64">
          <div class="mb-4 font-bold text-base border-b">Required</div>
          <div class="mb-2">
            <div class="font-bold">Name:</div>
            <input type="text" class="n-input w-64" v-model="obj.name" placeholder="str: Name" />
          </div>

          <div class="mb-2">
            <div class="font-bold">Begin Position:</div>
            <input type="text" class="n-input w-64" v-model="obj.begin_position" placeholder="str: Name of network" />
          </div>
          <div class="mb-2">
            <div class="font-bold">City:</div>
            <input type="text" class="n-input w-64" v-model="obj.city" placeholder="str: City" />
          </div>

          <div class="mb-2">
            <div class="font-bold">Longitude:</div>
            <input type="text" class="n-input w-64" v-model="obj.longitude" placeholder="float: Longitude" />
          </div>

          <div class="mb-2">
            <div class="font-bold">Latitude:</div>
            <input type="text" class="n-input w-64" v-model="obj.latitude" placeholder="float: Latitude" />
          </div>

          <div class="mb-2">
            <div class="font-bold">National Station Code:</div>
            <input type="text" class="n-input w-64" v-model="obj.national_station_code" placeholder="str: National Station Code" />
          </div>
          <div class="mb-2">
            <div class="font-bold">Network:</div>
            <!-- <input type="text" class="n-input w-64" v-model="obj.network_id" placeholder="str: Network" /> -->
            <n-select v-model="obj.network_id" class="w-64">
              <n-option v-for="a in networks" :key="a.value" :value="a.value" :label="a.label" />
            </n-select>
          </div>

          <div class="mb-2">
            <div class="font-bold">Media:</div>
            <!-- <input type="text" class="n-input w-64" v-model="obj.media_monitored" placeholder="str: Media Monitored" /> -->
            <n-select v-model="obj.media_monitored" class="w-64">
              <n-option v-for="a in media" :key="a.value" :value="a.value" :label="a.label" />
            </n-select>
          </div>

          <div class="mb-2">
            <div class="font-bold">Mobile:</div>
            <input type="text" class="n-input w-64" v-model="obj.mobile" placeholder="str: Mobile" />
          </div>
          <div class="mb-2">
            <div class="font-bold">Measurement Regime:</div>
            <!-- <input type="text" class="n-input w-64" v-model="obj.measurement_regime" placeholder="str: Measurement Regime" /> -->
            <n-select v-model="obj.measurement_regime" class="w-64">
              <n-option v-for="a in measurement_regimes" :key="a.value" :value="a.value" :label="a.label" />
            </n-select>
          </div>
          <div class="mb-2">
            <div class="font-bold">Area Classification:</div>
            <!-- <input type="text" class="n-input w-64" v-model="obj.area_classification" placeholder="str: Area Classification" /> -->
            <n-select v-model="obj.area_classification" class="w-64">
              <n-option v-for="a in area_classifications" :key="a.value" :value="a.value" :label="a.label" />
            </n-select>
          </div>

          <div class="mb-2">
            <div class="font-bold">Municipality:</div>
            <input type="text" class="n-input w-64" v-model="obj.municipality" placeholder="str: Municipality" />
          </div>
        </div>
      </div>
      <div class="flex w-1/2">
        <div class="h-full w-64">
          <div class="mb-4 font-bold text-base border-b">Optional</div>
          <div class="mb-2">
            <div class="font-bold">Street Width:</div>
            <input type="text" class="n-input w-64" v-model="obj.street_width" placeholder="int: Street width" />
          </div>

          <div class="mb-2">
            <div class="font-bold">Eoi Code:</div>
            <input type="text" class="n-input w-64" v-model="obj.eoi_code" placeholder="str: Eoi Code" />
          </div>

          <div class="mb-2">
            <div class="font-bold">End Position:</div>
            <input type="text" class="n-input w-64" v-model="obj.end_position" placeholder="str: Name of network" />
          </div>

          <div class="mb-2">
            <div class="font-bold">Altitude:</div>
            <input type="text" class="n-input w-64" v-model="obj.altitude" placeholder="float: Altitude" />
          </div>

          <div class="mb-2">
            <div class="font-bold">EPSG:</div>
            <input type="text" class="n-input w-64" v-model="obj.epsg" placeholder="int: EPSG" />
          </div>

          <div class="mb-2">
            <div class="font-bold">Distance Junction:</div>
            <input type="text" class="n-input w-64" v-model="obj.distance_junction" placeholder="int: Distance Junction" />
          </div>

          <div class="mb-2">
            <div class="font-bold">Traffic Volume:</div>
            <input type="text" class="n-input w-64" v-model="obj.traffic_volume" placeholder="int: Traffic Volume" />
          </div>

          <div class="mb-2">
            <div class="font-bold">Heavy Duty Fraction:</div>
            <input type="text" class="n-input w-64" v-model="obj.heavy_duty_fraction" placeholder="float: Heavy Duty Fraction" />
          </div>

          <div class="mb-2">
            <div class="font-bold">Height Facade:</div>
            <input type="text" class="n-input w-64" v-model="obj.height_facades" placeholder="float: Height Facades" />
          </div>

          <div class="mb-2">
            <div class="font-bold">Network:</div>
            <input type="text" class="n-input w-64" v-model="obj.network" placeholder="str: Network" />
          </div>
        </div>
      </div>
    </div>
  </side-bar-crud>
</template>
<style></style>
