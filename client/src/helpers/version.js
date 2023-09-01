import { Get } from "./request";

const Version = {
  compare(v1, v2) {
    if (typeof v1 !== "string") return false;
    if (typeof v2 !== "string") return false;
    v1 = v1.split(".");
    v2 = v2.split(".");
    const k = Math.min(v1.length, v2.length);
    for (let i = 0; i < k; ++i) {
      v1[i] = parseInt(v1[i], 10);
      v2[i] = parseInt(v2[i], 10);
      if (v1[i] > v2[i]) return 1;
      if (v1[i] < v2[i]) return -1;
    }
    return v1.length == v2.length ? 0 : v1.length < v2.length ? -1 : 1;
  },
  async get() {
    try {
      var result = await Get("/api/version");
      var compared = Version.compare(result.latest, result.current);
      return { current: result.current, isLatest: compared != 1 };
    } catch (error) {
      return { current: result.current, isLatest: true };
    }
  }
};

export default Version;
