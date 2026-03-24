// Maps eea_times.notation → datetime granularity
const TIMESTEP_GRANULARITY = {
  hour:      "hour",
  "n-hour":  "hour",
  day:       "day",
  week:      "day",
  fortnight: "day",
  dc:        "day",
  month:     "month",
  quarter:   "month",
  year:      "year",
};

// Maps meantype_string → datetime granularity
const MEANTYPE_GRANULARITY = {
  hour:               "hour",
  "moving 8 hour":    "hour",
  "moving 8 hour max":"hour",
  "moving 24 hour":   "day",
  day:                "day",
  month:              "month",
  year:               "year",
  "winter year":      "year",
  "summer year":      "year",
  "winter season":    "year",
  "aot40 vegetation": "year",
  "aot40 forest":     "year",
};

// Derive granularity for a historical row.
// Raw / Original use the sampling point's own timestep notation;
// all aggregated meantypes use meantype_string.
export function granularityFromHistoricalRow(row) {
  if (!row) return null;
  const isRaw = row.meantype === 0 || row.meantype === 1000;
  if (isRaw) return TIMESTEP_GRANULARITY[row.timestep?.toLowerCase()] ?? null;
  return MEANTYPE_GRANULARITY[row.meantype_string?.toLowerCase()] ?? null;
}

// Derive granularity for a latest-data row (always uses the timestep notation).
export function granularityFromTimestep(timestep) {
  if (!timestep) return null;
  return TIMESTEP_GRANULARITY[timestep.toLowerCase()] ?? null;
}

// Wrap the relevant portion of a datetime string in <strong>.
// Expects strings like "YYYY-MM-DD HH:MM" or "YYYY-MM-DD HH:MM:SS".
const RANGES = { year: [0, 4], month: [5, 7], day: [8, 10], hour: [11, 13] };

export function highlightDatetime(datetime, granularity) {
  if (!datetime) return "";
  const range = granularity && RANGES[granularity];
  if (!range) return datetime;
  const [s, e] = range;
  return `${datetime.slice(0, s)}<strong style="font-size:1.1em">${datetime.slice(s, e)}</strong>${datetime.slice(e)}`;
}

// AG-Grid cellRenderer factory.
// getGranularity(rowData) → granularity string | null
export function datetimeCellRenderer(getGranularity) {
  return (params) => highlightDatetime(params.value, getGranularity(params.data));
}
