import Request from "../../../helpers/request"

const Service = {
    get: async function () {
        const payload = {
            method: "get",
            url: "/api/management/authorities",
        };
        return await Request(payload);
    },
    update: async function (data) {
        const payload = {
            method: "post",
            url: "/api/management/authorities/update",
            data
        };
        return await Request(payload);
    },
    insert: async function (data) {
        const payload = {
            method: "post",
            url: "/api/management/authorities/insert",
            data
        };
        return await Request(payload);
    },
    delete: async function (data) {
        const requestData = {
            method: "post",
            url: "/api/management/authorities/delete",
            data: data
        };
        return Request(requestData);
    }
}

export default Service;