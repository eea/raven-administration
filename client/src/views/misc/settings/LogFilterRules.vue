<script setup>
/**
 * Administrator editor for the Observation Change History filter rules.
 *
 * These are the instance-wide defaults. A QC user can switch individual rules on or
 * off from the history's own funnel menu, but only an administrator authors them —
 * which is why this lives under Settings, behind management + allnetworks.
 *
 * The field list is assembled client-side from core's own constants plus whatever
 * `filterFields` the installed plugins declare, so a plugin's column becomes
 * filterable here without core knowing anything about it. The server validates every
 * field against its own registry regardless; this list is for the dropdown, not for
 * trust.
 */
import { ref, computed, watch } from "vue";
import Popup from "../../../components/Popup.vue";
import IconClose from "~icons/mdi/close";
import {
  SOURCE_OPTIONS, VERIFICATION_OPTIONS, VALIDITY_OPTIONS,
} from "../../../components/observationlog/labels";

const props = defineProps({
  modelValue: { type: Object, default: () => ({}) },
});
const emit = defineEmits(["update:modelValue"]);

const rules = computed(() => props.modelValue?.rules ?? []);

/** Core filter fields. Kinds and ops mirror api/core/observation_log_filters.py. */
const CORE_FIELDS = [
  { key: "change_source", label: "Source", kind: "text", options: SOURCE_OPTIONS },
  { key: "changed_by", label: "Changed by", kind: "text" },
  { key: "old_verification", label: "Verification (old)", kind: "int", options: VERIFICATION_OPTIONS },
  { key: "new_verification", label: "Verification (new)", kind: "int", options: VERIFICATION_OPTIONS },
  { key: "old_validity", label: "Validity (old)", kind: "int", options: VALIDITY_OPTIONS },
  { key: "new_validity", label: "Validity (new)", kind: "int", options: VALIDITY_OPTIONS },
  { key: "old_value", label: "Value (old)", kind: "numeric" },
  { key: "new_value", label: "Value (new)", kind: "numeric" },
];

const OPS_BY_KIND = {
  text: ["eq", "ne", "in", "not_in", "contains", "not_contains", "empty", "not_empty"],
  int: ["eq", "ne", "in", "not_in", "empty", "not_empty"],
  numeric: ["eq", "ne", "between", "empty", "not_empty"],
  datetime: ["between", "empty", "not_empty"],
};

const OP_LABELS = {
  eq: "is", ne: "is not", in: "is one of", not_in: "is not one of",
  contains: "contains", not_contains: "does not contain",
  empty: "is empty", not_empty: "is not empty", between: "is between",
};

const pluginFields = computed(() =>
  Object.values(window.__ravenPlugins || {}).flatMap(
    (p) => p.observationLogExtension?.filterFields ?? []
  )
);

const allFields = computed(() => [...CORE_FIELDS, ...pluginFields.value]);
const fieldByKey = (key) => allFields.value.find((f) => f.key === key);
const opsFor = (key) => {
  const f = fieldByKey(key);
  if (!f) return [];
  return f.ops ?? OPS_BY_KIND[f.kind] ?? [];
};
const needsValue = (op) => op !== "empty" && op !== "not_empty";

// ---------------------------------------------------------------------------
// Editing
// ---------------------------------------------------------------------------

const showEditor = ref(false);
const draft = ref(null);

// Short random slug. Stable ids matter because user_log_preferences.rule_overrides
// references them: an array index would silently re-point every user's setting the
// moment a rule is reordered or deleted.
const newId = () => Math.random().toString(36).slice(2, 8);

const blankCondition = () => ({ field: "change_source", op: "eq", value: "" });

const openNew = () => {
  draft.value = {
    id: newId(), label: "", action: "hide", enabled_by_default: true,
    match: "all", conditions: [blankCondition()],
  };
  showEditor.value = true;
};

const openEdit = (rule) => {
  draft.value = JSON.parse(JSON.stringify(rule));
  showEditor.value = true;
};

const commit = (nextRules) =>
  emit("update:modelValue", { ...(props.modelValue ?? {}), rules: nextRules });

const saveDraft = () => {
  const d = draft.value;
  if (!d.label.trim()) d.label = describe(d) || "Untitled rule";
  const next = rules.value.some((r) => r.id === d.id)
    ? rules.value.map((r) => (r.id === d.id ? d : r))
    : [...rules.value, d];
  commit(next);
  showEditor.value = false;
};

const removeRule = (rule) => commit(rules.value.filter((r) => r.id !== rule.id));

const toggleDefault = (rule) =>
  commit(rules.value.map((r) =>
    r.id === rule.id ? { ...r, enabled_by_default: !r.enabled_by_default } : r));

const addCondition = () => draft.value.conditions.push(blankCondition());
const removeCondition = (i) => draft.value.conditions.splice(i, 1);

/** Reset op and value when the field changes, so an impossible pair cannot be saved. */
const onFieldChange = (condition) => {
  const ops = opsFor(condition.field);
  if (!ops.includes(condition.op)) condition.op = ops[0];
  condition.value = "";
};

const describe = (rule) =>
  (rule.conditions ?? [])
    .map((c) => {
      const f = fieldByKey(c.field);
      const name = f?.label ?? c.field;
      const op = OP_LABELS[c.op] ?? c.op;
      if (!needsValue(c.op)) return `${name} ${op}`;
      const opts = f?.options;
      const pretty = (v) => opts?.find((o) => String(o.value) === String(v))?.label ?? v;
      return `${name} ${op} ${Array.isArray(c.value) ? c.value.map(pretty).join(", ") : pretty(c.value)}`;
    })
    .join(rule.match === "any" ? " or " : " and ");

// `in` / `not_in` take a list; the input is comma-separated for compactness.
const listValue = (condition) =>
  Array.isArray(condition.value) ? condition.value.join(", ") : condition.value ?? "";
const setListValue = (condition, raw) => {
  condition.value = String(raw).split(",").map((s) => s.trim()).filter(Boolean);
};

watch(showEditor, (open) => { if (!open) draft.value = null; });
</script>

<template>
  <div>
    <div class="flex items-center justify-between">
      <label class="font-bold">Observation log filters</label>
      <button class="button" @click="openNew">Add rule</button>
    </div>
    <div class="text-sm text-nord3 mb-2">
      Instance defaults for the Observation Change History. Users can switch individual
      rules off from the history's filter menu.
    </div>

    <div v-if="!rules.length" class="text-sm text-nord3 py-2">
      No rules — the full history is shown to everyone.
    </div>

    <table v-else class="table w-full text-sm">
      <thead>
        <tr>
          <th>Rule</th>
          <th>Action</th>
          <th class="whitespace-nowrap">On by default</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="rule in rules" :key="rule.id">
          <td>
            <div>{{ rule.label }}</div>
            <div class="text-xs text-nord3">{{ describe(rule) }}</div>
          </td>
          <td>
            <span class="px-1.5 py-0.5 rounded text-xs font-medium"
                  :class="rule.action === 'keep' ? 'bg-nord14/20 text-nord14' : 'bg-nord11/20 text-nord11'">
              {{ rule.action === "keep" ? "show only" : "hide" }}
            </span>
          </td>
          <td>
            <input type="checkbox" :checked="rule.enabled_by_default !== false"
                   @change="toggleDefault(rule)" />
          </td>
          <td class="text-right whitespace-nowrap">
            <button class="button" @click="openEdit(rule)">Edit</button>
            <button class="button ml-1" @click="removeRule(rule)">Delete</button>
          </td>
        </tr>
      </tbody>
    </table>

    <popup :show="showEditor" title="Filter rule" @on-close="showEditor = false" class="max-w-2xl w-full">
      <div v-if="draft" class="flex flex-col gap-3">
        <div>
          <label class="font-bold">Name</label>
          <input class="input w-full" v-model="draft.label" placeholder="e.g. ADACS imports" />
        </div>

        <div class="flex gap-3">
          <div class="flex-1">
            <label class="font-bold">Action</label>
            <select class="select w-full" v-model="draft.action">
              <option value="hide">Hide matching entries</option>
              <option value="keep">Show only matching entries</option>
            </select>
          </div>
          <div class="flex-1">
            <label class="font-bold">Match</label>
            <select class="select w-full" v-model="draft.match">
              <option value="all">All conditions</option>
              <option value="any">Any condition</option>
            </select>
          </div>
          <div class="flex-1">
            <label class="font-bold">On by default</label>
            <div class="pt-2">
              <input type="checkbox" v-model="draft.enabled_by_default" />
            </div>
          </div>
        </div>

        <div>
          <div class="flex items-center justify-between">
            <label class="font-bold">Conditions</label>
            <button class="button" @click="addCondition">Add condition</button>
          </div>
          <div v-for="(c, i) in draft.conditions" :key="i" class="flex gap-2 items-center mt-2">
            <select class="select flex-1" v-model="c.field" @change="onFieldChange(c)">
              <option v-for="f in allFields" :key="f.key" :value="f.key">{{ f.label }}</option>
            </select>
            <select class="select w-40" v-model="c.op">
              <option v-for="op in opsFor(c.field)" :key="op" :value="op">{{ OP_LABELS[op] ?? op }}</option>
            </select>

            <template v-if="needsValue(c.op)">
              <input v-if="c.op === 'between'" class="input w-24" v-model="c.from" placeholder="from" />
              <input v-if="c.op === 'between'" class="input w-24" v-model="c.to" placeholder="to" />
              <input
                v-else-if="c.op === 'in' || c.op === 'not_in'"
                class="input flex-1"
                :value="listValue(c)"
                placeholder="comma separated"
                @input="setListValue(c, $event.target.value)"
              />
              <select
                v-else-if="fieldByKey(c.field)?.options"
                class="select flex-1"
                v-model="c.value"
              >
                <option v-for="o in fieldByKey(c.field).options" :key="o.value" :value="o.value">
                  {{ o.label }}
                </option>
              </select>
              <input v-else class="input flex-1" v-model="c.value" placeholder="value" />
            </template>
            <span v-else class="flex-1"></span>

            <icon-close
              v-if="draft.conditions.length > 1"
              class="text-nord3 hover:text-nord11 hover:cursor-pointer shrink-0"
              @click="removeCondition(i)"
            />
          </div>
        </div>

        <div class="text-sm text-nord3">
          Preview: {{ draft.action === "keep" ? "show only" : "hide" }} entries where
          {{ describe(draft) }}
        </div>

        <div class="flex justify-end gap-2">
          <button class="button" @click="showEditor = false">Cancel</button>
          <button class="button" @click="saveDraft">Save rule</button>
        </div>
      </div>
    </popup>
  </div>
</template>
