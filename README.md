# QFX WoW Addon UI Codex Skill

Version: 1.10.0

This package contains a Codex plugin with one skill:

- `qfx-wow-addon-ui`

It is designed for World of Warcraft addon UI design, architecture review, refactoring, and release packaging with QFX conventions.

## What v1.10.0 adds

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
- Adds stronger DB/default/profile/migration and import/export validation architecture rules.
- Adds optional library/media retry, compatibility boundary, public callback/API, lazy debug/profiler, and preview/test-mode architecture rules.

## Earlier v1.8.0 additions

- Adds a DandersFrames-inspired complex settings UI reference extracted from the uploaded reference addon.
- Adds persistent collapsible group rules with SavedVariables-backed state, group summaries, and automatic relayout.
- Adds semantic banner rules for info/warning/caution/danger/success notices.
- Adds `See Also` cross-page navigation guidance to avoid duplicate controls.
- Adds a searchable settings registry model with stable IDs, breadcrumbs, aliases, widget types, and jump/highlight callbacks.
- Adds guided setup wizard rules for first-run and multi-step batch configuration.
- Adds profile/global/spec/mode override indicator rules with reset-to-parent behavior.
- Adds preview-safe editor rules for visual configuration pages so Save commits and Cancel discards draft changes.
- Adds advanced diagnostic page guidance for large addons, with lazy loading and copyable bug-report data.
- Keeps QFX visual direction unchanged: Blizzard-native, lightweight, and no copied DandersFrames fonts, textures, libraries, or custom skin.

## Earlier v1.7.0 additions

- Adds a Plater-inspired reference pattern extracted from the uploaded reference addon.
- Adds rules for table-driven options pages: localized option tables, shared templates, and one global change callback.
- Adds tab-container guidance for many settings categories, including delayed creation for heavy pages.
- Adds searchable settings guidance: collect option metadata, group matches by tab and section, and avoid duplicating real controls.
- Adds reusable scroll-row guidance for spell/media/list editors using create-line plus refresh-line separation.
- Adds combat-state visibility guidance for settings panels that apply live changes.
- Adds a strict rule to use reference addons as design models only; do not copy their bundled fonts, textures, libraries, or brand assets into QFX addons unless licensing and need are explicit.

## Earlier v1.6.2 additions

- Adds duplicate-control rules to the Blizzard native UI checklist.
- Requires avoiding repeated controls with the same effective action on the same page unless their scope is clearly different.
- Recommends keeping the control closest to the affected setting group and avoiding duplicate footer buttons for actions already present in the page content.

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
$qfx-wow-addon-ui Do a deep architecture pass using Plater and DandersFrames patterns: controlled extension hooks, adapter/resolver/renderer pipeline, capability gates, self-healing media fallback, object pool reset, post-load validation, category import/export, auto-profile switching, safe profiler, and alert state machines.
```

```text
$qfx-wow-addon-ui Redesign this addon architecture using reference-addon patterns from Plater and DandersFrames: deterministic TOC load order, root namespace, lifecycle phases, module registry, DB/profile migration, targeted event dispatchers, import/export validation, public API boundary, and lazy diagnostics.
```

```text
$qfx-wow-addon-ui Apply DandersFrames-style complex settings patterns: persistent collapsible groups, semantic banners, See Also navigation, searchable settings registry, guided setup wizard, profile override indicators, preview-safe editors, and lazy diagnostics.
```

```text
$qfx-wow-addon-ui Apply Plater-style options design to this addon UI: tab categories, table-driven option rows, delayed heavy tabs, searchable settings, reusable scroll rows, and one global refresh callback.
```

```text
$qfx-wow-addon-ui Review this addon settings UI and architecture. Find release blockers, layout drift, architecture drift, localization gaps, taint risks, performance problems, and packaging completeness.
```

```text
$qfx-wow-addon-ui Make this settings page more compact. Fully use the template width, keep Blizzard-native style, and verify English/简体中文/繁體中文 labels do not overflow.
```

```text
$qfx-wow-addon-ui Apply this bug fix with minimal diff and give me a traceable report: changed files, risk level, rollback notes, TOC/SavedVariables impact, and in-game test steps.
```

## Reference files

The skill includes these references:

- `deep-reference-addon-patterns.md`
- `reference-addon-architecture-patterns.md`
- `dandersframes-complex-settings-ui.md`
- `plater-options-ui-patterns.md`
- `blizzard-native-ui-checklist.md`
- `qfx-ui-architecture.md`
- `wow-12-secret-value-taint.md`
- `ui-factory-dialog-mode-rules.md`
- `compact-multilingual-layout.md`
- `large-list-collection-sound-ui.md`
- `complex-addon-ui-patterns.md`
- `combat-lockdown-deferred-apply.md`
- `packaging-release-checklist.md`
- `modular-addon-architecture.md`
- `safe-font-media-rules.md`
- `savedvariables-migration.md`
- `refresh-performance-rules.md`
- `event-onupdate-rules.md`
- `version-compat-boundaries.md`
- `modification-traceability.md`
