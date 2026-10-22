// Select and scroll to grid rows named in a link, e.g. ?focus=AD_123,AD_456 from the
// Dataflow page's recalculation feedback.
//
// ag-Grid receives rowData through a prop watcher, so the row nodes may not exist yet on
// the tick the data lands, and first-data-rendered may already have fired -- the same
// reason Validate.vue polls before scrolling.
const waitForRows = async (getApi) => {
  for (let i = 0; i < 10; i++) {
    if (getApi()?.getDisplayedRowCount()) return true;
    await new Promise((resolve) => requestAnimationFrame(resolve));
  }
  return !!getApi()?.getDisplayedRowCount();
};

// Matched by key rather than through ag-Grid's getRowId: a getRowId makes the grid drop
// rows whose ids collide, and not every page's data is guaranteed unique on its key.
// Returns the number of rows found.
export async function focusRows(getApi, keyOf, keys) {
  if (!keys?.length || !(await waitForRows(getApi))) return 0;
  const api = getApi();
  const wanted = new Set(keys.map(String));
  const nodes = [];
  api.forEachNodeAfterFilterAndSort((node) => {
    if (wanted.has(keyOf(node.data))) nodes.push(node);
  });
  if (!nodes.length) return 0;

  api.deselectAll();
  nodes[0].setSelected(true);
  api.redrawRows(); // getRowStyle owns the highlight, so it has to re-run
  api.ensureNodeVisible(nodes[0], "middle");
  return nodes.length;
}

// The ?focus= value as a list of keys. A composite key is its values joined with "|".
export function focusKeys(query) {
  const raw = query?.focus;
  if (!raw) return [];
  return (Array.isArray(raw) ? raw : String(raw).split(",")).map((k) => k.trim()).filter(Boolean);
}
