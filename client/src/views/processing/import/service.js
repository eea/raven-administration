import { Upload } from "../../../helpers/request";

const Service = {
  upload: async (data) => Upload("/api/imports/observations", data)
};

export default Service;
