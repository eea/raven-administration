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
const measurement_regimes = ref([]);
const area_classifications = ref([]);
const stations = ref([]);
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
  columns.value = Columns;
  await loadData();
});

const loadData = async () => {
  stations.value = await Service.get();
};

const cmp_stations = computed(() => {
  var t = stations.value.filter((p) => {
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
  stations.value = await Service.get();
  Eventy.showHideMessage("Station saved", "success", 5000);
  close();
};

const saveAdd = async (o) => {
  await Service.insert(o);
  stations.value = await Service.get();
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
  tblToCsv("stationsId", "stations");
};
</script>

<template>
  <common-layout>
    <confirm :show="showConfirm" title="Delete" text="Are you sure you want to delete station?" @close="close" @ok="saveDelete" />
    <contextmenu-crud :show="showContextmenu" :ev="ev" @click-outside="close" @on-edit="onEdit" @onDelete="onDelete" />

    <l-edit :show="showAdd" @close="close" @save="saveAdd" :station="selected" :media="media" :networks="networks" :measurement_regimes="measurement_regimes" :area_classifications="area_classifications" />
    <l-edit :show="showEdit" @close="close" @save="saveEdit" :station="selected" :media="media" :networks="networks" :measurement_regimes="measurement_regimes" :area_classifications="area_classifications" />

    <tool-bar title="Stations" filter-text="Type to filter stations " v-model="q" @add-click="showAdd = true" @download-click="onDownload" :column-picker="columns" />

    <div>
      <table id="stationsId" class="n-table">
        <tr>
          <th v-if="columns.find((c) => c.col == 'Id')?.checked">Id</th>
          <th v-if="columns.find((c) => c.col == 'Name')?.checked">Name</th>
          <th v-if="columns.find((c) => c.col == 'Begin position')?.checked">Begin position</th>
          <th v-if="columns.find((c) => c.col == 'End position')?.checked">End position</th>
          <th v-if="columns.find((c) => c.col == 'Network')?.checked">Network</th>
          <th v-if="columns.find((c) => c.col == 'City')?.checked">City</th>
          <th v-if="columns.find((c) => c.col == 'National Station Code')?.checked">National Station Code</th>
          <th v-if="columns.find((c) => c.col == 'Media')?.checked">Media</th>
          <th v-if="columns.find((c) => c.col == 'Mobile')?.checked">Mobile</th>
          <th v-if="columns.find((c) => c.col == 'Measurement Regime')?.checked">Measurement Regime</th>
          <th v-if="columns.find((c) => c.col == 'Area Classification')?.checked">Area Classification</th>
          <th v-if="columns.find((c) => c.col == 'Distance Junction')?.checked">Distance Junction</th>
          <th v-if="columns.find((c) => c.col == 'Traffic Volume')?.checked">Traffic Volume</th>
          <th v-if="columns.find((c) => c.col == 'Heavy Duty Fraction')?.checked">Heavy Duty Fraction</th>
          <th v-if="columns.find((c) => c.col == 'Street Width')?.checked">Street Width</th>
          <th v-if="columns.find((c) => c.col == 'Height Facade')?.checked">Height Facade</th>
          <th v-if="columns.find((c) => c.col == 'Municipality')?.checked">Municipality</th>
          <th v-if="columns.find((c) => c.col == 'Eoi Code')?.checked">Eoi Code</th>
        </tr>
        <tr v-for="row in cmp_stations" @contextmenu.prevent="onContextMenu(row, $event)" @click="selected = {}" :class="cls_rowClass(row)">
          <td v-if="columns.find((c) => c.col == 'Id')?.checked">{{ row.id }}</td>
          <td v-if="columns.find((c) => c.col == 'Name')?.checked">{{ row.name }}</td>
          <td v-if="columns.find((c) => c.col == 'Begin position')?.checked">{{ row.begin_position }}</td>
          <td v-if="columns.find((c) => c.col == 'End position')?.checked">{{ row.end_position }}</td>
          <td v-if="columns.find((c) => c.col == 'Network')?.checked">{{ row.network }}</td>
          <td v-if="columns.find((c) => c.col == 'City')?.checked">{{ row.city }}</td>
          <td v-if="columns.find((c) => c.col == 'National Station Code')?.checked">{{ row.national_station_code }}</td>
          <td v-if="columns.find((c) => c.col == 'Media')?.checked">{{ row.media_monitored_name }}</td>
          <td v-if="columns.find((c) => c.col == 'Mobile')?.checked">{{ row.mobile }}</td>
          <td v-if="columns.find((c) => c.col == 'Measurement Regime')?.checked">{{ row.measurement_regime_name }}</td>
          <td v-if="columns.find((c) => c.col == 'Area Classification')?.checked">{{ row.area_classification_name }}</td>
          <td v-if="columns.find((c) => c.col == 'Distance Junction')?.checked">{{ row.distance_junction }}</td>
          <td v-if="columns.find((c) => c.col == 'Traffic Volume')?.checked">{{ row.traffic_volume }}</td>
          <td v-if="columns.find((c) => c.col == 'Heavy Duty Fraction')?.checked">{{ row.heavy_duty_fraction }}</td>
          <td v-if="columns.find((c) => c.col == 'Street Width')?.checked">{{ row.street_width }}</td>
          <td v-if="columns.find((c) => c.col == 'Height Facade')?.checked">{{ row.height_facades }}</td>
          <td v-if="columns.find((c) => c.col == 'Municipality')?.checked">{{ row.municipality }}</td>
          <td v-if="columns.find((c) => c.col == 'Eoi Code')?.checked">{{ row.eoi_code }}</td>
        </tr>
      </table>
    </div>
  </common-layout>
</template>
