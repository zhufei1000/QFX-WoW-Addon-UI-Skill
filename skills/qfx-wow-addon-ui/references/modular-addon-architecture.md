# Modular Addon Architecture

Use the EllesmereUI-style method as the baseline modular architecture for QFX addons, scaled by addon size. Earlier QFX, Plater-inspired, and DandersFrames-inspired rules are supplements, not competing architecture systems.

## Size tiers

### Small addon

Use when the addon has one main feature, few settings, and no complex lists or editors.

Recommended shape:

```text
AddonName.lua or Core.lua
Localization.lua      optional
Options.lua           optional
Compat.lua            optional
```

Rules:
- Keep it simple.
- One root namespace.
- One small event frame.
- Runtime can load before options exist.
- Native Blizzard controls by default.
- No page cache unless settings are already heavy.
- No central dispatcher unless repeated/high-frequency events exist.

### Medium QFX addon

Use when the addon has multiple modules, a real settings panel, or several runtime features.

Recommended shape:

```text
Core/
  Init.lua
  Events.lua
  DB.lua
  Migration.lua
  Localization.lua
UI/
  UIFactory.lua
  MainFrame.lua
  Options.lua
  Dropdown.lua
  Lists.lua
Modules/
  ModuleName.lua
Compat/
  Version.lua
Media/
  Media.lua
```

Rules:
- One module registry.
- One UI factory.
- One DB/default/migration layer.
- Runtime modules expose APIs to options pages.
- Options UI is lazy-created.
- Repeated controls use factory helpers or table-driven option rows.
- Repeated refreshes use `RequestRefresh` or equivalent.

### Large addon or addon suite

Use when the addon has many modules, saved lists, import/export, profile switching, visual editors, child addons, or heavy diagnostics.

Recommended additions:

```text
UI/
  ModuleRegistry.lua
  PageCache.lua
  RefreshRegistry.lua
  SearchRegistry.lua
Core/
  Dispatcher.lua
  RefreshQueue.lua
Profiles/
  Profiles.lua
ImportExport/
  ImportExport.lua
Debug/
  Diagnostics.lua
API.lua                 optional
```

Rules:
- One registered settings shell.
- Modules register title, description, pages, page builders, refresh hooks, and reset hooks.
- Page cache is allowed but must have invalidation rules.
- Widget refresh callbacks should handle value/status refreshes.
- Central dispatch should handle shared high-frequency events.
- Search indexes real setting metadata; it does not duplicate controls.
- Debug/profiling is lazy-loaded or explicitly enabled.
- Public API is separate from private internals.

## Settings shell contract

A module should register with the shell instead of creating its own independent options frame when the addon has a shared settings UI.

```lua
QFX.UI:RegisterModule("ModuleKey", {
    title = L["Module Title"],
    description = L["Module description."],
    pages = { "General", "Advanced" },
    buildPage = function(pageName, parent, y) end,
    refresh = function(pageName) end,
    reset = function() end,
})
```

The shell owns navigation, scroll, page cache, common buttons, and search. The module owns feature logic, settings definitions, and apply behavior.

## Load order

Prefer deterministic load order:

```text
Libraries if used
Locales
Defaults
DB / Migration
Compat
Core utilities
Event dispatcher / refresh queue
UI factory
Runtime modules
Options page builders
Final bootstrap
```

Runtime modules must not require option pages to be opened.

## Rules

- Do not create duplicate module registries, DB layers, locale tables, UI factories, media resolvers, refresh queues, search registries, or event buses.
- Child addons should not become independent unless explicitly requested.
- Defaults must load before DB initialization.
- Localization must load before UI creation.
- Compatibility checks should live in one boundary instead of being scattered through every file.
- High-frequency events should use targeted or central dispatchers when practical.
- Public APIs should be documented and separate from private internals.
- Import/export should validate and migrate data before applying it.
- Debug/profiling should be lazy-loaded or explicitly enabled, not always active.
- Object pools are allowed only with explicit reset/release discipline; rebuild small stale-prone UI pieces when pooling causes state leaks.

## Supplementary references

Use these as supplements to the baseline method:

- `references/qfx-ui-architecture.md` for UI shell, UI factory, page cache, and option-row rules.
- `references/refresh-performance-rules.md` for refresh queues, widget callbacks, page cache, and bulk import refresh.
- `references/event-onupdate-rules.md` for central dispatch, temporary OnUpdate, and weak-table state.
- `references/reference-addon-architecture-patterns.md` for broader reference-addon architecture.
- `references/deep-reference-addon-patterns.md` for advanced extension systems, resolver pipelines, diagnostics, and alert state machines.
