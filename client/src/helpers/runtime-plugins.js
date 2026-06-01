/**
 * Runtime plugin registry.
 * Populated by IIFE plugin scripts before the Vue app mounts.
 * MenuBar reads from this to include runtime-registered sidebar groups.
 */
import { reactive } from "vue";

// { pluginId: { menuGroups: [{ group, show, items }] } }
export const runtimePlugins = reactive({});

export function registerMenuGroups(pluginId, groups) {
  runtimePlugins[pluginId] = { menuGroups: groups };
}
