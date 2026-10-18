# QFX WoW Addon UI Skill

Version: 1.27.0

This package contains one reusable agent skill, `qfx-wow-addon-ui`, for World of Warcraft addon UI design, architecture review, API-safe refactoring, and release packaging with QFX conventions. It works as a **Codex plugin** and as an **opencode skill** (or any agent that reads `SKILL.md` frontmatter).

- `skills/qfx-wow-addon-ui/SKILL.md`
- `skills/qfx-wow-addon-ui/references/*.md`
- `skills/qfx-wow-addon-ui/assets/*` (official contact icons)

## What v1.27.0 changes

- Adds a **Detect and handle secrets** section to the secret/taint reference: `issecretvalue`, `canaccessvalue`, `issecrettable`, `canaccesstable`, the `C_Secrets.*` and `C_RestrictedActions.*` queries, `Enum.SecretAspect` widget checks, a canonical guard pattern for secret health/power, and the rule never to `pcall` a restriction error as a probe. Previously the skill described the restrictions but named none of the detection APIs.
- Adds **Client branches and interface versions** to `SKILL.md`: the current interface number for each client family (120105 / 50504 / 11509 / 38002 / 20506), multi-client TOC gating, the 12.x TOC directives that matter for UI work, and the restricted Blizzard-facing directive list.
- Adds `C_AddOns` runtime metadata guidance (`GetAddOnMetadata`, `IsAddOnLoaded`, `LoadAddOn`, `GetNumAddOns`, `GetAddOnInfo`) and retires the deprecated bare globals.
- Marks the 12.0.7 → 12.1.0 migration reference as a **historical archive** and retires its "redo the live diff" closeout requirement; the current contract lives in the live API baseline.
- Refreshes the `wow-12-api-source-rules` and `wow-12-secret-value-taint` baselines from **12.1.0.69214** to **12.1.5.70448**, and records branch `ptr` as **12.1.7.70424**.
- Documents the API-verification fallback when a client install does not expose `Blizzard_APIDocumentationGenerated`: installed-addon usage first, then the Warcraft Wiki `API:` page, then `Gethe/wow-ui-source`.
- Changes the "update this skill" workflow: repository sync is **opt-in** (no forced push), and the version files live in the repository root, not in an installed copy.

## What v1.26.1 changes

- Refreshes the authoritative Live WoW API provenance from **12.1.5.70391** to **12.1.5.70448** (verified 2026-10-18): no `Blizzard_APIDocumentationGenerated` change in that Live commit.
- Documents the five-second BonusRollFrame UI refresh ticker and cancellation in GroupLootFrame, with QFXBeggar compatibility notes; this is not an API contract change.
- Records new **PTR 12.1.7.70424** API previews (PTR-only): `GroupBuffItem.displaySpellID`, `C_ActionBar.EnableActionCombatActionRangeCheck` and event, `C_Spell.IsActiveSpell` / `GetItemCooldown`, `C_SpellBook.IsSpellBookItemLowRank`, and new Unit interaction APIs, retaining Secret restrictions and return semantics.
- Updates branch provenance and maintains existing Live 12.1.5 Secret/Aura/CooldownViewer safety rules.

## What v1.26.0 changes

- Moves the official WoW API baseline to **Live 12.1.5.70391** and records PTR2 **12.1.5.70340** as the current warning branch.
- Promotes the former PTR2-only 12.1.5 contracts to Live: `C_UnitAuras.GetRefreshCarryOverDuration()`, `CooldownSetSpellFlags.SelectHighestLevelLinkedSpell`, Secret-returning `GetArenaOpponentSpec(index)`, and the animation ForbiddenAspects `QueryAnimationProgress` / `AddAnimations`.
- Records the Live Aura Sound contract: `C_UnitAuras.AddAuraSound` is restricted, playback stops after five seconds, and `throttleSeconds` must stay within 0–5 seconds.
- Adds the Live SocialRestrictions / Age Verification / VoiceChat Chat Messaging Lockdown rules and updates the TTS ConditionalSecret guidance.
- Notes that the key high-risk generated API files currently match between Live 70391 and PTR2 70340; Live 70391 itself only advances `version.txt` over 70340.
- Refreshes CombatLog guidance for the current split ordinary/Shared/Internal/Secure documentation model.

## What v1.25.2 changes

- Documents the hover feedback for the contact icons: reuse the icon texture as an ADD highlight so the whole icon lights up; the default round mouse-hilight reads as a small dot on 20px icons.

## What v1.25.1 changes

- Uses the white GitHub mark so the icon stays readable on dark settings panels (the black variant was nearly invisible there).

## What v1.25.0 changes

- Adds the official GitHub mark to `skills/qfx-wow-addon-ui/assets/` (`GitHubIcon.tga` / `GitHubIcon.png`).
- Documents the three-icon contact row used by QFX addons: Discord invite, QQ group number, and the addon's GitHub repository address, each clickable to copy.

## What v1.24.0 changes

- Ships the official brand icons in `skills/qfx-wow-addon-ui/assets/`: `DiscordIcon.tga` / `QQGroupIcon.tga` (64x64, WoW-ready) plus `.png` previews.
- The QQ penguin is the official icon extracted from the local QQ client (`QQNT\QQ.exe` associated icon); the Discord mark comes from the GitHub Explore topic icon.
- Documents in-addon usage: copy the TGAs into the addon's `Media/`, reference them without extension, place them next to the author line (bottom of the settings navigation) or in the relevant settings section, and pair them with the copy-dialog pattern.

## What v1.23.0 changes

- Adds the official QFX community channels (Discord invite and QQ group) to `SKILL.md` and this README, so addon support notices and "request a unit frame adaptation" prompts always use the same contacts.
- Documents the recommended in-addon pattern for contact channels: small clickable icons that open a copy dialog, because WoW exposes no clipboard API (pre-select the text and instruct the user to press Ctrl+C).

## What v1.22.0 changes

- Updates the WoW API reference baseline to **Live 12.1.0.69933** and **PTR2 12.1.5.69952** (re-verified 2026-09-25; no newer Gethe build was present).
- Records Live 69933 `ForbiddenAspect.SetTexture` / `QueryRotation`, the corresponding `SimpleTextureBaseAPI` checks, and `IsRaidMarkerActive` becoming secret during Chat Messaging Lockdown.
- Promotes `C_LFGInfo.IsInMatchmadeRaidWithoutRoleRequirements()` from the older PTR warning to a Live contract.
- Documents PTR2 69952 `C_UnitAuras.GetRefreshCarryOverDuration()` in detail, including Blizzard CooldownViewer/AuraContainer Pandemic-window usage and its difference from `GetRefreshExtendedDuration()`.
- Documents PTR2 69952 `GetArenaOpponentSpec(index)` as a Secret-returning API, not a normal addon-readable specialization ID.
- Records `CooldownSetSpellFlags.SelectHighestLevelLinkedSpell` and the animation ForbiddenAspects `QueryAnimationProgress` / `AddAnimations`.
- Bumps the skill/plugin package metadata to v1.22.0.

## What v1.21.0 changes

- Adds the mandatory game-client sync check to `SKILL.md` (addon workflow step 14) and `references/release-and-compatibility.md`: after any WoW addon code change, check the game's `Interface/AddOns/` for the addon folder. If it is installed, back up and sync the changed files immediately without waiting for a request; if it is not installed, do not create it and sync only when the user explicitly asks.
- Documents locating the game installation from the Blizzard registry key (`InstallPath`) or the known `_retail_` / `_classic_` folders, and matching addon folder names exactly so a similarly named folder is never treated as the same addon.

## What v1.20.0 changes

- Adds the mandatory repository sync rule to `SKILL.md` ("When asked to update this skill", rule 8): after every local skill change, commit and push to `https://github.com/zhufei1000/QFX-WoW-Addon-UI-Skill` (`main`), bump the version across `README.md`, `INSTALL.md`, and `.codex-plugin/plugin.json`, refresh the local plugin package copy, and rebuild its release zip. The installed skill must never stay ahead of the repository, and a local change is not complete until the repository holds it.
- Rule 5 now points at the sync rule so a version bump and the push always happen in the same pass.

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

## Community

- Discord: https://discord.gg/HVJ2y4v7k4
- QQ group: 1049855225
