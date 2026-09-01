/**
 * Composable that allows installed plugins to extend a named page with extra
 * fields and service interception — without modifying the page itself.
 *
 * Usage in any page component (extendOptions is async — it may fetch lookups):
 *   const { extendOptions, extendService } = usePluginPageExtension('samplingpoints')
 *   const service = extendService(BaseService)
 *   options.value = await extendOptions(pageOptions(lookups))
 *
 * Plugin client.js registers extensions via:
 *   window.__ravenPlugins[id].pageExtensions[pageName] = {
 *     extraProperties: [...],   // field defs in Manager/Crud format
 *     extraLookups: {           // optional; enables type: 'lookup' plugin fields
 *       myLookup: () => Promise<[{ value, label }]>
 *     },
 *     serviceHook: {
 *       afterGet(rows) { ... return rows; },
 *       onSave(data)  { ... }    // called before core update/insert
 *     }
 *   }
 *
 * extraLookups exists because a lookup field needs two things that live in different
 * places: the field definition (options.properties) and the option list keyed by
 * `lookup` (options.lookups). Merging only the former left plugins unable to offer a
 * dropdown at all, so they fell back to exposing raw foreign-key integers.
 */
export default function usePluginPageExtension(pageName) {
  function getExtensions() {
    const plugins = window.__ravenPlugins || {};
    return Object.values(plugins).filter(
      (p) => p.pageExtensions && p.pageExtensions[pageName]
    );
  }

  /**
   * Merge plugin extraProperties into options.properties, and plugin extraLookups
   * into options.lookups. Returns the base options unchanged if no plugin extends
   * this page — a plugin-free install sees the exact object pageOptions() built.
   */
  async function extendOptions(baseOptions) {
    const extensions = getExtensions();
    if (!extensions.length) return baseOptions;
    const extra = extensions.flatMap((p) => p.pageExtensions[pageName].extraProperties || []);

    const base = baseOptions.lookups || {};
    const lookups = { ...base };
    // Providers are resolved concurrently, and one that rejects yields an empty list
    // rather than taking the page down: the plugin that owns the data may be absent,
    // disabled, or refused by permission, and none of those is this page's problem.
    await Promise.all(
      extensions.flatMap((p) =>
        Object.entries(p.pageExtensions[pageName].extraLookups || {}).map(async ([key, fn]) => {
          // Core lookups win. A plugin registering `pollutants` would otherwise replace
          // the option list behind a core field, silently breaking a form it does not own.
          if (Object.prototype.hasOwnProperty.call(base, key)) {
            console.warn(
              `[${p.pluginId}] extraLookups '${key}' ignored on page '${pageName}': ` +
                'a core lookup already uses that key'
            );
            return;
          }
          lookups[key] = (await Promise.resolve(fn()).catch(() => [])) || [];
        })
      )
    );

    return {
      ...baseOptions,
      properties: [...(baseOptions.properties || []), ...extra],
      lookups,
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
