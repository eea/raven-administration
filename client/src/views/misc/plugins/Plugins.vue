<script setup>
import { onMounted, ref, computed } from "vue";
import CommonLayout from "../../../components/CommonLayout.vue";
import Popup from "../../../components/Popup.vue";
import Eventy from "../../../helpers/eventy";
import PluginService from "./service";

// Plugin modules from installed frontend plugins (build-time glob — dev mode / Docker Compose)
const pluginModules = import.meta.glob("../../../plugins/*/index.js", { eager: true });
const frontendPluginIds = computed(() => new Set([
  ...Object.values(pluginModules).map((m) => m.pluginId).filter(Boolean),
  ...Object.keys(window.__ravenPlugins || {}),
]));

const installed = ref([]);
const catalog = ref([]);
const configPlugin = ref(null);
const configData = ref({});
const showConfig = ref(false);
const restarting = ref(false);

onMounted(async () => {
  await refresh();
});

const refresh = async () => {
  installed.value = await PluginService.list();
  try {
    catalog.value = await PluginService.catalog();
  } catch {
    catalog.value = [];
  }
};

const anyRestartRequired = computed(() => installed.value.some((p) => p.restart_required));

// Compare two semver strings; returns true if a > b
const semverGt = (a, b) => {
  const parse = (v) => String(v ?? '0').split(/[-+]/)[0].split('.').map((n) => parseInt(n) || 0);
  const [av, bv] = [parse(a), parse(b)];
  for (let i = 0; i < 3; i++) {
    if ((av[i] ?? 0) > (bv[i] ?? 0)) return true;
    if ((av[i] ?? 0) < (bv[i] ?? 0)) return false;
  }
  return false;
};

// Map of plugin_id → catalog entry for installed plugins that have a newer version available
const updatable = computed(() => {
  const map = {};
  for (const p of installed.value) {
    const newer = catalog.value.find((c) => c.id === p.id && semverGt(c.version, p.version));
    if (newer) map[p.id] = newer;
  }
  return map;
});

// Catalog entries that are NOT yet installed
const available = computed(() => {
  const installedIds = new Set(installed.value.map((p) => p.id));
  return catalog.value.filter((c) => !installedIds.has(c.id));
});

const injectPluginScript = (pluginId) => new Promise((resolve) => {
  const s = document.createElement("script");
  s.src = `/api/plugins/${pluginId}/client.js?t=${Date.now()}`;
  s.onload = resolve;
  s.onerror = resolve; // non-fatal
  document.head.appendChild(s);
});

const toggle = async (plugin) => {
  Eventy.showMessage("Updating plugin...", "loading");
  if (plugin.enabled) {
    await PluginService.disable(plugin.id);
  } else {
    await PluginService.enable(plugin.id);
  }
  await refresh();
  Eventy.emit("plugins-updated");
  Eventy.showHideMessage("Plugin updated", "success", 3000);
};

const install = async (catalogEntry) => {
  Eventy.showMessage("Installing plugin, please wait...", "loading");
  const result = await PluginService.install({
    id: catalogEntry.id,
    name: catalogEntry.name,
    version: catalogEntry.version,
    description: catalogEntry.description,
    download_url: catalogEntry.download_url,
  });
  await refresh();
  Eventy.emit("plugins-updated");
  if (result?.restart_required) {
    Eventy.showHideMessage("Plugin installed. Restart the server to activate backend changes.", "success", 8000);
  } else {
    await injectPluginScript(catalogEntry.id);
    Eventy.showHideMessage("Plugin installed. Reload the page to activate it.", "success", 5000);
  }
};

const openConfig = async (plugin) => {
  configPlugin.value = plugin;
  configData.value = await PluginService.getConfig(plugin.id);
  showConfig.value = true;
};

const saveConfig = async () => {
  Eventy.showMessage("Saving config...", "loading");
  await PluginService.saveConfig(configPlugin.value.id, configData.value);
  showConfig.value = false;
  Eventy.showHideMessage("Config saved", "success", 3000);
};

const closeConfig = () => {
  showConfig.value = false;
  configPlugin.value = null;
  configData.value = {};
};

const restartServer = async () => {
  restarting.value = true;
  Eventy.showMessage("Restarting server, please wait…", "loading");
  try {
    await PluginService.restart();
    Eventy.showHideMessage("Server restarting. Page will reload shortly…", "success", 6000);
    // Wait a few seconds for the container to come back up, then reload
    setTimeout(() => window.location.reload(), 5000);
  } catch (err) {
    const msg = err?.response?.data?.description ?? err?.message ?? "Unknown error";
    Eventy.showHideMessage(msg, "error", 12000);
    restarting.value = false;
  }
};

const rebuild = async () => {
  window.location.reload();
};

const onImageField = (key, event) => {
  const file = event.target.files[0];
  if (!file) return;
  if (file.size > 100 * 1024) {
    Eventy.showHideMessage("Image too large. Please use an image under 100 KB.", "error", 5000);
    event.target.value = "";
    return;
  }
  const reader = new FileReader();
  reader.onload = (e) => { configData.value[key] = e.target.result; };
  reader.readAsDataURL(file);
};

// Get configSchema from runtime-loaded global registry, then fall back to build-time glob
const getConfigSchema = (pluginId) => {
  const runtime = window.__ravenPlugins?.[pluginId]?.configSchema;
  if (runtime) return runtime;
  const mod = Object.values(pluginModules).find((m) => m.pluginId === pluginId);
  return mod?.configSchema ?? [];
};
</script>

<template>
  <common-layout>
    <!-- Config Popup -->
    <popup :show="showConfig" :title="`Configure: ${configPlugin?.name}`" @on-close="closeConfig" class="max-w-xl w-full">
      <div v-if="getConfigSchema(configPlugin?.id).length > 0">
        <div class="mb-3" v-for="field in getConfigSchema(configPlugin?.id)" :key="field.key">
          <div class="font-bold mb-1">{{ field.label }}:</div>
          <input v-if="field.type === 'text'" type="text" class="input w-full" v-model="configData[field.key]" />
          <input v-else-if="field.type === 'number'" type="number" class="input w-full" v-model="configData[field.key]" />
          <div v-else-if="field.type === 'checkbox'" class="flex gap-2 cursor-pointer" @click="configData[field.key] = !configData[field.key]">
            <input type="checkbox" :checked="configData[field.key]" class="self-center" readonly />
            <span class="self-center text-sm text-nord3">{{ field.label }}</span>
          </div>
          <div v-else-if="field.type === 'image'" class="flex flex-col gap-2">
            <img v-if="configData[field.key]" :src="configData[field.key]" class="h-10 w-10 object-contain border border-nord4 rounded" />
            <input type="file" accept="image/*" class="input w-full" @change="onImageField(field.key, $event)" />
            <div class="text-xs text-nord3">Max 100 KB. Changes take effect after saving and reloading the page.</div>
            <button v-if="configData[field.key]" class="button text-xs self-start" @click="configData[field.key] = ''">Remove image</button>
          </div>
        </div>
      </div>
      <div v-else class="text-nord3 text-sm mb-4">
        This plugin has no configurable settings.
      </div>
      <div class="border-t border-gray-300 mt-4 pt-3 flex gap-3 justify-end">
        <button class="button" @click="saveConfig">Save</button>
        <button class="button" @click="closeConfig">Cancel</button>
      </div>
    </popup>

    <div class="p-4 flex flex-col gap-6 max-w-4xl">
      <div class="text-xl font-bold">Plugin Manager</div>

      <!-- Server restart required banner (backend plugin installed) -->
      <div v-if="anyRestartRequired" class="border border-nord13 bg-nord13/10 rounded p-3 flex gap-4 items-center">
        <div class="text-nord13 font-bold text-xl shrink-0">⚠</div>
        <div class="flex-1">
          <div class="font-bold">Server restart required</div>
          <div class="text-sm text-nord3">
            A plugin with backend code was installed. The server must restart to register the new API endpoints.
            In Kubernetes, run: <code class="bg-nord6 px-1 rounded">kubectl rollout restart deployment/raven-api</code>
          </div>
        </div>
        <button class="button shrink-0" :disabled="restarting" @click="restartServer" title="Docker deployments only">
          <span v-if="restarting">⏳ Restarting…</span>
          <span v-else>🔄 Restart Server</span>
        </button>
      </div>

      <!-- Installed plugins -->
      <div>
        <div class="font-bold text-lg border-b border-nord4 mb-3">Installed</div>
        <div v-if="installed.length === 0" class="text-nord3 text-sm">No plugins installed.</div>
        <div class="flex flex-col gap-3">
          <div v-for="plugin in installed" :key="plugin.id"
               class="border border-nord4 rounded p-4 flex gap-4 items-start bg-white">
            <div class="flex-1">
              <div class="flex items-center gap-2">
                <div class="font-bold">{{ plugin.name }}</div>
                <div class="text-xs text-nord3 bg-nord5 px-2 py-0.5 rounded">v{{ plugin.version }}</div>
                <div v-if="plugin.restart_required" class="text-xs text-nord13 bg-nord13/10 px-2 py-0.5 rounded font-bold">restart required</div>
                <div v-if="!frontendPluginIds.has(plugin.id)" class="text-xs text-nord9 bg-nord9/10 px-2 py-0.5 rounded">backend only</div>
                <div v-if="updatable[plugin.id]" class="text-xs text-nord14 bg-nord14/10 px-2 py-0.5 rounded font-bold">update available</div>
              </div>
              <div class="text-sm text-nord3 mt-1">{{ plugin.description }}</div>
            </div>
            <div class="flex gap-2 items-center shrink-0">
              <button class="button text-sm" @click="openConfig(plugin)" title="Configure">⚙️ Config</button>
              <button v-if="updatable[plugin.id]" class="button text-sm"
                      @click="install(updatable[plugin.id])" :title="`Update to v${updatable[plugin.id].version}`">
                🆙 v{{ updatable[plugin.id].version }}
              </button>
              <div class="flex items-center gap-2 cursor-pointer" @click="toggle(plugin)">
                <div class="text-sm">{{ plugin.enabled ? 'Enabled' : 'Disabled' }}</div>
                <div :class="['w-10 h-5 rounded-full transition-colors', plugin.enabled ? 'bg-nord14' : 'bg-nord4']" class="relative">
                  <div :class="['absolute top-0.5 w-4 h-4 bg-white rounded-full shadow transition-transform', plugin.enabled ? 'translate-x-5' : 'translate-x-0.5']"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Available from catalog -->
      <div>
        <div class="font-bold text-lg border-b border-nord4 mb-3">Available</div>
        <div v-if="catalog.length === 0 && available.length === 0" class="text-nord3 text-sm">Could not reach plugin registry, or no plugins available.</div>
        <div v-else-if="available.length === 0" class="text-nord3 text-sm">All available plugins are already installed.</div>
        <div class="flex flex-col gap-3">
          <div v-for="entry in available" :key="entry.id"
               class="border border-nord4 rounded p-4 flex gap-4 items-start bg-white">
            <div class="flex-1">
              <div class="flex items-center gap-2">
                <div class="font-bold">{{ entry.name }}</div>
                <div class="text-xs text-nord3 bg-nord5 px-2 py-0.5 rounded">v{{ entry.version }}</div>
              </div>
              <div class="text-sm text-nord3 mt-1">{{ entry.description }}</div>
            </div>
            <button class="button text-sm shrink-0" @click="install(entry)">⬇️ Install</button>
          </div>
        </div>
      </div>
    </div>
  </common-layout>
</template>
