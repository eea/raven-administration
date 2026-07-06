<script setup>
import { ref, watch } from "vue";
import Popup from "../Popup.vue";
import Confirm from "../Confirm.vue";
import Service from "./service";
import Eventy from "../../helpers/eventy";
import IconEdit from "~icons/mdi/pencil-outline";
import IconDelete from "~icons/mdi/delete-outline";
import IconCheck from "~icons/mdi/check";
import IconCancel from "~icons/mdi/close";
import IconChevronDown from "~icons/mdi/chevron-down";
import IconChevronRight from "~icons/mdi/chevron-right";

// View/rename/delete the current user's favorites. `timeseries` (the host
// view's sampling point list) is used to render a favorite's series as
// readable labels — without it only the series count is shown.
const props = defineProps({
  show: Boolean,
  timeseries: { type: Array, default: () => [] }
});

const emit = defineEmits(["on-close"]);

const favorites = ref([]);
const editingId = ref(null);
const editName = ref("");
const expandedId = ref(null);
const pendingDelete = ref(null);

const load = async () => {
  favorites.value = await Service.list();
};

watch(
  () => props.show,
  (v) => {
    if (v) {
      editingId.value = null;
      expandedId.value = null;
      pendingDelete.value = null;
      load();
    }
  }
);

const seriesLabels = (favorite) => {
  const ids = new Set((favorite.config?.seriesIds || []).map(String));
  return props.timeseries.filter((t) => ids.has(String(t.sampling_point_id))).map((t) => [t.station, t.pollutant, t.timestep].filter(Boolean).join(", "));
};

const startEdit = (favorite) => {
  editingId.value = favorite.id;
  editName.value = favorite.name;
};

const saveEdit = async (favorite) => {
  if (!editName.value.trim()) return;
  await Service.update({ id: favorite.id, name: editName.value.trim(), config: favorite.config });
  editingId.value = null;
  Eventy.showHideMessage("Favorite updated", "success", 3000);
  await load();
};

const onDelete = async () => {
  await Service.delete({ id: pendingDelete.value.id });
  pendingDelete.value = null;
  Eventy.showHideMessage("Favorite deleted", "success", 3000);
  await load();
};
</script>

<template>
  <Popup :show="show" title="Favorites" @on-close="emit('on-close')" class="w-[32rem]!">
    <div class="flex flex-col pt-1">
      <div v-if="!favorites.length" class="text-sm text-nord3 py-4 text-center select-none">No favorites yet — save one from the add/edit plot popup</div>

      <div v-for="f in favorites" :key="f.id" class="border-b border-nord6 last:border-b-0">
        <div class="flex items-center gap-2 py-2">
          <component :is="expandedId === f.id ? IconChevronDown : IconChevronRight" class="text-nord3 cursor-pointer shrink-0" @click="expandedId = expandedId === f.id ? null : f.id" />

          <template v-if="editingId === f.id">
            <input v-model="editName" class="input flex-1 py-0.5!" @keyup.enter="saveEdit(f)" @keyup.esc="editingId = null" />
            <icon-check class="text-nord14 cursor-pointer shrink-0" title="Save name" @click="saveEdit(f)" />
            <icon-cancel class="text-nord3 cursor-pointer shrink-0" title="Cancel" @click="editingId = null" />
          </template>

          <template v-else>
            <span class="flex-1 truncate text-sm font-medium">{{ f.name }}</span>
            <span class="text-xs text-nord3 shrink-0">{{ (f.config?.seriesIds || []).length }} series</span>
            <span class="text-xs text-nord3 shrink-0">{{ f.created }}</span>
            <icon-edit class="text-nord10 cursor-pointer shrink-0" title="Rename" @click="startEdit(f)" />
            <icon-delete class="text-nord11 cursor-pointer shrink-0" title="Delete" @click="pendingDelete = f" />
          </template>
        </div>

        <div v-if="expandedId === f.id" class="pl-8 pb-2 flex flex-col gap-0.5">
          <div v-for="(label, i) in seriesLabels(f)" :key="i" class="text-xs text-nord2">{{ label }}</div>
          <div v-if="!seriesLabels(f).length" class="text-xs text-nord3">No matching series found</div>
        </div>
      </div>
    </div>

    <Confirm :show="!!pendingDelete" title="Delete Favorite" :text="`Are you sure you want to delete '${pendingDelete?.name}'?`" @close="pendingDelete = null" @ok="onDelete" />
  </Popup>
</template>
