<script setup>
import { ref, onMounted, watch } from 'vue';
import Service from './service';

// Codemirror with R
import Codemirror from 'codemirror-editor-vue3';
import 'codemirror/addon/display/placeholder.js';
import 'codemirror/mode/r/r.js';

// Configuration
const defaultSections = 7;
const cmOptions = { mode: 'text/x-rsrc' };

// Reactive state
const sections = ref([]);
const filename = ref('');
const files = ref([]);
const selectedFile = ref(null);
const saving = ref(false);
const unsaved = ref(false);
const justCleared = ref(false);
const statusText = ref('Working document (not saved)');
const importedFiles = ref([]);

// Factory for section objects to avoid duplication
const createSection = (id, code = '') => ({
  id,
  code,
  expanded: Boolean(code && String(code).trim()),
  output: '',
  plot: null,
  error: null,
  objects: [],
  running: false,
  status: 'idle',
});

// Initialize empty notebook
const initEmptySections = (count = defaultSections) => {
  sections.value = Array.from({ length: count }, (_, i) => createSection(i, ''));
};

initEmptySections();

// Normalize response from Service.runCode into predictable fields
const normalizeServiceResult = (res) => {
  const out = { output: '', plot: null, objects: [], error: null };

  // Output normalization
  if (Array.isArray(res.output) && res.output.length === 1) {
    out.output = String(res.output[0]).replace(/^\[1\]\s*/gm, '');
  } else if (typeof res.output === 'string') {
    out.output = res.output;
  }

  // Plot can be an array or a string
  if (Array.isArray(res.plot)) {
    out.plot = res.plot.length && String(res.plot[0]).trim() ? `data:image/png;base64,${res.plot[0]}` : null;
  } else if (typeof res.plot === 'string') {
    out.plot = String(res.plot).trim() ? `data:image/png;base64,${res.plot}` : null;
  }

  // Objects
  out.objects = Array.isArray(res.objects) ? res.objects : [];

  // Error handling
  if (Array.isArray(res.error)) {
    out.error = res.error.length ? res.error.join('\n') : null;
  } else if (res.error && typeof res.error === 'object' && Object.keys(res.error).length === 0) {
    out.error = null;
  } else {
    out.error = res.error && String(res.error).trim() ? res.error : null;
  }

  return out;
};

// Run single snippet. By default reset the R workspace before running a single snippet.
// Pass doReset=false when calling as part of Run All to avoid resetting between sections.
const runSnippet = async (section, doReset = true) => {
  if (!section.code || !String(section.code).trim()) {
    Object.assign(section, { output: '', plot: null, error: null, objects: [], running: false, status: 'idle' });
    return;
  }

  section.output = '';
  section.plot = null;
  section.error = null;
  section.running = true;
  section.status = 'running';

  if (doReset) {
    await Service.resetWorkspace();
    await sourceImportedFiles();
  }

  try {
    const res = await Service.runCode(section.code);
    console.log(res);
    const normalized = normalizeServiceResult(res || {});
    section.output = normalized.output;
    section.plot = normalized.plot;
    section.objects = normalized.objects;
    section.error = normalized.error;
  } catch (err) {
    section.error = err && err.message ? err.message : String(err);
  } finally {
    section.running = false;
    section.status = 'done';
  }
};

// Run all snippets
const runAll = async () => {
  await Service.resetWorkspace();
  await sourceImportedFiles();
  for (const section of sections.value) {
    await runSnippet(section, false);
  }
};

// Add / toggle helpers
const addSection = () => sections.value.push(createSection(sections.value.length, ''));
const toggleExpand = (section) => (section.expanded = !section.expanded);

// Section delimiter used in the single .R file to separate snippets.
const SECTION_DELIMITER = (idx) => `# ---SECTION ${idx} ---`;

// Join sections into a single .R file content using safe delimiters
const joinSections = () => sections.value.map((s, idx) => `${SECTION_DELIMITER(idx)}\n${s.code || ''}`).join('\n\n');

// Parse combined .R file into sections split by delimiter. More tolerant than earlier split.
const parseSections = (content) => {
  if (!content) return [];
  // Find delimiter lines and split accordingly
  const parts = content.split(/(?=#\s*-{3}SECTION)/);
  return parts.map((p) => {
    const lines = p.split('\n');
    if (lines[0].match(/^#\s*-{3}SECTION/)) lines.shift();
    return lines.join('\n').replace(/\n+$/, '');
  });
};

// Save notebook to server (create or update depending on selectedFile)
const saveNotebookFile = async () => {
  if (!filename.value) return;
  saving.value = true;
  const content = joinSections();
  const targetName = filename.value.endsWith('.R') ? filename.value : `${filename.value}.R`;
  if (selectedFile.value && selectedFile.value === targetName) {
    await Service.updateRFile(targetName, content);
  } else {
    await Service.saveRFile(targetName, content);
    selectedFile.value = targetName;
  }
  await loadFiles();
  saving.value = false;
  unsaved.value = false;
  statusText.value = 'Saved work';
};

const updateFile = async () => {
  if (!selectedFile.value) return;
  saving.value = true;
  const content = joinSections();
  await Service.updateRFile(selectedFile.value, content);
  await loadFiles();
  saving.value = false;
  unsaved.value = false;
  statusText.value = 'Saved work';
};

const newFile = () => {
  initEmptySections();
  filename.value = '';
  selectedFile.value = null;
  justCleared.value = true;
  unsaved.value = false;
  statusText.value = 'Working document (not saved)';
};

const deleteFile = async (name) => {
  if (!window.confirm(`Are you sure you want to delete "${name}"?`)) return;
  await Service.deleteRFile(name);
  await loadFiles();
  if (selectedFile.value === name) newFile();
};

// Load available files
const loadFiles = async () => {
  const res = await Service.listRFiles();
  files.value = res || [];
};

// Source/import all tracked imported files into the R persistent env
const sourceImportedFiles = async () => {
  for (const f of importedFiles.value) {
    try {
      await Service.importFile(f);
    } catch (err) {
      // ignore per-file errors but consider logging
      console.error('Failed to import', f, err);
    }
  }
};

// Import a saved file into the R persistent session
const importFile = async (name) => {
  const res = await Service.importFile(name);
  if (!importedFiles.value.includes(name)) importedFiles.value.push(name);
  return res;
};

// Load a single file and parse into sections
const loadFile = async (name) => {
  const res = await Service.getRFile(name);
  const content = res.content || '';
  const parsed = parseSections(content);
  if (parsed.length) {
    sections.value = parsed.map((code, idx) => createSection(idx, code));
  } else {
    sections.value = [createSection(0, content)];
  }
  selectedFile.value = name;
  filename.value = name.replace(/\.R$/, '');
  unsaved.value = false;
  statusText.value = 'Loaded file';
};

// Watch for changes to mark unsaved
watch(
  () => sections.value.map((s) => s.code).join('\n'),
  (newV, oldV) => {
    const changed = newV !== oldV;
    if (justCleared.value && !filename.value && !selectedFile.value) {
      justCleared.value = false;
      unsaved.value = false;
      statusText.value = 'Working document (not saved)';
      return;
    }
    unsaved.value = changed;
    statusText.value = unsaved.value && !filename.value && !selectedFile.value ? 'Working document (not saved)' : unsaved.value ? 'Unsaved changes' : 'Saved work';
  }
);

onMounted(loadFiles);
</script>

<template>
  <div class="p-4 bg-gray-100 min-h-screen">
    <div class="flex justify-between mb-4">
      <h2 class="text-xl font-bold">R Notebook</h2>
    </div>

    <div class="mb-5 bg-white p-4 rounded shadow">
      <div class="mb-5">
        <label class="font-bold">Workspace</label>
      </div>
        <div class="mb-3 text-sm text-gray-600">
          <em>
            A persistent R object named <strong>ravendb_conn</strong> is created automatically and provides a connection to your Raven database. Use it in R snippets (for example: <code>dbReadTable(ravendb_conn, "observations")</code>).
          </em>
        </div>
      <div>
        <span :class="unsaved ? 'text-yellow-600 font-bold' : 'text-gray-600'">{{ statusText }}</span>
      </div>
      <div>
        <input v-model="filename" placeholder="Filename" class="border p-1 rounded w-full" />
      </div> 
      <div class="mt-5 space-x-4">
        <button @click="saveNotebookFile" :disabled="saving || !filename" class="bg-green-500 text-white px-2 py-1 rounded">Save</button>
        <button v-if="selectedFile" @click="updateFile" class="bg-yellow-500 text-white px-2 py-1 rounded">Update</button>
        <button @click="newFile" class="bg-gray-200 hover:bg-gray-300 text-gray-700 px-2 py-1 rounded">Clear</button>
      </div>
  
    </div>
    <div class="flex space-x-4">
      <div class="flex-1">
        <!-- Controls for the code area -->
        <div class="mb-4 flex items-center space-x-2">
          <button @click="runAll" class="btn btn-primary">Run All</button>
          <button @click="addSection" class="btn btn-secondary">Add Section</button>
        </div>
        <div v-for="section in sections" :key="section.id" class="mb-4 p-2 bg-white rounded shadow">
      <div class="flex justify-between items-center cursor-pointer">
        <div class="flex-1" @click="toggleExpand(section)">
          <small>Section {{ section.id + 1 }}</small>
          <div v-if="!section.expanded" class="text-gray-600 whitespace-pre">{{ section.code ? section.code.split('\n')[0] : 'Click to edit...' }}</div>
        </div>
        <button @click.stop="runSnippet(section)" :disabled="section.running" class="btn btn-sm btn-success ml-2">▶️</button>
        <span class="ml-2">
          <span
            :class="['status-dot', section.status === 'idle' ? 'status-idle' : section.status === 'running' ? 'status-running' : 'status-done']"
            :title="section.status === 'idle' ? 'Idle' : section.status === 'running' ? 'Running' : 'Finished'"
          ></span>
        </span>
        <button @click.stop="toggleExpand(section)" class="ml-2 text-gray-500 hover:text-gray-700" title="Collapse/Expand">
          <span v-if="section.expanded">&#x25B2;</span>
          <span v-else>&#x25BC;</span>
        </button>
      </div>

      <div v-if="section.expanded" class="mt-2">
        <Codemirror
          v-model:value="section.code"
          :options="cmOptions"
          border
          placeholder="Write R code here..."
          :height="300"
        />
      </div>

      <!-- Output -->
      <div v-if="section.expanded && (section.output || section.error || section.plot || (section.objects && section.objects.length))" class="mt-2 bg-gray-50 p-2 rounded">
        <div v-if="section.output" class="text-gray-800 whitespace-pre-wrap">{{ section.output }}</div>
        <div v-if="section.error" class="text-red-600 whitespace-pre-wrap">{{ section.error }}</div>
        <div v-if="section.objects && section.objects.length" class="mt-3 text-sm text-gray-600 bg-white italic">
          Objects:
          <ul class="list-disc ml-5">
            <li v-for="obj in section.objects" :key="obj">{{ obj }}</li>
          </ul>
        </div>
        <img v-if="section.plot" :src="section.plot" class="border rounded mt-2"/>
      </div>
        </div>
      </div>
      <aside class="w-1/3 p-2 bg-white rounded shadow">
        <div class="flex items-start justify-between">
          <label class="font-bold">Saved Files:</label>
        </div>
        <div class="mt-2 overflow-auto max-h-80">
          <!-- Header row for the grid (12-column layout so filename gets more space) -->
          <div class="grid grid-cols-12 gap-2 text-xs font-semibold text-gray-600 border-b pb-1">
            <div class="col-span-6">File</div>
            <div class="col-span-2">Status</div>
            <div class="col-span-2 text-center">Import</div>
            <div class="col-span-2 text-center">Delete</div>
          </div>

          <ul class="mt-2 space-y-2">
            <li v-for="file in files" :key="file" class="grid grid-cols-12 gap-2 items-center">
              <!-- File name (click to load) -->
              <div class="col-span-6 truncate">
                <button @click="loadFile(file)" class="text-left w-full text-blue-600 hover:underline truncate" :title="file">{{ file }}</button>
              </div>

              <!-- Status -->
              <div class="col-span-2">
                <span v-if="importedFiles.includes(file)" class="text-xs text-green-600">Imported</span>
              </div>

              <!-- Import button -->
              <div class="col-span-2 text-center">
                <button
                  @click.prevent="importFile(file)"
                  :disabled="importedFiles.includes(file)"
                  class="text-sm px-2 py-1 bg-gray-100 rounded disabled:opacity-50"
                >
                  Import
                </button>
              </div>

              <!-- Delete button -->
              <div class="col-span-2 text-center">
                <button @click.prevent="deleteFile(file)" class="text-sm text-red-600 hover:underline">Delete</button>
              </div>
            </li>
          </ul>
        </div>
      </aside>
    </div>
  </div>
</template>

<style scoped>
.bg-gray-100 {
  background-color: #f5f5f5;
}
textarea {
  resize: vertical;
}
.status-dot {
  display: inline-block;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 1px solid rgba(0,0,0,0.08);
}
.status-idle {
  background-color: #d1d5db; /* gray-300 */
}
.status-running {
  background-color: #f59e0b; /* amber-500 / orange */
}
.status-done {
  background-color: #10b981; /* emerald-500 / green */
}
</style>
