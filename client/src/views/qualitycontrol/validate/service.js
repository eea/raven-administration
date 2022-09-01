import Request from "../../../helpers/request";

const Service = {
  get: async function (data) {
    const requestData = {
      method: "post",
      url: "/api/qualitycontrol/validate/timevalues",
      data,
    };
    return Request(requestData);
  },
  timeseries: async function () {
    const requestData = {
      method: "get",
      url: "/api/qualitycontrol/validate/timeseries",
    };
    return Request(requestData);
  },
  validate: async function (data) {
    const requestData = {
      method: "post",
      url: "/api/qualitycontrol/validate/flag",
      data,
    };
    return Request(requestData);
  },
};

export default Service;
