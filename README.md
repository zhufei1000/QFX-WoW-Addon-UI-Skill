# QFX WoW Addon UI Codex Skill

Version: 1.6.0

This package contains a Codex plugin with one skill:

- `qfx-wow-addon-ui`

It is designed for World of Warcraft addon UI design, review, and refactoring with QFX conventions.

## What v1.6 adds

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

## Earlier v1.5 additions

- Slider value layout standard: min label under the left end, max label under the right end, and current value centered below the slider on the same line.
- Avoid right-side slider value text in compact/two-column cards because it can crowd adjacent controls or clip at the panel edge.
- Slider drag guidance now explicitly allows immediate current-value text updates while deferring heavy refresh work.

## Earlier v1.4 additions

- Modification traceability rules: every change must report modified/added/deleted files, TOC impact, SavedVariables impact, risk level, rollback notes, and in-game tests.
- Minimal-diff discipline: do not reformat unrelated code, rename unrelated functions, or rewrite architecture during a focused bug fix.
- Clean runtime code rule: no `modified by AI`, date-stamped edit markers, or noisy comments; comments must explain real WoW API, taint, migration, compatibility, or performance behavior.
- Development trace guidance: use `docs/CHANGELOG_DEV.md` or `_DEV_CHANGELOG.md` only when appropriate, and keep dev-only logs out of release zips unless requested.
- Release package cleanliness: distinguish public changelog bullets from internal trace notes.

## Earlier v1.3 additions

- Modular addon architecture rules: Core, DB, Migration, Localization, UIFactory, Options, Media, Compat, and feature modules.
- No-duplicate-architecture rules: do not create second module registries, DB layers, locale tables, UI factories, or media resolvers.
- Safe font/media rules: resolve AUTO/DEFAULT/BLIZZARD presets to real asset paths before calling WoW APIs such as `FontString:SetFont()`.
- SavedVariables migration rules for old user profiles, per-module settings, and per-mode settings.
- Refresh-performance rules: no full `ApplyAll` rebuild for tiny option changes; use targeted refresh and slider throttling.
- Event and OnUpdate discipline: centralized idempotent event registration and no permanent idle polling.
- Version-compatibility boundaries for Retail/Classic/MoP/Titan and reference-addon usage.
- Clear parent/sub-addon dependency rules: do not make child addons independent unless explicitly requested.

## Earlier v1.2 additions

- Compact, multilingual, width-aware layout rules for English, 简体中文, and 繁體中文.
- Strict UI factory/control reuse rules.
- Dialog, popup, dropdown z-order, and mode-specific control rules.
- Large list, saved collection, sound picker, TTS, and LibSharedMedia rules.
- Combat-lockdown deferred-apply pattern.
- Sub-addon, TOC, media, library, and release packaging checklist.
- Required final summary format for code changes.

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
$qfx-wow-addon-ui Apply complex addon UI patterns to this saved-list editor: shared scrollable dropdown, stable drag/drop keys, batched refresh, and language-safe editor refresh.
```

```text
$qfx-wow-addon-ui Review this addon settings UI. Find release blockers, layout drift, localization gaps, taint risks, and performance problems.
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
$qfx-wow-addon-ui Refactor this addon into a modular structure without creating a second architecture. Add safe font/media fallback, SavedVariables migration, targeted refresh, and event/OnUpdate guards.
```

```text
$qfx-wow-addon-ui Apply this bug fix with minimal diff and give me a traceable report: changed files, risk level, rollback notes, TOC/SavedVariables impact, and in-game test steps.
```


## Reference files

The skill includes these references:

- `blizzard-native-ui-checklist.md`
- `qfx-ui-architecture.md`
- `wow-12-secret-value-taint.md`
- `ui-factory-dialog-mode-rules.md`
- `compact-multilingual-layout.md`
- `large-list-collection-sound-ui.md`
- `combat-lockdown-deferred-apply.md`
- `packaging-release-checklist.md`
- `modular-addon-architecture.md`
- `safe-font-media-rules.md`
- `savedvariables-migration.md`
- `refresh-performance-rules.md`
- `event-onupdate-rules.md`
- `version-compat-boundaries.md`
- `modification-traceability.md`
