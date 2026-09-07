<script setup>
import { computed, onMounted, ref } from "vue";
import Eventy from "../../../helpers/eventy";
import Service from "./service";
import IconAdd from "~icons/material-symbols/add";
import IconEdit from "~icons/material-symbols/edit-outline";
import IconDelete from "~icons/material-symbols/delete-outline";

// Its own page rather than the generic Manager: the primary key is
// (id, authority_role_id, email), and Manager's delete addresses rows by a single
// `id` while its update posts only the edited values, so the original key would be
// unrecoverable the moment a key column changed.

const rows = ref([]);
const lookups = ref({ instances: [], objects: [], statuses: [] });
const loading = ref(false);
const saving = ref(false);

// null = form closed; {} = adding; otherwise the key being edited.
const editing = ref(null);
const form = ref({});

const BLANK = {
  id: null,
  authority_role_id: null,
  email: null,
  authority_name: null,
  person_name: null,
  authority_url: null,
  authority_address: null,
  authority_instance_id: null,
  authority_status_id: null,
};

const KEY = ["id", "authority_role_id", "email"];

const isNew = computed(() => editing.value !== null && !editing.value.id);
const canSave = computed(
  () => !!form.value.id && !!form.value.authority_role_id && !!form.value.email
        && !!form.value.authority_name
);

const load = async () => {
  loading.value = true;
  try {
    const [data, lk] = await Promise.all([Service.get(), Service.lookups()]);
    rows.value = data;
    lookups.value = lk;
  } catch {
    Eventy.showHideMessage("Failed to load authorities.", "error", 4000);
  } finally {
    loading.value = false;
  }
};

const openAdd = () => {
  form.value = { ...BLANK };
  editing.value = {};
};

const openEdit = (row) => {
  form.value = Object.fromEntries(Object.keys(BLANK).map((k) => [k, row[k] ?? null]));
  editing.value = Object.fromEntries(KEY.map((k) => [k, row[k]]));
};

const onSave = async () => {
  if (!canSave.value) return;
  saving.value = true;
  try {
    if (isNew.value) {
      await Service.insert(form.value);
    } else {
      await Service.update(editing.value, form.value);
    }
    editing.value = null;
    await load();
    Eventy.showHideMessage("Authority saved.", "success", 3000);
  } catch {
    // Request already surfaced the server message (key clash, FK, validation).
  } finally {
    saving.value = false;
  }
};

const onDelete = async (row) => {
  if (!confirm(`Delete ${row.authority_name} as ${row.authority_role_id} for ${row.id}?`)) {
    return;
  }
  try {
    await Service.delete(Object.fromEntries(KEY.map((k) => [k, row[k]])));
    await load();
    Eventy.showHideMessage("Authority deleted.", "success", 3000);
  } catch {
    /* message already shown */
  }
};

onMounted(load);
</script>

<template>
  <div class="p-4">
    <div class="flex items-center justify-between mb-2">
      <h1 class="text-lg font-semibold">Authorities</h1>
      <button v-if="!editing" class="button" @click="openAdd">
        <span class="flex items-center gap-1.5"><icon-add class="text-base" /> Add authority</span>
      </button>
    </div>

    <p class="text-xs text-nord3 mb-4 max-w-3xl">
      The bodies responsible for air quality reporting and assessment, and what each is
      responsible for (AQR3 AUT). A row is identified by the instance it applies to, its role
      and its email — all three together — so one instance can carry several authorities: a
      country reports both the authority that submits and, separately, its national reference
      laboratory. CountryCode is the fourth key attribute and comes from Settings, not from
      here.
    </p>

    <div v-if="editing" class="mb-4 p-3 border border-nord4 rounded bg-white max-w-3xl">
      <p class="text-[11px] text-nord3 mb-3">
        Instance id, role and email are the primary key. Changing any of them on an existing
        row moves that row; it does not create a second one.
      </p>
      <div class="grid grid-cols-2 gap-3 mb-3">
        <div>
          <label class="block text-xs font-semibold text-nord3 mb-1">
            Instance id <span class="text-nord11">*</span>
          </label>
          <input v-model="form.id" class="input w-full text-sm"
                 placeholder="a country code, NUTS code, zone id or network id" />
          <p class="text-[11px] text-nord3 mt-0.5">
            AUT_02 — cross-checked against ARZ, STA, SPO or MOD depending on the instance
          </p>
        </div>
        <div>
          <label class="block text-xs font-semibold text-nord3 mb-1">
            Instance <span class="text-nord11">*</span>
          </label>
          <select v-model="form.authority_instance_id" class="input w-full text-sm">
            <option :value="null">— select —</option>
            <option v-for="o in lookups.instances" :key="o.value" :value="o.value">
              {{ o.label }}
            </option>
          </select>
          <p class="text-[11px] text-nord3 mt-0.5">AUT_05 — what kind of id the above is</p>
        </div>
        <div>
          <label class="block text-xs font-semibold text-nord3 mb-1">
            Role <span class="text-nord11">*</span>
          </label>
          <select v-model="form.authority_role_id" class="input w-full text-sm">
            <option :value="null">— select —</option>
            <option v-for="o in lookups.objects" :key="o.value" :value="o.value">
              {{ o.label }}
            </option>
          </select>
        </div>
        <div>
          <label class="block text-xs font-semibold text-nord3 mb-1">
            Email <span class="text-nord11">*</span>
          </label>
          <input v-model="form.email" class="input w-full text-sm" placeholder="contact email" />
          <p class="text-[11px] text-nord3 mt-0.5">
            Part of the key — it is what separates two organisations holding the same role
          </p>
        </div>
        <div>
          <label class="block text-xs font-semibold text-nord3 mb-1">
            Organisation <span class="text-nord11">*</span>
          </label>
          <input v-model="form.authority_name" class="input w-full text-sm"
                 placeholder="name of the institute or organisation" />
        </div>
        <div>
          <label class="block text-xs font-semibold text-nord3 mb-1">Person</label>
          <input v-model="form.person_name" class="input w-full text-sm"
                 placeholder="contact person" />
        </div>
        <div>
          <label class="block text-xs font-semibold text-nord3 mb-1">URL</label>
          <input v-model="form.authority_url" class="input w-full text-sm"
                 placeholder="website" />
        </div>
        <div>
          <label class="block text-xs font-semibold text-nord3 mb-1">Address</label>
          <input v-model="form.authority_address" class="input w-full text-sm"
                 placeholder="physical address" />
        </div>
        <div>
          <label class="block text-xs font-semibold text-nord3 mb-1">Status</label>
          <select v-model="form.authority_status_id" class="input w-full text-sm">
            <option :value="null">— none —</option>
            <option v-for="o in lookups.statuses" :key="o.value" :value="o.value">
              {{ o.label }}
            </option>
          </select>
        </div>
      </div>
      <div class="flex justify-end pt-2 gap-4">
        <button class="button" :disabled="saving || !canSave" @click="onSave">
          {{ saving ? "Saving…" : "Save" }}
        </button>
        <button class="button" @click="editing = null">Cancel</button>
      </div>
    </div>

    <div v-if="loading" class="text-nord3 text-sm py-4">Loading…</div>
    <div v-else-if="rows.length === 0" class="text-nord3 text-sm py-4">
      No authorities recorded.
    </div>
    <div v-else class="overflow-x-auto">
      <table class="table w-full text-sm">
        <thead>
          <tr>
            <th>Instance id</th>
            <th>Instance</th>
            <th>Role</th>
            <th>Email</th>
            <th>Organisation</th>
            <th>Person</th>
            <th>Status</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in rows" :key="`${r.id}|${r.authority_role_id}|${r.email}`">
            <td class="font-mono text-xs">{{ r.id }}</td>
            <td>{{ r.authority_instance ?? r.authority_instance_id ?? "—" }}</td>
            <td>{{ r.authority_role ?? r.authority_role_id }}</td>
            <td class="text-xs">{{ r.email }}</td>
            <td>{{ r.authority_name }}</td>
            <td class="text-xs">{{ r.person_name ?? "—" }}</td>
            <td>{{ r.authority_status ?? "—" }}</td>
            <td class="whitespace-nowrap">
              <button class="text-nord10 hover:text-nord9 mr-2" title="Edit" @click="openEdit(r)">
                <icon-edit class="text-base" />
              </button>
              <button class="text-nord11 hover:opacity-70" title="Delete" @click="onDelete(r)">
                <icon-delete class="text-base" />
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
