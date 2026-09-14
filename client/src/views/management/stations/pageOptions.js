const HELP_REPORT = {
  help:
    "Whether this site is part of the EEA reporting obligation. Raven holds " +
    "industrial, internal and research stations that are monitored operationally " +
    "and never reported; this is where you say so.\n" +
    "Off means the station and all of its sampling points are left out of every " +
    "AQR3 table. On is not enough on its own: the station also needs an EoI code, " +
    "because AQR3 is keyed on it. A station marked for reporting without one is " +
    "listed on the Dataflow page rather than dropped in silence."
};

const HELP_EOI = {
  help:
    "AQR3 STA_02 StationEoICode, assigned by EIONET. Leave it empty for a site " +
    "that has none — an industrial or internal monitoring point. It is an " +
    "identifier, not a decision: whether the station is reported is the EEA " +
    "Reporting checkbox.\n" +
    "It cannot be changed once reported: the guide says a station keeps its EoI " +
    "code even after a significant relocation."
};

const pageOptions = (lookups) => ({
  entityName: "Station",
  showRequiredAndoptionalSideBySideInCrud: false,
  properties: [
    // REQUIRED
    { type: "text", label: "Id", prop: "id", placeholder: "str: A unique id", required: true, default: null, enableInEdit: false, showInGrid: true },
    { type: "text", label: "Name", prop: "name", placeholder: "str: Name of station", required: true, default: null, enableInEdit: true, showInGrid: true },
    { type: "text", label: "National Code", prop: "station_national_code", placeholder: "str: National station code", required: true, default: null, enableInEdit: true, showInGrid: false },
    { type: "number", label: "Latitude", prop: "latitude", placeholder: "float: Latitude", required: true, default: null, enableInEdit: true, showInGrid: false },
    { type: "number", label: "Longitude", prop: "longitude", placeholder: "float: Longitude", required: true, default: null, enableInEdit: true, showInGrid: false },
    { type: "number", label: "Altitude", prop: "altitude", placeholder: "float: Altitude (meters)", required: true, default: null, enableInEdit: true, showInGrid: false },
    { type: "lookup", label: "Area", prop: "station_area", prop_id: "station_area_id", lookup: "areaclassifications", required: true, default: null, enableInEdit: true, showInGrid: true },
    { type: "lookup", label: "Network", prop: "network", prop_id: "network_id", lookup: "networks", required: true, default: null, enableInEdit: true, showInGrid: true },
    { type: "checkbox", label: "Supersite", prop: "supersite", required: true, default: false, enableInEdit: true, showInGrid: true },
    { type: "lookup", label: "Document", prop: "document", prop_id: "document_id", lookup: "documents", required: true, default: null, enableInEdit: true, showInGrid: false },

    // OPTIONAL
    // Both of these were required until 4.502.22. An EoI code is assigned by EIONET,
    // so a site outside the reporting obligation has none, and demanding one here was
    // why 66 of 174 stations on the development database carry an invented code.
    { type: "checkbox", label: "EEA Reporting", prop: "report_to_eea", ...HELP_REPORT, required: false, default: true, enableInEdit: true, showInGrid: true },
    { type: "text", label: "EoI Code", prop: "station_eoi_code", placeholder: "str: EOI code, empty if the site has none", ...HELP_EOI, required: false, default: null, enableInEdit: true, showInGrid: true }
  ],
  lookups: lookups
});

export default pageOptions;
