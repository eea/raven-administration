<script setup>
/**
 * Observation Change History — the single implementation.
 *
 * Replaces verify/ObservationLog.vue and validate/ObservationLogPopup.vue, which
 * were ~95% identical and differed only in how they got their rows: Verify
 * pre-fetched 500 and passed them in as a prop, Validate paged itself at limit=10.
 *
 * This one always self-fetches. That is not tidiness for its own sake — a component
 * handed its rows as a prop cannot refetch, and filtering has to happen in SQL so
 * that `limit` counts visible rows and has_more/offset stay truthful. Toggling a
 * filter therefore resets paging and refetches rather than re-rendering.
 */
import { ref, computed, watch } from "vue";
import Popup from "../Popup.vue";
import Service from "./service";
import ObservationLogFilterMenu from "./ObservationLogFilterMenu.vue";
import useObservationLogExtension from "../../composables/useObservationLogExtension";
import useObservationLogFilters from "../../composables/useObservationLogFilters";
import { CORE_COLUMNS, verLabel, valLabel, srcColor } from "./labels";

const props = defineProps({
  show: Boolean,
  samplingPointId: { type: [String, Number], default: null },
  fromDt: { type: String, default: null },
  toDt: { type: String, default: null },
  pageSize: { type: Number, default: 50 },
});

const emit = defineEmits(["close"]);

const logRows = ref([]);
const hasMore = ref(false);
const offset = ref(0);
const loading = ref(false);

const { extraColumns, cell, reset: resetExt, fetchFor } = useObservationLogExtension();
const filters = useObservationLogFilters();
const {
  rules, activeRuleCount, hiddenColumns, isVisible, isUnavailable,
  isSuspended, sessionDisabledIds, applyServerFilters, loadPreferences,
} = filters;

const visibleCoreColumns = computed(() => CORE_COLUMNS.filter((c) => isVisible(c.key)));
const visibleExtraColumns = computed(() => extraColumns.value.filter((c) => isVisible(c.key)));

/** Every toggleable column, core and plugin, for the menu's Columns section. */
const allColumns = computed(() => [
  ...CORE_COLUMNS.map((c) => ({ key: c.key, label: c.label })),
  ...extraColumns.value.map((c) => ({ key: c.key, label: c.label })),
]);

const reload = async () => {
  logRows.value = [];
  offset.value = 0;
  hasMore.value = false;
  resetExt();
  await loadMore();
};

const loadMore = async () => {
  if (loading.value || !props.samplingPointId) return;
  loading.value = true;
  try {
    const result = await Service.log({
      samplingPointId: props.samplingPointId,
      fromDt: props.fromDt,
      toDt: props.toDt,
      limit: props.pageSize,
      offset: offset.value,
      disabledRules: sessionDisabledIds.value,
    });
    applyServerFilters(result.filters);
    logRows.value.push(...result.rows);
    hasMore.value = result.has_more;
    offset.value += result.rows.length;
    // Per page, for the rows this page actually added. Fetching once on open left
    // every "Load more" row without plugin values.
    await fetchFor({
      samplingPointId: props.samplingPointId,
      logIds: result.rows.map((r) => r.id),
    });
  } finally {
    loading.value = false;
  }
};

watch(
  () => [props.show, props.samplingPointId],
  async ([show]) => {
    if (!show || !props.samplingPointId) return;
    filters.resumeAll();       // a fresh open starts with the filters applied
    await loadPreferences();
    await reload();
  },
  { immediate: true }
);

/**
 * Toggling a rule refetches from offset 0 rather than re-rendering. The rule set is
 * part of the query, so continuing to page with a different one would interleave two
 * result sets at the same offsets.
 */
const onToggleRule = async (rule) => {
  await filters.toggleRule(rule);
  await reload();
};

const onShowAll = async () => {
  filters.suspendAll();
  await reload();
};

const onResumeAll = async () => {
  filters.resumeAll();
  await reload();
};

const isEmpty = computed(() => logRows.value.length === 0 && !loading.value);
// "Nothing here" and "your filters hid everything" are different problems and need
// different wording -- otherwise a house-wide default rule looks like a broken page.
const isEmptyByFilter = computed(() => isEmpty.value && activeRuleCount.value > 0);
</script>

<template>
  <!--
    Near-full-screen, and the body owns its own scrolling rather than using Popup's
    default overflow-y-auto: with every column shown the table is wider than the popup,
    so the horizontal scrollbar has to be reachable without scrolling to the bottom of
    the rows first.

    The cap is in px on purpose. `html, body` set text-[14px], so 1rem = 14px here and
    rem-based widths come out ~12.5% smaller than they read — max-w-5xl (64rem) was
    896px, not 1024px. 1680px comfortably clears the ~1554px the full column set needs.
  -->
  <popup
    :show="show"
    title="Observation Change History"
    @on-close="emit('close')"
    class="w-[95vw] max-w-[1680px] h-[85vh]"
    body-class="flex-1 min-h-0 flex flex-col"
  >
    <template #actions>
      <observation-log-filter-menu
        :columns="allColumns"
        :hidden-columns="hiddenColumns"
        :rules="rules"
        :is-unavailable="isUnavailable"
        :is-suspended="isSuspended"
        @toggle-column="filters.toggleColumn"
        @toggle-rule="onToggleRule"
        @resume-all="onResumeAll"
      />
    </template>

    <!--
      One v-if chain, not a chain plus a loose sibling: exactly one of these claims
      flex-1, otherwise two flex-1 children would split the height between an empty
      header-only table and the loading message. Centred because the popup now has a
      fixed height, so a top-aligned message would sit above a large blank area.
    -->
    <div v-if="loading && logRows.length === 0" class="flex-1 min-h-0 flex items-center justify-center text-nord3 text-sm">
      Loading…
    </div>
    <div v-else-if="isEmptyByFilter" class="flex-1 min-h-0 flex flex-col items-center justify-center text-nord3 text-sm">
      <div>No entries match the {{ activeRuleCount }} active filter{{ activeRuleCount === 1 ? "" : "s" }}.</div>
      <button class="button mt-2" @click="onShowAll">Show all</button>
    </div>
    <div v-else-if="isEmpty" class="flex-1 min-h-0 flex items-center justify-center text-nord3 text-sm">
      No history entries found.
    </div>
    <!--
      One scroll container owning BOTH axes, height-constrained by flex-1 min-h-0.
      That is the whole fix: an element only pins its horizontal scrollbar to its own
      bottom edge when it has a definite height. The previous overflow-x-auto div was
      as tall as the table, so its scrollbar sat hundreds of pixels below the popup.
    -->
    <div v-else class="flex-1 min-h-0 overflow-auto">
      <table class="table w-full text-sm">
        <!-- Sticky against the scroller above, not the popup panel. .table th is
             already opaque (bg-gray-100), so rows cannot show through. -->
        <thead class="sticky top-0 z-10">
          <tr>
            <th v-for="col in visibleCoreColumns" :key="col.key" class="whitespace-nowrap border-b border-nord4">
              {{ col.label }}
            </th>
            <th v-for="col in visibleExtraColumns" :key="col.key" class="whitespace-nowrap border-b border-nord4">
              {{ col.label }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in logRows" :key="r.id">
            <td v-if="isVisible('changed_at')" class="whitespace-nowrap font-mono text-xs">{{ r.changed_at }}</td>
            <td v-if="isVisible('changed_by')">
              <div class="max-w-[10rem] truncate" :title="r.changed_by ?? ''">{{ r.changed_by ?? "—" }}</div>
            </td>
            <td v-if="isVisible('change_source')">
              <span class="px-1.5 py-0.5 rounded text-xs font-medium" :class="srcColor(r.change_source)">
                {{ r.change_source }}
              </span>
            </td>
            <td v-if="isVisible('period_from')" class="whitespace-nowrap font-mono text-xs">{{ r.period_from }}</td>
            <td v-if="isVisible('period_to')" class="whitespace-nowrap font-mono text-xs">{{ r.period_to }}</td>
            <td v-if="isVisible('verification')" class="whitespace-nowrap">
              <span v-if="r.old_verification != null || r.new_verification != null">
                <span class="text-nord11">{{ verLabel(r.old_verification) }}</span>
                <span class="text-nord3 mx-1">→</span>
                <span class="text-nord14">{{ verLabel(r.new_verification) }}</span>
              </span>
              <span v-else class="text-nord3">—</span>
            </td>
            <td v-if="isVisible('validity')" class="whitespace-nowrap">
              <span v-if="r.old_validity != null || r.new_validity != null">
                <span class="text-nord11">{{ valLabel(r.old_validity) }}</span>
                <span class="text-nord3 mx-1">→</span>
                <span class="text-nord14">{{ valLabel(r.new_validity) }}</span>
              </span>
              <span v-else class="text-nord3">—</span>
            </td>
            <td v-if="isVisible('value')" class="whitespace-nowrap font-mono text-xs">
              <span v-if="r.old_value != null || r.new_value != null">
                {{ r.old_value ?? "—" }} → {{ r.new_value ?? "—" }}
              </span>
              <span v-else class="text-nord3">—</span>
            </td>
            <!--
              Capped on an inner div, not the td: .table sets no table-layout, so auto
              layout applies and max-width on a cell is only loosely honoured, while on
              a block child it is exact. Without this a single 89-character migrated
              comment sets the column width for every row and costs ~640px.
            -->
            <td v-for="col in visibleExtraColumns" :key="col.key" class="text-sm">
              <div class="max-w-[20rem] truncate" :title="cell(r.id, col.key)">{{ cell(r.id, col.key) }}</div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Outside the scroller, so it stays put instead of scrolling away sideways. -->
    <div class="mt-3 flex justify-center shrink-0" v-if="hasMore">
      <button class="button" :disabled="loading" @click="loadMore">
        {{ loading ? "Loading…" : "Load more" }}
      </button>
    </div>
  </popup>
</template>
