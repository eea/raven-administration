import { Get, Post, Delete } from "../../../helpers/request";

const PluginService = {
  list:        async ()              => Get("/api/misc/plugins"),
  catalog:     async ()              => Get("/api/misc/plugins/catalog"),
  install:     async (plugin)        => Post("/api/misc/plugins/install", plugin),
  uninstall:   async (id)            => Delete(`/api/misc/plugins/${id}`),
  enable:      async (id)            => Post(`/api/misc/plugins/${id}/enable`),
  disable:     async (id)            => Post(`/api/misc/plugins/${id}/disable`),
  getConfig:   async (id)            => Get(`/api/misc/plugins/${id}/config`),
  saveConfig:  async (id, config)    => Post(`/api/misc/plugins/${id}/config`, config),
  restart:     async ()              => Post("/api/misc/plugins/restart"),
};

export default PluginService;
