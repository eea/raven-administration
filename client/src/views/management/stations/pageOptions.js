const pageOptions = (lookups) => ({
  showRequiredAndoptionalSideBySideInCrud: true,
  properties: [
    // REQUIRED
    { type: "text", label: "Id", prop: "id", placeholder: "str: A unique id", required: true, default: null, showInEdit: false, showInGrid: true },
    { type: "text", label: "Name", prop: "name", placeholder: "str: Name of authority", required: true, default: null, showInEdit: true, showInGrid: true },

    { type: "lookup", label: "Network", prop_id: "network_id", prop: "network", lookup: "networks", required: true, default: null, showInEdit: true, showInGrid: true },
    { type: "lookup", label: "Area classification", prop_id: "area_classification_id", prop: "area_classification", required: true, lookup: "areaclassifications", default: null, showInEdit: true, showInGrid: true },
    { type: "lookup", label: "Media monitored", prop_id: "media_id", prop: "media", required: true, lookup: "media", default: null, showInEdit: true, showInGrid: false },
    { type: "lookup", label: "Measurement regime", prop_id: "measurement_regime_id", prop: "measurement_regime", required: true, lookup: "measurementregimes", default: null, showInEdit: true, showInGrid: false },

    { type: "text", label: "Eoi", prop: "eoi_code", placeholder: "str: Eoi Code", required: true, default: null, showInEdit: true, showInGrid: false },

    { type: "number", label: "Longitude", prop: "longitude", placeholder: "float: Longitude", required: true, default: null, showInEdit: true, showInGrid: false },
    { type: "number", label: "Latitude", prop: "latitude", placeholder: "float: Latitude", required: true, default: null, showInEdit: true, showInGrid: false },
    { type: "number", label: "Altitude", prop: "altitude", placeholder: "float: Altitude", required: true, default: null, showInEdit: true, showInGrid: false },
    { type: "number", label: "Epsg", prop: "epsg", placeholder: "int: Epsg", required: true, default: null, showInEdit: true, showInGrid: false },

    { type: "text", label: "Begin", prop: "begin_position", placeholder: "str: YYYY-MM-DDTHH:mm:ssZ", required: true, default: null, showInEdit: true, showInGrid: false },

    { type: "checkbox", label: "Mobile", prop: "mobile", required: true, default: false, showInEdit: true, showInGrid: false },

    // OPTIONAL
    { type: "text", label: "National Station Code", prop: "national_station_code", placeholder: "str: National station code", required: false, default: null, showInEdit: true, showInGrid: false },
    { type: "text", label: "Municipality", prop: "municipality", placeholder: "str: Municipality", required: false, default: null, showInEdit: true, showInGrid: false },
    { type: "text", label: "City", prop: "city", placeholder: "str: City", required: false, default: null, showInEdit: true, showInGrid: false },
    { type: "number", label: "Street Width", prop: "street_Width", placeholder: "int: Street Width", required: false, default: null, showInEdit: true, showInGrid: false },
    { type: "number", label: "Distance Junction", prop: "distance_junction", placeholder: "int: Distance Junction", required: false, default: null, showInEdit: true, showInGrid: false },
    { type: "number", label: "Traffic Volume", prop: "traffic_volume", placeholder: "int: Traffic Volume", required: false, default: null, showInEdit: true, showInGrid: false },
    { type: "number", label: "Heavy Duty Fraction", prop: "heavy_duty_fraction", placeholder: "float: Heavy Duty Fraction", required: false, default: null, showInEdit: true, showInGrid: false },
    { type: "number", label: "Height Facade", prop: "height_facade", placeholder: "float: Height Facade", required: false, default: null, showInEdit: true, showInGrid: false },
    { type: "text", label: "End", prop: "end_position", placeholder: "str: YYYY-MM-DDTHH:mm:ssZ", required: false, default: null, showInEdit: true, showInGrid: false },

    // OTHER
    {
      type: "gridOnly",
      label: "Referenced by",
      prop: "ref_count",
      default: 0,
      showInGrid: true,
      cls_func: (row) => (row.ref_count == 0 ? "text-nord11" : "text-nord10")
    }
  ],
  lookups: lookups
});

export default pageOptions;
