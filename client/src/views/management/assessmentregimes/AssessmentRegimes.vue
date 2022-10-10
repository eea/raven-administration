<script setup>
import LEdit from "./LEdit.vue";

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
const columns = ref([]);
const columnsPicked = ref([]);

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
  await loadData();
});

// id: str
//     name: str
//     objecttype: str
//     reportingmetric: str
//     protectiontarget: str
//     assessmentthresholdexceedance: str
//     include: str
//     thresholdclassificationyear: str
//     thresholdclassificationreport: str
//     zoneid: str
//     zone_name: str
//     pollutant: str
//     pollutant_name: str
//     data: list

const loadData = async () => {
  assessmentRegimes.value = await Service.get();
  columns.value = { id: "Id", name: "Name", objecttype: "Object Type", reportingmetric: "Reporting Metric", protectiontarget: "Protection Target", assessmentthresholdexceedance: "Assessment Threshold Exceedance", include: "Include", thresholdclassificationyear: "Threshold Classification Year", thresholdclassificationreport: "Threshold Classification Report", zoneid: "Zone", pollutant: "Pollutant" };
  columnsPicked.value = ["id", "name", "objecttype", "reportingmetric", "protectiontarget", "assessmentthresholdexceedance", "include", "thresholdclassificationyear", "thresholdclassificationreport", "zoneid", "pollutant"];
  console.log("assessmentRegimes", assessmentRegimes.value);
  console.log("colums", columns.value);
  console.log("columnsPicked", columnsPicked.value);
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

const columnsChanged = (column) => {
  console.log("columnsChanged", column);
  if (columnsPicked.value.includes(column)) {
    columnsPicked.value = columnsPicked.value.filter((c) => c !== column);
  } else {
    columnsPicked.value.push(column);
  }
};

const onDownload = () => {
  tblToCsv("id", "assessmentRegimes");
};
</script>

<template>
  <common-layout>
    <confirm :show="showConfirm" title="Delete" text="Are you sure you want to delete the assessment regime?" @close="close" @ok="saveDelete" />
    <contextmenu-crud :show="showContextmenu" :ev="ev" @click-outside="close" @on-edit="onEdit" @onDelete="onDelete" />

    <l-edit :show="showAdd" @close="close" @save="saveAdd" :edit="false" :assessmentregime="selected" :zones="zones" :pollutants="pollutants" :assessmentTypes="assessmentTypes" />
    <l-edit :show="showEdit" @close="close" @save="saveEdit" :edit="true" :assessmentregime="selected" :zones="zones" :pollutants="pollutants" :assessmentTypes="assessmentTypes" />

    <tool-bar title="Assessment Regimes" filter-text="Type to filter Assessment Regimes" v-model="q" @add-click="showAdd = true" @download-click="onDownload" :column-picker="columns" :columns-picked="columnsPicked" @columns-changed="columnsChanged" />

    <div>
      <table id="assessmentRegimesId" class="n-table">
        <tr>
          <th v-if="columnsPicked.includes('id')">Id</th>
          <th v-if="columnsPicked.includes('name')">Name</th>
          <th v-if="columnsPicked.includes('objecttype')">Object Type</th>
          <th v-if="columnsPicked.includes('reportingmetric')">Reporting Metric</th>
          <th v-if="columnsPicked.includes('protectiontarget')">Protection Target</th>
          <th v-if="columnsPicked.includes('assessmentthresholdexceedance')">Assessment Threshold Exceedance</th>
          <th v-if="columnsPicked.includes('include')">Include</th>
          <th v-if="columnsPicked.includes('thresholdclassificationyear')">Threshold Classification Year</th>
          <th v-if="columnsPicked.includes('thresholdclassificationreport')">Threshold Classification Report</th>
          <th v-if="columnsPicked.includes('zoneid')">Zone</th>
          <th v-if="columnsPicked.includes('pollutant')">Pollutant</th>
        </tr>
        <tr v-for="row in cmp_assessmentregimes" @contextmenu.prevent="onContextMenu(row, $event)" @click="selected = {}" :class="cls_rowClass(row)">
          <td v-if="columnsPicked.includes('id')">{{ row.id }}</td>
          <td v-if="columnsPicked.includes('name')">{{ row.name }}</td>
          <td v-if="columnsPicked.includes('objecttype')">{{ row.objecttype }}</td>
          <td v-if="columnsPicked.includes('reportingmetric')">{{ row.reportingmetric }}</td>
          <td v-if="columnsPicked.includes('protectiontarget')">{{ row.protectiontarget }}</td>
          <td v-if="columnsPicked.includes('assessmentthresholdexceedance')">{{ row.assessmentthresholdexceedance }}</td>
          <td v-if="columnsPicked.includes('include')">{{ row.include }}</td>
          <td v-if="columnsPicked.includes('thresholdclassificationyear')">{{ row.thresholdclassificationyear }}</td>
          <td v-if="columnsPicked.includes('thresholdclassificationreport')">{{ row.thresholdclassificationreport }}</td>
          <td v-if="columnsPicked.includes('zoneid')">{{ row.zone_name }}</td>
          <td v-if="columnsPicked.includes('pollutant')">{{ row.pollutant_name }}</td>
        </tr>
      </table>
    </div>
  </common-layout>
</template>
