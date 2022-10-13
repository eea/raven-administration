<script setup>
import LEdit from "./LEdit.vue";

import Service from "./service";
import ManagementService from "../managementservice";
import Eventy from "../../../helpers/eventy";
import { tblToCsv, compare } from "../../../helpers/utils";
import ToolBar from "../../../components/ToolBar.vue";
import Columns from "./columns";

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
  measurement_types.value = await ManagementService.measurement_types();
  measurement_methods.value = await ManagementService.measurement_methods();
  measurement_equipment.value = await ManagementService.measurement_equipment();
  equiv_demonstrations.value = await ManagementService.equiv_demonstrations();
  concentrations.value = await ManagementService.concentrations();
  timesteps.value = await ManagementService.timesteps();
  responsible_authorities.value = await ManagementService.responsible_authorities();
  columns.value = Columns;

  await loadData();
});

const loadData = async () => {
  processes.value = await Service.get();
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

    <tool-bar title="processes" filter-text="Type to filter processes " v-model="q" @add-click="showAdd = true" @download-click="onDownload" :column-picker="columns" />

    <div>
      <table id="processesId" class="n-table">
        <tr>
          <th v-if="columns.find((c) => c.col == 'Id')?.checked">Id</th>
          <th v-if="columns.find((c) => c.col == 'Measurement Type')?.checked">Measurement Type</th>
          <th v-if="columns.find((c) => c.col == 'Measurement Method')?.checked">Measurement Method</th>
          <th v-if="columns.find((c) => c.col == 'Other Measurement Method')?.checked">Other Measurement Method</th>
          <th v-if="columns.find((c) => c.col == 'Sampling Method')?.checked">Sampling Method</th>
          <th v-if="columns.find((c) => c.col == 'Other Sampling Method')?.checked">Other Sampling Method</th>
          <th v-if="columns.find((c) => c.col == 'Analytical Tech')?.checked">Analytical Tech</th>
          <th v-if="columns.find((c) => c.col == 'Other Analytical Tech')?.checked">Other Analytical Tech</th>
          <th v-if="columns.find((c) => c.col == 'Sampling Equipment')?.checked">Sampling Equipment</th>
          <th v-if="columns.find((c) => c.col == 'Measurement Equipment')?.checked">Measurement Equipment</th>
          <th v-if="columns.find((c) => c.col == 'Equiv Demonstration')?.checked">Equiv Demonstration</th>
          <th v-if="columns.find((c) => c.col == 'Equiv Demonstration Report')?.checked">Equiv Demonstration Report</th>
          <th v-if="columns.find((c) => c.col == 'Detection Limit')?.checked">Detection Limit</th>
          <th v-if="columns.find((c) => c.col == 'Detection Limit Uom')?.checked">Detection Limit Uom</th>
          <th v-if="columns.find((c) => c.col == 'Uncertainty Estimate')?.checked">Uncertainty Estimate</th>
          <th v-if="columns.find((c) => c.col == 'Documentation')?.checked">Documentation</th>
          <th v-if="columns.find((c) => c.col == 'Qa Report')?.checked">Qa Report</th>
          <th v-if="columns.find((c) => c.col == 'Duration Number')?.checked">Duration Number</th>
          <th v-if="columns.find((c) => c.col == 'Duration Unit')?.checked">Duration Unit</th>
          <th v-if="columns.find((c) => c.col == 'Cadence Number')?.checked">Cadence Number</th>
          <th v-if="columns.find((c) => c.col == 'Cadence Unit')?.checked">Cadence Unit</th>
          <th v-if="columns.find((c) => c.col == 'Responsible Authority Id')?.checked">Responsible Authority Id</th>
          <th v-if="columns.find((c) => c.col == 'Other Measurement Equipment')?.checked">Other Measurement Equipment</th>
          <th v-if="columns.find((c) => c.col == 'Other Sampling Equipment')?.checked">Other Sampling Equipment</th>
        </tr>
        <tr v-for="row in cmp_processes" @contextmenu.prevent="onContextMenu(row, $event)" @click="selected = {}" :class="cls_rowClass(row)">
          <td v-if="columns.find((c) => c.col == 'Id')?.checked">{{ row.id }}</td>
          <td v-if="columns.find((c) => c.col == 'Measurement Type')?.checked">{{ row.measurement_type_name }}</td>
          <td v-if="columns.find((c) => c.col == 'Measurement Method')?.checked">{{ row.measurement_method_name }}</td>
          <td v-if="columns.find((c) => c.col == 'Other Measurement Method')?.checked">{{ row.other_measurement_method }}</td>
          <td v-if="columns.find((c) => c.col == 'Sampling Method')?.checked">{{ row.sampling_method }}</td>
          <td v-if="columns.find((c) => c.col == 'Other Sampling Method')?.checked">{{ row.other_sampling_method }}</td>
          <td v-if="columns.find((c) => c.col == 'Analytical Tech')?.checked">{{ row.analytical_tech }}</td>
          <td v-if="columns.find((c) => c.col == 'Other Analytical Tech')?.checked">{{ row.other_analytical_tech }}</td>
          <td v-if="columns.find((c) => c.col == 'Sampling Equipment')?.checked">{{ row.sampling_equipment }}</td>
          <td v-if="columns.find((c) => c.col == 'Measurement Equipment')?.checked">{{ row.measurement_equipment_name }}</td>
          <td v-if="columns.find((c) => c.col == 'Equiv Demonstration')?.checked">{{ row.equiv_demonstration_name }}</td>
          <td v-if="columns.find((c) => c.col == 'Equiv Demonstration Report')?.checked">{{ row.equiv_demonstration_report }}</td>
          <td v-if="columns.find((c) => c.col == 'Detection Limit')?.checked">{{ row.detection_limit }}</td>
          <td v-if="columns.find((c) => c.col == 'Detection Limit Uom')?.checked">{{ row.detection_limit_uom_name }}</td>
          <td v-if="columns.find((c) => c.col == 'Uncertainty Estimate')?.checked">{{ row.uncertainty_estimate }}</td>
          <td v-if="columns.find((c) => c.col == 'Documentation')?.checked">{{ row.documentation }}</td>
          <td v-if="columns.find((c) => c.col == 'Qa Report')?.checked">{{ row.qa_report }}</td>
          <td v-if="columns.find((c) => c.col == 'Duration Number')?.checked">{{ row.duration_number }}</td>
          <td v-if="columns.find((c) => c.col == 'Duration Unit')?.checked">{{ row.duration_unit_name }}</td>
          <td v-if="columns.find((c) => c.col == 'Cadence Number')?.checked">{{ row.cadence_number }}</td>
          <td v-if="columns.find((c) => c.col == 'Cadence Unit')?.checked">{{ row.cadence_unit_name }}</td>
          <td v-if="columns.find((c) => c.col == 'Responsible Authority Id')?.checked">{{ row.responsible_authority_id }}</td>
          <td v-if="columns.find((c) => c.col == 'Other Measurement Equipment')?.checked">{{ row.other_measurement_equipment }}</td>
          <td v-if="columns.find((c) => c.col == 'Other Sampling Equipment')?.checked">{{ row.other_sampling_equipment }}</td>
        </tr>
      </table>
    </div>
  </common-layout>
</template>
