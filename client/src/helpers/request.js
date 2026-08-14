import axios from "axios";
import ErrorParser from "./error.parser";
import Eventy from "../helpers/eventy";

// `raw` returns the whole axios response instead of just its body, for the few
// callers that need the response headers (the AQR3 ZIP reports which tables were
// empty in one). Everything else keeps getting the body.
export const Request = async (payload, { raw = false } = {}) => {
  try {
    Eventy.showProgress();
    const response = await axios(payload);
    Eventy.hideProgress();
    if (response) return raw ? response : response.data;
  } catch (error) {
    console.log("ERR", error);
    const message = ErrorParser.asMessage(error);
    Eventy.failProgress();
    Eventy.showHideMessage(message, "error", 60000);
    throw new Error(message);
  }
};

export const Get = async (url) => {
  const payload = {
    method: "get",
    url: url
  };
  return await Request(payload);
};

export const Post = async (url, data) => {
  const payload = {
    method: "post",
    url: url,
    data: data
  };
  return await Request(payload);
};

export const Upload = async (url, data) => {
  const payload = {
    method: "post",
    url: url,
    headers: { "Content-Type": "multipart/form-data" },
    data: data
  };
  return await Request(payload);
};

export const Download = async (url, data) => {
  const payload = {
    method: "post",
    url: url,
    responseType: "blob",
    data: data
  };
  return await Request(payload);
};

// Same download, but resolves to the full response so the caller can read
// headers. The file is still saved by the response interceptor.
export const DownloadWithHeaders = async (url, data) => {
  const payload = {
    method: "post",
    url: url,
    responseType: "blob",
    data: data
  };
  return await Request(payload, { raw: true });
};

export const DownloadGet = async (url) => {
  const payload = {
    method: "get",
    url: url,
    responseType: "blob"
  };
  return await Request(payload);
};

export const Delete = async (url) => {
  const payload = {
    method: "delete",
    url: url
  };
  return await Request(payload);
};

export const Put = async (url, data) => {
  const payload = {
    method: "put",
    url: url,
    data: data
  };
  return await Request(payload);
};

export default Request;
