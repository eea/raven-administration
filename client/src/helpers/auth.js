import { Post, Get } from "./request";

const Auth = {
  isAuth() {
    var token = sessionStorage.getItem("token");
    if (!token || token == "undefined" || token == "null") return false;
    return true;
  },
  getToken() {
    return sessionStorage.getItem("token");
  },
  async signin(username, password) {
    var resp = await Post("/api/auth/signin", { username, password });
    if (!resp.token) throw Error("Internal error. Could not get a valid token");
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
  },
  async canCreateAdmin() {
    const resp = await Get("/api/auth/cancreateadmin");
    return resp.cancreateadmin;
  },
  async create(password) {
    await Post("/api/auth/create", { password });
  }
};

export default Auth;
