import Request from "../../../helpers/request"

const Service = {
    get: async function (data) {
        const requestData = {
            method: "get",
            url: "/api/data/latest",
            data
        };
        return Request(requestData);
    }
};

export default Service;
