import { Post } from "./request";

const Auth = {
  isAuth() {
    var token = sessionStorage.getItem("token");
    return token ? true : false;
  },
  getToken() {
    return sessionStorage.getItem("token");
  },
  async signin(username, password) {
    var resp = Post("/api/auth/signin", { username, password });
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
