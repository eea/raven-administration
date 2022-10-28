import axios from "axios";
import Auth from "./auth";

const Interceptor = {
  response: async function () {
    axios.interceptors.response.use(
      (response) => {
        return response;
      },
      (error) => {
        if (401 === error.response.status) {
          Auth.signout();
          window.location.href = "/login";
        } else if (403 === error.response.status) {
          window.location.href = "/forbidden";
        } else if (404 === error.response.status && !error.response.request.responseURL.toLowerCase().includes("api")) {
          window.location.href = "/notfound";
        } else {
          return Promise.reject(error);
        }
      }
    );
  },
  request: async function () {
    axios.interceptors.request.use(
      (config) => {
        const token = Auth.getToken();
        const auth = token ? `Bearer ${token}` : "";
        config.headers.common["Authorization"] = auth;
        return config;
      },
      (error) => Promise.reject(error)
    );
  },
  default: async function () {
    axios.defaults.headers.common = {
      Accept: "application/json"
    };
  }
};

export default Interceptor;
