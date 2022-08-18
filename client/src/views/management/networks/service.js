import Request from "../../../helpers/request"

const Service = {
    get: async function () {
        const payload = {
            method: "get",
            url: "/api/management/networks",
        };
        return await Request(payload);
    },
    update: async function (data) {
        const payload = {
            method: "post",
            url: "/api/management/networks/update",
            data
        };
        return await Request(payload);
    },
    insert: async function (data) {
        const payload = {
            method: "post",
            url: "/api/management/networks/insert",
            data
        };
        return await Request(payload);
    },
    delete: async function (data) {
        const requestData = {
            method: "post",
            url: "/api/management/networks/delete",
            data: data
        };
        return Request(requestData);
    },
    authorities: async function () {
        const payload = {
            method: "get",
            url: "/api/management/networks/authorities",
        };
        return await Request(payload);
    },
    levels: async function () {
        const payload = {
            method: "get",
            url: "/api/management/networks/levels",
        };
        return await Request(payload);
    },
    media: async function () {
        const payload = {
            method: "get",
            url: "/api/management/networks/media",
        };
        return await Request(payload);
    },
    timezones: async function () {
        const payload = {
            method: "get",
            url: "/api/management/networks/timezones",
        };
        return await Request(payload);
    },

}

export default Service;