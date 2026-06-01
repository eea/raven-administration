import { createApp } from "vue";
import * as Vue from "vue";
import App from "./App.vue";
import "./assets/style.css";
// import "./assets/n-elements.css";
import { disableTextSelectOnShiftDown } from "./helpers/utils";
import "./helpers/branding"; // ensure window.__ravenBranding is set before plugins load

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

// ── Runtime plugin API ─────────────────────────────────────────────────────
// Exposed before IIFE plugins load so plugins can register routes and menu
// groups without requiring build-time changes to eea-raven.
import Eventy from "./helpers/eventy";
import { registerMenuGroups } from "./helpers/runtime-plugins";

window.RavenVue = Vue;
window.__ravenRuntime = {
  addRoute: (route) => router.addRoute(route),
  registerMenuGroups,
  emit: (e, data) => Eventy.emit(e, data),
};

// Load runtime plugins (from the API) before mounting so branding/etc apply before first paint.
// This works in both Docker Compose and Kubernetes — no build step required.
async function loadRuntimePlugins() {
  try {
    const resp = await fetch("/api/misc/plugins/enabled");
    if (!resp.ok) return;
    const plugins = await resp.json();
    for (const p of plugins) {
      if (!p.has_client) continue;
      await new Promise((resolve) => {
        const script = document.createElement("script");
        script.src = `/api/plugins/${p.id}/client.js`;
        script.onload = resolve;
        script.onerror = resolve; // non-fatal — continue loading other plugins
        document.head.appendChild(script);
      });
    }
  } catch {
    // Non-fatal: app works without plugins
  }
}

await loadRuntimePlugins();
app.mount("#app");
