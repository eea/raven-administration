// Wind rose and pollution rose from the Historical page's rows (core and plugin rows alike).
// Pure functions, no Vue: WindRose.vue draws what these return.

export const SECTORS = 16;
export const SECTOR_WIDTH = 360 / SECTORS;
export const SECTOR_NAMES = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"];
export const CALM = 0.5; // m/s: below this the wind has no meaningful direction

// Speed classes (m/s), lower bound inclusive; calms are counted separately.
export const SPEED_CLASSES = [
  { from: 0.5, to: 2, label: "0.5–2" },
  { from: 2, to: 4, label: "2–4" },
  { from: 4, to: 6, label: "4–6" },
  { from: 6, to: 8, label: "6–8" },
  { from: 8, to: Infinity, label: "≥ 8" }
];

const DIRECTION = /dir|retning|\bwd\b|\bdd\b/i;
const SPEED = /speed|hastighet|\bws\b|\bff\b/i;
const DEGREE_UNITS = ["°", "deg", "degree", "degrees", "grader"];
const MET_UNITS = ["°", "deg", "degree", "degrees", "grader", "m/s", "°c", "degc", "%", "hpa", "mm"];

/** One entry per plotted series: { id, label, component, unit }. */
export function listSeries(rows) {
  const out = new Map();
  for (const r of rows) {
    if (!out.has(r.sampling_point_id)) {
      out.set(r.sampling_point_id, {
        id: r.sampling_point_id,
        component: r.component || "",
        unit: r.unit || "",
        label: `${r.station || ""} – ${r.component || ""}${r.unit ? ` (${r.unit})` : ""}`
      });
    }
  }
  return [...out.values()];
}

const unitIs = (s, units) => units.includes((s.unit || "").trim().toLowerCase());

export const isDirection = (s) => DIRECTION.test(s.component) || unitIs(s, DEGREE_UNITS);
export const isSpeed = (s) => !isDirection(s) && (SPEED.test(s.component) || unitIs(s, ["m/s"]));

/** Best guess of which plotted series are wind direction, wind speed and a pollutant. */
export function guessWindSeries(series) {
  const dir = series.find(isDirection) || null;
  const speed = series.find(isSpeed) || null;
  const others = series.filter((s) => s !== dir && s !== speed);
  const pollutant = others.find((s) => !unitIs(s, MET_UNITS)) || null;
  return { dir: dir?.id ?? null, speed: speed?.id ?? null, pollutant: pollutant?.id ?? null };
}

const usable = (r) => r.valid !== false && r.value !== null && r.value !== undefined && Number.isFinite(Number(r.value));

function byDatetime(rows, id) {
  const m = new Map();
  if (!id) return m;
  for (const r of rows) if (r.sampling_point_id === id && usable(r)) m.set(r.datetime, Number(r.value));
  return m;
}

/** Sector index 0..15 (0 = N) for a direction in degrees; 350° and 10° are both N. */
export function sectorOf(deg) {
  const d = ((deg % 360) + 360) % 360;
  return Math.floor((d + SECTOR_WIDTH / 2) / SECTOR_WIDTH) % SECTORS;
}

/**
 * Wind rose: share of all paired values per sector and speed class.
 * Returns { n, calm (percent), sectors: [[percent per speed class]], from, to }.
 */
export function windRose(rows, dirId, speedId) {
  const dirs = byDatetime(rows, dirId);
  const speeds = byDatetime(rows, speedId);
  const sectors = Array.from({ length: SECTORS }, () => SPEED_CLASSES.map(() => 0));
  let n = 0, calm = 0, from = null, to = null;
  for (const [t, d] of dirs) {
    const s = speeds.get(t);
    if (s === undefined) continue;
    n++;
    if (from === null || t < from) from = t;
    if (to === null || t > to) to = t;
    if (s < CALM) { calm++; continue; }
    const cls = SPEED_CLASSES.findIndex((c) => s >= c.from && s < c.to);
    sectors[sectorOf(d)][cls]++;
  }
  const pct = (x) => (n ? (x / n) * 100 : 0);
  return { n, calm: pct(calm), sectors: sectors.map((cs) => cs.map(pct)), from, to };
}

/**
 * Pollution rose: mean pollutant value per wind sector. With a speed series, calm hours
 * are left out of the sectors and their mean is reported separately.
 * Returns { n, calmMean, calmN, sectors: [{ mean, n }], from, to }.
 */
export function pollutionRose(rows, dirId, pollutantId, speedId) {
  const dirs = byDatetime(rows, dirId);
  const values = byDatetime(rows, pollutantId);
  const speeds = byDatetime(rows, speedId);
  const sums = Array.from({ length: SECTORS }, () => ({ sum: 0, n: 0 }));
  let n = 0, calmSum = 0, calmN = 0, from = null, to = null;
  for (const [t, d] of dirs) {
    const v = values.get(t);
    if (v === undefined) continue;
    const s = speedId ? speeds.get(t) : null;
    if (speedId && s === undefined) continue;
    n++;
    if (from === null || t < from) from = t;
    if (to === null || t > to) to = t;
    if (s !== null && s < CALM) { calmSum += v; calmN++; continue; }
    const b = sums[sectorOf(d)];
    b.sum += v;
    b.n++;
  }
  return {
    n,
    calmN,
    calmMean: calmN ? calmSum / calmN : null,
    sectors: sums.map((b) => ({ mean: b.n ? b.sum / b.n : null, n: b.n })),
    from,
    to
  };
}

/** Round numbers for ring labels: about four rings up to at least `max`. */
export function niceRings(max) {
  if (!(max > 0)) return [1];
  const raw = max / 4;
  const mag = 10 ** Math.floor(Math.log10(raw));
  const step = [1, 2, 2.5, 5, 10].map((f) => f * mag).find((s) => s >= raw);
  const rings = [];
  for (let v = step; v < max + step * 0.999; v += step) rings.push(+v.toPrecision(6));
  return rings;
}
