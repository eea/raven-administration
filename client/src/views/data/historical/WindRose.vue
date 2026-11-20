<script setup>
import { ref, computed, watch } from "vue";
import { SECTORS, SECTOR_WIDTH, SECTOR_NAMES, SPEED_CLASSES, CALM, listSeries, guessWindSeries, windRose, pollutionRose, niceRings } from "./windrose";

// rows: the Historical page's plotted rows; meantype: the mean type they were plotted with.
const props = defineProps({
  rows: { type: Array, default: () => [] },
  meantype: { type: String, default: "0" }
});

const series = computed(() => listSeries(props.rows));
const dirId = ref(null);
const speedId = ref(null);
const pollutantId = ref(null);
const mode = ref("wind");

// Re-guess whenever a new plot brings a different set of series.
watch(
  () => series.value.map((s) => s.id).join("|"),
  () => {
    const g = guessWindSeries(series.value);
    dirId.value = g.dir;
    speedId.value = g.speed;
    pollutantId.value = g.pollutant;
    if (mode.value === "pollution" && !g.pollutant) mode.value = "wind";
  },
  { immediate: true }
);

// Directions averaged over long periods do not describe the wind well.
const coarse = computed(() => !["1000", "0", "1"].includes(String(props.meantype)));

const wind = computed(() => (dirId.value && speedId.value ? windRose(props.rows, dirId.value, speedId.value) : null));
const pollution = computed(() => (dirId.value && pollutantId.value ? pollutionRose(props.rows, dirId.value, pollutantId.value, speedId.value) : null));
const pollutantUnit = computed(() => series.value.find((s) => s.id === pollutantId.value)?.unit || "");

// --- geometry -----------------------------------------------------------------
const SIZE = 420;
const C = SIZE / 2;
const R = 165;      // outer radius of the scale
const HOLE = 22;    // centre circle that holds the calm figure
const GAP = 1.5;    // degrees left empty on each side of a wedge

const point = (r, deg) => {
  const a = (deg * Math.PI) / 180;
  return [C + r * Math.sin(a), C - r * Math.cos(a)];
};

function wedge(r0, r1, a0, a1) {
  const [x0, y0] = point(r0, a0), [x1, y1] = point(r1, a0), [x2, y2] = point(r1, a1), [x3, y3] = point(r0, a1);
  return `M${x0},${y0} L${x1},${y1} A${r1},${r1} 0 0 1 ${x2},${y2} L${x3},${y3} A${r0},${r0} 0 0 0 ${x0},${y0} Z`;
}

const sectorAngles = (i) => [i * SECTOR_WIDTH - SECTOR_WIDTH / 2 + GAP, i * SECTOR_WIDTH + SECTOR_WIDTH / 2 - GAP];

// Sequential scales: light -> dark blue for speed classes, yellow -> red for concentrations.
const SPEED_COLORS = ["#c6dbef", "#9ecae1", "#6baed6", "#3182bd", "#08519c"];
function heat(t) {
  const lo = [235, 203, 139], hi = [191, 97, 106]; // nord13 -> nord11
  const c = lo.map((v, k) => Math.round(v + (hi[k] - v) * Math.min(1, Math.max(0, t))));
  return `rgb(${c.join(",")})`;
}

const fmt = (v, d = 1) => (v === null || v === undefined ? "–" : Number(v).toFixed(d));

const rose = computed(() => {
  if (mode.value === "wind") {
    const w = wind.value;
    if (!w || !w.n) return null;
    const totals = w.sectors.map((cs) => cs.reduce((a, b) => a + b, 0));
    const rings = niceRings(Math.max(...totals));
    const max = rings[rings.length - 1];
    const scale = (pct) => HOLE + ((R - HOLE) * pct) / max;
    const wedges = [];
    w.sectors.forEach((cs, i) => {
      const [a0, a1] = sectorAngles(i);
      let acc = 0;
      cs.forEach((pct, k) => {
        if (pct <= 0) return;
        wedges.push({
          d: wedge(scale(acc), scale(acc + pct), a0, a1),
          fill: SPEED_COLORS[k],
          title: `${SECTOR_NAMES[i]}, ${SPEED_CLASSES[k].label} m/s: ${fmt(pct)} %  (sector total ${fmt(totals[i])} %)`
        });
        acc += pct;
      });
    });
    return {
      wedges,
      rings: rings.map((v) => ({ r: scale(v), label: `${+v.toFixed(2)} %` })),
      centre: `${fmt(w.calm)} %`,
      centreTitle: `Calm (< ${CALM} m/s): ${fmt(w.calm)} % of ${w.n} values`,
      n: w.n, from: w.from, to: w.to
    };
  }
  const p = pollution.value;
  if (!p || !p.n) return null;
  const means = p.sectors.map((s) => s.mean ?? 0);
  const rings = niceRings(Math.max(...means));
  const max = rings[rings.length - 1];
  const scale = (v) => HOLE + ((R - HOLE) * v) / max;
  const wedges = p.sectors
    .map((s, i) => {
      if (s.mean === null) return null;
      const [a0, a1] = sectorAngles(i);
      return {
        d: wedge(HOLE, scale(Math.max(0, s.mean)), a0, a1),
        fill: heat(s.mean / max),
        title: `${SECTOR_NAMES[i]}: mean ${fmt(s.mean)} ${pollutantUnit.value}  (n = ${s.n})`
      };
    })
    .filter(Boolean);
  return {
    wedges,
    rings: rings.map((v) => ({ r: scale(v), label: `${+v.toFixed(2)}` })),
    centre: p.calmMean === null ? "" : fmt(p.calmMean),
    centreTitle: p.calmMean === null ? "" : `Calm (< ${CALM} m/s): mean ${fmt(p.calmMean)} ${pollutantUnit.value}  (n = ${p.calmN})`,
    n: p.n, from: p.from, to: p.to
  };
});

const compass = [0, 90, 180, 270].map((deg, i) => {
  const [x, y] = point(R + 16, deg);
  return { x, y, label: ["N", "E", "S", "W"][i] };
});
const spokes = Array.from({ length: SECTORS / 2 }, (_, i) => {
  const [x1, y1] = point(HOLE, i * 45), [x2, y2] = point(R, i * 45);
  return { x1, y1, x2, y2 };
});
</script>

<template>
  <div class="flex flex-col gap-3">
    <div class="flex flex-wrap items-end gap-4 text-sm">
      <div class="flex gap-1">
        <button class="button" :class="{ 'opacity-50': mode !== 'wind' }" @click="mode = 'wind'">Wind rose</button>
        <button class="button" :class="{ 'opacity-50': mode !== 'pollution' }" :disabled="!pollutantId" @click="mode = 'pollution'">Pollution rose</button>
      </div>
      <label class="flex flex-col gap-1">
        <span class="font-bold">Wind direction</span>
        <select class="select" v-model="dirId">
          <option :value="null">–</option>
          <option v-for="s in series" :key="s.id" :value="s.id">{{ s.label }}</option>
        </select>
      </label>
      <label class="flex flex-col gap-1">
        <span class="font-bold">Wind speed</span>
        <select class="select" v-model="speedId">
          <option :value="null">–</option>
          <option v-for="s in series" :key="s.id" :value="s.id">{{ s.label }}</option>
        </select>
      </label>
      <label v-if="mode === 'pollution' || pollutantId" class="flex flex-col gap-1">
        <span class="font-bold">Pollutant</span>
        <select class="select" v-model="pollutantId">
          <option :value="null">–</option>
          <option v-for="s in series" :key="s.id" :value="s.id">{{ s.label }}</option>
        </select>
      </label>
    </div>

    <div v-if="coarse" class="text-xs text-nord11">
      Wind direction is averaged over each period with this mean type. Use Hour or Original for a representative rose.
    </div>

    <div v-if="!dirId || (mode === 'wind' ? !speedId : !pollutantId)" class="text-sm text-nord3">
      Pick a wind direction and {{ mode === "wind" ? "a wind speed" : "a pollutant" }} series from the plotted series.
    </div>
    <div v-else-if="!rose" class="text-sm text-nord3">No times where the selected series all have valid values.</div>

    <div v-else class="flex flex-wrap items-center gap-6">
      <svg :viewBox="`0 0 ${SIZE} ${SIZE}`" :width="SIZE" :height="SIZE" class="max-w-full h-auto text-nord3" role="img" :aria-label="mode === 'wind' ? 'Wind rose' : 'Pollution rose'">
        <g fill="none" stroke="currentColor" stroke-opacity="0.25">
          <circle v-for="ring in rose.rings" :key="ring.r" :cx="C" :cy="C" :r="ring.r" />
          <line v-for="(s, i) in spokes" :key="i" :x1="s.x1" :y1="s.y1" :x2="s.x2" :y2="s.y2" />
        </g>
        <path v-for="(w, i) in rose.wedges" :key="i" :d="w.d" :fill="w.fill" stroke="white" stroke-width="0.5">
          <title>{{ w.title }}</title>
        </path>
        <g fill="currentColor" font-size="10">
          <text v-for="ring in rose.rings" :key="'l' + ring.r" :x="C + 3" :y="C - ring.r - 2">{{ ring.label }}</text>
        </g>
        <g fill="currentColor" font-size="13" font-weight="bold" text-anchor="middle" dominant-baseline="middle">
          <text v-for="c in compass" :key="c.label" :x="c.x" :y="c.y">{{ c.label }}</text>
        </g>
        <circle :cx="C" :cy="C" :r="HOLE" fill="white" stroke="currentColor" stroke-opacity="0.4">
          <title>{{ rose.centreTitle }}</title>
        </circle>
        <text :x="C" :y="C" fill="currentColor" font-size="10" text-anchor="middle" dominant-baseline="middle">{{ rose.centre }}</text>
      </svg>

      <div class="flex flex-col gap-2 text-xs text-nord3">
        <template v-if="mode === 'wind'">
          <div class="font-bold">Wind speed (m/s)</div>
          <div v-for="(c, k) in SPEED_CLASSES" :key="c.label" class="flex items-center gap-2">
            <span class="inline-block w-3 h-3" :style="{ background: SPEED_COLORS[k] }"></span>{{ c.label }}
          </div>
          <div>Centre: calm (&lt; {{ CALM }} m/s)</div>
          <div>Radius: share of all values</div>
        </template>
        <template v-else>
          <div class="font-bold">Mean per wind direction</div>
          <div>{{ pollutantUnit }}</div>
          <div v-if="speedId">Centre: mean during calm (&lt; {{ CALM }} m/s)</div>
        </template>
        <div class="mt-2">{{ rose.n }} values, {{ rose.from }} – {{ rose.to }}</div>
      </div>
    </div>
  </div>
</template>
