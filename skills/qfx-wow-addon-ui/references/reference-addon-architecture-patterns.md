# Reference Addon Architecture Patterns

This reference extracts architecture ideas from the two uploaded high-download reference addons: Plater and DandersFrames.

Use these ideas as architecture patterns, not as code or asset sources. Do not copy their bundled fonts, textures, libraries, private implementation code, or brand-specific systems unless the user explicitly asks and licensing is verified.

## 1. Architecture lessons worth absorbing

The shared strength of both reference addons is not only UI polish. They are maintainable because they separate concerns clearly:

- deterministic load order in the TOC;
- one root namespace plus feature subnamespaces;
- defaults loaded before runtime code;
- database/profile/migration isolated from feature code;
- localization loaded before any UI or user-facing strings;
- UI builders separated from runtime feature engines;
- compatibility and API fallbacks centralized;
- import/export and profile logic treated as first-class modules;
- debug/profiling/diagnostics available without being normal runtime hot paths;
- external API surface documented and kept separate from private internals;
- load-on-demand pages and tools for heavy option panels.

For QFX addons, apply the architecture pattern at the right scale. Do not make a small addon look like Plater or DandersFrames if it only has three options.

## 2. Recommended architecture tiers

### Small addon

Use this for one-feature addons such as a simple alert or minimap helper.

```text
AddonName.toc
Core.lua
DB.lua
Localization.lua
Options.lua
```

Rules:

- One root table from `local addonName, ns = ...`.
- One DB/defaults file.
- One options file.
- No module registry unless there are real modules.
- No public API unless another addon needs to call it.

### Medium QFX addon

Use this for QFXToolBox-style plugins with several independent features.

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
  Dialogs.lua
  Dropdown.lua
Modules/
  ChatBar.lua
  FocusInterrupt.lua
  QuickLoot.lua
Media/
  Media.lua
Compat/
  Version.lua
  Blizzard.lua
Debug/
  Diagnostics.lua
API.lua              optional
```

Rules:

- Use one module registry owned by Core.
- Each module exposes `:OnInitialize()`, `:OnEnable()`, `:OnDisable()`, and targeted refresh/apply functions only when needed.
- Module files should not create their own DB layer, locale resolver, or UI factory.
- Options UI calls module APIs; it should not duplicate module business rules.

### Large complex addon

Use this when the addon has profiles, import/export, designers, large lists, click-casting, unit frames, or external integrations.

```text
Core/
DB/
Profile/
Migration/
Locales/
UI/
Options/
Modules/
Features/
Designer/
ImportExport/
Compat/
Debug/
API.lua
```

Rules:

- Add clear lifecycle phases.
- Add versioned migrations.
- Add import/export validation.
- Add diagnostics and performance counters.
- Add a documented public API only for stable functions.
- Keep heavy designers, search pages, debug panels, and import tools lazy-loaded where possible.

## 3. Deterministic TOC load order

Both reference addons rely on predictable load order. QFX addons should do the same.

Recommended order:

```text
# Libraries
Libs\...

# Localization
Locales\enUS.lua
Locales\zhCN.lua
Locales\zhTW.lua

# Templates / XML, if used
AddonName.xml

# Core constants and defaults
Core\Version.lua
Core\Defaults.lua
Core\DB.lua
Core\Migration.lua
Core\Localization.lua

# Internal data and utility modules
Core\Util.lua
Core\Events.lua
Core\Scheduler.lua

# UI factory before UI pages
UI\UIFactory.lua
UI\Skin.lua
UI\Dropdown.lua
UI\Dialogs.lua

# Runtime modules
Modules\FeatureA.lua
Modules\FeatureB.lua

# Options and tools
UI\Options.lua
ImportExport\ImportExport.lua
Debug\Diagnostics.lua
API.lua

# Final bootstrap
Core\LoadFinished.lua
```

Rules:

- Defaults must load before DB initialization.
- Localization must load before any UI is created.
- UI factory must load before UI pages.
- Runtime modules should not depend on option pages.
- Final bootstrap may register load-on-demand factories and run post-load validation.
- Keep TOC comments useful; they are architecture documentation.

## 4. Root namespace and private internals

Use one root namespace from the addon table:

```lua
local addonName, QFX = ...
```

Recommended structure:

```lua
QFX.Core = QFX.Core or {}
QFX.DB = QFX.DB or {}
QFX.UI = QFX.UI or {}
QFX.Modules = QFX.Modules or {}
QFX.Media = QFX.Media or {}
QFX.Compat = QFX.Compat or {}
QFX.Debug = QFX.Debug or {}
QFX.API = QFX.API or {}
QFX.Internal = QFX.Internal or {}
```

Rules:

- Use `Internal` or file-local locals for private implementation details.
- Expose globals only when other addons or macros need them.
- Do not let external scripts overwrite arbitrary internals.
- If an external API is needed, create `API.lua` with documented functions and callbacks.
- Avoid multiple competing root tables such as `Addon`, `Core`, `Manager`, and `Engine` unless they are clearly nested under one namespace.

## 5. Lifecycle phases

A stable addon should have explicit lifecycle phases.

Recommended phases:

```text
ADDON_LOADED
  create defaults, DB tables, migrations, media registration, secure frame creation if required

PLAYER_LOGIN
  initialize runtime modules, register normal events, create UI entry points

PLAYER_ENTERING_WORLD
  apply live state that depends on world/group/instance data

PLAYER_REGEN_DISABLED
  stop unsafe editors, mark protected changes as deferred

PLAYER_REGEN_ENABLED
  apply queued protected changes and refresh layout

PLAYER_LOGOUT
  clean saved data, trim logs, persist positions
```

Rules:

- Secure/protected frames that must exist after combat reload should be created during the safe early window when possible.
- Do not create protected frames lazily in combat.
- Do not let option pages be required for runtime modules to function.
- Keep lifecycle code idempotent; repeated calls should not double-register events or duplicate frames.

## 6. Module registry

For medium and large QFX addons, use one module registry.

Rules:

- Module names must be stable and not localized.
- A module should own its events, runtime state, and targeted refresh methods.
- The registry should prevent duplicate registration.
- Modules should not directly rebuild the whole UI unless their scope requires it.
- Modules should not each create separate slash commands, minimap buttons, or profile systems without a clear reason.

## 7. Event dispatchers and event hygiene

DandersFrames shows a strong pattern with a roster unit event dispatcher: avoid global `UNIT_*` events when only roster units matter.

QFX rules:

- Centralize event registration where practical.
- Use targeted event dispatchers for high-frequency or unit-specific events.
- Prefer `RegisterUnitEvent` for known unit tokens instead of filtering global unit events in Lua.
- For roster-wide unit events, maintain a small pool of per-unit event frames if necessary.
- Avoid secret-value comparisons such as unsafe `UnitIsUnit` paths in Retail 12.x when string token matching is sufficient.
- Unregister events when a module is disabled or no subscriber remains.
- Keep test mode separate from live event dispatch if fake unit tokens cannot be registered with WoW APIs.

## 8. Scheduler and refresh coalescing

Large addons should coalesce repeated refreshes.

Rules:

- Provide `RequestRefresh(reason, scope)` or similar.
- Merge repeated refresh requests in the same frame.
- Let `full` override weaker reasons.
- Keep a last-refresh reason and counter for diagnostics.
- Slider text may update immediately, but heavy layout apply should be throttled.
- Bulk import should not call full rebuild per imported item.

## 9. Database, defaults, and migrations

Rules:

- Keep defaults in a dedicated file or section.
- Store a DB schema version.
- Run migrations once per profile/schema version.
- Deep-copy defaults when creating new profiles or mode-specific settings.
- Do not mutate the defaults table at runtime.
- Keep per-character data separate from global/profile data.
- Trim logs and transient caches before saving if they do not need to persist.
- For multi-mode settings, document ownership: global, profile, character, spec, mode, or runtime.

## 10. Profiles and import/export

For addons with profiles, import/export deserves its own module.

Rules:

- Include addon identifier, data type, version, and schema in exported strings.
- Validate imported data before applying it.
- Create a backup or preserve current profile before destructive import.
- Support unique profile naming when importing multiple profiles.
- Separate profile import from module import if the addon has several data categories.
- Keep Wago/share/import APIs stable if external tools consume them.
- Do not trust serialized text; guard decode/decompress/deserialize steps with `pcall`.

Recommended import pipeline:

```text
Decode -> Decompress -> Deserialize -> Validate -> Migrate -> Preview/Summary -> Apply -> Refresh
```

## 11. Media and optional libraries

Rules:

- Optional libraries must be requested with safe `LibStub(..., true)` where possible.
- Missing optional libraries should degrade gracefully.
- Media registration should happen early, but retry after `ADDON_LOADED` if SharedMedia loads later.
- Store media by logical name when possible, but always resolve to a real path before calling `SetFont`, `SetTexture`, or sound playback.
- Clear media/font caches when new SharedMedia entries are registered.
- Do not bundle heavy media libraries unless the addon needs them.

## 12. Compatibility boundaries

Rules:

- Centralize Retail/Classic/MoP/Titan/Midnight API checks in `Compat/Version.lua` or similar.
- Define fallback wrappers for renamed APIs.
- Keep external addon compatibility in `Compat/AddonName.lua` only when actually needed.
- Do not spread expansion checks through every feature file.
- If a feature is disabled for a version due to secret-value taint or missing API, document the reason near the compatibility boundary.

## 13. Public API and extension points

Rules:

- Keep a documented `API.lua` separate from private internals.
- Version the API if external users rely on it.
- Use callbacks for events other addons need to react to.
- Fire callbacks coalesced when possible instead of spamming during roster/layout updates.
- Expose stable functions, not raw DB tables.
- If user scripts/plugins are supported, provide a controlled whitelist of allowed hooks and override points.
- Do not allow user scripts to replace core lifecycle functions unless that is an explicit advanced design goal.

## 14. Debug, logs, and diagnostics

Rules:

- Provide bounded logs for important errors or recent actions.
- Keep log size small and trim old entries.
- Add debug channels such as `DB`, `UI`, `MEDIA`, `IMPORT`, `EVENT`, and `PERF`.
- Diagnostics should be lazy-loaded or hidden under Advanced.
- Profilers and OnUpdate registries should be disabled unless explicitly enabled.
- Provide copyable diagnostic summaries for bug reports.
- Never collect or expose private account data by default.

## 15. Test mode and preview mode

Rules:

- Test mode should not depend on real combat/party/raid state.
- Fake preview data should go through the same renderer when possible.
- Test frames should be pooled and cleaned up.
- Test mode must not register fake unit tokens with APIs that only accept real units.
- Closing options should not leave test frames or OnUpdate loops active unless explicitly requested.

## 16. File and folder naming rules

- Use stable English folder/file names.
- Keep one concern per file when the addon is medium or large.
- Split giant files once they mix runtime engine, UI builder, DB migration, and import/export logic.
- Do not split so aggressively that one tiny feature needs ten files.
- Keep comments near TOC entries when load order matters.

## 17. What not to copy from reference addons

Do not copy blindly:

- huge custom frameworks when QFX needs native lightweight UI;
- all bundled fonts/textures/sounds;
- every debug module into release runtime;
- public scripting systems unless the addon truly needs user scripts;
- heavyweight profile/import systems for small addons;
- version-specific hacks without understanding the API reason.

## 18. Architecture review checklist

When reviewing or designing a QFX addon, check:

- Is there one root namespace?
- Is TOC order deterministic and commented?
- Are defaults, DB, migrations, locale, UI, runtime modules, media, compat, debug, and API separated at the right scale?
- Are modules idempotent and lifecycle-aware?
- Are high-frequency events centralized or targeted?
- Are refreshes coalesced?
- Are profiles and imports validated and migratable?
- Are optional libraries safe when missing?
- Are compatibility fallbacks centralized?
- Are public APIs documented and private internals protected?
- Are diagnostics available without adding idle overhead?
- Is the release zip clean and complete?
