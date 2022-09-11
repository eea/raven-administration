import { Post } from "./request";

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
    if (!resp.token) throw Error("Internal error. Could not get a valid response");
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
};

export default Auth;
