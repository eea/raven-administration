import axios from "axios";
import ErrorParser from "./error.parser";
import Eventy from "../helpers/eventy";

export const Request = async (payload) => {
  try {
    Eventy.showProgress();
    const response = await axios(payload);
    Eventy.hideProgress();
    if (response) return response.data;
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

export const Download = async (url) => {
  const payload = {
    method: "get",
    url: url,
    responseType: "blob"
  };
  return await Request(payload);
};

export default Request;
