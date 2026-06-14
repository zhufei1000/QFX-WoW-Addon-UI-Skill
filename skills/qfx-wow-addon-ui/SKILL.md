# QFX WoW Addon UI Skill

Use this skill when reviewing, designing, refactoring, or packaging World of Warcraft addon user interfaces, addon architectures, and WoW API-safe code, especially QFX-style addons.

This skill is optimized for:
- Blizzard-native WoW UI style.
- Compact but readable settings panels.
- English, Simplified Chinese, and Traditional Chinese localization.
- WoW 12.x / Midnight API source-grounding and secret-value / taint safety.
- Multi-version addon UI packaging.
- QFX addon conventions: lightweight, modular, native-looking, minimal performance cost.
- Complex addon UI patterns: singleton scrollable dropdowns, large saved-list rendering, drag/drop collections, language-safe editor dialogs, and batched UI refresh.
- Plater-inspired option-panel patterns: tabbed categories, table-driven option rows, reusable templates, load-on-demand heavy tabs, searchable settings, reusable scroll rows, and one global change callback.
- DandersFrames-inspired complex settings patterns: persistent collapsible groups, semantic banners, See Also navigation, searchable settings registry, guided setup wizard, profile override indicators, preview-safe editors, and advanced diagnostics.
- Reference-addon architecture patterns from Plater and DandersFrames: deterministic TOC load order, root namespace boundaries, lifecycle phases, module registry, event dispatchers, DB/profile migration, import/export validation, compatibility boundaries, public API separation, and lazy diagnostics.
- Deep reference-addon patterns: controlled extension hooks, adapter/resolver/renderer pipelines, capability gates, self-healing media fallback, object-pool reset discipline, post-load validation, category-scoped imports, auto-profile switching, safe profiling, foreign attachment scans, alert state machines, option dependency graphs, and design tokens.

## Core goals

When this skill is active, prefer:

1. Native Blizzard controls over custom-drawn controls.
2. Compact width-aware layout over tall sparse pages.
3. Shared UI factory helpers over one-off widget code.
4. Clear module boundaries over giant mixed UI files.
5. Localized strings over hardcoded UI text.
6. Deferred combat-safe apply over direct protected-frame changes in combat.
7. Release-ready packaging checks over code-only edits.
8. Minimal-diff, traceable changes with clear rollback notes.
9. Reference-addon patterns as design guidance, not asset or library copying.
10. Complex settings navigation over dumping every option into one long scroll page.
11. Proven reference-addon architecture patterns over ad-hoc file growth.
12. Source-grounded WoW API usage over memory-based API guesses.

## Mandatory WoW UI constraints

### Native first

Prefer Blizzard templates and standard visual behavior:
- `UIPanelButtonTemplate`
- `UICheckButtonTemplate`
- `UIDropDownMenuTemplate` or a project-local wrapper that mimics Blizzard dropdown behavior
- `OptionsSliderTemplate` or native slider equivalents
- `InputBoxTemplate`
- `BackdropTemplateMixin` where required

Do not mix many visual systems in the same panel unless the addon already does so and a migration is explicitly requested.

### Reference addon use

When the user supplies a reference addon such as Plater or DandersFrames, extract reusable design and architecture rules only:
- tab organization;
- table-driven option definitions;
- shared templates and helpers;
- search/index behavior;
- persistent collapsible groups;
- semantic banners and cross-page navigation;
- guided setup and preview-safe editors;
- profile override indicators;
- advanced diagnostics;
- scroll-row creation and refresh separation;
- combat-safe visibility and refresh behavior;
- deterministic TOC load order and lifecycle phases;
- root namespace, public/private boundary, and documented API;
- DB/profile migration and import/export validation;
- targeted event dispatchers and lazy diagnostics;
- controlled extension hooks and trigger registries;
- adapter/resolver/renderer pipelines;
- self-healing media fallbacks and post-load validation;
- safe profilers, foreign attachment scanners, and alert state machines.

Do not copy bundled fonts, textures, icons, sounds, third-party libraries, or brand-specific art from the reference addon into QFX addons unless the user explicitly requests it and licensing is verified.

## WoW 12.x API source-grounding rules

For Retail 12.x / Midnight API correctness, read `references/wow-12-api-source-rules.md` before writing or changing code that calls WoW APIs.

Key rules:
- A GitHub search did not find a ready-made public `WoW 12.0 API Codex Skill`; use current source/resource repositories and API documentation instead.
- Prefer current FrameXML/UI source, extracted interface resources/API dumps, Warcraft Wiki API notes, and same-branch addon examples in that order.
- Match the branch and build before trusting signatures: live, ptr, ptr2, beta, Retail, Classic, MoP, TBC, and Titan must not be mixed.
- Treat spell, aura, cast/interrupt, unit, tooltip, C_ namespace, secure frame, addon compartment, minimap, TTS, template, mixin, and deprecated global APIs as high-risk until verified.
- Isolate version-sensitive APIs in `Compat` wrappers; do not scatter raw branch checks through feature modules.
- Never invent a 12.x API signature from memory. If unsure, search current source/dumps/wiki, wrap the API, and report the assumption.
- Secret-value and taint errors require redesign around safe events, fixed timers, cached safe values, or user configuration, not only nil/boolean guards.

## Secret value / taint safety

For Retail 12.x and modern WoW builds:
- Do not compare, store, serialize, or arithmetic secret values.
- Avoid direct decisions based on protected/secret results during combat.
- Be careful with APIs returning protected booleans, spell availability, cooldowns, unit health/power, aura internals, or interruptibility.
- Prefer event-driven approximations, fixed timers, cached safe values, or user-provided configuration.

If a reported error includes phrases like:
- `a secret boolean value`
- `a secret number value`
- `execution tainted by`

then treat it as a taint/secret-value issue, not a normal Lua type bug.

## Plater-inspired options UI patterns

For addons with many option categories, read `references/plater-options-ui-patterns.md`.

Key rules:
- Use a tab container when one scrolling page would become too long or mixed.
- Put category definitions in one table with stable tab names and localized labels.
- Use load-on-demand creation for heavy tabs such as search, profile, designer, media, import/export, or advanced pages.
- Describe rows through option tables where possible: `type`, `name`, `desc`, `get`, `set`, `values`, `min`, `max`, and `step`.
- Route option changes through one global callback that updates DB cache and applies only the required refresh.
- Keep search as an index over existing option metadata, not a second duplicate settings UI.
- For scroll lists, split line creation from line refresh and reuse row frames.
- Show combat state clearly when live changes may be blocked or deferred.

## DandersFrames-inspired complex settings UI patterns

For large addons with many modules, profiles, visual editors, or first-run setup flows, read `references/dandersframes-complex-settings-ui.md`.

Key rules:
- Use persistent collapsible groups to keep large pages compact without losing setting context.
- Use semantic banners for combat lockdown, destructive actions, secret-value limitations, missing libraries, and compatibility warnings.
- Use `See Also` cross-page navigation instead of duplicating the same setting in several tabs.
- Register searchable settings metadata with stable IDs, breadcrumbs, aliases, widget type, and jump/highlight callbacks.
- Use guided setup wizards only for first-run or multi-step batch configuration; wizards must write through the same DB/module APIs as the real settings page.
- Show profile/global/spec/mode override status when settings can come from multiple layers, and provide safe reset-to-parent behavior.
- For visual editors, use preview-safe proxy data so Save commits and Cancel discards changes.
- Advanced diagnostic pages should be lazy-loaded, hidden from normal users, and useful for bug reports without constantly running expensive scanners.

## Reference-addon architecture patterns

For plugin architecture ideas extracted from Plater and DandersFrames, read `references/reference-addon-architecture-patterns.md` and `references/deep-reference-addon-patterns.md`.

Key rules:
- Use deterministic TOC load order: libraries, locales, templates, defaults, DB/migration, utilities, UI factory, modules, options/tools, final bootstrap.
- Use one root namespace from `local addonName, ns = ...`; keep private internals file-local or under `Internal`.
- Scale architecture by addon size: small addons stay simple, medium addons get modules, large addons get profile/import/export/API/debug boundaries.
- Define lifecycle phases for `ADDON_LOADED`, `PLAYER_LOGIN`, `PLAYER_ENTERING_WORLD`, combat enter/leave, and logout.
- Runtime modules must not require option pages to be opened.
- Use one module registry; prevent duplicate module, DB, UI factory, locale, media, and event systems.
- Use targeted event dispatchers for high-frequency unit events; avoid many modules filtering the same global event independently.
- Coalesce refreshes with `RequestRefresh(reason, scope)` and record last refresh reason for diagnostics.
- Keep DB defaults, schema version, migrations, profiles, and per-character data clearly separated.
- Import/export should use a validate pipeline: decode, decompress, deserialize, validate, migrate, preview/summary, apply, refresh.
- Optional libraries and media must degrade gracefully and resolve to real asset paths before WoW API calls.
- Public API and callbacks belong in `API.lua`; expose stable functions, not raw internal DB tables.

## Deep architecture patterns

For advanced larger-addon work, read `references/deep-reference-addon-patterns.md`.

Key rules:
- Add controlled extension/scripting systems only when the addon truly needs presets, user packs, external integrations, or user-defined logic.
- Extension systems need a fixed hook catalog, trigger registry, metadata, guarded dispatch, error quarantine, and a small public API instead of raw DB access.
- Use Adapter / Resolver / Renderer pipelines for complex visual editors, text systems, aura/alert systems, minimap providers, and preview pages.
- Centralize capability gates and feature flags so missing APIs, optional libraries, combat safety, and known taint risks have clear reasons.
- Imported profiles must self-heal missing media by resolving assets, falling back to stock paths, warning once, and exposing diagnostics.
- Use object pools only with explicit reset/release discipline; rebuild small stale-prone components when pooling causes state leaks.
- Auto-profile switching must be explicit, validated, combat-safe, and visible in diagnostics.
- Profilers and debug hooks must be opt-in, ownership-filtered, and must never wrap Blizzard secure frames or foreign addon frames.
- Alert engines should use explicit state machines and cleanup all timers/tickers on stop, profile switch, spec change, logout, or module disable.
- Centralize option dependency graphs so enabling/disabling child controls is consistent and explainable.

## Recommended UI and architecture structure

For medium or large QFX addons, prefer this structure and scale it down for small addons:

```text
Core/
  Init.lua
  Events.lua
  DB.lua
  Migration.lua
  Localization.lua
UI/
  UIFactory.lua
  Skin.lua
  MainFrame.lua
  Options.lua
  Dialogs.lua
  Dropdown.lua
Modules/
  ModuleName.lua
Media/
  Media.lua
Compat/
  Version.lua
  Blizzard.lua
Debug/
  Diagnostics.lua
ImportExport/
  ImportExport.lua      if needed
API.lua                 if external access is needed
```

Do not create a second architecture inside an addon that already has one. Extend the existing one.

## UI factory rules

A project-local UI factory should centralize:
- Button creation.
- Checkbox creation.
- Dropdown creation.
- Slider creation.
- Section/card creation.
- Font/color helpers.
- Tooltip helpers.
- Consistent spacing constants.
- Optional table-driven options row creation for large settings panels.
- Optional collapsible-section, banner, search-registration, setting-highlight, and wizard helpers for complex settings panels.

The UI factory should not know addon business rules. Business logic belongs in modules/controllers.

## Slider layout standard

For QFX addon sliders, use this layout unless the user says otherwise:
- Slider track on the main row.
- Minimum label under the left end of the slider.
- Maximum label under the right end of the slider.
- Current value centered under the slider.
- Minimum, current, and maximum labels must be on the same horizontal line.
- Do not place the current value to the right side of the slider in compact cards.

## Large list and collection UI rules

For saved sound lists, voice collections, addon lists, module lists, or large option lists:
- Reuse row frames.
- Do not rebuild every row for every tiny state change.
- Keep selection state independent from row object lifetime.
- Empty collections must still be selectable if edit/delete actions apply to the collection itself.
- If an enabled/visible checkbox controls list membership, sorting rows must update immediately when the item is hidden/shown.
- Dragging an item out of a collection must preserve the item identity until drop completes.

## Sound, TTS, and media picker rules

For sound/TTS addon UIs:
- Built-in sound lists can be long; use searchable or scrollable dropdowns/lists.
- LibSharedMedia integration should not break if the library is missing.
- TTS test buttons must use the same playback path as real alerts where possible.
- TTS channel controls should not be disabled unless WoW API limitations require it.
- File path inputs should explain valid relative paths.
- Do not assume every client locale has the same TTS voice behavior.

## Combat lockdown deferred apply

If a setting touches protected frames or frames likely to become protected:
- If not in combat, apply immediately.
- If in combat, save the setting, mark apply pending, show a small note if needed, and apply on `PLAYER_REGEN_ENABLED`.

Never spam chat for every deferred setting change.

## Packaging and release checklist

Before returning a release zip or publishable package, verify:
- TOC exists and points to files that exist.
- SavedVariables are declared if used.
- Libraries are present if referenced.
- Media files are present if referenced.
- No missing sub-addons were dropped from the package.
- No debug-only test files are accidentally included unless requested.
- Version number is updated consistently.
- Version numbers use three-part decimal integer progression: `MAJOR.MINOR.PATCH`; for example, `1.1.10` is newer than `1.1.9`.
- Zip root folder is correct.
- Release zip name uses addon name plus official version only, for example `QFXToolBox_0.44.20.zip`.
- English, Simplified Chinese, and Traditional Chinese localization files are included if the addon claims three-language support.

## Modification traceability

For any code or package modification, final responses should include:
- Files changed.
- Files added.
- Files deleted.
- TOC impact.
- SavedVariables impact.
- API assumptions or branch/build assumptions.
- Risk level.
- Rollback notes.
- In-game test steps.

Use this even for small UI-only changes unless the user asks for a very short response.

## Minimal-diff discipline

When fixing a specific issue:
- Do not reformat unrelated files.
- Do not rename unrelated functions.
- Do not migrate architecture unless requested.
- Do not delete fallbacks unless you are sure they are obsolete and the user agrees.
- Do not change feature behavior while doing UI-only work.

## Common user preferences for QFX addons

Assume these preferences unless the user says otherwise:
- Native Blizzard-style UI, not modern web-style UI.
- Lightweight performance.
- No unnecessary animation.
- Three-language support: English, 简体中文, 繁體中文.
- Default language follows client unless a force-language option exists.
- Compact panels that use available width.
- Tooltips on section titles for explanations.
- No unnecessary ElvUI/NDui compatibility unless the addon actually interacts with their frames.
- Release zips should include all sub-addons.

## What to do when asked to optimize an addon UI, architecture, or API usage

1. Inspect existing UI, architecture, and API usage first.
2. Identify whether the addon uses native controls, Ace, custom controls, or mixed controls.
3. Preserve functionality and SavedVariables unless the user requests behavior changes.
4. Centralize repeated UI logic into the existing factory/helpers.
5. For WoW 12.x work, verify changed APIs against current source/resources/wiki, isolate risky calls in Compat wrappers, and report branch/build assumptions.
6. For large option panels, consider Plater-style tab segmentation, option-table rows, delayed heavy tabs, searchable metadata, and reusable scroll rows.
7. For very complex settings, consider DandersFrames-style collapsible groups, semantic banners, See Also navigation, setting search registry, first-run wizard, profile override indicators, preview-safe editors, and lazy diagnostic pages.
8. For plugin architecture, apply reference-addon patterns: TOC order, root namespace, lifecycle phases, module registry, DB/profile migration, targeted events, import/export validation, API boundary, and lazy diagnostics.
9. Check combat-lockdown and secret-value risks if the UI applies live settings.
10. Package and report changes clearly.

## What to do when asked to update this skill

1. Preserve the existing skill structure.
2. Add or update focused reference files rather than dumping everything into `SKILL.md`.
3. Update `README.md`, `.codex-plugin/plugin.json`, and `INSTALL.md` version if the skill version changes.
4. Keep names generic unless a file is intentionally a case study.
5. Avoid reference names that make a reusable rule look like it only applies to one addon.
6. When using a reference addon or API source, document extracted rules and explicitly avoid copying assets/libraries unless requested and licensed.

## Reference loading guide

When a task involves a specific concern, read the matching reference:

- WoW 12.x API source rules: `references/wow-12-api-source-rules.md`
- Deep reference addon patterns: `references/deep-reference-addon-patterns.md`
- Reference addon architecture patterns: `references/reference-addon-architecture-patterns.md`
- DandersFrames-style complex settings UI: `references/dandersframes-complex-settings-ui.md`
- Plater-style options UI model: `references/plater-options-ui-patterns.md`
- Native UI consistency: `references/blizzard-native-ui-checklist.md`
- Architecture and UI factory: `references/qfx-ui-architecture.md`
- Secret values and taint: `references/wow-12-secret-value-taint.md`
- Dialog/dropdown/popup rules: `references/ui-factory-dialog-mode-rules.md`
- Compact multilingual layout: `references/compact-multilingual-layout.md`
- Large saved lists / collections / sounds: `references/large-list-collection-sound-ui.md`
- Complex addon UI patterns: `references/complex-addon-ui-patterns.md`
- Combat lockdown apply: `references/combat-lockdown-deferred-apply.md`
- Packaging/release: `references/packaging-release-checklist.md`
- Modular architecture: `references/modular-addon-architecture.md`
- Safe font/media handling: `references/safe-font-media-rules.md`
- SavedVariables migration: `references/savedvariables-migration.md`
- Refresh performance: `references/refresh-performance-rules.md`
- Event/OnUpdate discipline: `references/event-onupdate-rules.md`
- Version compatibility: `references/version-compat-boundaries.md`
- Modification traceability: `references/modification-traceability.md`

## Output expectations

When reviewing UI, architecture, or API safety, return:
- Priority issues.
- Suggested fixes.
- Files likely involved.
- API assumptions or source checks needed.
- Risk level.
- Test steps.

When modifying files, return:
- Download link or commit summary.
- Changed/added/deleted files.
- What changed.
- What did not change.
- API assumptions or branch/build assumptions.
- Test steps.
- Rollback notes.
