<script setup>
import LEdit from "./LEdit.vue";

import Service from "./service";
import ManagementService from "../managementservice";
import Eventy from "../../../helpers/eventy";
import { tblToCsv, compare } from "../../../helpers/utils";
import ToolBar from "../../../components/ToolBar.vue";
import Columns from "./columns";

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
  columns.value = Columns;

  await loadData();
});

const loadData = async () => {
  observing_capabilities.value = await Service.get();
  console.log("observing_capabilities", observing_capabilities.value);
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

    <tool-bar title="Observing Capabilities" filter-text="Type to filter" v-model="q" @add-click="showAdd = true" @download-click="onDownload" :column-picker="columns" />

    <div>
      <table id="observing_capabilitiesId" class="n-table">
        <tr>
          <th v-if="columns.find((c) => c.col == 'Id')?.checked">Id</th>
          <th v-if="columns.find((c) => c.col == 'Begin position')?.checked">Begin position</th>
          <th v-if="columns.find((c) => c.col == 'End position')?.checked">End position</th>
          <th v-if="columns.find((c) => c.col == 'Process type')?.checked">Process type</th>
          <th v-if="columns.find((c) => c.col == 'Result nature')?.checked">Result nature</th>
          <th v-if="columns.find((c) => c.col == 'Sampling point')?.checked">Sampling point</th>
          <th v-if="columns.find((c) => c.col == 'Process')?.checked">Process</th>
          <th v-if="columns.find((c) => c.col == 'Sample')?.checked">Sample</th>
        </tr>
        <tr v-for="row in cmp_observing_capabilities" @contextmenu.prevent="onContextMenu(row, $event)" @click="selected = {}" :class="cls_rowClass(row)">
          <td v-if="columns.find((c) => c.col == 'Id')?.checked">{{ row.id }}</td>
          <td v-if="columns.find((c) => c.col == 'Begin position')?.checked">{{ row.begin_position }}</td>
          <td v-if="columns.find((c) => c.col == 'End position')?.checked">{{ row.end_position }}</td>
          <td v-if="columns.find((c) => c.col == 'Process type')?.checked">{{ row.process_type_name }}</td>
          <td v-if="columns.find((c) => c.col == 'Result nature')?.checked">{{ row.result_nature_name }}</td>
          <td v-if="columns.find((c) => c.col == 'Sampling point')?.checked">{{ row.sampling_point_id }}</td>
          <td v-if="columns.find((c) => c.col == 'Process')?.checked">{{ row.process_id }}</td>
          <td v-if="columns.find((c) => c.col == 'Sample')?.checked">{{ row.sample_id }}</td>
        </tr>
      </table>
    </div>
  </common-layout>
</template>
