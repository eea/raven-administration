<script setup>
import LEdit from "./LEdit.vue";
import Columns from "./columns";

import Service from "./service";
import ManagementService from "../managementservice";
import Eventy from "../../../helpers/eventy";
import { tblToCsv, compare } from "../../../helpers/utils";
import ToolBar from "../../../components/ToolBar.vue";

const q = ref("");
const zones = ref([]);
const pollutants = ref([]);
const assessmentRegimes = ref([]);
const assessmentTypes = ref([]);
const exceedances = ref([]);
const columns = ref([]);

const showEdit = ref(false);
const showAdd = ref(false);
const selected = ref({});
const ev = ref({});
const showContextmenu = ref(false);
const showConfirm = ref(false);

onMounted(async () => {
  zones.value = await ManagementService.zones();
  pollutants.value = await ManagementService.pollutants();
  assessmentTypes.value = await ManagementService.assessment_types();
  exceedances.value = await ManagementService.assessment_exceedances();
  columns.value = Columns;
  await loadData();
});

const loadData = async () => {
  assessmentRegimes.value = await Service.get();
};

const cmp_assessmentregimes = computed(() => {
  var t = assessmentRegimes.value.filter((p) => {
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
  console.log("onEdit", selected.value);
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
  assessmentRegimes.value = await Service.get();
  Eventy.showHideMessage("Station saved", "success", 5000);
  close();
};

const saveAdd = async (o) => {
  await Service.insert(o);
  assessmentRegimes.value = await Service.get();
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
  tblToCsv("id", "assessmentRegimes");
};
</script>

<template>
  <common-layout>
    <confirm :show="showConfirm" title="Delete" text="Are you sure you want to delete the assessment regime?" @close="close" @ok="saveDelete" />
    <contextmenu-crud :show="showContextmenu" :ev="ev" @click-outside="close" @on-edit="onEdit" @onDelete="onDelete" />

    <l-edit :show="showAdd" @close="close" @save="saveAdd" :edit="false" :assessmentregime="selected" :zones="zones" :pollutants="pollutants" :assessmentTypes="assessmentTypes" :exceedances="exceedances" />
    <l-edit :show="showEdit" @close="close" @save="saveEdit" :edit="true" :assessmentregime="selected" :zones="zones" :pollutants="pollutants" :assessmentTypes="assessmentTypes" :exceedances="exceedances" />

    <tool-bar title="Assessment Regimes" filter-text="Type to filter Assessment Regimes" v-model="q" @add-click="showAdd = true" @download-click="onDownload" :column-picker="columns" />

    <div>
      <table id="assessmentRegimesId" class="n-table">
        <tr>
          <th v-if="columns.find((c) => c.col == 'Id')?.checked">Id</th>
          <th v-if="columns.find((c) => c.col == 'Name')?.checked">Name</th>
          <th v-if="columns.find((c) => c.col == 'Zone')?.checked">Zone</th>
          <th v-if="columns.find((c) => c.col == 'Pollutant')?.checked">Pollutant</th>
          <th v-if="columns.find((c) => c.col == 'Object Type')?.checked">Object Type</th>
          <th v-if="columns.find((c) => c.col == 'Reporting Metric')?.checked">Reporting Metric</th>
          <th v-if="columns.find((c) => c.col == 'Protection Target')?.checked">Protection Target</th>
          <th v-if="columns.find((c) => c.col == 'Year')?.checked">Year</th>
          <th v-if="columns.find((c) => c.col == 'Report')?.checked">Threshold Classification Report</th>
          <th v-if="columns.find((c) => c.col == 'Exceedance')?.checked">Exceedance</th>
          <th v-if="columns.find((c) => c.col == 'Include')?.checked">Include</th>
        </tr>
        <tr v-for="row in cmp_assessmentregimes" @contextmenu.prevent="onContextMenu(row, $event)" @click="selected = {}" :class="cls_rowClass(row)">
          <td v-if="columns.find((c) => c.col == 'Id')?.checked">{{ row.id }}</td>
          <td v-if="columns.find((c) => c.col == 'Name')?.checked">{{ row.name }}</td>
          <td v-if="columns.find((c) => c.col == 'Zone')?.checked">{{ row.zone_name }}</td>
          <td v-if="columns.find((c) => c.col == 'Pollutant')?.checked">{{ row.pollutant_name }}</td>
          <td v-if="columns.find((c) => c.col == 'Object Type')?.checked">{{ row.objecttype }}</td>
          <td v-if="columns.find((c) => c.col == 'Reporting Metric')?.checked">{{ row.reportingmetric }}</td>
          <td v-if="columns.find((c) => c.col == 'Protection Target')?.checked">{{ row.protectiontarget }}</td>
          <td v-if="columns.find((c) => c.col == 'Year')?.checked">{{ row.thresholdclassificationyear }}</td>
          <td v-if="columns.find((c) => c.col == 'Report')?.checked">{{ row.thresholdclassificationreport }}</td>
          <td v-if="columns.find((c) => c.col == 'Exceedance')?.checked">{{ row.assessmentthresholdexceedance }}</td>
          <td v-if="columns.find((c) => c.col == 'Include')?.checked">{{ row.include }}</td>
        </tr>
      </table>
    </div>
  </common-layout>
</template>
