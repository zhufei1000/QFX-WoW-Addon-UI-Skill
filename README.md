# QFX WoW Addon UI Skill

Version: 1.19.0

This package contains one reusable agent skill, `qfx-wow-addon-ui`, for World of Warcraft addon UI design, architecture review, API-safe refactoring, and release packaging with QFX conventions. It works as a **Codex plugin** and as an **opencode skill** (or any agent that reads `SKILL.md` frontmatter).

- `skills/qfx-wow-addon-ui/SKILL.md`
- `skills/qfx-wow-addon-ui/references/*.md`

## What v1.19.0 changes

- Makes the QFXWidgets control factory (QFXUI skin) the standard settings UI: `SKILL.md` replaces the "native first" rules with a "QFXWidgets first" section, and the slider anatomy, visual standards, UI states, keyboard conventions, and workflow steps now follow the factory's tokens and behaviour.
- Adds `references/qfxwidgets-factory.md`: the factory contract (control cfgs, tokens, refresh/page model, combat rules, media helpers, extra controls) plus the lazy loading rules for core + load-on-demand Config hosts.
- Adds `references/qfxwidgets-ui-checklist.md` and refreshes `references/ui-visual-standards.md`, `qfx-ui-architecture.md`, `complex-addon-ui-patterns.md`, and the remaining references to the QFXWidgets/QFXUI baseline.
- Adds the lazy factory loading rule: a core addon keeps `QFXWidgets.lua` out of its startup `.toc`, resolves the factory at use time (`rawget(_G, "QFXWidgets")`, then `EnsureConfigLoaded()`), lets a standalone factory addon win when installed, and applies skin/media where it actually loads.
- Removes the superseded `references/blizzard-native-ui-checklist.md`; the QFXWidgets checklist replaces it.
- Updates the example prompts, plugin metadata, and reference list for the factory standard.

## What v1.18.0 changes

- Adds YAML frontmatter (`name` + `description`) to `SKILL.md` so the skill is discoverable by opencode and other `SKILL.md`-based agents.
- Rewrites `SKILL.md` from 477 lines to a lean overview that delegates detail to references, removing duplicated architecture/refresh/supplement passages.
- Consolidates small overlapping references:
  - packaging, version compatibility, SavedVariables migration, and traceability → `references/release-and-compatibility.md`
  - large lists, collections, sound/TTS, and font/media safety → `references/lists-media-sound-ui.md`
  - UI factory/dialog/mode rules and combat-lockdown deferred apply → folded into `references/complex-addon-ui-patterns.md`
- Documents the opencode install path alongside the Codex plugin install.
- Syncs version numbers across `README.md`, `INSTALL.md`, and `.codex-plugin/plugin.json`.

## Core design guidance

The skill uses one scalable QFX method for small, medium, and large addons:

- QFXWidgets factory controls (QFXUI skin) as the standard settings UI.
- English-first layout sizing, then zhCN / zhTW verification.
- Shared UI factories and modular architecture.
- Deferred heavy options initialization.
- Page cache and targeted widget refresh where useful.
- Centralized high-frequency event dispatch.
- Coalesced refresh/apply queues.
- Temporary active-only `OnUpdate` instead of permanent idle polling.
- Combat-safe deferred apply.
- Source-grounded WoW API verification before coding.
- Secret / taint / ForbiddenAspect-aware design.

## WoW API baseline

For current Retail 12.1 development, read:

- `skills/qfx-wow-addon-ui/references/wow-12.1.0-live-api-final-zhCN.md`

Current baseline:

```text
Live: 12.1.0.69497
PTR:  12.1.0.69587
```

Rules:

- Live is the production contract.
- PTR is warning/compatibility input only until the same API reaches `live`.
- Never mix branches or infer API signatures from memory.
- Re-check `Blizzard_APIDocumentationGenerated` whenever the build changes.
- Treat Aura, Unit, Spell/Cooldown, TTS, secure frames, ScriptBindings, and Secret/Forbidden APIs as high risk.

## Install in opencode

Copy the skill folder into a scanned skill path:

```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\.config\opencode\skills" | Out-Null
Copy-Item -Recurse -Force ".\skills\qfx-wow-addon-ui" "$env:USERPROFILE\.config\opencode\skills\qfx-wow-addon-ui"
```

Alternatively use the auto-loaded external path `~/.agents/skills/qfx-wow-addon-ui`. Restart opencode after copying; the skill loads from `SKILL.md` frontmatter and is not hot-reloaded.

## Install as a Codex plugin

1. Copy the plugin folder to a local plugin location, for example:

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

Depending on your marketplace root, adjust `source.path` so it points to the plugin folder. Restart Codex and install the plugin from Plugins.

## Install as a raw skill only (Codex)

```bash
mkdir -p ~/.agents/skills
cp -R qfx-wow-addon-ui-plugin/skills/qfx-wow-addon-ui ~/.agents/skills/qfx-wow-addon-ui
```

Restart Codex if the skill does not appear.

## Example prompts

```text
Use qfx-wow-addon-ui to review this addon with the primary QFX design method: choose small/medium/large scale, build settings with the QFXWidgets factory, size the layout from English first, defer heavy options, use page cache and widget refresh where useful, centralize high-frequency events, coalesce refreshes, avoid permanent OnUpdate, and keep combat-safe applies.
```

```text
Use qfx-wow-addon-ui to review this multilingual settings UI with English as the base layout language, then verify Simplified Chinese and Traditional Chinese for overflow, clipping, row balance, and runtime language switching.
```

```text
Use qfx-wow-addon-ui to verify this addon against WoW 12.x API sources before coding: check current UI source/resources, branch/build, deprecated APIs, secret-value/taint risk, compatibility wrappers, and final API assumptions.
```

```text
Use qfx-wow-addon-ui to review this addon settings UI and architecture. Find release blockers, layout drift, architecture drift, localization gaps, taint risks, API risks, performance problems, and packaging completeness.
```

## Reference files

The skill includes references for:

- QFX UI architecture and modular addon design.
- Refresh/performance and event/OnUpdate rules.
- English-first multilingual layout, typography, visual standards, and accessibility.
- Complex UI patterns, lists, media, dialogs, and combat-safe apply.
- Plater / DandersFrames / EllesmereUI-inspired architecture patterns.
- WoW 12.x API source-grounding, the 12.0.7 → 12.1 migration history, and the current 12.1 Live/PTR baseline.
- Secret-value / taint / ForbiddenAspect safety.
- QFXWidgets factory contract, lazy factory loading, and the settings UI checklist.
- Packaging, compatibility, SavedVariables migration, and modification traceability.

The authoritative current API file is:

`skills/qfx-wow-addon-ui/references/wow-12.1.0-live-api-final-zhCN.md`
