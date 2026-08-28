import { Get, Post } from "../../helpers/request";

/**
 * The one client for /api/qualitycontrol/log.
 *
 * Replaces the two near-identical `log` entries that lived in the verify and
 * validate view services. Both pages now page through the same endpoint the same
 * way, which is what makes a shared history popup possible.
 */
const Service = {
  /**
   * @param {object}   p
   * @param {string}   p.samplingPointId
   * @param {string}  [p.fromDt]          period overlap filter; applied only with toDt
   * @param {string}  [p.toDt]
   * @param {number}  [p.limit=50]        counts VISIBLE rows — filtering happens in SQL
   * @param {number}  [p.offset=0]
   * @param {string[]}[p.disabledRules]   rule ids switched off for this session only
   */
  log: async ({ samplingPointId, fromDt, toDt, limit = 50, offset = 0, disabledRules }) => {
    const q = new URLSearchParams({
      sampling_point_id: samplingPointId,
      limit: String(limit),
      offset: String(offset),
    });
    if (fromDt && toDt) {
      q.set("from_dt", fromDt);
      q.set("to_dt", toDt);
    }
    if (disabledRules?.length) q.set("disabled_rules", disabledRules.join(","));
    return Get(`/api/qualitycontrol/log?${q.toString()}`);
  },

  preferences: async () => Get("/api/qualitycontrol/log/preferences"),
  savePreferences: async (config) => Post("/api/qualitycontrol/log/preferences", { config }),
};

export default Service;
