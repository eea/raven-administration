<script setup>
import LEdit from "./LEdit.vue";

import Service from "./service";
import ManagementService from "../managementservice";
import Eventy from "../../../helpers/eventy";
import { tblToCsv, compare } from "../../../helpers/utils";
import ToolBar from "../../../components/ToolBar.vue";

const q = ref("");
const samplingpoints = ref([]);
const result_nature_values = ref([]);
const processtype_values = ref([]);
const samples = ref([]);
const processes = ref([]);

const observing_capabilities = ref([]);
const columns = ref([]);
const columnsPicked = ref([]);

const showEdit = ref(false);
const showAdd = ref(false);
const selected = ref({});
const ev = ref({});
const showContextmenu = ref(false);
const showConfirm = ref(false);

onMounted(async () => {
  samplingpoints.value = await ManagementService.samplingpoints();
  result_nature_values.value = await ManagementService.result_nature_values();
  processtype_values.value = await ManagementService.processtype_values();
  samples.value = await ManagementService.samples();
  processes.value = await ManagementService.processes();

  await loadData();
});

const loadData = async () => {
  observing_capabilities.value = await Service.get();
  //  oc.id,
  //     oc.begin_position,
  //     oc.end_position,
  //     oc.process_type,
  //     oc.result_nature,
  //     oc.sampling_point_id,
  //     oc.process_id,
  //     oc.sample_id,
  //     ptv.label as process_type_name,
  //     rnv.label as result_nature_name
  columns.value = { id: "Id", begin_position: "Begin position", end_position: "End position", process_type: "Process type", result_nature: "Result nature", sampling_point_id: "Sampling point", process_id: "Process", sample_id: "Sample" };
  columnsPicked.value = ["id", "begin_position", "end_position", "process_type", "result_nature", "sampling_point_id", "process_id", "sample_id", "process_type_name", "result_nature_name"];
  console.log("observing_capabilities", observing_capabilities.value);
  console.log("colums", columns.value);
  console.log("columnsPicked", columnsPicked.value);
};

const cmp_observing_capabilities = computed(() => {
  var t = observing_capabilities.value.filter((p) => {
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
  observing_capabilities.value = await Service.get();
  Eventy.showHideMessage("Station saved", "success", 5000);
  close();
};

const saveAdd = async (o) => {
  await Service.insert(o);
  observing_capabilities.value = await Service.get();
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
  tblToCsv("id", "observing_capabilities");
};
</script>

<template>
  <common-layout>
    <confirm :show="showConfirm" title="Delete" text="Are you sure you want to delete the observing_capability?" @close="close" @ok="saveDelete" />
    <contextmenu-crud :show="showContextmenu" :ev="ev" @click-outside="close" @on-edit="onEdit" @onDelete="onDelete" />

    <l-edit :show="showAdd" @close="close" @save="saveAdd" :observingcapability="selected" :result_nature_values="result_nature_values" :processtype_values="processtype_values" :samples="samples" :processes="processes" :samplingpoints="samplingpoints" />
    <l-edit :show="showEdit" @close="close" @save="saveEdit" :observingcapability="selected" :result_nature_values="result_nature_values" :processtype_values="processtype_values" :samples="samples" :processes="processes" :samplingpoints="samplingpoints" />

    <tool-bar title="observing_capabilities" filter-text="Type to filter observing_capabilities " v-model="q" @add-click="showAdd = true" @download-click="onDownload" :column-picker="columns" :columns-picked="columnsPicked" @columns-changed="columnsChanged" />

    <div>
      <table id="observing_capabilitiesId" class="n-table">
        <tr>
          <th v-if="columnsPicked.includes('id')">Id</th>
          <th v-if="columnsPicked.includes('begin_position')">Begin Position</th>
          <th v-if="columnsPicked.includes('end_position')">End Position</th>
          <th v-if="columnsPicked.includes('process_type')">Process Type</th>
          <th v-if="columnsPicked.includes('result_nature')">Result Nature</th>
          <th v-if="columnsPicked.includes('sampling_point_id')">Sampling Point Id</th>
          <th v-if="columnsPicked.includes('process_id')">Process Id</th>
          <th v-if="columnsPicked.includes('sample_id')">Sample Id</th>
        </tr>
        <tr v-for="row in cmp_observing_capabilities" @contextmenu.prevent="onContextMenu(row, $event)" @click="selected = {}" :class="cls_rowClass(row)">
          <td v-if="columnsPicked.includes('id')">{{ row.id }}</td>
          <td v-if="columnsPicked.includes('begin_position')">{{ row.begin_position }}</td>
          <td v-if="columnsPicked.includes('end_position')">{{ row.end_position }}</td>
          <td v-if="columnsPicked.includes('process_type')">{{ row.process_type_name }}</td>
          <td v-if="columnsPicked.includes('result_nature')">{{ row.result_nature_name }}</td>
          <td v-if="columnsPicked.includes('sampling_point_id')">{{ row.sampling_point_id }}</td>
          <td v-if="columnsPicked.includes('process_id')">{{ row.process_id }}</td>
          <td v-if="columnsPicked.includes('sample_id')">{{ row.sample_id }}</td>
        </tr>
      </table>
    </div>
  </common-layout>
</template>
