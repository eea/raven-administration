<script setup>
import LEdit from "./LEdit.vue";
import LAdd from "./LAdd.vue";

import Service from "./service";
import Eventy from "../../../helpers/eventy";
import { tblToCsv, compare, filterList } from "../../../helpers/utils";
import ToolBar from "../../../components/ToolBar.vue";

const q = ref("");
const authorities = ref([]);
const levels = ref([]);
const media = ref([]);
const timezones = ref([]);
const networks = ref([]);

const showEdit = ref(false);
const showAdd = ref(false);
const selected = ref({});
const ev = ref({});
const showContextmenu = ref(false);
const showConfirm = ref(false);

onMounted(async () => {
  authorities.value = await Service.authorities();
  levels.value = await Service.levels();
  media.value = await Service.media();
  timezones.value = await Service.timezones();
  await loadData();
});

const loadData = async () => {
  networks.value = await Service.get();
};

const cmp_networks = computed(() => filterList(q.value, networks.value));

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
  networks.value = await Service.get();
  Eventy.showHideMessage("Network saved", "success", 5000);
  close();
};

const saveAdd = async (o) => {
  await Service.insert(o);
  networks.value = await Service.get();
  Eventy.showHideMessage("Network saved", "success", 5000);
  close();
};

const saveDelete = async (o) => {
  showConfirm.value = false;
  await Service.delete(selected.value);
  await loadData();
  Eventy.showHideMessage("Network deleted", "success", 5000);
  close();
};

const onDownload = () => {
  tblToCsv("networksId", "networks");
};
</script>

<template>
  <common-layout>
    <confirm :show="showConfirm" title="Delete" text="Are you sure you want to delete network?" @close="close" @ok="saveDelete" />
    <contextmenu-crud :show="showContextmenu" :ev="ev" @click-outside="close" @on-edit="onEdit" @onDelete="onDelete" />

    <l-add :show="showAdd" @close="close" @save="saveAdd" :authorities="authorities" :levels="levels" :media="media" :timezones="timezones" />
    <l-edit :show="showEdit" @close="close" @save="saveEdit" :network="selected" :authorities="authorities" :levels="levels" :media="media" :timezones="timezones" />

    <tool-bar title="Networks" filter-text="Type to filter networks " v-model="q" @add-click="showAdd = true" @download-click="onDownload" />

    <div>
      <table id="networksId" class="n-table">
        <tr>
          <th>Id</th>
          <th>Name</th>
          <th>Media monitored</th>
          <th>Organisation level</th>
          <th>Authority</th>
          <th>Timezone</th>
          <th>Begin</th>
          <th>End</th>
        </tr>
        <tr v-for="row in cmp_networks" @contextmenu.prevent="onContextMenu(row, $event)" @click="selected = {}" :class="cls_rowClass(row)">
          <td>{{ row.id }}</td>
          <td>{{ row.name }}</td>
          <td>{{ row.media }}</td>
          <td>{{ row.organisationlevel }}</td>
          <td>{{ row.authority }}</td>
          <td>{{ row.timezone }}</td>
          <td>{{ row.begin_position }}</td>
          <td>{{ row.end_position }}</td>
        </tr>
      </table>
    </div>
  </common-layout>
</template>
