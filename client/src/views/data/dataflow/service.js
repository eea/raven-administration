import { Get, Post } from "../../../helpers/request";

const Service = {
  dataflow: async (type, year, timezone, description) => Get(`/api/dataflow?type=${type}&year=${year}&timezone=${timezone}&description=${description}`)
};

export default Service;
