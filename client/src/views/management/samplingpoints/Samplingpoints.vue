<script setup>
import LEdit from "./LEdit.vue";

import Service from "./service";
import ManagementService from "../managementservice";
import Eventy from "../../../helpers/eventy";
import { tblToCsv, compare } from "../../../helpers/utils";
import ToolBar from "../../../components/ToolBar.vue";

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
const columnsPicked = ref([]);

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
  columns.value = { id: "Id", media_monitored: "Media", station: "Station", measurement_regime: "Measurement regime", mobile: "Mobile", assessment_type: "Assessment type", station_classification: "Station classification", used_aqd: "Used aqd", main_emission_sources: "Main emission sources", traffic_emissions: "Traffic emissions", heating_emissions: "Heating emissions", industrial_emissions: "Industrial emissions", distance_source: "Distance source", change_aei_stations: "Change aei stations", begin_position: "Begin position", end_position: "End position", logger_id: "Logger id", pollutant: "Pollutant", concentration: "Concentration", timestep: "Timestep", from_time: "From time", to_time: "To time" };
  columnsPicked.value = ["id", "station", "station_classification", "pollutant", "concentration", "timestep", "begin_position"];
  console.log("samplingPoints", samplingPoints.value);
  console.log("colums", columns.value);
  console.log("columnsPicked", columnsPicked.value);
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

const columnsChanged = (column) => {
  console.log("columnsChanged", column);
  if (columnsPicked.value.includes(column)) {
    columnsPicked.value = columnsPicked.value.filter((c) => c !== column);
  } else {
    columnsPicked.value.push(column);
  }
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

    <tool-bar title="samplingPoints" filter-text="Type to filter samplingPoints " v-model="q" @add-click="showAdd = true" @download-click="onDownload" :column-picker="columns" :columns-picked="columnsPicked" @columns-changed="columnsChanged" />

    <div>
      <table id="samplingPointsId" class="n-table">
        <tr>
          <!-- SamplingPointsModel -->
          <th v-if="columnsPicked.includes('id')">Id</th>
          <th v-if="columnsPicked.includes('media_monitored')">Media</th>
          <th v-if="columnsPicked.includes('station')">Station</th>
          <th v-if="columnsPicked.includes('mobile')">Mobile</th>
          <th v-if="columnsPicked.includes('measurement_regime')">Measurment Regime</th>
          <th v-if="columnsPicked.includes('assessment_type')">Assessment Type</th>
          <th v-if="columnsPicked.includes('station_classification')">Station Classification</th>
          <th v-if="columnsPicked.includes('used_aqd')">Used AQD</th>
          <th v-if="columnsPicked.includes('main_emission_sources')">Main Emisison Sources</th>
          <th v-if="columnsPicked.includes('traffic_emissions')">Traffic Emissions</th>
          <th v-if="columnsPicked.includes('heating_emissions')">Heating Emissions</th>
          <th v-if="columnsPicked.includes('industrial_emissions')">Industrial Emissions</th>
          <th v-if="columnsPicked.includes('distance_source')">Distance Source</th>
          <th v-if="columnsPicked.includes('change_aei_stations')">Change AEI Stations</th>
          <th v-if="columnsPicked.includes('begin_position')">Begin Position</th>
          <th v-if="columnsPicked.includes('end_position')">End Position</th>
          <th v-if="columnsPicked.includes('logger_id')">Logger</th>
          <th v-if="columnsPicked.includes('pollutant')">Pollutant</th>
          <th v-if="columnsPicked.includes('concentration')">Concentration</th>
          <th v-if="columnsPicked.includes('timestep')">Timestep</th>
          <th v-if="columnsPicked.includes('from_time')">From Time</th>
          <th v-if="columnsPicked.includes('to_time')">To Time</th>
        </tr>
        <tr v-for="row in cmp_samplingpoints" @contextmenu.prevent="onContextMenu(row, $event)" @click="selected = {}" :class="cls_rowClass(row)">
          <td v-if="columnsPicked.includes('id')">{{ row.id }}</td>
          <td v-if="columnsPicked.includes('media_monitored')">{{ row.media_monitored_name }}</td>
          <td v-if="columnsPicked.includes('station')">{{ row.station }}</td>
          <td v-if="columnsPicked.includes('mobile')">{{ row.mobile }}</td>
          <td v-if="columnsPicked.includes('measurement_regime')">{{ row.measurement_regime_name }}</td>
          <td v-if="columnsPicked.includes('assessment_type')">{{ row.assessment_type_name }}</td>
          <td v-if="columnsPicked.includes('station_classification')">{{ row.station_classification_name }}</td>
          <td v-if="columnsPicked.includes('used_aqd')">{{ row.used_aqd }}</td>
          <td v-if="columnsPicked.includes('main_emission_sources')">{{ row.main_emission_sources }}</td>
          <td v-if="columnsPicked.includes('traffic_emissions')">{{ row.traffic_emissions }}</td>
          <td v-if="columnsPicked.includes('heating_emissions')">{{ row.heating_emissions }}</td>
          <td v-if="columnsPicked.includes('industrial_emissions')">{{ row.industrial_emissions }}</td>
          <td v-if="columnsPicked.includes('distance_source')">{{ row.distance_source }}</td>
          <td v-if="columnsPicked.includes('change_aei_stations')">{{ row.change_aei_stations }}</td>
          <td v-if="columnsPicked.includes('begin_position')">{{ row.begin_position }}</td>
          <td v-if="columnsPicked.includes('end_position')">{{ row.end_position }}</td>
          <td v-if="columnsPicked.includes('logger_id')">{{ row.logger_id }}</td>
          <td v-if="columnsPicked.includes('pollutant')">{{ row.pollutant_name }}</td>
          <td v-if="columnsPicked.includes('concentration')">{{ row.concentration_name }}</td>
          <td v-if="columnsPicked.includes('timestep')">{{ row.timestep_name }}</td>
          <td v-if="columnsPicked.includes('from_time')">{{ row.from_time }}</td>
          <td v-if="columnsPicked.includes('to_time')">{{ row.to_time }}</td>
        </tr>
      </table>
    </div>
  </common-layout>
</template>
