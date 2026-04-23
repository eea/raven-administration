import { reactive } from "vue";

export const branding = reactive({
  appName: "Raven4",
  subtitle: "Administration",
  tabTitle: "Raven",
});

// Expose globally so standalone runtime-loaded plugin scripts can write to the reactive store
window.__ravenBranding = branding;
