import Request from "./request"

const Auth = {
    isAuth() {
        var token = sessionStorage.getItem("token");
        return token ? true : false;
    },
    getToken() {
        return sessionStorage.getItem("token")
    },
    async signin(username, password) {
        const payload = {
            method: "post",
            url: "/api/auth/signin",
            data: { username, password }
        };
        var resp = await Request(payload);
        sessionStorage.setItem("token", resp.token);
    },
    signout() {
        sessionStorage.removeItem("token");
    },
    async me() {
        const payload = {
            method: "get",
            url: "/api/auth/me"
        };
        return await Request(payload);
    }
}

export default Auth;