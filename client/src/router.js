import { createWebHistory, createRouter } from "vue-router";
import Auth from "./helpers/auth";
import Eventy from "./helpers/eventy";

const Login = () => import("./views/login/Login.vue");

const Authorities = () => import("./views/management/authorities/Authorities.vue");
const Zones = () => import("./views/management/zones/Zones.vue");
const Networks = () => import("./views/management/networks/Networks.vue");
const Stations = () => import("./views/management/stations/Stations.vue");
const SamplingPoints = () => import("./views/management/samplingpoints/Samplingpoints.vue");
const Processes = () => import("./views/management/processes/Processes.vue");
const Samples = () => import("./views/management/samples/Samples.vue");
const ObservingCapabilities = () => import("./views/management/observingcapabilities/ObservingCapabilities.vue");
const AssessmentRegimes = () => import("./views/management/assessmentregimes/AssessmentRegimes.vue");
const Attainments = () => import("./views/management/attainments/Attainments.vue");
const Exceedances = () => import("./views/management/exceedances/Exceedances.vue");
const Settings = () => import("./views/management/settings/Settings.vue");

const Latest = () => import("./views/data/latest/Latest.vue");
const Historical = () => import("./views/data/historical/Historical.vue");
const Dataflow = () => import("./views/data/dataflow/Dataflow.vue");
const Map = () => import("./views/data/map/Map.vue");

const Import = () => import("./views/processing/import/Import.vue");
const Calculate = () => import("./views/processing/calculate/Calculate.vue");
const Convert = () => import("./views/processing/convert/Convert.vue");
const AutoValidate = () => import("./views/processing/autovalidate/Autovalidate.vue");
const Scale = () => import("./views/processing/scale/Scale.vue");

const Validate = () => import("./views/qualitycontrol/validate/Validate.vue");
const Verify = () => import("./views/qualitycontrol/verify/Verify.vue");

const Users = () => import("./views/access/users/Users.vue");
const Groups = () => import("./views/access/groups/Groups.vue");

const Forbidden = () => import("./views/forbidden/Forbidden.vue");
const Notfound = () => import("./views/notfound/Notfound.vue");

const routes = [
  { path: "/", component: Latest, name: "Home" },
  { path: "/login", component: Login, name: "Login" },

  { path: "/management/authorities", component: Authorities, name: "Authorities" },
  { path: "/management/zones", component: Zones, name: "Zones" },
  { path: "/management/networks", component: Networks, name: "Networks" },
  { path: "/management/stations", component: Stations, name: "Stations" },
  { path: "/management/samplingpoints", component: SamplingPoints, name: "SamplingPoints" },
  { path: "/management/processes", component: Processes, name: "Processes" },
  { path: "/management/samples", component: Samples, name: "Samples" },
  { path: "/management/observingcapabilities", component: ObservingCapabilities, name: "ObservingCapabilities" },
  { path: "/management/assessmentregimes", component: AssessmentRegimes, name: "AssessmentRegimes" },
  { path: "/management/attainments", component: Attainments, name: "Attainments" },
  { path: "/management/exceedances", component: Exceedances, name: "Exceedances" },
  { path: "/management/settings", component: Settings, name: "Settings" },

  { path: "/data/latest", component: Latest, name: "Latest" },
  { path: "/data/historical", component: Historical, name: "Historical" },
  { path: "/data/dataflow", component: Dataflow, name: "Dataflow" },
  { path: "/data/map", component: Map, name: "Map" },

  { path: "/processing/import", component: Import, name: "Import" },
  { path: "/processing/calculate", component: Calculate, name: "Calculate" },
  { path: "/processing/convert", component: Convert, name: "Convert" },
  { path: "/processing/autovalidate", component: AutoValidate, name: "AutoValidate" },
  { path: "/processing/scale", component: Scale, name: "Scale" },

  { path: "/qualitycontrol/validate", component: Validate, name: "Validate" },
  { path: "/qualitycontrol/verify", component: Verify, name: "Verify" },

  { path: "/acess/users", component: Users, name: "Users" },
  { path: "/acess/groups", component: Groups, name: "Groups" },

  { path: "/forbidden", component: Forbidden, name: "Forbidden" },
  { path: "/:pathMatch(.*)*", component: Notfound }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

router.beforeEach(async (to, from, next) => {
  Eventy.hideMessage();
  var isAuth = Auth.isAuth();
  if (to.name !== "Login" && !isAuth) next({ name: "Login" });
  else next();
});

export default router;
