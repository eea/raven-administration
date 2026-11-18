/**
 * Navigation model shared by the sidebar (MenuBar.vue), the header breadcrumb
 * (TopBar.vue) and the quick-jump palette (NavPalette.vue).
 *
 * The group/item list and its permission gating are unchanged from the old
 * MenuBar.vue; only icons were added. Plugins keep contributing groups exactly
 * as before ({ group, show, items: [{ name, comp, show }] }); a plugin item may
 * optionally carry `icon` (an iconify-style component) and otherwise gets the
 * group's or a generic icon.
 */
import { ref, reactive, computed, markRaw } from "vue";
import { jwtDecode } from "jwt-decode";
import Auth from "../helpers/auth";
import Version from "../helpers/version";
import Eventy from "../helpers/eventy";
import { Get } from "../helpers/request";
import { runtimePlugins } from "../helpers/runtime-plugins";

// ── icons ─────────────────────────────────────────────────────────────────
import IGManagement from "~icons/tabler/building-broadcast-tower";
import IGData from "~icons/tabler/chart-area-line";
import IGImport from "~icons/tabler/transform";
import IGQuality from "~icons/tabler/shield-check";
import IGMisc from "~icons/tabler/settings";
import IGAccess from "~icons/tabler/users-group";
import IGPlugin from "~icons/tabler/puzzle";
import IPoint from "~icons/tabler/point";

import IDocuments from "~icons/tabler/file-text";
import IAuthorities from "~icons/tabler/building-bank";
import IZones from "~icons/tabler/map-2";
import INetworks from "~icons/tabler/topology-star-3";
import IStations from "~icons/tabler/building-broadcast-tower";
import ISamplingPoints from "~icons/tabler/map-pin";
import IProcesses from "~icons/tabler/flask";
import IRegimes from "~icons/tabler/clipboard-check";
import IAssessmentData from "~icons/tabler/database";
import ISR from "~icons/tabler/radar-2";
import IModels from "~icons/tabler/cpu";
import IPLA from "~icons/tabler/adjustments-horizontal";
import ICAM from "~icons/tabler/scale";
import IDashboard from "~icons/tabler/layout-dashboard";
import ILatest from "~icons/tabler/clock-bolt";
import IHistorical from "~icons/tabler/chart-line";
import IDataflow from "~icons/tabler/cloud-upload";
import IStatistics from "~icons/tabler/chart-bar";
import IExceedances from "~icons/tabler/alert-triangle";
import IMap from "~icons/tabler/map";
import IRNotebook from "~icons/tabler/notebook";
import IImport from "~icons/tabler/file-import";
import IAutoValidate from "~icons/tabler/wand";
import IConvert from "~icons/tabler/arrows-exchange";
import ICalculate from "~icons/tabler/math-function";
import IScale from "~icons/tabler/ruler-measure";
import ISPGroups from "~icons/tabler/stack-2";
import IValidate from "~icons/tabler/checks";
import IVerify from "~icons/tabler/rosette-discount-check";
import ISettings from "~icons/tabler/settings";
import IPreAgg from "~icons/tabler/stack-push";
import IAqi from "~icons/tabler/wind";
import INotifications from "~icons/tabler/bell";
import IPlugins from "~icons/tabler/puzzle";
import IUpgrade from "~icons/tabler/rocket";
import IUsers from "~icons/tabler/user";
import IGroups from "~icons/tabler/users-group";

const GROUP_ICONS = {
  Management: IGManagement,
  Data: IGData,
  "Import process": IGImport,
  "Quality control": IGQuality,
  Misc: IGMisc,
  Access: IGAccess
};

const ITEM_ICONS = {
  Documents: IDocuments,
  Authorities: IAuthorities,
  Zones: IZones,
  Networks: INetworks,
  Stations: IStations,
  SamplingPoints: ISamplingPoints,
  Processes: IProcesses,
  AssessmentRegimes: IRegimes,
  AssessmentData: IAssessmentData,
  SpatialRepresentativeness: ISR,
  Models: IModels,
  PollutionLevelAdjustment: IPLA,
  ComplianceAssessmentMethod: ICAM,
  Dashboard: IDashboard,
  Latest: ILatest,
  Historical: IHistorical,
  Dataflow: IDataflow,
  Statistics: IStatistics,
  DataExceedances: IExceedances,
  Map: IMap,
  RNotebook: IRNotebook,
  Import: IImport,
  AutoValidate: IAutoValidate,
  Convert: IConvert,
  Calculate: ICalculate,
  Scale: IScale,
  SamplingPointGroups: ISPGroups,
  Validate: IValidate,
  Verify: IVerify,
  Settings: ISettings,
  PreAggregation: IPreAgg,
  Aqi: IAqi,
  Notifications: INotifications,
  PluginManager: IPlugins,
  FinishTheUpgrade: IUpgrade,
  Users: IUsers,
  Groups: IGroups
};

// Plugin modules – resolved at build time. Empty when no plugins installed.
const pluginModules = import.meta.glob("../plugins/*/index.js", { eager: true });

// ── shared state (module singletons) ──────────────────────────────────────
const modules = ref([]);
const version = ref({ current: "-", isLatest: true });
const pluginStatus = ref({});
const user = reactive({ name: "", initials: "" });
let initialised = false;

// A plugin may declare the group permission keys that gate it, via
// window.__ravenPlugins[id].groupPermissions (the same list the Groups editor
// renders as checkboxes). If it declares any and the user's JWT grants none of
// them, hide the plugin's menu groups. Plugins that declare none stay visible.
const isPluginPermitted = (pid, jwt) => {
  const declared = (window.__ravenPlugins?.[pid]?.groupPermissions ?? []).map((g) => g.key);
  if (!declared.length) return true;
  const pp = jwt.plugin_permissions ?? {};
  return declared.some((k) => pp[k]);
};

const readUser = (jwt) => {
  // `name` is a claim from get_claims(); `sub` is the username (JWT identity).
  const name = jwt.name || jwt.sub || "";
  user.name = typeof name === "string" ? name : "";
  user.initials =
    user.name
      .split(/[\s._@-]+/)
      .filter(Boolean)
      .slice(0, 2)
      .map((s) => s[0].toUpperCase())
      .join("") || "?";
};

const getmodules = () => {
  const token = sessionStorage.getItem("token");
  if (!token) return [];
  const jwt = jwtDecode(token);
  readUser(jwt);
  const rawModules = [
    {
      group: "Management",
      show: jwt.management,
      items: [
        { name: "Documents", comp: "Documents", show: jwt.management && jwt.allnetworks },
        { name: "Authorities", comp: "Authorities", show: jwt.management && jwt.allnetworks },
        { name: "Zones", comp: "Zones", show: jwt.management && jwt.allnetworks },
        { name: "Networks", comp: "Networks", show: jwt.management },
        { name: "Stations", comp: "Stations", show: jwt.management },
        { name: "Sampling Points", comp: "SamplingPoints", show: jwt.management },
        { name: "Sampling Processes", comp: "Processes", show: jwt.management },
        { name: "Assessment Regime Zones", comp: "AssessmentRegimes", show: jwt.management && jwt.allnetworks },
        { name: "Assessment Data", comp: "AssessmentData", show: jwt.management && jwt.allnetworks },
        { name: "Spatial Representativeness", comp: "SpatialRepresentativeness", show: jwt.management },
        { name: "Models / OBE", comp: "Models", show: jwt.management && jwt.allnetworks },
        { name: "Pollution Level Adjustments", comp: "PollutionLevelAdjustment", show: jwt.management && jwt.allnetworks },
        { name: "Compliance Assessment Method", comp: "ComplianceAssessmentMethod", show: jwt.management && jwt.allnetworks }
      ]
    },
    {
      group: "Data",
      show: jwt.data || jwt.exporting,
      items: [
        { name: "Dashboard", comp: "Dashboard", show: jwt.data },
        { name: "Latest data", comp: "Latest", show: jwt.data },
        { name: "Historical data", comp: "Historical", show: jwt.data },
        { name: "Dataflow", comp: "Dataflow", show: jwt.exporting },
        { name: "Statistics", comp: "Statistics", show: jwt.data },
        { name: "Exceedances", comp: "DataExceedances", show: jwt.data },
        { name: "Map", comp: "Map", show: jwt.data },
        { name: "R Notebook", comp: "RNotebook", show: jwt.data }
      ]
    },
    {
      group: "Import process",
      show: jwt.processing,
      items: [
        { name: "Manual import", comp: "Import", show: jwt.processing && jwt.allnetworks },
        { name: "Auto validate", comp: "AutoValidate", show: jwt.processing },
        { name: "Convert", comp: "Convert", show: jwt.processing },
        { name: "Calculate", comp: "Calculate", show: jwt.processing },
        { name: "Scale", comp: "Scale", show: jwt.processing },
        { name: "Groups", comp: "SamplingPointGroups", show: jwt.processing }
      ]
    },
    {
      group: "Quality control",
      show: jwt.qualitycontrol,
      items: [
        { name: "Validate", comp: "Validate", show: jwt.qualitycontrol },
        { name: "Verify", comp: "Verify", show: jwt.qualitycontrol }
      ]
    },
    {
      group: "Misc",
      show: jwt.management && jwt.allnetworks,
      items: [
        { name: "Settings", comp: "Settings", show: jwt.management && jwt.allnetworks },
        { name: "Pre aggregation", comp: "PreAggregation", show: jwt.management && jwt.allnetworks },
        { name: "Local AQI", comp: "Aqi", show: jwt.management && jwt.allnetworks },
        { name: "Notifications", comp: "Notifications", show: jwt.management && jwt.allnetworks },
        { name: "Plugins", comp: "PluginManager", show: jwt.management && jwt.allnetworks },
        { name: "Finish the upgrade", comp: "FinishTheUpgrade", show: jwt.management && jwt.allnetworks }
      ]
    },
    {
      group: "Access",
      show: jwt.users,
      items: [
        { name: "Users", comp: "Users", show: jwt.users },
        { name: "Groups", comp: "Groups", show: jwt.users }
      ]
    },
    // Plugin-contributed menu groups (build-time)
    ...Object.values(pluginModules).flatMap((m) => {
      const pid = m.pluginId;
      const isEnabled = pid ? (pluginStatus.value[pid]?.enabled ?? true) : true;
      if (!isEnabled || (pid && !isPluginPermitted(pid, jwt))) return [];
      return m.getMenuGroups?.(jwt) ?? m.menuGroups ?? [];
    }),
    // Plugin-contributed menu groups (runtime — registered via window.__ravenRuntime)
    // Dropping the groups entirely (rather than setting show: false) keeps them out
    // of the show-ORing merge below, which would otherwise reveal a core group
    // header — e.g. Management — to a user who lacks the core claim for it.
    ...Object.entries(runtimePlugins).flatMap(([pid, p]) => {
      const isEnabled = pluginStatus.value[pid]?.enabled ?? true;
      if (!isEnabled || !isPluginPermitted(pid, jwt)) return [];
      return p.menuGroups ?? [];
    })
  ];
  // Merge groups with the same name so runtime plugins can contribute items to
  // existing core groups (e.g. "Quality control") without causing Vue key collisions.
  const merged = [];
  const byGroup = {};
  for (const m of rawModules) {
    if (byGroup[m.group]) {
      byGroup[m.group].items = [...byGroup[m.group].items, ...m.items];
      byGroup[m.group].show = byGroup[m.group].show || m.show;
    } else {
      const copy = { ...m, items: [...m.items] };
      byGroup[m.group] = copy;
      merged.push(copy);
    }
  }
  // Decorate with icons (markRaw: components must not become reactive).
  for (const g of merged) {
    g.icon = markRaw(GROUP_ICONS[g.group] ?? IGPlugin);
    g.items = g.items.map((i) => ({ ...i, icon: markRaw(i.icon ?? ITEM_ICONS[i.comp] ?? IPoint) }));
  }
  return merged;
};

const refresh = () => {
  modules.value = getmodules();
};

const loadPluginStatus = async () => {
  if (!Auth.isAuth()) return;
  try {
    const list = await Get("/api/misc/plugins");
    pluginStatus.value = Object.fromEntries((list ?? []).map((p) => [p.id, p]));
  } catch {
    pluginStatus.value = {};
  }
  refresh();
};

const init = async () => {
  refresh();
  if (initialised) return;
  initialised = true;
  Eventy.listen("plugins-updated", loadPluginStatus);
  version.value = await Version.get();
  await loadPluginStatus();
};

/** Visible groups with only their visible items. */
const visibleGroups = computed(() =>
  modules.value
    .filter((g) => g.show)
    .map((g) => ({ ...g, items: g.items.filter((i) => i.show) }))
    .filter((g) => g.items.length)
);

/** Look up the group + item for a route name. */
const findByRoute = (routeName) => {
  for (const g of visibleGroups.value) {
    const item = g.items.find((i) => i.comp === routeName);
    if (item) return { group: g, item };
  }
  return null;
};

const restartRequired = computed(() => Object.values(pluginStatus.value).some((p) => p.restart_required));

export function useNavigation() {
  return { modules, visibleGroups, version, pluginStatus, user, restartRequired, init, refresh, findByRoute };
}
