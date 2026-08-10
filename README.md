# QFX WoW Addon UI Codex Skill

Version: 1.15.0

This package contains a Codex plugin with one skill:

- `qfx-wow-addon-ui`

It is designed for World of Warcraft addon UI design, architecture review, API-safe refactoring, and release packaging with QFX conventions.

## What v1.15.0 changes

- Re-verifies the WoW 12.1.0 PTR API migration reference against `Gethe/wow-ui-source` live 12.0.7.68974 vs ptr 12.1.0.69189 generated API documentation (2026-08-10).
- Confirms `RequiresUnitAuraAccess` is new in 12.1 and records the full 16-API list (live 12.0.7 has 0).
- Confirms `ForbiddenAspect` (11 values) is newly introduced in 12.1, and `SecretAspect` gains `RadialProgress`.
- Confirms old Aura sound APIs (`AddPrivateAuraAppliedSound` / `RemovePrivateAuraAppliedSound` / `TriggerPrivateAuraShowDispelType`) are removed in 12.1 and replaced by `AddAuraSound` / `RemoveAuraSound`.
- Adds verified detail for `CustomAuraButtonDispelTypeTextureOptions` fields, `UnitAuraSortRule`/`UnitAuraSortDirection` (not new), `RequiresValidUnitAuraInstance` precondition, and Unit identity secret predicate coverage.
- Wires the 12.1 migration reference into `SKILL.md` reference loading and WoW 12.x API source-grounding sections.

## Earlier v1.14.0 changes

- Strengthens the multilingual UI rule: design layout from English first, then verify Simplified Chinese and Traditional Chinese.
- Updates `compact-multilingual-layout.md` with an English-first layout baseline for labels, buttons, dropdowns, tabs, section titles, column widths, and card widths.
- Adds guidance that English overflow should be fixed by layout structure, not by shrinking fonts or designing a Chinese-tight layout first.
- Adds a button-width helper pattern that measures English and current localized text, then uses the larger width plus padding.
- Updates `SKILL.md` so English-first sizing is part of the core goals, mandatory UI constraints, UI factory responsibilities, slider review, common user preferences, and optimization workflow.

## Earlier v1.13.0 changes

- Makes the EllesmereUI-style design method the primary QFX UI architecture baseline instead of a separate reference module.
- Folds the new method into existing core references: `qfx-ui-architecture.md`, `modular-addon-architecture.md`, `refresh-performance-rules.md`, and `event-onupdate-rules.md`.
- Removes the standalone `modular-ui-runtime-performance-patterns.md` reference to avoid parallel or competing design modules.
- Defines one scalable method for small, medium, and large addons: small addons stay simple, medium addons use modules and lazy options, and large addons add settings shell, page cache, search registry, central dispatcher, diagnostics, import/export, and optional API boundaries.
- Keeps previous QFX, Plater, DandersFrames, Blizzard-native UI, and WoW 12.x API rules as supplements. When they conflict with the primary method on UI lifecycle, refresh strategy, event dispatch, or runtime performance, the EllesmereUI-style method wins.
- Keeps QFX Blizzard-native visuals as the default; the skill adopts the architecture and runtime behavior, not the reference addon's custom-drawn visual skin or assets.

## Earlier v1.12.0 additions

- Added an EllesmereUI / EllesmereUIActionBars reference review covering registered settings shell, deferred options loading, page cache, widget refresh callbacks, central dispatch, coalesced refresh, temporary OnUpdate, weak-table frame state, and combat-safe deferred apply.

## Earlier v1.11.0 additions

- Adds `wow-12-api-source-rules.md` for WoW 12.x / Midnight API-source grounding.
- Documents that no ready-made public `WoW 12.0 API Codex Skill` was found during the GitHub search, so this skill references current API/source repositories instead.
- Adds source priority rules: current FrameXML/UI source, extracted interface resources/API dumps, Warcraft Wiki API notes, and same-branch addon examples.
- Adds branch/build discipline for live, ptr, ptr2, beta, Retail, Classic, MoP, TBC, and Titan branches.
- Adds high-risk API categories requiring verification before use: spell, aura, cast/interrupt, unit, tooltip, C_ namespace, secure frame, addon compartment, minimap, TTS, templates, mixins, and deprecated globals.
- Adds compatibility-wrapper rules so version-sensitive APIs are isolated in `Compat` instead of scattered across modules.
- Adds a source-grounded 12.x code-review checklist to reduce wrong API usage.

## Earlier v1.10.0 additions

- Adds a deep reference-addon pattern guide from a second pass over Plater and DandersFrames.
- Adds controlled extension and scripting-system rules: fixed hook catalog, trigger registry, guarded dispatch, metadata, quarantine, and stable public API.
- Adds Adapter / Resolver / Renderer pipeline rules for complex visual editors, text systems, aura/alert systems, minimap providers, and previews.
- Adds capability gates and feature-flag rules for API availability, optional libraries, combat safety, and known taint risks.
- Adds self-healing configuration rules for imported profiles that reference missing fonts, textures, sounds, or SharedMedia entries.
- Adds object-pool reset discipline, including when not to pool stale-prone UI components.
- Adds post-load validation, category-scoped import/export merging, explicit auto-profile switching, safe ownership-filtered profilers, foreign attachment scanning, alert state machines, option dependency graphs, and design-token rules.

## Earlier v1.9.0 additions

- Adds a reference-addon architecture pattern guide extracted from the two uploaded high-download reference addons: Plater and DandersFrames.
- Adds deterministic TOC load-order rules covering libraries, locales, templates, defaults, DB/migration, utilities, UI factory, modules, options/tools, and final bootstrap.
- Adds root namespace and public/private boundary rules using one addon table, private internals, and optional documented `API.lua`.
- Adds architecture tiers for small, medium, and large QFX addons so small addons are not over-engineered.
- Adds lifecycle phase guidance for `ADDON_LOADED`, `PLAYER_LOGIN`, `PLAYER_ENTERING_WORLD`, combat enter/leave, and logout.
- Adds module registry rules, targeted event dispatcher guidance, refresh coalescing rules, and diagnostic counters.

## Earlier v1.8.0 additions

- Adds a DandersFrames-inspired complex settings UI reference extracted from the uploaded reference addon.
- Adds persistent collapsible group rules with SavedVariables-backed state, group summaries, and automatic relayout.
- Adds semantic banner rules for info/warning/caution/danger/success notices.
- Adds `See Also` cross-page navigation guidance to avoid duplicate controls.
- Adds a searchable settings registry model with stable IDs, breadcrumbs, aliases, widget types, and jump/highlight callbacks.
- Adds guided setup wizard rules for first-run and multi-step batch configuration.
- Adds profile/global/spec/mode override indicator rules with reset-to-parent behavior.

## Earlier v1.7.0 additions

- Adds a Plater-inspired reference pattern extracted from the uploaded reference addon.
- Adds rules for table-driven options pages: localized option tables, shared templates, and one global change callback.
- Adds tab-container guidance for many settings categories, including delayed creation for heavy pages.
- Adds searchable settings guidance: collect option metadata, group matches by tab and section, and avoid duplicating real controls.
- Adds reusable scroll-row guidance for spell/media/list editors using create-line plus refresh-line separation.

## Install as a local personal plugin

1. Copy `qfx-wow-addon-ui-plugin` to a local plugin folder, for example:

```bash
mkdir -p ~/.codex/plugins
cp -R qfx-wow-addon-ui-plugin ~/.codex/plugins/qfx-wow-addon-ui-plugin
```

2. Add or update `~/.agents/plugins/marketplace.json`:

```json
{
  "name": "local-qfx-plugins",
  "interface": {
    "displayName": "Local QFX Plugins"
  },
  "plugins": [
    {
      "name": "qfx-wow-addon-ui-plugin",
      "source": {
        "source": "local",
        "path": "./.codex/plugins/qfx-wow-addon-ui-plugin"
      },
      "policy": {
        "installation": "AVAILABLE",
        "authentication": "ON_INSTALL"
      },
      "category": "Developer Tools"
    }
  ]
}
```

Depending on your marketplace root, adjust `source.path` so it points to the plugin folder.

3. Restart Codex and install the plugin from Plugins.

## Install as a raw skill only

Copy the skill folder directly:

```bash
mkdir -p ~/.agents/skills
cp -R qfx-wow-addon-ui-plugin/skills/qfx-wow-addon-ui ~/.agents/skills/qfx-wow-addon-ui
```

Restart Codex if the skill does not appear.

## Example prompts

```text
$qfx-wow-addon-ui Use the primary QFX design method to review this addon: choose small/medium/large scale, preserve native visuals, size the layout from English first, defer heavy options, use page cache and widget refresh where useful, centralize high-frequency events, coalesce refreshes, avoid permanent OnUpdate, and keep combat-safe applies.
```

```text
$qfx-wow-addon-ui Review this multilingual settings UI using English as the base layout language, then verify Simplified Chinese and Traditional Chinese for overflow, clipping, row balance, and runtime language switching.
```

```text
$qfx-wow-addon-ui Verify this addon against WoW 12.x API sources before coding: check current UI source/resources, branch/build, deprecated APIs, secret-value/taint risk, compatibility wrappers, and final API assumptions.
```

```text
$qfx-wow-addon-ui Review this addon settings UI and architecture. Find release blockers, layout drift, architecture drift, localization gaps, taint risks, API risks, performance problems, and packaging completeness.
```

## Reference files

The skill includes these references:

- `qfx-ui-architecture.md`
- `modular-addon-architecture.md`
- `refresh-performance-rules.md`
- `event-onupdate-rules.md`
- `compact-multilingual-layout.md`
- `wow-12-api-source-rules.md`
- `deep-reference-addon-patterns.md`
- `reference-addon-architecture-patterns.md`
- `dandersframes-complex-settings-ui.md`
- `plater-options-ui-patterns.md`
- `blizzard-native-ui-checklist.md`
- `wow-12-secret-value-taint.md`
- `ui-factory-dialog-mode-rules.md`
- `large-list-collection-sound-ui.md`
- `complex-addon-ui-patterns.md`
- `combat-lockdown-deferred-apply.md`
- `packaging-release-checklist.md`
- `safe-font-media-rules.md`
- `savedvariables-migration.md`
- `version-compat-boundaries.md`
- `modification-traceability.md`
