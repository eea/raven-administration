import Request from "../../../helpers/request";

const Service = {
  get: async function () {
    const requestData = {
      method: "get",
      url: "/api/processing/convert"
    };
    return Request(requestData);
  },
  insert: async function (data) {
    const requestData = {
      method: "post",
      url: "/api/processing/convert/insert",
      data: data
    };
    return Request(requestData);
  },
  update: async function (data) {
    const requestData = {
      method: "post",
      url: "/api/processing/convert/update",
      data: data
    };
    return Request(requestData);
  },
  delete: async function (data) {
    const requestData = {
      method: "post",
      url: "/api/processing/convert/delete",
      data: data
    };
    return Request(requestData);
  },
  units: async function () {
    const requestData = {
      method: "get",
      url: "/api/processing/convert/units"
    };
    return Request(requestData);
  },
  timeseries: async function () {
    const requestData = {
      method: "get",
      url: "/api/processing/convert/timeseries"
    };
    return Request(requestData);
  }
};

export default Service;
