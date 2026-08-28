import { ref, computed } from "vue";

/**
 * Composable letting installed plugins add columns to the Observation Change
 * History, keyed by observation_log.id — without modifying the history components.
 *
 * Usage:
 *   const { extraColumns, cell, reset, fetchFor } = useObservationLogExtension();
 *   reset();
 *   await fetchFor({ samplingPointId, logIds: rows.map(r => r.id) });
 *   // in the template:  cell(row.id, col.key)
 *
 * Plugin client.js registers via:
 *   window.__ravenPlugins[id].observationLogExtension = {
 *     extraColumns: [{ key: 'log_text', label: 'Comment' }],
 *     getExtraData(ctx) { ... return Map<logId, { log_text: ... }>; }
 *   }
 *
 * ctx carries BOTH the sampling point and the ids of the rows actually on screen:
 *
 *   { samplingPointId, logIds: [...] }
 *
 * The ids matter. Previously ctx held only samplingPointId, so a plugin could do no
 * better than guess — nilu-qa fetched the newest 2000 log rows and hoped they matched
 * what the page had loaded. After the AirQUIS import that guess missed most of the
 * data: 483 of 532 sampling points have more than 2000 log rows (worst: 136k), leaving
 * ~72% of comments permanently blank. Passing the visible ids makes the lookup exact
 * and unbounded, and mirrors what the Validate grid already does for its own plugin
 * column via columnExtension.getRowData(ids).
 *
 * fetchFor MERGES rather than replaces, so paginated views ("Load more") can call it
 * per page with only the new ids.
 */
export default function useObservationLogExtension() {
  const extMap = ref(new Map());

  // Every plugin that registers one — not just the first. The previous inline
  // version broke out of the loop after one, so a second plugin was silently ignored.
  const extensions = () =>
    Object.values(window.__ravenPlugins || {})
      .map((p) => p.observationLogExtension)
      .filter(Boolean);

  const extraColumns = computed(() =>
    extensions().flatMap((e) => e.extraColumns || [])
  );

  const hasExtensions = computed(() => extraColumns.value.length > 0);

  function reset() {
    extMap.value = new Map();
  }

  /**
   * Fetch extension data for the given rows and merge it in.
   * Never throws: a failing plugin leaves the columns blank rather than breaking
   * the history itself.
   */
  async function fetchFor(ctx) {
    const exts = extensions();
    if (!exts.length) return;
    if (!ctx?.logIds?.length) return;

    const results = await Promise.all(
      exts.map((e) =>
        Promise.resolve()
          .then(() => e.getExtraData(ctx))
          .catch(() => new Map())
      )
    );

    // Copy-on-write so Vue sees the change; merge per row so two plugins can each
    // contribute different keys for the same log entry.
    const merged = new Map(extMap.value);
    for (const m of results) {
      if (!m || typeof m.forEach !== "function") continue;
      m.forEach((value, logId) => {
        merged.set(logId, { ...(merged.get(logId) || {}), ...value });
      });
    }
    extMap.value = merged;
  }

  // DISPLAY ONLY. The ?? "" collapses "this log row has no extension row" and "the
  // extension row exists but the comment is empty" into the same value, which is fine
  // for a table cell and wrong for anything that has to distinguish them. Filtering
  // deliberately does not go through here: it happens in SQL (see
  // api/core/observation_log_filters.py), where NOT EXISTS keeps the two cases apart.
  const cell = (logId, key) => extMap.value.get(logId)?.[key] ?? "";

  return { extraColumns, hasExtensions, extMap, reset, fetchFor, cell };
}
