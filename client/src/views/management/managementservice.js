import { Get, Post } from "../../helpers/request";

const ManagementService = {
  networks: async () => Get("/api/management/selects/network"),
  authorities: async () => Get("/api/management/selects/authorities"),
  levels: async () => Get("/api/management/selects/levels"),
  media: async () => Get("/api/management/selects/media"),
  timezones: async () => Get("/api/management/selects/timezones"),
  measurement_regimes: async () => Get("/api/management/selects/measurementregimes"),
  area_classifications: async () => Get("/api/management/selects/areaclassifications")
};

export default ManagementService;
