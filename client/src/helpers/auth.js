import { jwtDecode } from "jwt-decode";
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
  // Decoded token claims (management, data, processing, exporting, allnetworks, networks,
  // name), or {} when not signed in. For hiding controls whose endpoint would reject the
  // call — the API verifies every claim itself, this only avoids provoking a 403 the
  // response interceptor turns into a redirect to /forbidden.
  claims() {
    const token = Auth.getToken();
    if (!token || token == "undefined" || token == "null") return {};
    try {
      return jwtDecode(token);
    } catch {
      return {};
    }
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
