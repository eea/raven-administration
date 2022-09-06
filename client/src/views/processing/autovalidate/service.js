import Request from "../../../helpers/request";

const Service = {
  get: async function () {
    const payload = {
      method: "get",
      url: "/api/processing/autovalidate"
    };
    return await Request(payload);
  },
  update: async function (data) {
    const payload = {
      method: "post",
      url: "/api/processing/autovalidate/update",
      data
    };
    return await Request(payload);
  },
  insert: async function (data) {
    const payload = {
      method: "post",
      url: "/api/processing/autovalidate/insert",
      data
    };
    return await Request(payload);
  },
  delete: async function (data) {
    const requestData = {
      method: "post",
      url: "/api/processing/autovalidate/delete",
      data: data
    };
    return Request(requestData);
  },
  pollutants: async function () {
    const requestData = {
      method: "get",
      url: "/api/processing/autovalidate/pollutants"
    };
    return Request(requestData);
  }
};

export default Service;
