---
name: qfx-wow-addon-ui
description: Review, design, refactor, and package World of Warcraft addon UI, architecture, and API-safe Lua using QFX conventions. Use when working on WoW addons (Lua, .toc, SavedVariables, FrameXML), especially QFXWidgets-built settings panels (QFXUI skin), options pages, multilingual (English/Simplified Chinese/Traditional Chinese) layouts, EllesmereUI/Plater/DandersFrames-style modular architecture, combat lockdown, taint or secret-value safety, WoW 12.x (Midnight) API migration, and release packaging.
license: MIT
---

# QFX WoW Addon UI

Use this skill when reviewing, designing, refactoring, or packaging World of Warcraft addon UI, architecture, or API-safe code, especially QFX-style addons.

Optimized for: the QFXWidgets settings-control factory (QFXUI skin) as the standard settings UI; English-first layout sizing verified in 简体中文 / 繁體中文; compact settings panels; trilingual localization; WoW 12.x / Midnight API source-grounding and secret-value / taint safety; multi-version packaging; QFX conventions (lightweight, modular, minimal performance cost).

## Core goals

Prefer:

1. One scalable EllesmereUI-style architecture, scaled to addon size (see `references/qfx-ui-architecture.md`).
2. QFXWidgets controls (the QFXUI skin) as the single settings factory, over Blizzard templates, AceGUI, or hand-drawn widget code.
3. English-first layout sizing over Chinese-first layouts that overflow after translation.
4. Compact width-aware layout over tall sparse pages.
5. The shared QFXWidgets factory over per-addon `UIFactory.lua` copies or one-off widgets.
6. Clear module boundaries over giant mixed files.
7. Localized strings over hardcoded UI text.
8. Deferred combat-safe apply over direct protected-frame edits in combat.
9. Runtime modules that work without opening any options page.
10. Deferred heavy options init; widget refresh callbacks; coalesced refresh/apply.
11. Central dispatch for high-frequency events; temporary active-only `OnUpdate`.
12. Weak-table state for Blizzard/foreign frames when ownership or taint risk exists.
13. Source-grounded WoW API use over recalled signatures.
14. Minimal, traceable diffs with rollback notes.
15. Release-ready packaging checks over code-only edits.
16. Reference-addon patterns as design guidance, never asset/library copying.

## Required UI constraints

### QFXWidgets first

QFXWidgets (`QFXWidgets.lua`, global `QFXWidgets` / `ns.QFXWidgets`) is the standard settings-control factory for QFX addons. Read `references/qfxwidgets-factory.md` before building or reviewing any settings row, page, editor, picker, or dialog.

- Build rows with `W:DualRow` and the documented control cfgs (`toggle`, `slider`, `dropdown`, `segmented`, `button`, `buttonRow`, `color`, `colorMode`, `keybind`, `input`); use the extra controls (Tabs, TabPanel, CheckGrid, ColorGrid, SearchableDropdown, ListRows, ReorderList, Cog, ScrollPage, MultilineBox, Confirm, StatusRow, ResetRow) instead of new widget code.
- Use `W:BeginPage(owner)` / `W:EndPage()` around page rebuilds and `W:Refresh(owner)` / `W:RefreshPage(owner)` for updates; the factory re-reads every `getValue` and re-applies disabled states.
- Drive combat safety with `blockInCombat` / `combatTooltip` and refresh on `PLAYER_REGEN_ENABLED`.
- Keep hosts state-only: `getValue`/`setValue` closures call module APIs; no business logic and no DB writes inside the factory.
- Never mix QFXWidgets with AceGUI, Blizzard option templates, or hand-drawn controls in the same settings panel. Extend QFXWidgets itself when a control is missing.
- Copy `QFXWidgets.lua` into the addon (or its Config sub-addon) before the page files and keep it verbatim; it is a version-guarded singleton, so embedded copies never duplicate. In a core addon plus load-on-demand Config host, prefer lazy loading: put the factory only in the Config `.toc`, resolve it at use time (`rawget(_G, "QFXWidgets")`, then `EnsureConfigLoaded()`), and apply skin/media where it actually loads (see `references/qfxwidgets-factory.md`).

### English-first multilingual layout

For EN + 简体中文 + 繁體中文 support, design width from English first, then verify the Chinese locales. English is the base because its strings are usually longer.

- Size labels, buttons, dropdowns, tabs, section titles, and column widths against English strings.
- If English overflows, fix the layout structure (wider control, full-width row, shorter visible label, tooltip description, fewer columns, more space) instead of shrinking fonts below the QFX standard.
- Never design a tight Chinese layout and translate to English afterward.

Details: `references/compact-multilingual-layout.md`, `references/ui-typography-localization-zh.md`.

### Visual standards

Follow the QFXWidgets token baseline so repeated work stays consistent. Read `references/ui-visual-standards.md` and `references/qfxwidgets-factory.md` before building panels.

- Layout tokens come from `W.Theme`: row 32px (slider rows 38px), section header 28px, wide button 34px, control height 20px, pads 10/16, slider track 110px, label 12px / section 11px.
- Control sizes come from `W.Skin`/`W:Tokens()`: toggle 30x16, checkbox 16px, button 20px high / 88px min width, color swatch 22px (16px in grids), value box 44px, stepper column 18px, segmented pill min 38px, menu row 20px.
- QFXUI colors come from the active skin (accent `#4a9cfa`, dark blue fills, steel-blue borders); never hardcode or per-control override colors.
- Labels sit left and controls right-anchor; long labels ellipsize with `...` and show the full text on hover; numeric values right-align, text values left-align.
- Dialog tiers: confirm `W:Confirm` at 360px standard width; clamp to screen and respect UI scale.
- Preserve scroll position across tab switches and reopen (`page:ScrollTo(0)` only when a page switch should start at the top).

### UI states and accessibility

Panels must cover empty, loading, error, success, and confirm states, and follow the factory keyboard conventions. Read `references/ui-states-accessibility.md`.

- Empty lists show a localized hint plus one action button.
- Long operations show a native spinner/progress and refresh only the affected region.
- Input errors are inline and non-modal, paired with text, not color alone.
- Destructive actions use `W:Confirm` with a verb-labeled danger accept button; Esc and backdrop cancel.
- Keyboard behavior follows QFXWidgets: Esc closes menus/popups/confirms, Enter commits inputs, the searchable dropdown picks the first match on Enter; do not claim Tab/arrow navigation the factory does not implement.
- Keep QFXUI contrast (text on controlBg/menuBg) readable; factory sizes are 12px labels, 11px sections, 10px slider min/max at the floor; test at 150%+ UI scale.
- Animations stay short (150-300ms), non-looping, stoppable, and skipped when the player disables motion.

## Architecture by addon size

Full structure and examples: `references/qfx-ui-architecture.md`, `references/modular-addon-architecture.md`.

- **Small**: simple root namespace, small DB/defaults, optional localization/options, one local event frame. Build any settings rows with an embedded `QFXWidgets.lua`. Do not add a settings shell, page cache, search registry, or central dispatcher unless repeated settings, heavy lists, or high-frequency events exist.
- **Medium**: `Core/` (Init, Events, DB, Migration, Localization), `UI/` (QFXWidgets.lua, MainFrame, Options, Dialogs), `Modules/`, `Media/`, `Compat/` (Version, Blizzard). Runtime modules expose `Enable`, `Disable`, `Apply`, `Refresh`, optional `GetStatus`. Options pages call module APIs; they never own runtime state. Heavy options UI is created only when opened. Repeated refreshes use `RequestRefresh`.
- **Large / suite**: add only needed boundaries — `ModuleRegistry`, `PageCache`, `RefreshRegistry`, `SearchRegistry`, `Dispatcher`, `RefreshQueue`, lazy `Diagnostics`, `ImportExport`, and `API.lua` for external access. One registered shell for module navigation; page cache with explicit invalidation; widget refresh callbacks; central dispatch; search indexes real setting metadata (no duplicate controls); diagnostics lazy-loaded.

## Runtime and performance discipline

Details: `references/refresh-performance-rules.md`, `references/event-onupdate-rules.md`.

- Coalesce refreshes via `RequestRefresh(reason, scope)`; merge repeated reasons and record the last reason for diagnostics.
- Centralize high-frequency events in one dispatcher instead of many modules filtering the same global event.
- Use widget refresh callbacks for value/status updates instead of full-page rebuilds.
- Use temporary, active-only `OnUpdate`; never permanent idle polling.
- Use weak-table side state for foreign/Blizzard frames; do not wrap secure frames.

## Combat lockdown and apply safety

Details: `references/complex-addon-ui-patterns.md`.

If a setting touches protected frames or frames likely to become protected: save immediately, apply immediately out of combat, and if in combat mark apply pending and apply once on `PLAYER_REGEN_ENABLED`. Never mutate protected frames in combat, never spam chat for each deferred change, and never lose the user's setting because apply was delayed.

## WoW 12.x API grounding and secret/taint safety

Read `references/wow-12-api-source-rules.md` before writing or changing code that calls WoW APIs. For 12.0.7 → 12.1.0 migration, read `references/wow-12.0.7-to-12.1-api-migration-zhCN.md`. For the current live baseline, read `references/wow-12.1.0-live-api-final-zhCN.md`.

- Prefer current FrameXML/UI source, extracted interface resources/API dumps, Warcraft Wiki notes, then same-branch addon examples.
- Match the branch and build first (live, ptr, beta, Retail, Classic, MoP, TBC, Titan must not be mixed). Live is the production contract; PTR is warning-only.
- Treat spell, aura, cast/interrupt, unit, tooltip, `C_` namespaces, secure frames, addon compartment, minimap, TTS, templates, mixins, and deprecated globals as high-risk until verified.
- Isolate version-sensitive APIs in `Compat` wrappers; never scatter branch checks through feature modules.
- Never invent a 12.x signature from memory. If unsure, search current sources, wrap the API, and report the assumption.
- Do not compare, store, serialize, or do arithmetic on secret values; avoid combat decisions based on protected/secret results. Prefer event-driven approximations, fixed timers, cached safe values, or user configuration.
- If an error mentions `a secret boolean value`, `a secret number value`, or `execution tainted by`, treat it as a taint/secret issue, not a normal Lua type bug.

Details: `references/wow-12-secret-value-taint.md`.

## Options UI supplements

Use the primary QFX method first; these are supplements for large settings panels.

- **Plater-inspired** (`references/plater-options-ui-patterns.md`): tab container; one table of category definitions; load-on-demand for heavy tabs; table-driven option rows (map metadata onto QFXWidgets cfgs: `type`, `text`, `getValue`, `setValue`, `values`, `min`, `max`, `step`); one global change callback; search as an index over existing metadata; split row creation from row refresh.
- **DandersFrames-inspired** (`references/dandersframes-complex-settings-ui.md`): persistent collapsible groups; semantic banners (combat lockdown, destructive, secret limits, missing libs); `See Also` cross-page navigation; searchable metadata with stable IDs, breadcrumbs, aliases, jump/highlight; first-run wizards that write through the same DB/module APIs; profile/global/spec override indicators with safe reset-to-parent; preview-safe proxy editors; lazy advanced diagnostics.
- **Reference-architecture** (`references/reference-addon-architecture-patterns.md`, `references/deep-reference-addon-patterns.md`): deterministic TOC load order; one root namespace; lifecycle phases (`ADDON_LOADED`, `PLAYER_LOGIN`, `PLAYER_ENTERING_WORLD`, combat enter/leave, logout); one module registry; DB defaults/schema/migrations/profiles separated; import/export validation pipeline (decode → decompress → deserialize → validate → migrate → preview → apply → refresh); graceful media fallbacks; stable public API in `API.lua`. Add controlled extension hooks, adapter/resolver/renderer pipelines, capability gates, object pools, auto-profile switching, and opt-in profilers only when the addon truly needs them.

## Lists, media, and complex UI

Details: `references/lists-media-sound-ui.md`, `references/complex-addon-ui-patterns.md`.

- Reuse row frames; do not rebuild every row on every state change; keep selection state independent from row lifetime.
- Split data building, row creation, row rendering, selection, drag/drop, and refresh.
- Drag start records stable identity (`sourceKey`, `sourceType`, `sourceGroup`, optional `sourceIndex`); drop targets use stable keys.
- Empty collections stay selectable if edit/delete applies to the collection itself.
- Long sound/LibSharedMedia lists use `W:SearchableDropdown` fed by `W:MediaList(kind)`; missing LibSharedMedia must return empty lists and must not break the UI.
- Resolve font/media presets to real asset paths before `SetFont`/media calls; never pass `AUTO`, `DEFAULT`, `BLIZZARD`, empty string, or nil.

## Slider layout standard

Use the QFXWidgets slider anatomy: label on the left, track on the row, min label under the left end and max under the right end, value box (44px) at the right edge, and the `+`/`-` stepper column flush right of the box. Dragging commits once on release and refreshes the page once; steppers nudge one clamped step and dim at the ends; `steppers = false` drops the column. Full-width `W:Slider` rows are for long labels. Validate with English min/max labels before accepting the Chinese layout.

## Packaging and reporting

Details: `references/release-and-compatibility.md`.

- Before returning a release zip: TOC exists and references existing files; SavedVariables declared; libraries and media present; no sub-addons dropped; no debug files included; no changelog documents included (`CHANGELOG.md`, release notes, dev logs - QFX release zips never carry a changelog, it stays in the workspace/repo); version updated consistently; correct zip root; zip name is `<Addon>_<version>.zip`; all claimed locale files included.
- Versions are three-part decimal integers `MAJOR.MINOR.PATCH`; `1.1.10` is newer than `1.1.9`. PATCH for fixes/polish/localization, MINOR for features/modules, MAJOR for rewrites or incompatible SavedVariables changes.
- Before overwriting installed addon files in the game client, back up the replaced files to a local workspace folder (for example `archive/<Addon>_client_backup_YYYYMMDD/`). Never store backups inside the game installation (`_retail_/`, `_classic_/`, etc.) or inside `Interface/AddOns/`.
- Do not overwrite player-generated client files (companion-app config files, SavedVariables) unless the task requires it; verify synced files by hash after copying.
- Report changes with: files changed/added/deleted, TOC impact, SavedVariables impact, API or branch/build assumptions, risk level, rollback notes, and in-game test steps.

## Minimal-diff discipline

When fixing a specific issue: do not reformat unrelated files, rename unrelated functions, migrate architecture, delete fallbacks, or change feature behavior during UI-only work. Do not add AI/date trace comments; put dev traces in a dev changelog kept out of release zips.

## Common QFX preferences

Assume unless told otherwise: settings UI built with QFXWidgets and the QFXUI skin; lightweight performance; no unnecessary animation (factory toggle animation stays at 75ms); EN/zhCN/zhTW support with English as the base layout language; default language follows client unless a force-language option exists; compact panels using available width; tooltips on section titles; QFXWidgets theme/skin tokens instead of ad-hoc sizes and colors; quiet state feedback (inline errors, spinner on long loads, `W:Confirm` only for destructive actions); no unnecessary ElvUI/NDui compatibility unless the addon actually interacts with their frames; release zips include all sub-addons but never changelog documents.

## Workflows

When asked to optimize an addon UI, architecture, or API usage:

1. Inspect existing UI, architecture, and API usage first.
2. Identify QFXWidgets vs Ace vs Blizzard-template vs custom/mixed controls.
3. Choose the scale: small, medium, or large.
4. Apply the EllesmereUI-style method as the primary structure, scaled down when needed.
5. Inspect/draft English UI strings first; size labels, buttons, dropdowns, tabs, columns against English before checking Chinese.
6. Preserve functionality and SavedVariables unless behavior changes are requested.
7. Migrate repeated UI logic into QFXWidgets; do not create a second factory or fork widget code.
8. For 12.x work, verify changed APIs against current sources, isolate risky calls in `Compat` wrappers, and report branch/build assumptions.
9. For large panels, apply tabs, option-table rows, delayed heavy tabs, searchable metadata, reusable scroll rows, page cache, widget refresh callbacks, and one global refresh/apply queue.
10. For very complex settings, add DandersFrames-style groups/banners/search/wizard/override indicators/preview-safe editors/lazy diagnostics only when useful.
11. Apply the QFXWidgets visual standards and check empty/loading/error/confirm states plus the factory keyboard conventions before finishing any panel.
12. Check combat-lockdown and secret-value risks if the UI applies live settings.
13. Package and report changes clearly.

When asked to update this skill:

1. Preserve the existing structure.
2. Integrate new primary rules into existing references instead of creating competing files.
3. Add a focused reference only when the content is truly separate.
4. Keep names generic unless a file is intentionally a case study.
5. Update `README.md`, `.codex-plugin/plugin.json`, and `INSTALL.md` version when the skill version changes.
6. When using a reference addon or API source, document extracted rules and do not copy assets/libraries unless requested and licensed.
7. Treat `QFXWidgets.lua` as the factory source of truth: when its API or tokens change (its internal `VERSION` bump), update `references/qfxwidgets-factory.md` and any affected rows in this skill in the same pass.

## Reference loading guide

- Primary architecture: `references/qfx-ui-architecture.md`
- QFXWidgets settings factory (controls, tokens, refresh, combat, media): `references/qfxwidgets-factory.md`
- Modular scale tiers: `references/modular-addon-architecture.md`
- Refresh, page cache, widget callbacks: `references/refresh-performance-rules.md`
- Events, OnUpdate, dispatch, weak-table state: `references/event-onupdate-rules.md`
- Compact multilingual / English-first layout: `references/compact-multilingual-layout.md`
- Typography and trilingual text quality: `references/ui-typography-localization-zh.md`
- Visual standards (spacing, sizes, colors, dialogs, scroll): `references/ui-visual-standards.md`
- UI states and accessibility: `references/ui-states-accessibility.md`
- QFXWidgets UI consistency and duplicate controls: `references/qfxwidgets-ui-checklist.md`
- Complex UI, lists, dialogs, combat-safe apply: `references/complex-addon-ui-patterns.md`
- List, collection, sound/TTS, and media safety: `references/lists-media-sound-ui.md`
- Plater-style options model: `references/plater-options-ui-patterns.md`
- DandersFrames-style settings: `references/dandersframes-complex-settings-ui.md`
- Reference-addon architecture supplements: `references/reference-addon-architecture-patterns.md`
- Deep advanced architecture: `references/deep-reference-addon-patterns.md`
- WoW 12.x API source rules: `references/wow-12-api-source-rules.md`
- Secret values and taint: `references/wow-12-secret-value-taint.md`
- 12.0.7 → 12.1 PTR migration: `references/wow-12.0.7-to-12.1-api-migration-zhCN.md`
- Current 12.1 Live API baseline: `references/wow-12.1.0-live-api-final-zhCN.md`
- Packaging, compatibility, SavedVariables, reporting: `references/release-and-compatibility.md`

## Output expectations

- **Review**: priority issues, suggested fixes, files likely involved, API/source checks needed, risk level, test steps.
- **File changes**: download link or commit summary, changed/added/deleted files, what changed and did not change, API/branch assumptions, test steps, rollback notes.
