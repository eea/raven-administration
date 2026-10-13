import * as L from "leaflet";
import { setWorkerUrl } from "maplibre-gl";
import workerUrl from "maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url";
import "maplibre-gl/dist/maplibre-gl.css";
import { maplibreGL } from "@maplibre/maplibre-gl-leaflet";

// The basemap under every Raven map: OpenFreeMap's keyless vector tiles, drawn by
// maplibre inside the Leaflet map.
//
// It replaced CARTO's raster light_all tiles, which now need an API key. The
// switch was silent: the CDN still answers HTTP 200 image/png, but every tile at every
// zoom is the same "API KEY REQUIRED" placeholder, so the maps went blank with nothing in
// the console. Ported from sensor-insight (f67217a, client/src/views/map/basemap.ts),
// which hit the same thing.
//
// Two things make it work, and each fails as a plain grey map rather than an error:
//
//  - setWorkerUrl. maplibre resolves its worker relative to its own bundle, which Vite
//    relocates, so it is pointed at the chunk Vite emits.
//  - One Leaflet. vue-leaflet loads its own copy (leaflet-src.esm) unless told to use
//    the global one, and the maplibre layer extends the `leaflet` main build. Every <LMap>
//    that calls addBasemap therefore sets :use-global-leaflet="true". Importing
//    `leaflet` here sets window.L to that instance (its UMD build does); the fallback
//    only covers a build that does not.
setWorkerUrl(workerUrl);
window.L = window.L ?? L;

// Add the basemap to a Leaflet map -- an <LMap>'s leafletObject, from its @ready handler.
export const addBasemap = (leafletMap) => maplibreGL({ style: BASEMAP_STYLE }).addTo(leafletMap);

// Hand-authored light style over OpenFreeMap's raw vector tiles: ~16 layers rather than
// positron's ~55, and no sprite, so no icons are fetched. Nord and deliberately low
// contrast, so the markers drawn on top stay the loudest thing on screen.
const C = {
  land:        "#f2f4f7",
  water:       "#dce3ec",
  green:       "rgba(163, 190, 140, 0.10)",
  glacier:     "rgba(255, 255, 255, 0.60)",
  building:    "rgba(76, 86, 106, 0.10)",
  coast:       "rgba(76, 86, 106, 0.38)",
  border:      "rgba(76, 86, 106, 0.42)",
  borderMinor: "rgba(76, 86, 106, 0.16)",
  road:        "rgba(76, 86, 106, 0.30)",
  roadMinor:   "rgba(76, 86, 106, 0.16)",
  label:       "#4c566a",
  labelMinor:  "rgba(76, 86, 106, 0.80)",
  labelFaint:  "rgba(76, 86, 106, 0.50)",
  halo:        "rgba(242, 244, 247, 0.90)",
}

const SOURCE = "openmaptiles"
const FONT = ["Noto Sans Regular"]

// Romanised name where the tiles carry one, so labels stay readable everywhere.
const NAME =
  ["coalesce", ["get", "name:latin"], ["get", "name:en"], ["get", "name"]]

export const BASEMAP_STYLE = {
  version: 8,
  glyphs: "https://tiles.openfreemap.org/fonts/{fontstack}/{range}.pbf",
  sources: {
    [SOURCE]: {
      type: "vector",
      url: "https://tiles.openfreemap.org/planet",
      attribution:
        '<a href="https://openfreemap.org" target="_blank">OpenFreeMap</a> © ' +
        '<a href="https://www.openmaptiles.org/" target="_blank">OpenMapTiles</a> · Data © ' +
        '<a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a>',
    },
  },
  layers: [
    { id: "land", type: "background", paint: { "background-color": C.land } },

    {
      id: "green",
      type: "fill",
      source: SOURCE,
      "source-layer": "landcover",
      filter: ["in", ["get", "class"], ["literal", ["wood", "grass"]]],
      paint: { "fill-color": C.green },
    },
    {
      id: "glacier",
      type: "fill",
      source: SOURCE,
      "source-layer": "landcover",
      filter: ["==", ["get", "class"], "ice"],
      paint: { "fill-color": C.glacier },
    },
    {
      id: "water",
      type: "fill",
      source: SOURCE,
      "source-layer": "water",
      paint: { "fill-color": C.water },
    },
    {
      id: "waterway",
      type: "line",
      source: SOURCE,
      "source-layer": "waterway",
      minzoom: 5,
      paint: {
        "line-color": C.water,
        "line-width": ["interpolate", ["linear"], ["zoom"], 5, 0.4, 9, 1.6],
      },
    },
    {
      id: "coastline",
      type: "line",
      source: SOURCE,
      "source-layer": "water",
      paint: {
        "line-color": C.coast,
        "line-width": ["interpolate", ["linear"], ["zoom"], 3, 0.8, 8, 1.3],
      },
    },

    // Buildings only appear at the zooms where someone is checking which street a sensor sits on.
    {
      id: "building",
      type: "fill",
      source: SOURCE,
      "source-layer": "building",
      minzoom: 14,
      paint: { "fill-color": C.building },
    },

    {
      id: "boundary-region",
      type: "line",
      source: SOURCE,
      "source-layer": "boundary",
      minzoom: 5.5,
      filter: ["all", ["==", ["get", "admin_level"], 4], ["==", ["get", "maritime"], 0]],
      paint: { "line-color": C.borderMinor, "line-width": 0.6 },
    },
    {
      id: "boundary-country",
      type: "line",
      source: SOURCE,
      "source-layer": "boundary",
      filter: [
        "all",
        ["==", ["get", "admin_level"], 2],
        ["==", ["get", "maritime"], 0],
        ["!=", ["get", "disputed"], 1],
      ],
      paint: {
        "line-color": C.border,
        "line-width": ["interpolate", ["linear"], ["zoom"], 3, 0.7, 8, 1.4],
      },
    },

    {
      id: "road",
      type: "line",
      source: SOURCE,
      "source-layer": "transportation",
      minzoom: 7,
      filter: [
        "in",
        ["get", "class"],
        ["literal", ["motorway", "trunk", "primary", "secondary", "tertiary"]],
      ],
      paint: {
        "line-color": C.road,
        "line-width": [
          "interpolate", ["linear"], ["zoom"],
          7,  ["case", ["==", ["get", "class"], "motorway"], 1, 0.6],
          12, ["case", ["==", ["get", "class"], "motorway"], 2.4, 1.2],
          16, 4,
        ],
      },
    },
    {
      id: "road-minor",
      type: "line",
      source: SOURCE,
      "source-layer": "transportation",
      minzoom: 11,
      filter: ["in", ["get", "class"], ["literal", ["minor", "service", "track"]]],
      paint: {
        "line-color": C.roadMinor,
        "line-width": ["interpolate", ["linear"], ["zoom"], 11, 0.5, 16, 1.8],
      },
    },

    // Country names bow out once regional detail arrives, rather than stacking under it.
    {
      id: "label-country",
      type: "symbol",
      source: SOURCE,
      "source-layer": "place",
      minzoom: 2,
      maxzoom: 7.5,
      filter: ["==", ["get", "class"], "country"],
      layout: {
        "text-field": NAME,
        "text-font": FONT,
        "text-transform": "uppercase",
        "text-letter-spacing": 0.18,
        "text-size": ["interpolate", ["linear"], ["zoom"], 3, 10, 6, 13],
        "text-max-width": 6,
      },
      paint: { "text-color": C.labelFaint, "text-halo-color": C.halo, "text-halo-width": 1 },
    },
    // Cities split by rank so the big ones show early and the rest wait their turn.
    {
      id: "label-city-major",
      type: "symbol",
      source: SOURCE,
      "source-layer": "place",
      minzoom: 4,
      filter: [
        "all",
        ["==", ["get", "class"], "city"],
        ["any", ["<=", ["get", "rank"], 4], ["==", ["get", "capital"], 2]],
      ],
      layout: {
        "text-field": NAME,
        "text-font": FONT,
        "text-size": ["interpolate", ["linear"], ["zoom"], 4, 10.5, 8, 13.5],
        "text-max-width": 8,
      },
      paint: { "text-color": C.label, "text-halo-color": C.halo, "text-halo-width": 1.2 },
    },
    {
      id: "label-city",
      type: "symbol",
      source: SOURCE,
      "source-layer": "place",
      minzoom: 6.5,
      filter: ["all", ["==", ["get", "class"], "city"], [">", ["get", "rank"], 4]],
      layout: {
        "text-field": NAME,
        "text-font": FONT,
        "text-size": ["interpolate", ["linear"], ["zoom"], 6.5, 10, 9, 12],
        "text-max-width": 8,
      },
      paint: { "text-color": C.labelMinor, "text-halo-color": C.halo, "text-halo-width": 1.1 },
    },
    {
      id: "label-town",
      type: "symbol",
      source: SOURCE,
      "source-layer": "place",
      minzoom: 9,
      filter: ["in", ["get", "class"], ["literal", ["town", "village"]]],
      layout: {
        "text-field": NAME,
        "text-font": FONT,
        "text-size": ["interpolate", ["linear"], ["zoom"], 9, 9.5, 13, 12],
        "text-max-width": 8,
      },
      paint: { "text-color": C.labelMinor, "text-halo-color": C.halo, "text-halo-width": 1.1 },
    },
    // Hamlets and neighbourhoods are pure clutter on a world view, but they are what
    // orients you once you are zoomed to a single sensor. Hence their own late tier.
    {
      id: "label-neighbourhood",
      type: "symbol",
      source: SOURCE,
      "source-layer": "place",
      minzoom: 13,
      filter: ["in", ["get", "class"], ["literal", ["suburb", "hamlet", "neighbourhood"]]],
      layout: {
        "text-field": NAME,
        "text-font": FONT,
        "text-size": ["interpolate", ["linear"], ["zoom"], 13, 9.5, 16, 11.5],
        "text-max-width": 8,
      },
      paint: { "text-color": C.labelFaint, "text-halo-color": C.halo, "text-halo-width": 1 },
    },
  ],
}
