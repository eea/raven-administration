import { Get, Post, Put, Delete } from "../../../helpers/request";

const RNotebookService = {
  // Run arbitrary R code
  runCode: async (code) => {
    return Post("/api/rnotebook/run", { code });
  },

  // List objects in R workspace
  listObjects: async () => {
    return Get("/api/rnotebook/ls");
  },

  // Reset workspace
  resetWorkspace: async () => {
    return Post("/api/rnotebook/reset");
  },

  // Import a saved .R file into the R persistent session via the Flask helper
  importFile: async (filename) => {
    return Post('/api/rnotebook/import', { filename });
  },

  // Save the current R workspace to a .R file via the Flask helper
  runRCode: async (code) => {
    return Post(`/api/rnotebook/run_r`, { code });
  },

  // List saved .R files
  listRFiles: async () => {
    return Get(`/api/rnotebook/rfiles`);
  },

  // Get the content of a saved .R file
  getRFile: async (filename) => {
    const encoded = encodeURIComponent(filename);
    return Get(`/api/rnotebook/rfiles/${encoded}`);
  },

  // Save a new .R file
  saveRFile: async (filename, content) => {
    return Post(`/api/rnotebook/rfiles`, { filename, content });
  },

  // Update an existing .R file
  updateRFile: async (filename, content) => {
    const encoded = encodeURIComponent(filename);
    return Put(`/api/rnotebook/rfiles/${encoded}`, { content });
  },

  // Delete a saved .R file
  deleteRFile: async (filename) => {
    const encoded = encodeURIComponent(filename);
    return Delete(`/api/rnotebook/rfiles/${encoded}`);
  }

};

export default RNotebookService;