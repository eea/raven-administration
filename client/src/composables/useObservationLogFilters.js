import { ref, computed } from "vue";
import Service from "../components/observationlog/service";

/**
 * Column visibility and filter-rule state for the Observation Change History.
 *
 * The rules themselves are authored by an administrator under Settings and evaluated
 * in SQL — see api/core/observation_log_filters.py for why filtering cannot happen in
 * the browser without breaking pagination. This composable owns only the *user's* side
 * of it: which rules they have switched on or off, and which columns they hide.
 *
 * Those preferences live server-side (user_log_preferences), not in localStorage, so
 * they follow a user between machines.
 *
 * Two kinds of "off", deliberately distinct:
 *   - an override, persisted, meaning "I don't want this rule";
 *   - a session suspension ("Show all"), which reveals everything for one look
 *     without rewriting what the user sees tomorrow.
 */
export default function useObservationLogFilters() {
  // Server-resolved rules: the stored definition plus `enabled` and `scope`.
  const rules = ref([]);
  const hiddenColumns = ref(new Set());
  // Rule ids suspended for this viewing only. Never persisted.
  const sessionDisabled = ref(new Set());
  const savingPrefs = ref(false);

  // Mirrors user_log_preferences.rule_overrides; a map so a rule the administrator
  // ships switched off can still be switched on.
  const ruleOverrides = ref({});

  /** Adopt the `filters` block that rides along with every page of log rows. */
  function applyServerFilters(filters) {
    if (!filters) return;
    rules.value = filters.rules ?? [];
    hiddenColumns.value = new Set(filters.hidden_columns ?? []);
  }

  const activeRules = computed(() => rules.value.filter((r) => r.enabled));
  const activeRuleCount = computed(() => activeRules.value.length);

  /**
   * A rule naming a field no loaded plugin provides — typically its plugin was
   * disabled. Shown greyed rather than dropped: silently ignoring a rule would
   * quietly change what the history shows without saying so.
   */
  function isUnavailable(rule) {
    if (rule.scope === "server") return false;
    const known = knownFieldKeys();
    return (rule.conditions ?? []).some((c) => !known.has(c.field));
  }

  function knownFieldKeys() {
    const keys = new Set();
    for (const p of Object.values(window.__ravenPlugins || {})) {
      for (const f of p.observationLogExtension?.filterFields ?? []) keys.add(f.key);
    }
    return keys;
  }

  const isVisible = (key) => !hiddenColumns.value.has(key);

  async function persist() {
    savingPrefs.value = true;
    try {
      await Service.savePreferences({
        rule_overrides: ruleOverrides.value,
        hidden_columns: [...hiddenColumns.value],
      });
    } catch {
      // A failed save must not take the history down with it; the user simply sees
      // their change revert on the next open.
    } finally {
      savingPrefs.value = false;
    }
  }

  /** Toggle a column. Display-only, so no refetch. */
  async function toggleColumn(key) {
    const next = new Set(hiddenColumns.value);
    next.has(key) ? next.delete(key) : next.add(key);
    hiddenColumns.value = next;
    await persist();
  }

  /**
   * Toggle a rule. Returns true when the caller must reload from offset 0.
   *
   * It always must: the rule set is part of the query, and paging with one rule set
   * then continuing with another would interleave two different result sets at the
   * same offsets.
   */
  async function toggleRule(rule) {
    const nowEnabled = !rule.enabled;
    ruleOverrides.value = { ...ruleOverrides.value, [rule.id]: nowEnabled };
    // Switching a rule back on also lifts any session suspension of it, otherwise
    // the click would appear to do nothing.
    if (nowEnabled && sessionDisabled.value.has(rule.id)) {
      const next = new Set(sessionDisabled.value);
      next.delete(rule.id);
      sessionDisabled.value = next;
    }
    await persist();
    return true;
  }

  /** Suspend every rule for this view only. Backs the empty-state "Show all". */
  function suspendAll() {
    sessionDisabled.value = new Set(rules.value.map((r) => r.id));
  }

  function resumeAll() {
    sessionDisabled.value = new Set();
  }

  const isSuspended = computed(() => sessionDisabled.value.size > 0);

  /** Sent to the endpoint as `disabled_rules`. */
  const sessionDisabledIds = computed(() => [...sessionDisabled.value]);

  /** Load the user's stored preferences. The rules come back with the rows. */
  async function loadPreferences() {
    try {
      const prefs = (await Service.preferences()) || {};
      ruleOverrides.value = prefs.rule_overrides ?? {};
    } catch {
      ruleOverrides.value = {};
    }
  }

  return {
    rules,
    activeRules,
    activeRuleCount,
    hiddenColumns,
    isVisible,
    isUnavailable,
    isSuspended,
    sessionDisabledIds,
    savingPrefs,
    applyServerFilters,
    loadPreferences,
    toggleColumn,
    toggleRule,
    suspendAll,
    resumeAll,
  };
}
