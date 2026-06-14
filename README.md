# QFX WoW Addon UI Codex Skill

Version: 1.8.0

This package contains a Codex plugin with one skill:

- `qfx-wow-addon-ui`

It is designed for World of Warcraft addon UI design, review, and refactoring with QFX conventions.

## What v1.8.0 adds

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

## Earlier v1.6.1 additions

- Adds color selector rules to the Blizzard native UI checklist.
- Requires compact textless color swatches instead of labeled `Color` / `颜色` buttons.
- Defines left-click color picker behavior, optional documented right-click reset behavior, immediate swatch refresh, and centralized swatch helper guidance.

## Earlier v1.6 additions

- Adds complex addon UI patterns as a dedicated reference.
- Adds lightweight Skin layer rules: unify native controls without moving business logic into Skin/UIFactory.
- Adds singleton scrollable dropdown popup rules for long sound/media lists, dialog z-order, current-selection positioning, and outside-click close.
- Adds large-list responsibility split: Builder, Renderer, RowFactory, RowRenderer, Selection, DragDrop/DropTarget/Geometry, and Refresh.
- Adds batched `RequestRefresh(reason)` rules to avoid repeated full rebuilds during language switches, imports, sliders, search/filter, and collection expand/collapse.
- Adds stable drag/drop identity rules using sourceKey/sourceType/dropKey instead of relying only on row frame references.
- Adds language switching rules that refresh UI text without wiping open editor drafts or import/export text.
- Adds localized toolbar/button width auto-fit rules.
- Adds native slider wrapper implementation details for clearing template Low/High/Text labels and using QFX bottom value labels.
- Adds editor dialog grid constant rules to avoid scattered magic coordinates.

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
$qfx-wow-addon-ui Apply DandersFrames-style complex settings patterns: persistent collapsible groups, semantic banners, See Also navigation, searchable settings registry, guided setup wizard, profile override indicators, preview-safe editors, and lazy diagnostics.
```

```text
$qfx-wow-addon-ui Review this addon settings UI. Find release blockers, layout drift, localization gaps, taint risks, performance problems, and packaging completeness.
```

```text
$qfx-wow-addon-ui Refactor the saved voice collection UI so collection rows can be selected, edited, deleted, and child sound items can be dragged out without lag. Also check long sound dropdowns, TTS test playback, and LibSharedMedia integration.
```

```text
$qfx-wow-addon-ui Add a Blizzard-native dropdown with scroll support to this popup, using the existing UI factory and EN/zhCN/zhTW localization.
```

```text
$qfx-wow-addon-ui Make this settings page more compact. Fully use the template width, keep Blizzard-native style, and verify English/简体中文/繁體中文 labels do not overflow.
```

```text
$qfx-wow-addon-ui Apply this bug fix with minimal diff and give me a traceable report: changed files, risk level, rollback notes, TOC/SavedVariables impact, and in-game test steps.
```

## Reference files

The skill includes these references:

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
