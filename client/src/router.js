import { createWebHistory, createRouter } from "vue-router";
import Auth from "./helpers/auth";

const Login = () => import("./views/login/Login.vue");

const Authorities = () => import("./views/management/authorities/Authorities.vue");
const Networks = () => import("./views/management/networks/Networks.vue");
const Stations = () => import("./views/management/stations/Stations.vue");
const SamplingPoints = () => import("./views/management/samplingpoints/Samplingpoints.vue");
const Processes = () => import("./views/management/processes/Processes.vue");
const Samples = () => import("./views/management/samples/Samples.vue");
const Zones = () => import("./views/management/zones/Zones.vue");

const Calculate = () => import("./views/processing/calculate/Calculate.vue");
const Convert = () => import("./views/processing/convert/Convert.vue");
const AutoValidate = () => import("./views/processing/autovalidate/Autovalidate.vue");

const Latest = () => import("./views/data/latest/Latest.vue");
const Historical = () => import("./views/data/historical/Historical.vue");
const Dataflow = () => import("./views/data/dataflow/Dataflow.vue");

const Validate = () => import("./views/qualitycontrol/validate/Validate.vue");
const Verify = () => import("./views/qualitycontrol/verify/Verify.vue");

const Notfound = () => import("./views/notfound/Notfound.vue");

const routes = [
  { path: "/", component: Latest, name: "Home" },
  { path: "/login", component: Login, name: "Login" },
  { path: "/management/authorities", component: Authorities, name: "Authorities" },
  { path: "/management/networks", component: Networks, name: "Networks" },
  { path: "/management/stations", component: Stations, name: "Stations" },
  { path: "/management/samplingpoints", component: SamplingPoints, name: "SamplingPoints" },
  { path: "/management/processes", component: Processes, name: "Processes" },
  { path: "/management/samples", component: Samples, name: "Samples" },
  { path: "/management/zones", component: Zones, name: "Zones" },

  { path: "/processing/calculate", component: Calculate, name: "Calculate" },
  { path: "/processing/convert", component: Convert, name: "Convert" },
  { path: "/processing/autovalidate", component: AutoValidate, name: "AutoValidate" },

  { path: "/data/latest", component: Latest, name: "Latest" },
  { path: "/data/historical", component: Historical, name: "Historical" },
  { path: "/data/dataflow", component: Dataflow, name: "Dataflow" },

  { path: "/qualitycontrol/validate", component: Validate, name: "Validate" },
  { path: "/qualitycontrol/verify", component: Verify, name: "Verify" },

  { path: "/:pathMatch(.*)*", component: Notfound }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

router.beforeEach(async (to, from, next) => {
  var isAuth = Auth.isAuth();
  if (to.name !== "Login" && !isAuth) next({ name: "Login" });
  else next();
});

export default router;
