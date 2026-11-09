<script setup>
import { useRouter } from "vue-router";

// What the last Recalculate compliance did, shown on Dataflow and on the Compliance
// assessment method page. A toast cannot carry it: a run can skip rows for several
// reasons, and one of them -- an assessment regime every one of whose rows was skipped
// -- means a regime is declared in AssessmentRegimeZone and reports no compliance at
// all, which nobody spots from a number.
//
// Each line links to the Management page where it is fixed, opened on the row (Manager
// reads ?focus=). The target follows from the reason:
//   not_linked                         the sampling point; the fix is a new Assessment data link
//   duplicate_key, pollutant_mismatch  the Assessment data link(s) that disagree
//   incomplete_regime, malformed_regime_id  the regime

defineProps({ summary: { type: Object, required: true } });
const emit = defineEmits(["dismiss"]);

const router = useRouter();
const openRows = (name, keys, query = {}) => {
  const focus = (keys ?? []).filter(Boolean).join(",");
  router.push({ name, query: focus ? { ...query, focus } : query });
};
const isModel = (id) => /^(MOD|OBE)_/.test(id ?? "");
const openMethod = (entry) => {
  const links = entry.assessment_data_ids ?? (entry.assessment_data_id ? [entry.assessment_data_id] : []);
  if (entry.code !== "not_linked" && links.length) return openRows("AssessmentData", links);
  openRows(isModel(entry.assessment_method_id) ? "Models" : "SamplingPoints", [entry.assessment_method_id]);
};
</script>

<template>
  <div class="mb-6 p-3 rounded border border-nord8 bg-nord8/10 text-sm">
    <div class="flex items-start">
      <div class="font-bold mb-1 flex-1">
        ComplianceAssessmentMethod: {{ summary.written }} row(s) stored for {{ summary.reporting_year }}
      </div>
      <button class="text-nord3 text-xs hover:underline" @click="emit('dismiss')">Dismiss</button>
    </div>

    <div v-if="summary.message" class="text-nord3">{{ summary.message }}</div>

    <div v-for="(count, code) in summary.skipped_by_reason" :key="code" class="text-nord3">
      {{ count }} skipped — {{ summary.skipped_labels?.[code] ?? code }}.
    </div>

    <div v-if="summary.out_of_scope" class="text-nord3">
      {{ summary.out_of_scope }} sampling point(s) left out as not part of the EEA
      reporting obligation. These are the same rows SamplingPoint.csv omits.
    </div>

    <!-- The one outcome a count cannot convey: a regime that reports nothing at all
         while still being declared in AssessmentRegimeZone. -->
    <div v-if="summary.regimes_without_rows?.length"
      class="mt-2 p-2 rounded border border-nord13 bg-nord13/20">
      <div class="font-bold">
        {{ summary.regimes_without_rows.length }} assessment regime(s) produced no
        compliance row at all
      </div>
      <div class="text-nord3 font-mono text-xs mt-1 max-h-32 overflow-auto">
        <template v-for="(regime, i) in summary.regimes_without_rows" :key="regime">
          <span v-if="i">, </span>
          <a class="hover:underline cursor-pointer text-nord10" @click="openRows('AssessmentRegimes', [regime])">{{ regime }}</a>
        </template>
      </div>
      <div class="text-nord3 text-xs mt-1">
        They are still declared in AssessmentRegimeZone, so the submission claims the
        regime exists and says nothing about whether it was met. Link a sampling point
        measuring the regime's own pollutant to each of them
        (<a class="hover:underline cursor-pointer text-nord10"
           @click="openRows('AssessmentData', [], { wizard: 1, year: summary.reporting_year })">link by zone →</a>).
      </div>
    </div>

    <ul v-if="summary.skipped?.length" class="mt-2 text-nord3 text-xs list-disc pl-5 max-h-64 overflow-auto">
      <li v-for="(entry, i) in summary.skipped" :key="i">
        <a v-if="entry.assessment_method_id" class="font-mono hover:underline cursor-pointer text-nord10"
          :title="entry.code === 'not_linked' ? 'Open the sampling point' : 'Open the Assessment data link(s)'"
          @click="openMethod(entry)">{{ entry.assessment_method_id }}</a>
        <span v-else class="font-mono">—</span>
        <template v-if="entry.assessment_regime_id">
          /
          <a class="font-mono hover:underline cursor-pointer text-nord10" title="Open the assessment regime"
            @click="openRows('AssessmentRegimes', [entry.assessment_regime_id])">{{ entry.assessment_regime_id }}</a>
        </template>
        — {{ entry.reason }}
        <a v-if="entry.code === 'not_linked'" class="hover:underline cursor-pointer text-nord10 whitespace-nowrap"
          @click="openRows('AssessmentData')">Add a link →</a>
      </li>
    </ul>
  </div>
</template>
