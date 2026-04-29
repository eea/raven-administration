/**
 * Composable that allows installed plugins to extend a named page with extra
 * fields and service interception — without modifying the page itself.
 *
 * Usage in any page component:
 *   const { extendOptions, extendService } = usePluginPageExtension('samplingpoints')
 *   const service = extendService(BaseService)
 *   options.value = extendOptions(pageOptions(lookups))
 *
 * Plugin client.js registers extensions via:
 *   window.__ravenPlugins[id].pageExtensions[pageName] = {
 *     extraProperties: [...],   // field defs in Manager/Crud format
 *     serviceHook: {
 *       afterGet(rows) { ... return rows; },
 *       onSave(data)  { ... }    // called before core update/insert
 *     }
 *   }
 */
export default function usePluginPageExtension(pageName) {
  function getExtensions() {
    const plugins = window.__ravenPlugins || {};
    return Object.values(plugins).filter(
      (p) => p.pageExtensions && p.pageExtensions[pageName]
    );
  }

  /**
   * Merge plugin extraProperties into the options.properties array.
   * Returns the base options unchanged if no plugin extends this page.
   */
  function extendOptions(baseOptions) {
    const extensions = getExtensions();
    if (!extensions.length) return baseOptions;
    const extra = extensions.flatMap((p) => p.pageExtensions[pageName].extraProperties || []);
    return {
      ...baseOptions,
      properties: [...(baseOptions.properties || []), ...extra],
    };
  }

  /**
   * Wrap a service object so plugin hooks are applied around get/update/insert.
   * Returns the base service unchanged if no plugin extends this page.
   */
  function extendService(baseService) {
    const extensions = getExtensions();
    if (!extensions.length) return baseService;

    const extraPropNames = new Set(
      extensions.flatMap((p) =>
        (p.pageExtensions[pageName].extraProperties || []).flatMap((f) =>
          [f.prop, f.prop_id].filter(Boolean)
        )
      )
    );
    const hooks = extensions
      .map((p) => p.pageExtensions[pageName].serviceHook)
      .filter(Boolean);

    function stripExtraProps(data) {
      return Object.fromEntries(
        Object.entries(data).filter(([k]) => !extraPropNames.has(k))
      );
    }

    return {
      ...baseService,

      async get() {
        let rows = await baseService.get();
        for (const hook of hooks) {
          if (hook.afterGet) rows = await hook.afterGet(rows);
        }
        return rows;
      },

      async update(data) {
        // Core update first — if it fails, plugin data is not saved either
        const result = await baseService.update(stripExtraProps(data));
        for (const hook of hooks) {
          if (hook.onSave) await hook.onSave(data);
        }
        return result;
      },

      async insert(data) {
        // Core insert must run first so FK constraint is satisfied
        const result = await baseService.insert(stripExtraProps(data));
        for (const hook of hooks) {
          if (hook.onSave) await hook.onSave(data);
        }
        return result;
      },
    };
  }

  return { extendOptions, extendService };
}
