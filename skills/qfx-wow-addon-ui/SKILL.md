# QFX WoW Addon UI Skill

Use this skill when reviewing, designing, refactoring, or packaging World of Warcraft addon user interfaces, addon architectures, and WoW API-safe code, especially QFX-style addons.

This skill is optimized for:
- Blizzard-native WoW UI style.
- English-first layout sizing, then Simplified Chinese and Traditional Chinese verification, so English labels do not overflow and Chinese layouts remain safe.
- Compact but readable settings panels.
- English, Simplified Chinese, and Traditional Chinese localization.
- WoW 12.x / Midnight API source-grounding and secret-value / taint safety.
- Multi-version addon UI packaging.
- QFX addon conventions: lightweight, modular, native-looking, minimal performance cost.
- EllesmereUI-style primary design method: one scalable architecture for small, medium, and large addons using a registered settings shell when needed, deferred options creation, page cache where useful, widget refresh callbacks, central event dispatch, coalesced refresh/apply queues, temporary OnUpdate, weak-table frame state, and combat-safe deferred apply.
- Plater-inspired option-panel supplements: tabbed categories, table-driven option rows, reusable templates, load-on-demand heavy tabs, searchable settings, reusable scroll rows, and one global change callback.
- DandersFrames-inspired complex settings supplements: persistent collapsible groups, semantic banners, See Also navigation, searchable settings registry, guided setup wizard, profile override indicators, preview-safe editors, and advanced diagnostics.
- Reference-addon architecture supplements from Plater and DandersFrames: deterministic TOC load order, root namespace boundaries, lifecycle phases, module registry, DB/profile migration, import/export validation, compatibility boundaries, public API separation, and lazy diagnostics.
- Deep reference-addon supplements: controlled extension hooks, adapter/resolver/renderer pipelines, capability gates, self-healing media fallback, object-pool reset discipline, post-load validation, category-scoped imports, auto-profile switching, safe profiling, foreign attachment scans, alert state machines, option dependency graphs, and design tokens.

## Core goals

When this skill is active, prefer:

1. The EllesmereUI-style scalable design method as the primary architecture baseline.
2. Native Blizzard controls over custom-drawn controls unless the user explicitly requests a modern custom skin.
3. English-first UI layout sizing over Chinese-first layouts that later overflow after translation.
4. Compact width-aware layout over tall sparse pages.
5. Shared UI factory helpers over one-off widget code.
6. Clear module boundaries over giant mixed UI files.
7. Localized strings over hardcoded UI text.
8. Deferred combat-safe apply over direct protected-frame changes in combat.
9. Runtime modules that do not require options pages to be opened.
10. Deferred heavy options initialization over startup-time settings construction.
11. Widget refresh callbacks and targeted refresh over repeated full-page rebuilds.
12. Central event dispatch and coalesced refresh over duplicate high-frequency event handlers.
13. Temporary active-only OnUpdate over permanent idle polling.
14. Weak-table state for Blizzard or foreign frames when ownership, lifecycle, or taint risk exists.
15. Release-ready packaging checks over code-only edits.
16. Minimal-diff, traceable changes with clear rollback notes.
17. Source-grounded WoW API usage over memory-based API guesses.
18. Reference-addon patterns as design guidance, not asset or library copying.

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

### English-first multilingual layout

For any UI that supports English, Simplified Chinese, and Traditional Chinese, design width from English first.

Rules:
- Treat English as the base layout language because English strings are usually longer than Chinese.
- Size labels, buttons, dropdowns, tabs, section titles, and column widths against English strings first.
- Then verify Simplified Chinese and Traditional Chinese.
- Do not design a tight Chinese layout and translate it to English afterward.
- If English overflows, fix the layout structure with a wider control, full-width row, shorter visible label, tooltip description, fewer columns, or more horizontal space.
- Do not solve English overflow by shrinking fonts below the QFX standard unless there is no better layout option.

For details, read `references/compact-multilingual-layout.md` and `references/ui-typography-localization-zh.md`.

### UI visual standards

Every QFX panel should follow one pixel-level visual baseline so repeated work stays consistent. Read `references/ui-visual-standards.md` before building panels.

Rules:
- Use a 4px spacing grid; row heights of 24/28/32px.
- Standard control sizes: buttons 22-24px high with min width 80px or measured EN text + 28px padding; checkbox 16px; color swatch 24-32px wide with no label inside.
- Left label column 160-200px, sized from English text first and kept under 40% of panel width; numeric values right-align, text values left-align.
- Keep a 3-level font hierarchy (title / label / desc) plus inherited template text; never shrink fonts below the QFX standard to fix overflow.
- Define semantic colors by purpose (normal, muted, warning, danger, success, accent) and never convey state with color alone.
- Dialogs use standard width tiers: narrow 320-400px, standard 640-720px, wide 800-960px; clamp to screen and respect UI scale.
- Preserve scroll position across tab switches and reopen; scroll target rows into view after search/jump.

### UI states and accessibility

Panels must cover empty, loading, error, success, and confirm states, and stay usable without a mouse. Read `references/ui-states-accessibility.md` for details.

Rules:
- Empty lists show a localized hint plus one action button.
- Long operations show the Blizzard spinner/progress and refresh only the affected region on completion.
- Input errors are inline and non-modal, paired with text, not color alone.
- Destructive actions (reset, delete, overwrite import) use a narrow confirm dialog with a verb-labeled danger button; Esc cancels.
- Panels are fully keyboard-navigable: logical Tab order, arrow keys in lists/dropdowns, visible focus state, Esc closes popup then dialog.
- Keep text contrast at Blizzard template levels; never go below 11px for user-facing text; test at 150%+ UI scale.
- Animations stay short (150-300ms), non-looping, stoppable, and skipped when the player disables motion.

### Reference addon use

When the user supplies a reference addon such as EllesmereUI, Plater, or DandersFrames, extract reusable design, architecture, and runtime rules only.

Use EllesmereUI-style rules as the primary design method for:
- small-addon, medium-addon, and large-addon architecture scaling;
- registered settings shells;
- module metadata and page builders;
- runtime/options separation;
- deferred options initialization;
- page cache and page invalidation;
- widget refresh callbacks;
- central high-frequency event dispatch;
- coalesced refresh and apply queues;
- temporary OnUpdate discipline;
- weak-table state storage;
- combat-safe deferred apply.

Use earlier QFX, Plater-inspired, DandersFrames-inspired, native-UI, and WoW API rules as supplements. If they conflict with the EllesmereUI-style method on UI lifecycle, refresh strategy, event dispatch, OnUpdate behavior, or runtime performance, prefer the EllesmereUI-style method.

This priority does not override the QFX visual preference. Keep QFX addons Blizzard-native by default unless the user explicitly asks for custom-drawn visuals.

Do not copy bundled fonts, textures, icons, sounds, third-party libraries, or brand-specific art from reference addons into QFX addons unless the user explicitly requests it and licensing is verified.

## Primary QFX design method

For all QFX addons, choose the right scale.

### Small addon

Use a simple root namespace, small DB/defaults, optional localization, optional options page, and one local event frame.

Do not add a large settings shell, page cache, search registry, or central dispatcher unless the addon has repeated settings, heavy lists, or high-frequency events.

### Medium addon

Use:

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
  Lists.lua
Modules/
  ModuleName.lua
Media/
  Media.lua
Compat/
  Version.lua
  Blizzard.lua
```

Rules:
- Runtime modules expose `Enable`, `Disable`, `Apply`, `Refresh`, and optional `GetStatus` functions.
- Options pages call module APIs; they do not own runtime state.
- Heavy options UI is created only when the settings panel is opened.
- Repeated controls use the shared UI factory or table-driven option rows.
- Repeated refreshes use `RequestRefresh` or equivalent.
- Layout width is validated against English strings before Chinese localization is considered complete.

### Large addon or addon suite

Add only the boundaries the addon needs:

```text
UI/
  ModuleRegistry.lua
  PageCache.lua
  RefreshRegistry.lua
  SearchRegistry.lua
Core/
  Dispatcher.lua
  RefreshQueue.lua
Debug/
  Diagnostics.lua
ImportExport/
  ImportExport.lua      if needed
API.lua                 if external access is needed
```

Rules:
- Use one registered settings shell for module navigation.
- Modules register title, description, pages, page builders, refresh hooks, and reset hooks.
- Page cache is allowed but must have invalidation rules.
- Widget refresh callbacks handle value/status refreshes.
- Central dispatch handles shared high-frequency events.
- Search indexes real setting metadata and jumps to real controls; it does not duplicate controls.
- Debug/profiling is lazy-loaded or explicitly enabled.
- The settings shell, tabs, module list, buttons, dropdowns, and searchable metadata are sized from English first.

## WoW 12.x API source-grounding rules

For Retail 12.x / Midnight API correctness, read `references/wow-12-api-source-rules.md` before writing or changing code that calls WoW APIs.

For migration or review of addons between 12.0.7 live and 12.1.0 PTR, read `references/wow-12.0.7-to-12.1-api-migration-zhCN.md`; it documents verified Aura access gating, the AuraContainer display layer, Unit identity/possession secret predicates, ForbiddenAspect/SecretAspect changes, and CooldownViewer data extensions for the current PTR build.

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

## Plater-inspired options UI supplements

For addons with many option categories, read `references/plater-options-ui-patterns.md` as a supplement to the primary QFX design method.

Key rules:
- Use a tab container when one scrolling page would become too long or mixed.
- Put category definitions in one table with stable tab names and localized labels.
- Use load-on-demand creation for heavy tabs such as search, profile, designer, media, import/export, or advanced pages.
- Describe rows through option tables where possible: `type`, `name`, `desc`, `get`, `set`, `values`, `min`, `max`, and `step`.
- Route option changes through one global callback that updates DB cache and applies only the required refresh.
- Keep search as an index over existing option metadata, not a second duplicate settings UI.
- For scroll lists, split line creation from line refresh and reuse row frames.
- Show combat state clearly when live changes may be blocked or deferred.

## DandersFrames-inspired complex settings supplements

For large addons with many modules, profiles, visual editors, or first-run setup flows, read `references/dandersframes-complex-settings-ui.md` as a supplement to the primary QFX design method.

Key rules:
- Use persistent collapsible groups to keep large pages compact without losing setting context.
- Use semantic banners for combat lockdown, destructive actions, secret-value limitations, missing libraries, and compatibility warnings.
- Use `See Also` cross-page navigation instead of duplicating the same setting in several tabs.
- Register searchable settings metadata with stable IDs, breadcrumbs, aliases, widget type, and jump/highlight callbacks.
- Use guided setup wizards only for first-run or multi-step batch configuration; wizards must write through the same DB/module APIs as the real settings page.
- Show profile/global/spec/mode override status when settings can come from multiple layers, and provide safe reset-to-parent behavior.
- For visual editors, use preview-safe proxy data so Save commits and Cancel discards changes.
- Advanced diagnostic pages should be lazy-loaded, hidden from normal users, and useful for bug reports without constantly running expensive scanners.

## Reference-addon architecture supplements

For plugin architecture ideas extracted from Plater and DandersFrames, read `references/reference-addon-architecture-patterns.md` and `references/deep-reference-addon-patterns.md` as supplements.

Key rules:
- Use deterministic TOC load order: libraries, locales, templates, defaults, DB/migration, utilities, UI factory, modules, options/tools, and final bootstrap.
- Use one root namespace from `local addonName, ns = ...`; keep private internals file-local or under `Internal`.
- Define lifecycle phases for `ADDON_LOADED`, `PLAYER_LOGIN`, `PLAYER_ENTERING_WORLD`, combat enter/leave, and logout.
- Runtime modules must not require option pages to be opened.
- Use one module registry; prevent duplicate module, DB, UI factory, locale, media, and event systems.
- Use targeted or central event dispatchers for high-frequency unit/events; avoid many modules filtering the same global event independently.
- Coalesce refreshes with `RequestRefresh(reason, scope)` and record last refresh reason for diagnostics.
- Keep DB defaults, schema version, migrations, profiles, and per-character data clearly separated.
- Import/export should use a validate pipeline: decode, decompress, deserialize, validate, migrate, preview/summary, apply, refresh.
- Optional libraries and media must degrade gracefully and resolve to real asset paths before WoW API calls.
- Public API and callbacks belong in `API.lua`; expose stable functions, not raw internal DB tables.

## Deep architecture supplements

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
- Semantic color and font-level constants matching `references/ui-visual-standards.md`.
- Optional table-driven options row creation for large settings panels.
- Optional empty-state, loading, inline-error, and confirm-dialog helpers for state-consistent panels.
- Optional collapsible-section, banner, search-registration, setting-highlight, wizard, page-cache, and widget-refresh helpers for complex settings panels.
- English-first sizing helpers for labels, buttons, tabs, dropdowns, and column widths.

The UI factory should not know addon business rules. Business logic belongs in modules/controllers.

## Slider layout standard

For QFX addon sliders, use this layout unless the user says otherwise:
- Slider track on the main row.
- Minimum label under the left end of the slider.
- Maximum label under the right end of the slider.
- Current value centered under the slider.
- Minimum, current, and maximum labels must be on the same horizontal line.
- Do not place the current value to the right side of the slider in compact cards.
- Validate the row with English min/current/max labels before accepting the Chinese layout.

## Large list and collection UI rules

For saved sound lists, voice collections, addon lists, module lists, or large option lists:
- Reuse row frames.
- Do not rebuild every row for every tiny state change.
- Keep selection state independent from row object lifetime.
- Empty collections must still be selectable if edit/delete actions apply to the collection itself.
- If an enabled/visible checkbox controls list membership, sorting rows must update immediately when the item is hidden/shown.
- Dragging an item out of a collection must preserve the item identity until drop completes.
- Split row creation from row refresh and refresh only visible rows when scrolling.
- During import or bulk edits, update the data model first and refresh once at the end.

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
- English is the base layout language; Chinese and Traditional Chinese are verified after English width passes.
- Default language follows client unless a force-language option exists.
- Compact panels that use available width.
- Tooltips on section titles for explanations.
- A consistent 4px spacing grid and standard control sizes across all pages.
- Quiet state feedback: inline errors, spinner on long loads, confirm dialogs only for destructive actions.
- No unnecessary ElvUI/NDui compatibility unless the addon actually interacts with their frames.
- Release zips should include all sub-addons.
- For architecture/performance conflicts after an EllesmereUI-style reference review, prefer its scalable primary method: small/medium/large architecture tiers, deferred options loading, page cache plus widget-refresh, central dispatch, coalesced refresh, temporary OnUpdate, and weak-table state.

## What to do when asked to optimize an addon UI, architecture, or API usage

1. Inspect existing UI, architecture, and API usage first.
2. Identify whether the addon uses native controls, Ace, custom controls, or mixed controls.
3. Choose the correct scale: small, medium, or large addon.
4. Use the EllesmereUI-style method as the primary structure, scaled down when needed.
5. Inspect or draft English UI strings first, then size labels, buttons, dropdowns, tabs, and columns against English before checking Chinese.
6. Preserve functionality and SavedVariables unless the user requests behavior changes.
7. Centralize repeated UI logic into the existing factory/helpers.
8. For WoW 12.x work, verify changed APIs against current source/resources/wiki, isolate risky calls in Compat wrappers, and report branch/build assumptions.
9. For large option panels, apply tabs, option-table rows, delayed heavy tabs, searchable metadata, reusable scroll rows, page cache, widget refresh callbacks, and one global refresh/apply queue.
10. For very complex settings, add DandersFrames-style collapsible groups, semantic banners, See Also navigation, setting search registry, first-run wizard, profile override indicators, preview-safe editors, and lazy diagnostic pages only when useful.
11. Apply the pixel-level visual standards (4px grid, control sizes, label column widths, semantic colors) and check empty/loading/error/confirm states plus keyboard navigation before finishing any panel.
12. Check combat-lockdown and secret-value risks if the UI applies live settings.
13. Package and report changes clearly.

## What to do when asked to update this skill

1. Preserve the existing skill structure.
2. Prefer integrating new primary design rules into existing core references instead of creating a separate competing reference file.
3. Add new focused reference files only when the content is truly separate.
4. Update `README.md`, `.codex-plugin/plugin.json`, and `INSTALL.md` version if the skill version changes.
5. Keep names generic unless a file is intentionally a case study.
6. Avoid reference names that make a reusable rule look like it only applies to one addon.
7. When using a reference addon or API source, document extracted rules and explicitly avoid copying assets/libraries unless requested and licensed.
8. When the user explicitly says a supplied reference should win conflicts, add a priority note and summarize the scope of the override.

## Reference loading guide

When a task involves a specific concern, read the matching reference:

- Architecture and UI factory / primary QFX method: `references/qfx-ui-architecture.md`
- Modular architecture scale tiers: `references/modular-addon-architecture.md`
- Refresh performance, page cache, widget callbacks: `references/refresh-performance-rules.md`
- Event/OnUpdate discipline, central dispatch, weak-table state: `references/event-onupdate-rules.md`
- Compact multilingual and English-first layout: `references/compact-multilingual-layout.md`
- Typography and trilingual (EN/zhCN/zhTW) text quality: `references/ui-typography-localization-zh.md`
- Pixel-level visual standards (spacing, sizes, colors, dialogs, scroll): `references/ui-visual-standards.md`
- UI states, feedback, and accessibility: `references/ui-states-accessibility.md`
- WoW 12.x API source rules: `references/wow-12-api-source-rules.md`
- WoW 12.0.7 → 12.1.0 PTR API migration (Aura/Unit/CDM secret changes): `references/wow-12.0.7-to-12.1-api-migration-zhCN.md`
- Deep reference addon supplements: `references/deep-reference-addon-patterns.md`
- Reference addon architecture supplements: `references/reference-addon-architecture-patterns.md`
- DandersFrames-style complex settings UI: `references/dandersframes-complex-settings-ui.md`
- Plater-style options UI model: `references/plater-options-ui-patterns.md`
- Native UI consistency: `references/blizzard-native-ui-checklist.md`
- Secret values and taint: `references/wow-12-secret-value-taint.md`
- Dialog/dropdown/popup rules: `references/ui-factory-dialog-mode-rules.md`
- Large saved lists / collections / sounds: `references/large-list-collection-sound-ui.md`
- Complex addon UI patterns: `references/complex-addon-ui-patterns.md`
- Combat lockdown apply: `references/combat-lockdown-deferred-apply.md`
- Packaging/release: `references/packaging-release-checklist.md`
- Safe font/media handling: `references/safe-font-media-rules.md`
- SavedVariables migration: `references/savedvariables-migration.md`
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
