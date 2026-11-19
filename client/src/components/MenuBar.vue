<script setup>
/**
 * Application sidebar.
 *
 *  - desktop expanded : 264px, collapsible groups, filter box, user card
 *  - desktop collapsed: 72px icon rail; hovering (or tapping) a group icon opens a flyout
 *  - mobile           : off-canvas drawer, always expanded, closes on navigation
 */
import { computed, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import Auth from "../helpers/auth";
import Eventy from "../helpers/eventy";
import { branding } from "../helpers/branding";
import { copyToClipboard } from "../helpers/utilsCopy";
import { useNavigation } from "../composables/useNavigation";

import IconLogout from "~icons/tabler/logout";
import IconChevron from "~icons/tabler/chevron-down";
import IconSearch from "~icons/tabler/search";
import IconX from "~icons/tabler/x";
import IconPlugin from "~icons/tabler/puzzle";
import IconNewVersion from "~icons/tabler/cloud-download";
import IconCollapse from "~icons/tabler/layout-sidebar-left-collapse";
import IconExpand from "~icons/tabler/layout-sidebar-left-expand";
import IconLogo from "~icons/tabler/feather";
import IconPalette from "~icons/tabler/palette";
import { PALETTES, palette, applyPalette } from "../helpers/palette";

const props = defineProps({
  show: Boolean,
  collapsed: Boolean,
  mobile: Boolean,
  mobileOpen: Boolean
});
const emit = defineEmits(["close", "toggle-collapse"]);

const route = useRoute();
const router = useRouter();
const { visibleGroups, version, user, restartRequired, init, refresh } = useNavigation();

const rail = computed(() => props.collapsed && !props.mobile);

onMounted(init);
watch(
  () => props.show,
  () => refresh()
);

// ── group open/closed state (persisted) ────────────────────────────────────
const CLOSED_KEY = "raven_nav_closed_groups";
const readClosed = () => {
  try {
    return new Set(JSON.parse(localStorage.getItem(CLOSED_KEY) || "[]"));
  } catch {
    return new Set();
  }
};
const closed = ref(readClosed());
const toggleGroup = (g) => {
  const s = new Set(closed.value);
  s.has(g) ? s.delete(g) : s.add(g);
  closed.value = s;
  try {
    localStorage.setItem(CLOSED_KEY, JSON.stringify([...s]));
  } catch {
    /* storage unavailable: keep in memory */
  }
};

// ── filter ──────────────────────────────────────────────────────────────────
const q = ref("");
const filterInput = ref(null);
const filtered = computed(() => {
  const term = q.value.trim().toLowerCase();
  if (!term) return visibleGroups.value;
  return visibleGroups.value
    .map((g) => ({
      ...g,
      items: g.group.toLowerCase().includes(term) ? g.items : g.items.filter((i) => i.name.toLowerCase().includes(term))
    }))
    .filter((g) => g.items.length);
});
const isOpen = (g) => !!q.value.trim() || !closed.value.has(g.group);
const onFilterEnter = () => {
  const first = filtered.value[0]?.items[0];
  if (first) goto(first.comp);
};

const isActive = (comp) => route.name === comp;
const groupActive = (g) => g.items.some((i) => isActive(i.comp));

const goto = (comp) => {
  q.value = "";
  flyout.value = null;
  router.push({ name: comp });
  if (props.mobile) emit("close");
};

// The logo goes "home": the Home route redirects to the page marked
// "Opens here after login" (raven_default_view), so the two always agree.
const goHome = () => goto("Home");

// ── rail flyout ─────────────────────────────────────────────────────────────
const flyout = ref(null); // { group, top }
let flyoutTimer = null;
const openFlyout = (g, ev) => {
  clearTimeout(flyoutTimer);
  const rect = ev.currentTarget.getBoundingClientRect();
  const estimated = 56 + g.items.length * 38;
  const top = Math.max(8, Math.min(rect.top - 6, window.innerHeight - estimated - 8));
  flyout.value = { group: g, top };
};
const scheduleClose = () => {
  clearTimeout(flyoutTimer);
  flyoutTimer = setTimeout(() => (flyout.value = null), 160);
};
const keepFlyout = () => clearTimeout(flyoutTimer);
watch(rail, () => (flyout.value = null));

const cyclePalette = () => {
  const i = PALETTES.findIndex((p) => p.id === palette.value);
  applyPalette(PALETTES[(i + 1) % PALETTES.length].id);
};

// ── footer ──────────────────────────────────────────────────────────────────
const goto_git_changelog = () => {
  window.open("https://github.com/eea/raven-administration/blob/master/CHANGELOG.md", "_blank");
};

const signout = async () => {
  Auth.signout();
  router.push({ name: "Login" });
};

const onCopyVersion = async () => {
  // Version.get() seeds current as "-" until /api/version resolves; copying that would
  // silently put a dash on the clipboard.
  if (!version.value.current || version.value.current === "-") return;
  const ok = await copyToClipboard(version.value.current);
  Eventy.showHideMessage(ok ? `Version ${version.value.current} copied` : "Could not copy version", ok ? "success" : "error", 2000);
};

// "/" focuses the menu filter when the user is not typing somewhere.
const onKey = (e) => {
  if (e.key !== "/" || e.ctrlKey || e.metaKey || e.altKey) return;
  const t = e.target;
  if (t && (t.isContentEditable || ["INPUT", "TEXTAREA", "SELECT"].includes(t.tagName))) return;
  if (rail.value || !filterInput.value) return;
  e.preventDefault();
  filterInput.value.focus();
};
onMounted(() => window.addEventListener("keydown", onKey));

defineExpose({ focusFilter: () => filterInput.value?.focus() });
</script>

<template>
  <!-- mobile backdrop -->
  <Transition name="fade">
    <div v-if="mobile && mobileOpen && show" class="fixed inset-0 z-[480] bg-nord0/45 backdrop-blur-[2px]" @click="emit('close')" />
  </Transition>

  <aside
    v-show="show"
    class="nav n-text select-none flex flex-col text-[0.93rem] shrink-0 z-[490] transition-[width,transform] duration-300 ease-[cubic-bezier(.2,.8,.2,1)]"
    :class="[
      mobile ? 'fixed inset-y-0 left-0 w-[288px] max-w-[86vw] shadow-2xl' : 'relative h-full',
      mobile && !mobileOpen ? '-translate-x-full' : 'translate-x-0',
      !mobile && (rail ? 'w-[72px]' : 'w-[264px]')
    ]"
  >
    <!-- Brand -->
    <div class="flex items-center gap-3 h-16 shrink-0" :class="rail ? 'justify-center px-0' : 'px-4'">
      <a :href="router.resolve({ name: 'Home' }).href" class="flex items-center gap-3 min-w-0 no-underline! cursor-pointer"
        title="Go to start page" @click.prevent="goHome">
        <div class="logo grid place-items-center size-9 rounded-xl shrink-0 text-white shadow-lg shadow-black/25">
          <IconLogo class="text-[1.15rem]" />
        </div>
        <div v-if="!rail" class="min-w-0 leading-tight">
          <div class="font-display n-strong font-bold text-[1.05rem] tracking-tight truncate">{{ branding.appName }}</div>
          <div class="text-[0.72rem] uppercase tracking-[0.14em] n-faint truncate">{{ branding.subtitle }}</div>
        </div>
      </a>
      <button v-if="mobile" class="ml-auto grid place-items-center size-9 rounded-lg n-hover" @click="emit('close')" aria-label="Close menu">
        <IconX class="text-lg" />
      </button>
    </div>

    <!-- Filter -->
    <div v-if="!rail" class="px-3 pb-2">
      <label class="group flex items-center gap-2 h-9 px-2.5 rounded-lg n-field transition">
        <IconSearch class="n-muted shrink-0" />
        <input
          ref="filterInput"
          v-model="q"
          type="text"
          placeholder="Find page…"
          class="flex-1 min-w-0 bg-transparent outline-none focus-visible:outline-none n-strong n-placeholder text-sm"
          @keydown.enter="onFilterEnter"
          @keydown.esc="q = ''; $event.target.blur()"
        />
        <kbd v-if="!q" class="nav-kbd">/</kbd>
        <button v-else class="n-muted n-hover-accent" @click="q = ''"><IconX /></button>
      </label>
    </div>

    <!-- Alerts -->
    <div class="flex flex-col gap-1.5 shrink-0" :class="rail ? 'px-3 pb-2 items-center' : 'px-3 pb-2'">
      <button v-if="restartRequired" class="alert alert-warn" :class="rail && 'alert-rail'" title="Server restart required" @click="goto('PluginManager')">
        <IconPlugin class="shrink-0" />
        <span v-if="!rail" class="truncate">Server restart required</span>
      </button>
      <button v-if="!version.isLatest" class="alert alert-danger" :class="rail && 'alert-rail'" title="New version available" @click="goto_git_changelog">
        <IconNewVersion class="shrink-0" />
        <span v-if="!rail" class="truncate">New version available</span>
      </button>
    </div>

    <!-- Groups -->
    <nav class="flex-1 overflow-y-auto overflow-x-hidden nav-scroll pb-3" :class="rail ? 'px-3' : 'px-2'">
      <!-- expanded -->
      <template v-if="!rail">
        <div v-for="g in filtered" :key="g.group" class="mt-1 first:mt-0">
          <button class="w-full flex items-center gap-2 px-2.5 pt-3 pb-1.5 text-[0.7rem] font-semibold uppercase tracking-[0.12em] n-muted n-hover-text transition-colors" @click="toggleGroup(g.group)">
            <component :is="g.icon" class="text-[0.95rem]" :class="groupActive(g) ? 'n-accent' : ''" />
            <span class="flex-1 text-left truncate">{{ g.group }}</span>
            <IconChevron class="transition-transform duration-200" :class="isOpen(g) ? '' : '-rotate-90'" />
          </button>
          <div class="grid transition-[grid-template-rows] duration-250 ease-out" :class="isOpen(g) ? 'grid-rows-[1fr]' : 'grid-rows-[0fr]'">
            <ul class="overflow-hidden flex flex-col gap-px">
              <li v-for="i in g.items" :key="i.name">
                <a
                  :href="router.resolve({ name: i.comp }).href"
                  class="item no-underline!"
                  :class="isActive(i.comp) && 'item-active'"
                  @click.prevent="goto(i.comp)"
                >
                  <component :is="i.icon" class="item-icon" />
                  <span class="truncate">{{ i.name }}</span>
                </a>
              </li>
            </ul>
          </div>
        </div>
        <div v-if="!filtered.length" class="px-3 py-6 text-center text-sm n-muted">No pages match “{{ q }}”.</div>
      </template>

      <!-- rail -->
      <template v-else>
        <div class="flex flex-col items-center gap-1 pt-1">
          <button
            v-for="g in visibleGroups"
            :key="g.group"
            class="rail-btn"
            :class="[groupActive(g) && 'rail-btn-active', flyout?.group.group === g.group && 'rail-btn-open']"
            :aria-label="g.group"
            @mouseenter="openFlyout(g, $event)"
            @mouseleave="scheduleClose"
            @click="flyout?.group.group === g.group ? (flyout = null) : openFlyout(g, $event)"
          >
            <component :is="g.icon" class="text-[1.3rem]" />
          </button>
        </div>
      </template>
    </nav>

    <!-- Footer -->
    <div class="shrink-0 n-border-t p-2.5">
      <div class="flex items-center gap-2.5" :class="rail ? 'flex-col' : ''">
        <div class="avatar grid place-items-center size-9 rounded-full text-[0.8rem] font-semibold text-white shrink-0" :title="user.name">{{ user.initials }}</div>
        <div v-if="!rail" class="min-w-0 flex-1 leading-tight">
          <div class="n-strong text-sm font-medium truncate">{{ user.name || "Signed in" }}</div>
          <div class="text-[0.72rem] n-muted font-mono cursor-pointer n-hover-accent truncate" title="Double-click to copy" @dblclick="onCopyVersion">v{{ version.current }}</div>
        </div>
        <button class="grid place-items-center size-9 rounded-lg n-hover transition" title="Sign out" @click="signout">
          <IconLogout class="text-lg" />
        </button>
      </div>
      <!-- Palette picker (trial: compare colour schemes live) -->
      <div v-if="!rail" class="mt-2 flex items-center gap-2 px-2.5 h-8">
        <IconPalette class="n-muted text-base shrink-0" />
        <div class="flex items-center gap-1.5">
          <button
            v-for="p in PALETTES"
            :key="p.id"
            class="swatch"
            :class="palette === p.id && 'swatch-on'"
            :style="{ '--sw-nav': p.nav, '--sw-accent': p.accent }"
            :title="p.name"
            :aria-label="p.name + ' palette'"
            @click="applyPalette(p.id)"
          />
        </div>
      </div>
      <button v-else class="mt-1 w-full grid place-items-center h-8 rounded-lg n-hover" title="Next palette" @click="cyclePalette">
        <IconPalette class="text-base" />
      </button>
      <button v-if="!mobile" class="mt-2 w-full flex items-center gap-2 h-8 rounded-lg n-muted n-hover transition text-xs" :class="rail ? 'justify-center' : 'px-2.5'" :title="rail ? 'Expand sidebar' : 'Collapse sidebar'" @click="emit('toggle-collapse')">
        <IconExpand v-if="rail" class="text-base" />
        <template v-else>
          <IconCollapse class="text-base" />
          <span>Collapse</span>
        </template>
      </button>
    </div>
  </aside>

  <!-- Rail flyout -->
  <Teleport to="body">
    <Transition name="flyout">
      <div
        v-if="rail && flyout"
        class="fixed z-[600] left-[78px] w-64 rounded-xl nav-fly n-text py-2 text-[0.93rem]"
        :style="{ top: flyout.top + 'px' }"
        @mouseenter="keepFlyout"
        @mouseleave="scheduleClose"
      >
        <div class="px-3.5 pt-1 pb-2 flex items-center gap-2 text-[0.7rem] font-semibold uppercase tracking-[0.12em] n-muted">
          <component :is="flyout.group.icon" class="text-[0.95rem] n-accent" />
          {{ flyout.group.group }}
        </div>
        <div class="px-1.5 flex flex-col gap-px max-h-[70vh] overflow-y-auto nav-scroll">
          <a v-for="i in flyout.group.items" :key="i.name" :href="router.resolve({ name: i.comp }).href" class="item no-underline!" :class="isActive(i.comp) && 'item-active'" @click.prevent="goto(i.comp)">
            <component :is="i.icon" class="item-icon" />
            <span class="truncate">{{ i.name }}</span>
          </a>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
@reference "../assets/style.css";

/* Colours come from the palette variables in assets/palettes.css. Muted text and
   hover fills are mixed from --nav-fg, so the same classes serve a dark sidebar
   (fg white) and a light one (fg ink). */
.nav {
  background: var(--nav-bg);
  border-right: 1px solid var(--nav-border);
}
.nav-fly {
  background: var(--nav-fly-bg);
  box-shadow: 0 0 0 1px color-mix(in srgb, var(--nav-fg) 10%, transparent), 0 20px 40px -12px rgb(0 0 0 / 0.35);
}
.n-strong { color: color-mix(in srgb, var(--nav-fg) 94%, transparent); }
.n-text { color: color-mix(in srgb, var(--nav-fg) 70%, transparent); }
.n-muted { color: color-mix(in srgb, var(--nav-fg) 45%, transparent); }
.n-faint { color: color-mix(in srgb, var(--nav-fg) 50%, var(--nav-accent)); opacity: 0.75; }
.n-accent { color: var(--nav-accent); }
.n-placeholder::placeholder { color: color-mix(in srgb, var(--nav-fg) 38%, transparent); }
.n-hover { color: color-mix(in srgb, var(--nav-fg) 58%, transparent); }
.n-hover:hover { color: var(--nav-fg); background: color-mix(in srgb, var(--nav-fg) 8%, transparent); }
.n-hover-text:hover { color: color-mix(in srgb, var(--nav-fg) 75%, transparent); }
.n-hover-accent:hover { color: var(--nav-accent); }
.n-border-t { border-top: 1px solid color-mix(in srgb, var(--nav-fg) 8%, transparent); }
.n-field {
  background: color-mix(in srgb, var(--nav-fg) 5%, transparent);
  box-shadow: inset 0 0 0 1px color-mix(in srgb, var(--nav-fg) 9%, transparent);
}
.n-field:focus-within {
  background: color-mix(in srgb, var(--nav-fg) 7%, transparent);
  box-shadow: inset 0 0 0 1px color-mix(in srgb, var(--nav-accent) 60%, transparent);
}

.logo { background: var(--logo-bg); }
.avatar {
  background: var(--avatar-bg);
  box-shadow: 0 0 0 2px color-mix(in srgb, var(--nav-fg) 10%, transparent);
}

.nav-kbd {
  @apply shadow-none;
  border-color: color-mix(in srgb, var(--nav-fg) 15%, transparent);
  background: color-mix(in srgb, var(--nav-fg) 5%, transparent);
  color: color-mix(in srgb, var(--nav-fg) 45%, transparent);
}

.item {
  @apply relative flex items-center gap-3 h-9 px-2.5 rounded-lg cursor-pointer transition-colors duration-150;
  color: color-mix(in srgb, var(--nav-fg) 72%, transparent) !important;
}
.item:hover {
  background: color-mix(in srgb, var(--nav-fg) 7%, transparent);
  color: var(--nav-fg) !important;
}
.item-icon {
  @apply text-[1.15rem] shrink-0 transition-colors;
  color: color-mix(in srgb, var(--nav-fg) 45%, transparent);
}
.item:hover .item-icon { color: color-mix(in srgb, var(--nav-fg) 80%, transparent); }
.item-active,
.item-active:hover {
  @apply font-medium;
  color: var(--nav-active-fg) !important;
  background: var(--nav-active-bg);
  box-shadow: inset 0 0 0 1px var(--nav-active-ring);
}
.item-active::before {
  content: "";
  @apply absolute -left-2 top-1.5 bottom-1.5 w-1 rounded-r-full;
  background: var(--nav-accent);
}
.item-active .item-icon,
.item-active:hover .item-icon { color: var(--nav-accent); }

.rail-btn {
  @apply relative grid place-items-center size-11 rounded-xl transition;
  color: color-mix(in srgb, var(--nav-fg) 55%, transparent);
}
.rail-btn:hover,
.rail-btn-open {
  color: var(--nav-fg);
  background: color-mix(in srgb, var(--nav-fg) 9%, transparent);
}
.rail-btn-active,
.rail-btn-active:hover {
  color: var(--nav-accent);
  background: var(--nav-active-bg);
  box-shadow: inset 0 0 0 1px var(--nav-active-ring);
}

/* Alert text is mixed toward --nav-fg: light amber on a dark sidebar, dark amber on a light one. */
.alert {
  @apply w-full flex items-center gap-2 px-2.5 h-9 rounded-lg text-sm font-medium text-left transition hover:brightness-110;
}
.alert-warn {
  color: color-mix(in srgb, #f59e0b 65%, var(--nav-fg));
  background: color-mix(in srgb, #f59e0b 13%, transparent);
  box-shadow: inset 0 0 0 1px color-mix(in srgb, #f59e0b 28%, transparent);
}
.alert-danger {
  color: color-mix(in srgb, #f43f5e 65%, var(--nav-fg));
  background: color-mix(in srgb, #f43f5e 12%, transparent);
  box-shadow: inset 0 0 0 1px color-mix(in srgb, #f43f5e 26%, transparent);
}
.alert-rail {
  @apply size-11 justify-center px-0;
}

.swatch {
  @apply size-5 rounded-full cursor-pointer transition-transform hover:scale-115;
  background: linear-gradient(135deg, var(--sw-nav) 0 50%, var(--sw-accent) 50% 100%);
  box-shadow: 0 0 0 1px color-mix(in srgb, var(--nav-fg) 22%, transparent);
}
.swatch-on {
  box-shadow: 0 0 0 2px var(--nav-fly-bg), 0 0 0 3.5px var(--nav-accent);
}

.nav-scroll {
  scrollbar-color: color-mix(in srgb, var(--nav-fg) 15%, transparent) transparent;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
.flyout-enter-active,
.flyout-leave-active {
  transition: opacity 0.14s ease, transform 0.14s ease;
}
.flyout-enter-from,
.flyout-leave-to {
  opacity: 0;
  transform: translateX(-6px);
}
</style>
