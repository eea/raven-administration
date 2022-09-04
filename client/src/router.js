import { createWebHistory, createRouter } from "vue-router";
import Auth from "./helpers/auth";
import Home from "./views/home/Home.vue";
import Login from "./views/login/Login.vue";

import Authorities from "./views/management/authorities/Authorities.vue";
import Networks from "./views/management/networks/Networks.vue";
// import Stations from "./views/management/stations/Stations.vue";
import Zones from "./views/management/zones/Zones.vue";

// import Calculate from "./views/processing/calculate/Calculate.vue";
// import Convert from "./views/processing/convert/Convert.vue";
// import AutoValidate from "./views/processing/autovalidate/Autovalidate.vue";

import Latest from "./views/data/latest/Latest.vue";
import Historical from "./views/data/historical/Historical.vue";

import Validate from "./views/qualitycontrol/validate/Validate.vue";

// import Notfound from "./views/notfound/Notfound.vue"

const routes = [
  { path: "/", component: Latest, name: "Home" },
  { path: "/login", component: Login, name: "Login" },
  { path: "/management/authorities", component: Authorities, name: "Authorities" },
  { path: "/management/networks", component: Networks, name: "Networks" },
  // { path: '/management/stations', component: Stations, name: "Stations" },
  { path: "/management/zones", component: Zones, name: "Zones" },

  // { path: '/processing/calculate', component: Calculate, name: "Calculate" },
  // { path: '/processing/convert', component: Convert, name: "Convert" },
  // { path: '/processing/autovalidate', component: AutoValidate, name: "AutoValidate" },

  { path: "/data/latest", component: Latest, name: "Latest" },
  { path: "/data/historical", component: Historical, name: "Historical" },

  { path: "/qualitycontrol/validate", component: Validate, name: "Validate" },

  // { path: '/:pathMatch(.*)*', component: Notfound }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach(async (to, from, next) => {
  var isAuth = Auth.isAuth();
  if (to.name !== "Login" && !isAuth) next({ name: "Login" });
  else next();
});

export default router;
