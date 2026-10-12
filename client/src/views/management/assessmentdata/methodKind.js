// CAM_07 AssessmentType decides which kind of CAM_05 AssessmentMethodId a link names.
// The same rule as _method_mismatch in api/endpoints/management/assessmentdata/routes.py,
// which refuses anything else -- this only keeps the forms from offering it.
//
//   fixed, fixedrandom, indicative, other  -> a sampling point (measured)
//   model                                  -> a MOD_ model
//   objective                              -> an OBE_ model (objective estimation)

export const MEASUREMENT_TYPES = ["fixed", "fixedrandom", "indicative", "other"];
export const MODEL_PREFIX = { model: "MOD_", objective: "OBE_" };

// "sampling_point" | "model" | "objective" | null (no type chosen, or one unknown here)
export const methodKind = (type) => {
  if (MEASUREMENT_TYPES.includes(type)) return "sampling_point";
  if (type in MODEL_PREFIX) return type;
  return null;
};

// What the method field is called for a type.
export const methodLabel = (type) =>
  ({ sampling_point: "Sampling Point", model: "Model (MOD_)", objective: "Objective Estimation (OBE_)" })[
    methodKind(type)
  ] ?? "Assessment Method";

export const modelMatches = (type, id) => !!id && id.startsWith(MODEL_PREFIX[type] ?? "\u0000");

// Does this method fit this type?
export const fits = (type, { sampling_point_id, model_id }) => {
  const kind = methodKind(type);
  if (kind === "sampling_point") return !!sampling_point_id && !model_id;
  if (kind) return !sampling_point_id && modelMatches(kind, model_id);
  return false;
};

// The assessment types an existing link's method can carry. Its method is fixed once
// the link exists in the regime sub-table, so this is the whole choice there.
export const typesFor = (types, { sampling_point_id, model_id }) =>
  types.filter((t) =>
    sampling_point_id ? MEASUREMENT_TYPES.includes(t.value) : modelMatches(t.value, model_id)
  );
