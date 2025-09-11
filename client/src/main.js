import { createApp } from "vue";
import App from "./App.vue";
import "./assets/tailwind.css";
import "./assets/n-elements.css";
import { disableTextSelectOnShiftDown } from "./helpers/utils";

// INTERCEPT
import intercetor from "./helpers/interceptor";
intercetor.request();
intercetor.response();
intercetor.default();

const app = createApp(App);

// TOOLTIP
import Tooltip from "vue-follow-tooltip";
app.use(Tooltip, {
  delay: 100,
  center: true,
  offsetX: 0,
  offsetY: -60
});

// Disable text selection on shift down
disableTextSelectOnShiftDown();

// ROUTER
import router from "./router";
app.use(router);

app.mount("#app");
