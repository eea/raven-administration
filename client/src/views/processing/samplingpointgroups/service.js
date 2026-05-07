import { Get, Post } from "../../../helpers/request";

const Service = {
  groups: async () => Get("/api/processing/samplingpointgroups"),
  create: async (data) => Post("/api/processing/samplingpointgroups/insert", data),
  update: async (data) => Post("/api/processing/samplingpointgroups/update", data),
  delete: async (data) => Post("/api/processing/samplingpointgroups/delete", data),
  members: async (groupId) => Get(`/api/processing/samplingpointgroups/${groupId}/members`),
  addMember: async (groupId, data) => Post(`/api/processing/samplingpointgroups/${groupId}/members/add`, data),
  removeMember: async (groupId, data) => Post(`/api/processing/samplingpointgroups/${groupId}/members/remove`, data),
  samplingpoints: async (groupId = null) => Get(`/api/processing/samplingpointgroups/lookup/samplingpoints${groupId ? `?group_id=${groupId}` : ""}`)
};

export default Service;
