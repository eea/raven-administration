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
  await loadData();
});

const loadData = async () => {
  stations.value = await Service.get();
  columns.value = { id: "Id", name: "Name", begin_position: "Begin position", end_position: "End position", network: "Network", city: "City", national_station_code: "National Station Code", media_monitored_name: "Media", mobile: "Mobile", measurement_regime: "Measurement Regime", area_classification_name: "Area Classification", distance_junction: "Distance Junction", traffic_volume: "Traffic Volume", heavy_duty_fraction: "Heavy Duty Fraction", street_width: "Street Width", height_facades: "Height Facade", municipality: "Municipality", eoi_code: "Eoi Code" };
  columnsPicked.value = ["id", "name", "begin_position", "end_position", "network", "area_classification_name", "municipality", "eoi_code"];
  console.log("stations", stations.value);
  console.log("colums", columns.value);
  console.log("columnsPicked", columnsPicked.value);
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

const columnsChanged = (column) => {
  console.log("columnsChanged", column);
  if (columnsPicked.value.includes(column)) {
    columnsPicked.value = columnsPicked.value.filter((c) => c !== column);
  } else {
    columnsPicked.value.push(column);
  }
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

    <tool-bar title="stations" filter-text="Type to filter stations " v-model="q" @add-click="showAdd = true" @download-click="onDownload" :column-picker="columns" :columns-picked="columnsPicked" @columns-changed="columnsChanged" />

    <div>
      <table id="stationsId" class="n-table">
        <tr>
          <th v-if="columnsPicked.includes('id')">Id</th>
          <th v-if="columnsPicked.includes('name')">Name</th>
          <th v-if="columnsPicked.includes('begin_position')">Begin Position</th>
          <th v-if="columnsPicked.includes('end_position')">End Position</th>
          <th v-if="columnsPicked.includes('network')">Network</th>
          <th v-if="columnsPicked.includes('city')">City</th>
          <th v-if="columnsPicked.includes('national_station_code')">National Station Code</th>
          <th v-if="columnsPicked.includes('media_monitored_name')">Media Monitored</th>
          <th v-if="columnsPicked.includes('mobile')">Mobile</th>
          <th v-if="columnsPicked.includes('measurement_regime')">Measurement Regime</th>
          <th v-if="columnsPicked.includes('area_classification_name')">Area classification</th>
          <th v-if="columnsPicked.includes('distance_junction')">Distance Junction</th>
          <th v-if="columnsPicked.includes('traffic_volume')">Traffic Volume</th>
          <th v-if="columnsPicked.includes('heavy_duty_fraction')">Heavy Duty Fraction</th>
          <th v-if="columnsPicked.includes('street_width')">Street Width</th>
          <th v-if="columnsPicked.includes('height_facades')">Height Facades</th>
          <th v-if="columnsPicked.includes('municipality')">Municipality</th>
          <th v-if="columnsPicked.includes('eoi_code')">Eoi Code</th>
        </tr>
        <tr v-for="row in cmp_stations" @contextmenu.prevent="onContextMenu(row, $event)" @click="selected = {}" :class="cls_rowClass(row)">
          <td v-if="columnsPicked.includes('id')">{{ row.id }}</td>
          <td v-if="columnsPicked.includes('name')">{{ row.name }}</td>
          <td v-if="columnsPicked.includes('begin_position')">{{ row.begin_position }}</td>
          <td v-if="columnsPicked.includes('end_position')">{{ row.end_position }}</td>
          <td v-if="columnsPicked.includes('network')">{{ row.network }}</td>
          <td v-if="columnsPicked.includes('city')">{{ row.city }}</td>
          <td v-if="columnsPicked.includes('national_station_code')">{{ row.national_station_code }}</td>
          <td v-if="columnsPicked.includes('media_monitored_name')">{{ row.media_monitored_name }}</td>
          <td v-if="columnsPicked.includes('mobile')">{{ row.mobile }}</td>
          <td v-if="columnsPicked.includes('measurement_regime_name')">{{ row.measurement_regime_name }}</td>
          <td v-if="columnsPicked.includes('area_classification_name')">{{ row.area_classification_name }}</td>
          <td v-if="columnsPicked.includes('distance_junction')">{{ row.distance_junction }}</td>
          <td v-if="columnsPicked.includes('heavy_duty_fraction')">{{ row.heavy_duty_fraction }}</td>
          <td v-if="columnsPicked.includes('street_width')">{{ row.street_width }}</td>
          <td v-if="columnsPicked.includes('height_facades')">{{ row.height_facades }}</td>
          <td v-if="columnsPicked.includes('municipality')">{{ row.municipality }}</td>
          <td v-if="columnsPicked.includes('eoi_code')">{{ row.eoi_code }}</td>
        </tr>
      </table>
    </div>
  </common-layout>
</template>
