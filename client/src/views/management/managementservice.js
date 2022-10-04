import { Get, Post } from "../../helpers/request";

const ManagementService = {
  networks: async () => Get("/api/management/selects/network"),
  authorities: async () => Get("/api/management/selects/authorities"),
  levels: async () => Get("/api/management/selects/levels"),
  media: async () => Get("/api/management/selects/media"),
  timezones: async () => Get("/api/management/selects/timezones"),
  measurement_regimes: async () => Get("/api/management/selects/measurementregimes"),
  area_classifications: async () => Get("/api/management/selects/areaclassifications"),
  stations: async () => Get("/api/management/selects/stations"),
  station_classifications: async () => Get("/api/management/selects/stationclassifications"),
  pollutants: async () => Get("/api/management/selects/pollutants"),
  concentrations: async () => Get("/api/management/selects/concentrations"),
  timesteps: async () => Get("/api/management/selects/timesteps"),
  assessment_types: async () => Get("/api/management/selects/assessmenttypes")
};

export default ManagementService;
