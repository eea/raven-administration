<script setup>
import { ref, computed, onMounted } from "vue";

import CommonLayout from "../../../components/CommonLayout.vue";
import ToolBar from "../../../components/ToolBar.vue";
import Confirm from "../../../components/Confirm.vue";
import DataTable from "../../../components/DataTable.vue";
import CMenuItems from "../../../components/CMenuItems.vue";
import Popup from "../../../components/Popup.vue";

import Service from "./service";
import Eventy from "../../../helpers/eventy";

const groups = ref([]);
const samplingpoints = ref([]);
const selectedGroup = ref(null);
const q = ref("");

const showGroupPopup = ref(false);
const showConfirmDeleteGroup = ref(false);

const isEdit = ref(false);
const selectedSpIds = ref([]);
const initialMemberIds = ref([]);
const popupStationId = ref("");

const groupColumns = [
  { field: "id", headerName: "Group ID", width: 120 },
  { field: "station", headerName: "Station", flex: 1, filter: true },
  { field: "members", headerName: "Members", flex: 2, filter: true }
];

const getGroupRowId = (params) => String(params.data.id);

onMounted(async () => {
  await loadGroups();
  samplingpoints.value = await Service.samplingpoints();
});

const loadGroups = async () => {
  groups.value = await Service.groups();
};

const refreshSamplingpoints = async (groupId = null) => {
  samplingpoints.value = await Service.samplingpoints(groupId);
};

const cmp_popup_stations = computed(() => {
  const seen = new Set();
  const stations = [];
  for (const sp of samplingpoints.value) {
    if (!seen.has(sp.station_id)) {
      seen.add(sp.station_id);
      stations.push({ id: sp.station_id, name: sp.label.split(", ")[0] });
    }
  }
  return stations.sort((a, b) => a.name.localeCompare(b.name));
});

const cmp_popup_available_sps = computed(() => {
  if (!popupStationId.value) return [];
  return samplingpoints.value.filter((sp) => sp.station_id === popupStationId.value);
});

const spDisplayLabel = (sp) => sp.label.split(", ").slice(1).join(", ");

const confirmDeleteGroupText = computed(() => {
  if (!selectedGroup.value) return "";
  const count = Number(selectedGroup.value.member_count);
  if (count === 0) return "Are you sure you want to delete this group?";
  return `This will ungroup <strong>${count}</strong> sampling point${count === 1 ? "" : "s"}. Are you sure?`;
});

const onShowAdd = () => {
  isEdit.value = false;
  selectedSpIds.value = [];
  initialMemberIds.value = [];
  popupStationId.value = "";
  showGroupPopup.value = true;
};

const onOpenEdit = async (group) => {
  selectedGroup.value = group;
  isEdit.value = true;
  samplingpoints.value = await Service.samplingpoints(group.id);
  const currentMembers = await Service.members(group.id);
  const memberIds = currentMembers.map((m) => m.id);
  initialMemberIds.value = memberIds;
  selectedSpIds.value = [...memberIds];
  popupStationId.value = currentMembers.length ? currentMembers[0].station_id : "";
  showGroupPopup.value = true;
};

const onSaveGroup = async () => {
  if (isEdit.value) {
    const groupId = selectedGroup.value.id;
    const initial = new Set(initialMemberIds.value);
    const current = new Set(selectedSpIds.value);
    const toAdd = selectedSpIds.value.filter((id) => !initial.has(id));
    const toRemove = initialMemberIds.value.filter((id) => !current.has(id));
    for (const id of toAdd) await Service.addMember(groupId, { sampling_point_id: id });
    for (const id of toRemove) await Service.removeMember(groupId, { sampling_point_id: id });
    Eventy.showHideMessage("Group updated", "success", 3000);
    await Promise.all([loadGroups(), refreshSamplingpoints()]);
  } else {
    await Service.create({ sampling_point_ids: selectedSpIds.value });
    Eventy.showHideMessage("Group created", "success", 3000);
    await Promise.all([loadGroups(), refreshSamplingpoints()]);
  }
  showGroupPopup.value = false;
};

const onGroupContextMenuAction = ({ action, data }) => {
  if (data?.row) selectedGroup.value = data.row;
  if (action === "edit") {
    onOpenEdit(selectedGroup.value);
  } else if (action === "delete") {
    showConfirmDeleteGroup.value = true;
  }
};

const onGroupDoubleClick = (row) => {
  onOpenEdit(row);
};

const onDeleteGroup = async () => {
  await Service.delete({ id: selectedGroup.value.id });
  Eventy.showHideMessage("Group deleted", "success", 3000);
  showConfirmDeleteGroup.value = false;
  selectedGroup.value = null;
  await loadGroups();
};

const onPopupStationChange = () => {
  selectedSpIds.value = [];
};
</script>

<template>
  <common-layout>
    <confirm
      :show="showConfirmDeleteGroup"
      title="Delete group"
      :text="confirmDeleteGroupText"
      @close="showConfirmDeleteGroup = false"
      @ok="onDeleteGroup"
    />

    <popup :show="showGroupPopup" :title="isEdit ? 'Edit group' : 'New group'" @on-close="showGroupPopup = false">
      <div class="flex flex-col gap-5 min-w-[42rem]">

        <div class="flex flex-col gap-1">
          <label class="label">Station</label>
          <select class="select w-full" v-model="popupStationId" @change="onPopupStationChange" :disabled="isEdit">
            <option value="">Select station</option>
            <option v-for="st in cmp_popup_stations" :key="st.id" :value="st.id">{{ st.name }}</option>
          </select>
        </div>

        <div class="flex flex-col gap-1">
          <div class="flex items-center justify-between">
            <label class="label">Members</label>
            <span v-if="selectedSpIds.length" class="text-sm text-nord10 font-medium">{{ selectedSpIds.length }} selected</span>
          </div>
          <div class="border border-nord4 rounded-lg overflow-y-auto h-56" :class="!popupStationId ? 'opacity-40 pointer-events-none' : ''">
            <template v-if="cmp_popup_available_sps.length">
              <label
                v-for="sp in cmp_popup_available_sps"
                :key="sp.value"
                class="flex items-center gap-3 px-4 py-2.5 hover:bg-nord6 cursor-pointer select-none border-b border-nord5 last:border-b-0"
              >
                <input type="checkbox" :value="sp.value" v-model="selectedSpIds" class="w-4 h-4 accent-nord10 flex-shrink-0" />
                <span class="text-sm">{{ spDisplayLabel(sp) }}</span>
              </label>
            </template>
            <div v-else-if="popupStationId" class="px-4 py-5 text-sm text-nord3 text-center">
              No sampling points available for this station
            </div>
            <div v-else class="px-4 py-5 text-sm text-nord3 text-center">
              Select a station to see sampling points
            </div>
          </div>
        </div>

        <div class="flex justify-end gap-2 pt-1 border-t border-nord5">
          <button class="button" @click="onSaveGroup">Save</button>
          <button class="button" @click="showGroupPopup = false">Cancel</button>
        </div>
      </div>
    </popup>

    <tool-bar
      title="Groups"
      :show-download="false"
      :q="q"
      @update:q="q = $event"
      @add-click="onShowAdd"
    />

    <DataTable
      :columns="groupColumns"
      :data="groups"
      :search-word="q"
      :filter="false"
      :get-row-id="getGroupRowId"
      @context-menu-action="onGroupContextMenuAction"
      @on-double-click="onGroupDoubleClick"
    >
      <template #context-menu-items="{ handleAction }">
        <CMenuItems @edit="handleAction('edit')" @delete="handleAction('delete')" />
      </template>
    </DataTable>

  </common-layout>
</template>
