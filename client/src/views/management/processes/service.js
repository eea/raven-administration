import { Get, Post, Upload, Download } from "../../../helpers/request";

const Service = {
  get: async () => Get("/api/management/processes"),
  update: async (data) => Post("/api/management/processes/update", data),
  insert: async (data) => Post("/api/management/processes/insert", data),
  delete: async (data) => Post("/api/management/processes/delete", data),
  upload: async (data) => Upload("/api/imports/processes", data),
  download: async () => Download("/api/exports/processes"),

  timesteps: async () => Get("/api/management/lookups/timesteps?type=uom"),
  authorities: async () => Get("/api/management/lookups/authorities"),
  concentrations: async () => Get("/api/management/lookups/concentrations"),
  measurement_types: async () => Get("/api/management/lookups/measurementtypes"),
  measurement_methods: async () => Get("/api/management/lookups/measurementmethods"),
  measurement_equipment: async () => Get("/api/management/lookups/measurementequipment"),
  equiv_demonstrations: async () => Get("/api/management/lookups/equivdemonstrations")
};

export default Service;
