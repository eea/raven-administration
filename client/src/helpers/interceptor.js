import axios from "axios";
import Auth from "./auth";

const Interceptor = {
  response: async function () {
    axios.interceptors.response.use(
      (response) => {
        // is it a file?
        if (response.data instanceof Blob) {
          const filename = response.headers["content-disposition"].split("filename=")[1];
          const href = URL.createObjectURL(response.data);

          const link = document.createElement("a");
          link.href = href;
          link.setAttribute("download", filename);
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
          URL.revokeObjectURL(href);
        } else return response;
      },
      (error) => {
        if (error.response && (401 === error.response.status || 422 === error.response.status)) {
          Auth.signout();
          window.location.href = "/login";
        } else if (error.response && 403 === error.response.status) {
          window.location.href = "/forbidden";
        } else if (error.response && 404 === error.response.status && !error.response.request.responseURL.toLowerCase().includes("api")) {
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
        config.headers["Authorization"] = auth;
        return config;
      },
      (error) => Promise.reject(error)
    );
  },
  default: async function () {
    axios.defaults.headers = {
      Accept: "application/json"
    };
  }
};

export default Interceptor;
