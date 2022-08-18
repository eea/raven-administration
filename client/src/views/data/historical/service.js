import Request from "../../../helpers/request"

const Service = {
    get: async function (data) {
        const requestData = {
            method: "post",
            url: "/api/data/historical",
            data
        };
        return Request(requestData);
    },
    timeseries: async function () {
        const requestData = {
            method: "get",
            url: "/api/data/historical/timeseries"
        };
        return Request(requestData);
    }
};

export default Service;
