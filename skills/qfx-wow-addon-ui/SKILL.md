---
name: qfx-wow-addon-ui
description: Review, design, refactor, and package World of Warcraft addon UI, architecture, and API-safe Lua using QFX conventions. Use when working on WoW addons (Lua, .toc, SavedVariables, FrameXML), especially Blizzard-native settings panels, options pages, multilingual (English/Simplified Chinese/Traditional Chinese) layouts, EllesmereUI/Plater/DandersFrames-style modular architecture, combat lockdown, taint or secret-value safety, WoW 12.x (Midnight) API migration, and release packaging.
license: MIT
---

# QFX WoW Addon UI

Use this skill when reviewing, designing, refactoring, or packaging World of Warcraft addon UI, architecture, or API-safe code, especially QFX-style addons.

Optimized for: Blizzard-native UI; English-first layout sizing verified in 简体中文 / 繁體中文; compact settings panels; trilingual localization; WoW 12.x / Midnight API source-grounding and secret-value / taint safety; multi-version packaging; QFX conventions (lightweight, modular, native-looking, minimal performance cost).

## Core goals

Prefer:

1. One scalable EllesmereUI-style architecture, scaled to addon size (see `references/qfx-ui-architecture.md`).
2. Native Blizzard controls over custom-drawn controls, unless a custom skin is explicitly requested.
3. English-first layout sizing over Chinese-first layouts that overflow after translation.
4. Compact width-aware layout over tall sparse pages.
5. Shared UI factory helpers over one-off widget code.
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

### Native first

Prefer Blizzard templates: `UIPanelButtonTemplate`, `UICheckButtonTemplate`, `UIDropDownMenuTemplate` (or a local wrapper that mimics it), `OptionsSliderTemplate`, `InputBoxTemplate`, `BackdropTemplateMixin`. Do not mix native, AceGUI, and custom-drawn systems in one panel unless the addon already does and migration is requested.

### English-first multilingual layout

For EN + 简体中文 + 繁體中文 support, design width from English first, then verify the Chinese locales. English is the base because its strings are usually longer.

- Size labels, buttons, dropdowns, tabs, section titles, and column widths against English strings.
- If English overflows, fix the layout structure (wider control, full-width row, shorter visible label, tooltip description, fewer columns, more space) instead of shrinking fonts below the QFX standard.
- Never design a tight Chinese layout and translate to English afterward.

Details: `references/compact-multilingual-layout.md`, `references/ui-typography-localization-zh.md`.

### Visual standards

Follow one pixel-level baseline so repeated work stays consistent. Read `references/ui-visual-standards.md` before building panels.

- 4px spacing grid; row heights of 24/28/32px.
- Standard sizes: buttons 22-24px high, min width 80px or measured EN text + 28px padding; checkbox 16px; color swatch 24-32px wide with no label inside.
- Left label column 160-200px, sized from English first and kept under 40% of panel width; numeric values right-align, text values left-align.
- 3-level font hierarchy (title / label / desc) plus inherited template text.
- Semantic colors by purpose (normal, muted, warning, danger, success, accent); never convey state with color alone.
- Dialog width tiers: narrow 320-400px, standard 640-720px, wide 800-960px; clamp to screen and respect UI scale.
- Preserve scroll position across tab switches and reopen; scroll target rows into view after search/jump.

### UI states and accessibility

Panels must cover empty, loading, error, success, and confirm states, and stay usable without a mouse. Read `references/ui-states-accessibility.md`.

- Empty lists show a localized hint plus one action button.
- Long operations show a native spinner/progress and refresh only the affected region.
- Input errors are inline and non-modal, paired with text, not color alone.
- Destructive actions use a narrow confirm dialog with a verb-labeled danger button; Esc cancels.
- Panels are keyboard-navigable: logical Tab order, arrow keys in lists/dropdowns, visible focus, Esc closes popup then dialog.
- Keep contrast at Blizzard template levels; never below 11px for user-facing text; test at 150%+ UI scale.
- Animations stay short (150-300ms), non-looping, stoppable, and skipped when the player disables motion.

## Architecture by addon size

Full structure and examples: `references/qfx-ui-architecture.md`, `references/modular-addon-architecture.md`.

- **Small**: simple root namespace, small DB/defaults, optional localization/options, one local event frame. Do not add a settings shell, page cache, search registry, or central dispatcher unless repeated settings, heavy lists, or high-frequency events exist.
- **Medium**: `Core/` (Init, Events, DB, Migration, Localization), `UI/` (UIFactory, Skin, MainFrame, Options, Dialogs, Dropdown, Lists), `Modules/`, `Media/`, `Compat/` (Version, Blizzard). Runtime modules expose `Enable`, `Disable`, `Apply`, `Refresh`, optional `GetStatus`. Options pages call module APIs; they never own runtime state. Heavy options UI is created only when opened. Repeated refreshes use `RequestRefresh`.
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

- **Plater-inspired** (`references/plater-options-ui-patterns.md`): tab container; one table of category definitions; load-on-demand for heavy tabs; table-driven option rows (`type`, `name`, `desc`, `get`, `set`, `values`, `min`, `max`, `step`); one global change callback; search as an index over existing metadata; split row creation from row refresh.
- **DandersFrames-inspired** (`references/dandersframes-complex-settings-ui.md`): persistent collapsible groups; semantic banners (combat lockdown, destructive, secret limits, missing libs); `See Also` cross-page navigation; searchable metadata with stable IDs, breadcrumbs, aliases, jump/highlight; first-run wizards that write through the same DB/module APIs; profile/global/spec override indicators with safe reset-to-parent; preview-safe proxy editors; lazy advanced diagnostics.
- **Reference-architecture** (`references/reference-addon-architecture-patterns.md`, `references/deep-reference-addon-patterns.md`): deterministic TOC load order; one root namespace; lifecycle phases (`ADDON_LOADED`, `PLAYER_LOGIN`, `PLAYER_ENTERING_WORLD`, combat enter/leave, logout); one module registry; DB defaults/schema/migrations/profiles separated; import/export validation pipeline (decode → decompress → deserialize → validate → migrate → preview → apply → refresh); graceful media fallbacks; stable public API in `API.lua`. Add controlled extension hooks, adapter/resolver/renderer pipelines, capability gates, object pools, auto-profile switching, and opt-in profilers only when the addon truly needs them.

## Lists, media, and complex UI

Details: `references/lists-media-sound-ui.md`, `references/complex-addon-ui-patterns.md`.

- Reuse row frames; do not rebuild every row on every state change; keep selection state independent from row lifetime.
- Split data building, row creation, row rendering, selection, drag/drop, and refresh.
- Drag start records stable identity (`sourceKey`, `sourceType`, `sourceGroup`, optional `sourceIndex`); drop targets use stable keys.
- Empty collections stay selectable if edit/delete applies to the collection itself.
- Long sound/LibSharedMedia lists use a searchable/scrollable singleton dropdown; missing LibSharedMedia must not break the UI.
- Resolve font/media presets to real asset paths before `SetFont`/media calls; never pass `AUTO`, `DEFAULT`, `BLIZZARD`, empty string, or nil.

## Slider layout standard

Unless the user says otherwise: track on the main row; min label under the left end, max under the right end, current value centered under the track, all three on the same line. Do not place the current value to the right in compact cards. If `OptionsSliderTemplate` is used, hide/clear its built-in `Text`, `Low`, and `High` labels. Validate with English min/current/max labels before accepting the Chinese layout.

## Packaging and reporting

Details: `references/release-and-compatibility.md`.

- Before returning a release zip: TOC exists and references existing files; SavedVariables declared; libraries and media present; no sub-addons dropped; no debug files included; version updated consistently; correct zip root; zip name is `<Addon>_<version>.zip`; all claimed locale files included.
- Versions are three-part decimal integers `MAJOR.MINOR.PATCH`; `1.1.10` is newer than `1.1.9`. PATCH for fixes/polish/localization, MINOR for features/modules, MAJOR for rewrites or incompatible SavedVariables changes.
- Report changes with: files changed/added/deleted, TOC impact, SavedVariables impact, API or branch/build assumptions, risk level, rollback notes, and in-game test steps.

## Minimal-diff discipline

When fixing a specific issue: do not reformat unrelated files, rename unrelated functions, migrate architecture, delete fallbacks, or change feature behavior during UI-only work. Do not add AI/date trace comments; put dev traces in a dev changelog kept out of release zips.

## Common QFX preferences

Assume unless told otherwise: native Blizzard-style UI; lightweight performance; no unnecessary animation; EN/zhCN/zhTW support with English as the base layout language; default language follows client unless a force-language option exists; compact panels using available width; tooltips on section titles; consistent 4px grid and control sizes; quiet state feedback (inline errors, spinner on long loads, confirm dialogs only for destructive actions); no unnecessary ElvUI/NDui compatibility unless the addon actually interacts with their frames; release zips include all sub-addons.

## Workflows

When asked to optimize an addon UI, architecture, or API usage:

1. Inspect existing UI, architecture, and API usage first.
2. Identify native vs Ace vs custom vs mixed controls.
3. Choose the scale: small, medium, or large.
4. Apply the EllesmereUI-style method as the primary structure, scaled down when needed.
5. Inspect/draft English UI strings first; size labels, buttons, dropdowns, tabs, columns against English before checking Chinese.
6. Preserve functionality and SavedVariables unless behavior changes are requested.
7. Centralize repeated UI logic into the existing factory/helpers.
8. For 12.x work, verify changed APIs against current sources, isolate risky calls in `Compat` wrappers, and report branch/build assumptions.
9. For large panels, apply tabs, option-table rows, delayed heavy tabs, searchable metadata, reusable scroll rows, page cache, widget refresh callbacks, and one global refresh/apply queue.
10. For very complex settings, add DandersFrames-style groups/banners/search/wizard/override indicators/preview-safe editors/lazy diagnostics only when useful.
11. Apply the visual standards and check empty/loading/error/confirm states plus keyboard navigation before finishing any panel.
12. Check combat-lockdown and secret-value risks if the UI applies live settings.
13. Package and report changes clearly.

When asked to update this skill:

1. Preserve the existing structure.
2. Integrate new primary rules into existing references instead of creating competing files.
3. Add a focused reference only when the content is truly separate.
4. Keep names generic unless a file is intentionally a case study.
5. Update `README.md`, `.codex-plugin/plugin.json`, and `INSTALL.md` version when the skill version changes.
6. When using a reference addon or API source, document extracted rules and do not copy assets/libraries unless requested and licensed.

## Reference loading guide

- Primary architecture and UI factory: `references/qfx-ui-architecture.md`
- Modular scale tiers: `references/modular-addon-architecture.md`
- Refresh, page cache, widget callbacks: `references/refresh-performance-rules.md`
- Events, OnUpdate, dispatch, weak-table state: `references/event-onupdate-rules.md`
- Compact multilingual / English-first layout: `references/compact-multilingual-layout.md`
- Typography and trilingual text quality: `references/ui-typography-localization-zh.md`
- Visual standards (spacing, sizes, colors, dialogs, scroll): `references/ui-visual-standards.md`
- UI states and accessibility: `references/ui-states-accessibility.md`
- Native UI consistency and duplicate controls: `references/blizzard-native-ui-checklist.md`
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
