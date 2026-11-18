/**
 * Colour palette selection. The palettes themselves live in assets/palettes.css;
 * this only sets <html data-palette> and remembers the choice per browser.
 */
import { ref } from "vue";

const KEY = "raven_palette";

export const PALETTES = [
  { id: "graphite", name: "Graphite", nav: "#15181e", accent: "#0d9488" },
  { id: "forest", name: "Forest", nav: "#11241c", accent: "#15803d" },
  { id: "petrol", name: "Petrol", nav: "#0d2630", accent: "#0e7490" },
  { id: "copper", name: "Copper", nav: "#1f1b18", accent: "#c2410c" },
  { id: "light", name: "Light", nav: "#ffffff", accent: "#0f766e" },
  { id: "indigo", name: "Indigo", nav: "#111a33", accent: "#4f46e5" }
];
const DEFAULT = "graphite";

const read = () => {
  try {
    const v = localStorage.getItem(KEY);
    return PALETTES.some((p) => p.id === v) ? v : DEFAULT;
  } catch {
    return DEFAULT;
  }
};

export const palette = ref(read());

export const applyPalette = (id = palette.value) => {
  palette.value = PALETTES.some((p) => p.id === id) ? id : DEFAULT;
  document.documentElement.dataset.palette = palette.value;
  try {
    localStorage.setItem(KEY, palette.value);
  } catch {
    /* storage unavailable: choice lasts for this page only */
  }
};
