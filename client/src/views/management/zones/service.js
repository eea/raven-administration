import Request from "../../../helpers/request";

const Service = {
  get: async function () {
    const payload = {
      method: "get",
      url: "/api/management/zones",
    };
    return await Request(payload);
  },
  update: async function (data) {
    const payload = {
      method: "post",
      url: "/api/management/zones/update",
      data,
    };
    return await Request(payload);
  },
  insert: async function (data) {
    const payload = {
      method: "post",
      url: "/api/management/zones/insert",
      data,
    };
    return await Request(payload);
  },
  delete: async function (data) {
    const requestData = {
      method: "post",
      url: "/api/management/zones/delete",
      data: data,
    };
    return Request(requestData);
  },
  authorities: async function () {
    const payload = {
      method: "get",
      url: "/api/management/zones/authorities",
    };
    return await Request(payload);
  },
  types: async function () {
    const payload = {
      method: "get",
      url: "/api/management/zones/types",
    };
    return await Request(payload);
  },
};

export default Service;
