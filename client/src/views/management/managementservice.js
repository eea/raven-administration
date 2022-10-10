import { Get, Post } from "../../helpers/request";

const ManagementService = {
  area_classifications: async () => Get("/api/management/selects/areaclassifications"),
  assessment_exceedances: async () => Get("/api/management/selects/assessmentexceedances"),
  assessment_types: async () => Get("/api/management/selects/assessmenttypes"),
  authorities: async () => Get("/api/management/selects/authorities"),
  concentrations: async () => Get("/api/management/selects/concentrations"),
  equiv_demonstrations: async () => Get("/api/management/selects/equivdemonstrations"),
  levels: async () => Get("/api/management/selects/levels"),
  media: async () => Get("/api/management/selects/media"),
  measurement_regimes: async () => Get("/api/management/selects/measurementregimes"),
  measurement_types: async () => Get("/api/management/selects/measurementtypes"),
  measurement_methods: async () => Get("/api/management/selects/measurementmethods"),
  measurement_equipment: async () => Get("/api/management/selects/measurementequipment"),
  networks: async () => Get("/api/management/selects/network"),
  pollutants: async () => Get("/api/management/selects/pollutants"),
  processes: async () => Get("/api/management/selects/processes"),
  processtype_values: async () => Get("/api/management/selects/processtypevalues"),
  responsible_authorities: async () => Get("/api/management/selects/responsibleauthorities"),
  result_nature_values: async () => Get("/api/management/selects/resultnaturevalues"),
  samples: async () => Get("/api/management/selects/samples"),
  samplingpoints: async () => Get("/api/management/selects/samplingpoints"),
  stations: async () => Get("/api/management/selects/stations"),
  station_classifications: async () => Get("/api/management/selects/stationclassifications"),
  timesteps: async () => Get("/api/management/selects/timesteps"),
  timezones: async () => Get("/api/management/selects/timezones"),
  zones: async () => Get("/api/management/selects/zones")
};

export default ManagementService;
