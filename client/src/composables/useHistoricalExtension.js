import { reactive, computed } from "vue";

/**
 * Composable letting installed plugins add series to the Historical data page —
 * e.g. data fetched from an external API — without modifying the page itself.
 *
 * Plugin client.js registers via:
 *   window.__ravenPlugins[id].historicalExtension = {
 *     title: 'External sources',          // heading above the picker
 *     picker: SomeVueComponent,           // optional; v-model = the plugin's selection (array),
 *                                         // also receives :from and :to (Date)
 *     getSeries(ctx) { ... return rows }  // may be async
 *   }
 *
 * ctx = { selection, from_dt, to_dt, meantype, coverage } — the same values the page
 * posts to /api/data/historical, plus whatever the plugin's picker put in its selection.
 *
 * Rows use the shape of the core rows, because chart, legend, table, pivot and CSV are
 * all derived from that one array:
 *
 *   { sampling_point_id, datetime, datetime_begin?, value, actual_value, valid, coverage,
 *     station, component, unit, network, equipment?, equipment_identifier?,
 *     meantype, meantype_string, timestep }
 *
 * - sampling_point_id identifies the series. Namespace it (e.g. 'ext:mdir:9') so it can
 *   never collide with a real sampling point, and avoid dots: it becomes a grid field name.
 * - datetime is 'YYYY-MM-DD HH:mm:ss', on the same clock as the core rows.
 * - unit decides the y-axis: series with an identical unit string share one.
 */
export default function useHistoricalExtension() {
  const extensions = Object.entries(window.__ravenPlugins || {})
    .filter(([, p]) => p && p.historicalExtension && typeof p.historicalExtension.getSeries === "function")
    .map(([id, p]) => ({ id, ...p.historicalExtension }));

  const pickers = extensions.filter((e) => e.picker);

  // pluginId -> array of whatever the plugin's picker selected (opaque to core)
  const selections = reactive(Object.fromEntries(extensions.map((e) => [e.id, []])));

  const selectedCount = computed(() => extensions.reduce((n, e) => n + (selections[e.id]?.length || 0), 0));

  /**
   * Ask every extension for its rows. Never throws: a failing plugin contributes no
   * rows and one entry in `errors`, so the core series still plot.
   */
  async function fetchSeries(ctx) {
    const results = await Promise.all(
      extensions.map((e) =>
        Promise.resolve()
          .then(() => e.getSeries({ ...ctx, selection: [...(selections[e.id] || [])] }))
          .then((rows) => ({ rows: Array.isArray(rows) ? rows : [] }))
          .catch((err) => ({ rows: [], error: `${e.title || e.id}: ${err?.message || "failed to load"}` }))
      )
    );
    return {
      rows: results.flatMap((r) => r.rows),
      errors: results.map((r) => r.error).filter(Boolean)
    };
  }

  return { pickers, selections, selectedCount, fetchSeries };
}
