<script setup>
import LEdit from "./LEdit.vue";

import Service from "./service";
import ManagementService from "../managementservice";
import Eventy from "../../../helpers/eventy";
import { tblToCsv, compare } from "../../../helpers/utils";
import ToolBar from "../../../components/ToolBar.vue";

const q = ref("");
const measurement_types = ref([]);
const measurement_methods = ref([]);
const measurement_equipment = ref([]);
const equiv_demonstrations = ref([]);
const concentrations = ref([]);
const timesteps = ref([]);
const cadence_units = ref([]);
const responsible_authorities = ref([]);

const processes = ref([]);
const columns = ref([]);
const columnsPicked = ref([]);

const showEdit = ref(false);
const showAdd = ref(false);
const selected = ref({});
const ev = ref({});
const showContextmenu = ref(false);
const showConfirm = ref(false);

onMounted(async () => {
  // media.value = await ManagementService.media();
  // networks.value = await ManagementService.networks();
  // measurement_regimes.value = await ManagementService.measurement_regimes();
  // area_classifications.value = await ManagementService.area_classifications();
  // stations.value = await ManagementService.stations();
  // pollutants.value = await ManagementService.pollutants();
  // timesteps.value = await ManagementService.timesteps();
  // assessmentTypes.value = await ManagementService.assessment_types();
  // stationClassifications.value = await ManagementService.station_classifications();
  // concentrations.value = await ManagementService.concentrations();
  measurement_types.value = await ManagementService.measurement_types();
  measurement_methods.value = await ManagementService.measurement_methods();
  measurement_equipment.value = await ManagementService.measurement_equipment();
  equiv_demonstrations.value = await ManagementService.equiv_demonstrations();
  concentrations.value = await ManagementService.concentrations();
  timesteps.value = await ManagementService.timesteps();
  responsible_authorities.value = await ManagementService.responsible_authorities();

  await loadData();
});

const loadData = async () => {
  processes.value = await Service.get();
  // select id, measurement_type, measurement_method, other_measurement_method, sampling_method, other_sampling_method, analytical_tech, other_analytical_tech, sampling_equipment,
  // measurement_equipment, equiv_demonstration, equiv_demonstration_report, detection_limit, detection_limit_uom, uncertainty_estimate, documentation, qa_report, duration_number, duration_unit,
  // cadence_number, cadence_unit, responsible_authority_id, other_measurement_equipment, other_sampling_equipment from processes
  columns.value = { id: "Id", measurement_type: "Measurement Type", measurement_method: "Measurement Method", other_measurement_method: "Other Measurement Method", sampling_method: "Sampling Method", other_sampling_method: "Other Sampling Method", analytical_tech: "Analytical Tech", other_analytical_tech: "Other Analytical Tech", sampling_equipment: "Sampling Equipment", measurement_equipment: "Measurement Equipment", equiv_demonstration: "Equiv Demonstration", equiv_demonstration_report: "Equiv Demonstration Report", detection_limit: "Detection Limit", detection_limit_uom: "Detection Limit Uom", uncertainty_estimate: "Uncertainty Estimate", documentation: "Documentation", qa_report: "Qa Report", duration_number: "Duration Number", duration_unit: "Duration Unit", cadence_number: "Cadence Number", cadence_unit: "Cadence Unit", responsible_authority_id: "Responsible Authority Id", other_measurement_equipment: "Other Measurement Equipment", other_sampling_equipment: "Other Sampling Equipment" };
  columnsPicked.value = ["id", "measurement_method", "equiv_demonstration", "duration_number", "duration_unit", "cadence_number", "cadence_unit", "responsible_authority_id"];
  console.log("processes", processes.value);
  console.log("colums", columns.value);
  console.log("columnsPicked", columnsPicked.value);
};

const cmp_processes = computed(() => {
  var t = processes.value.filter((p) => {
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
  processes.value = await Service.get();
  Eventy.showHideMessage("Station saved", "success", 5000);
  close();
};

const saveAdd = async (o) => {
  await Service.insert(o);
  processes.value = await Service.get();
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
  tblToCsv("id", "processes");
};
</script>

<template>
  <common-layout>
    <confirm :show="showConfirm" title="Delete" text="Are you sure you want to delete the process?" @close="close" @ok="saveDelete" />
    <contextmenu-crud :show="showContextmenu" :ev="ev" @click-outside="close" @on-edit="onEdit" @onDelete="onDelete" />

    <l-edit :show="showAdd" @close="close" @save="saveAdd" :process="selected" :measurement_types="measurement_types" :measurement_methods="measurement_methods" :cadence_units="cadence_units" :concentrations="concentrations" :timesteps="timesteps" :equiv_demonstrations="equiv_demonstrations" :responsible_authorities="responsible_authorities" :measurement_equipment="measurement_equipment" />
    <l-edit :show="showEdit" @close="close" @save="saveEdit" :process="selected" :measurement_types="measurement_types" :measurement_methods="measurement_methods" :cadence_units="cadence_units" :concentrations="concentrations" :timesteps="timesteps" :equiv_demonstrations="equiv_demonstrations" :responsible_authorities="responsible_authorities" :measurement_equipment="measurement_equipment" />

    <tool-bar title="processes" filter-text="Type to filter processes " v-model="q" @add-click="showAdd = true" @download-click="onDownload" :column-picker="columns" :columns-picked="columnsPicked" @columns-changed="columnsChanged" />

    <div>
      <table id="processesId" class="n-table">
        <tr>
          <th v-if="columnsPicked.includes('id')">Id</th>
          <th v-if="columnsPicked.includes('measurement_type')">Measurement type</th>
          <th v-if="columnsPicked.includes('measurement_method')">Measurement method</th>
          <th v-if="columnsPicked.includes('other_measurement_method')">Other measurement method</th>
          <th v-if="columnsPicked.includes('sampling_method')">Sampling method</th>
          <th v-if="columnsPicked.includes('other_sampling_method')">Other sampling method</th>
          <th v-if="columnsPicked.includes('analytical_tech')">Analytical tech</th>
          <th v-if="columnsPicked.includes('other_analytical_tech')">Other analytical tech</th>
          <th v-if="columnsPicked.includes('sampling_equipment')">Sampling equipment</th>
          <th v-if="columnsPicked.includes('measurement_equipment')">Measurement equipment</th>
          <th v-if="columnsPicked.includes('equiv_demonstration')">Equiv demonstration</th>
          <th v-if="columnsPicked.includes('equiv_demonstration_report')">Equiv demonstration report</th>
          <th v-if="columnsPicked.includes('detection_limit')">Detection limit</th>
          <th v-if="columnsPicked.includes('detection_limit_uom')">Detection limit uom</th>
          <th v-if="columnsPicked.includes('uncertainty_estimate')">Uncertainty estimate</th>
          <th v-if="columnsPicked.includes('documentation')">Documentation</th>
          <th v-if="columnsPicked.includes('qa_report')">Qa report</th>
          <th v-if="columnsPicked.includes('duration_number')">Duration number</th>
          <th v-if="columnsPicked.includes('duration_unit')">Duration unit</th>
          <th v-if="columnsPicked.includes('cadence_number')">Cadence number</th>
          <th v-if="columnsPicked.includes('cadence_unit')">Cadence unit</th>
          <th v-if="columnsPicked.includes('responsible_authority_id')">Responsible authority id</th>
          <th v-if="columnsPicked.includes('other_measurement_equipment')">Other measurement equipment</th>
          <th v-if="columnsPicked.includes('other_sampling_equipment')">Other sampling equipment</th>
        </tr>
        <tr v-for="row in cmp_processes" @contextmenu.prevent="onContextMenu(row, $event)" @click="selected = {}" :class="cls_rowClass(row)">
          <td v-if="columnsPicked.includes('id')">{{ row.id }}</td>
          <td v-if="columnsPicked.includes('measurement_type')">{{ row.measurement_type_name }}</td>
          <td v-if="columnsPicked.includes('measurement_method')">{{ row.measurement_method_name }}</td>
          <td v-if="columnsPicked.includes('other_measurement_method')">{{ row.other_measurement_method }}</td>
          <td v-if="columnsPicked.includes('sampling_method')">{{ row.sampling_method }}</td>
          <td v-if="columnsPicked.includes('other_sampling_method')">{{ row.other_sampling_method }}</td>
          <td v-if="columnsPicked.includes('analytical_tech')">{{ row.analytical_tech }}</td>
          <td v-if="columnsPicked.includes('other_analytical_tech')">{{ row.other_analytical_tech }}</td>
          <td v-if="columnsPicked.includes('sampling_equipment')">{{ row.sampling_equipment }}</td>
          <td v-if="columnsPicked.includes('measurement_equipment')">{{ row.measurement_equipment_name }}</td>
          <td v-if="columnsPicked.includes('equiv_demonstration')">{{ row.equiv_demonstration_name }}</td>
          <td v-if="columnsPicked.includes('equiv_demonstration_report')">{{ row.equiv_demonstration_report }}</td>
          <td v-if="columnsPicked.includes('detection_limit')">{{ row.detection_limit }}</td>
          <td v-if="columnsPicked.includes('detection_limit_uom')">{{ row.detection_limit_uom_name }}</td>
          <td v-if="columnsPicked.includes('uncertainty_estimate')">{{ row.uncertainty_estimate }}</td>
          <td v-if="columnsPicked.includes('documentation')">{{ row.documentation }}</td>
          <td v-if="columnsPicked.includes('qa_report')">{{ row.qa_report }}</td>
          <td v-if="columnsPicked.includes('duration_number')">{{ row.duration_number }}</td>
          <td v-if="columnsPicked.includes('duration_unit')">{{ row.duration_unit_name }}</td>
          <td v-if="columnsPicked.includes('cadence_number')">{{ row.cadence_number }}</td>
          <td v-if="columnsPicked.includes('cadence_unit')">{{ row.cadence_unit_name }}</td>
          <td v-if="columnsPicked.includes('responsible_authority_id')">{{ row.responsible_authority }}</td>
          <td v-if="columnsPicked.includes('other_measurement_equipment')">{{ row.other_measurement_equipment }}</td>
          <td v-if="columnsPicked.includes('other_sampling_equipment')">{{ row.other_sampling_equipment }}</td>
        </tr>
      </table>
    </div>
  </common-layout>
</template>
