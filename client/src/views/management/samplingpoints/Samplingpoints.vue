<script setup>
import LEdit from "./LEdit.vue";

import Service from "./service";
import ManagementService from "../managementservice";
import Eventy from "../../../helpers/eventy";
import { tblToCsv, compare } from "../../../helpers/utils";
import ToolBar from "../../../components/ToolBar.vue";
import Columns from "./columns";

const q = ref("");
const media = ref([]);
const networks = ref([]);
const stations = ref([]);
const stationClassifications = ref([]);
const pollutants = ref([]);
const concentrations = ref([]);
const timesteps = ref([]);
const assessmentTypes = ref([]);
const measurement_regimes = ref([]);
const area_classifications = ref([]);
const samplingPoints = ref([]);
const columns = ref([]);

const showEdit = ref(false);
const showAdd = ref(false);
const selected = ref({});
const ev = ref({});
const showContextmenu = ref(false);
const showConfirm = ref(false);

onMounted(async () => {
  media.value = await ManagementService.media();
  networks.value = await ManagementService.networks();
  measurement_regimes.value = await ManagementService.measurement_regimes();
  area_classifications.value = await ManagementService.area_classifications();
  stations.value = await ManagementService.stations();
  pollutants.value = await ManagementService.pollutants();
  timesteps.value = await ManagementService.timesteps();
  assessmentTypes.value = await ManagementService.assessment_types();
  stationClassifications.value = await ManagementService.station_classifications();
  concentrations.value = await ManagementService.concentrations();
  await loadData();
});

const loadData = async () => {
  samplingPoints.value = await Service.get();
  console.log("samplingPoints", samplingPoints.value);
  columns.value = Columns;
};

const cmp_samplingpoints = computed(() => {
  var t = samplingPoints.value.filter((p) => {
    return !q.value || p.id.toLowerCase().includes(q.value.toLowerCase()) || p.name.toLowerCase().includes(q.value.toLowerCase()) || p.authority.toLowerCase().includes(q.value.toLowerCase()) || p.organisationlevel.toLowerCase().includes(q.value.toLowerCase());
  });
  return t;
});

const cls_rowClass = (row) => {
  if (compare(selected.value, row)) return " selected";
  return "";
};

const onContextMenu = (row, e) => {
  selected.value = row;
  ev.value = e;
  showContextmenu.value = true;
};

const onEdit = () => {
  if (showEdit.value) selected.value = {};
  showEdit.value = !showEdit.value;
  showContextmenu.value = false;
};

const onDelete = () => {
  if (showConfirm.value) selected.value = {};
  showConfirm.value = !showConfirm.value;
  showContextmenu.value = false;
};

const close = () => {
  showEdit.value = false;
  showAdd.value = false;
  selected.value = {};
  showContextmenu.value = false;
  showConfirm.value = false;
};

const saveEdit = async (o) => {
  await Service.update(o);
  samplingPoints.value = await Service.get();
  Eventy.showHideMessage("Station saved", "success", 5000);
  close();
};

const saveAdd = async (o) => {
  await Service.insert(o);
  samplingPoints.value = await Service.get();
  Eventy.showHideMessage("Station saved", "success", 5000);
  close();
};

const saveDelete = async (o) => {
  showConfirm.value = false;
  await Service.delete(selected.value);
  await loadData();
  Eventy.showHideMessage("Station deleted", "success", 5000);
  close();
};

const onDownload = () => {
  tblToCsv("id", "samplingPoints");
};
</script>

<template>
  <common-layout>
    <confirm :show="showConfirm" title="Delete" text="Are you sure you want to delete the samplingpoint?" @close="close" @ok="saveDelete" />
    <contextmenu-crud :show="showContextmenu" :ev="ev" @click-outside="close" @on-edit="onEdit" @onDelete="onDelete" />

    <l-edit :show="showAdd" @close="close" @save="saveAdd" :samplingpoint="selected" :media="media" :stations="stations" :pollutants="pollutants" :concentrations="concentrations" :timesteps="timesteps" :assessmentTypes="assessmentTypes" :stationClassifications="stationClassifications" :networks="networks" :measurement_regimes="measurement_regimes" :area_classifications="area_classifications" />
    <l-edit :show="showEdit" @close="close" @save="saveEdit" :samplingpoint="selected" :media="media" :stations="stations" :pollutants="pollutants" :concentrations="concentrations" :timesteps="timesteps" :assessmentTypes="assessmentTypes" :stationClassifications="stationClassifications" :networks="networks" :measurement_regimes="measurement_regimes" :area_classifications="area_classifications" />

    <tool-bar title="Sampling Points" filter-text="Type to filter samplingPoints " v-model="q" @add-click="showAdd = true" @download-click="onDownload" :column-picker="columns" />

    <div>
      <table id="samplingPointsId" class="n-table">
        <tr>
          <th v-if="columns.find((c) => c.col == 'Id')?.checked">Id</th>
          <th v-if="columns.find((c) => c.col == 'Media')?.checked">Media</th>
          <th v-if="columns.find((c) => c.col == 'Station')?.checked">Station</th>
          <th v-if="columns.find((c) => c.col == 'Mobile')?.checked">Mobile</th>
          <th v-if="columns.find((c) => c.col == 'Measurement Regime')?.checked">Measurement Regime</th>
          <th v-if="columns.find((c) => c.col == 'Assessment Type')?.checked">Assessment Type</th>
          <th v-if="columns.find((c) => c.col == 'Station Classification')?.checked">Station Classification</th>
          <th v-if="columns.find((c) => c.col == 'Used AQD')?.checked">Used AQD</th>
          <th v-if="columns.find((c) => c.col == 'Main Emission Sources')?.checked">Main Emission Sources</th>
          <th v-if="columns.find((c) => c.col == 'Traffic Emissions')?.checked">Traffic Emissions</th>
          <th v-if="columns.find((c) => c.col == 'Heating Emissions')?.checked">Heating Emissions</th>
          <th v-if="columns.find((c) => c.col == 'Industrial Emissions')?.checked">Industrial Emissions</th>
          <th v-if="columns.find((c) => c.col == 'Distance Source')?.checked">Distance Source</th>
          <th v-if="columns.find((c) => c.col == 'Change AEI Stations')?.checked">Change AEI Stations</th>
          <th v-if="columns.find((c) => c.col == 'Begin Position')?.checked">Begin Position</th>
          <th v-if="columns.find((c) => c.col == 'End position')?.checked">End Position</th>
          <th v-if="columns.find((c) => c.col == 'Logger Id')?.checked">Logger</th>
          <th v-if="columns.find((c) => c.col == 'Pollutant')?.checked">Pollutant</th>
          <th v-if="columns.find((c) => c.col == 'Concentration')?.checked">Concentration</th>
          <th v-if="columns.find((c) => c.col == 'Timestep')?.checked">Timestep</th>
          <th v-if="columns.find((c) => c.col == 'From Time')?.checked">From Time</th>
          <th v-if="columns.find((c) => c.col == 'To Time')?.checked">To Time</th>
        </tr>
        <tr v-for="row in cmp_samplingpoints" @contextmenu.prevent="onContextMenu(row, $event)" @click="selected = {}" :class="cls_rowClass(row)">
          <td v-if="columns.find((c) => c.col == 'Id')?.checked">{{ row.id }}</td>
          <td v-if="columns.find((c) => c.col == 'Media')?.checked">{{ row.media_monitored_name }}</td>
          <td v-if="columns.find((c) => c.col == 'Station')?.checked">{{ row.station }}</td>
          <td v-if="columns.find((c) => c.col == 'Mobile')?.checked">{{ row.mobile }}</td>
          <td v-if="columns.find((c) => c.col == 'Measurement Regime')?.checked">{{ row.measurement_regime_name }}</td>
          <td v-if="columns.find((c) => c.col == 'Assessment Type')?.checked">{{ row.assessment_type_name }}</td>
          <td v-if="columns.find((c) => c.col == 'Station Classification')?.checked">{{ row.station_classification_name }}</td>
          <td v-if="columns.find((c) => c.col == 'Used AQD')?.checked">{{ row.used_aqd }}</td>
          <td v-if="columns.find((c) => c.col == 'Main Emission Sources')?.checked">{{ row.main_emission_sources }}</td>
          <td v-if="columns.find((c) => c.col == 'Traffic Emissions')?.checked">{{ row.traffic_emissions }}</td>
          <td v-if="columns.find((c) => c.col == 'Heating Emissions')?.checked">{{ row.heating_emissions }}</td>
          <td v-if="columns.find((c) => c.col == 'Industrial Emissions')?.checked">{{ row.industrial_emissions }}</td>
          <td v-if="columns.find((c) => c.col == 'Distance Source')?.checked">{{ row.distance_source }}</td>
          <td v-if="columns.find((c) => c.col == 'Change AEI Stations')?.checked">{{ row.change_aei_stations }}</td>
          <td v-if="columns.find((c) => c.col == 'Begin Position')?.checked">{{ row.begin_position }}</td>
          <td v-if="columns.find((c) => c.col == 'End position')?.checked">{{ row.end_position }}</td>
          <td v-if="columns.find((c) => c.col == 'Logger Id')?.checked">{{ row.logger_id }}</td>
          <td v-if="columns.find((c) => c.col == 'Pollutant')?.checked">{{ row.pollutant_name }}</td>
          <td v-if="columns.find((c) => c.col == 'Concentration')?.checked">{{ row.concentration_name }}</td>
          <td v-if="columns.find((c) => c.col == 'Timestep')?.checked">{{ row.timestep_name }}</td>
          <td v-if="columns.find((c) => c.col == 'From Time')?.checked">{{ row.from_time }}</td>
          <td v-if="columns.find((c) => c.col == 'To Time')?.checked">{{ row.to_time }}</td>
        </tr>
      </table>
    </div>
  </common-layout>
</template>
