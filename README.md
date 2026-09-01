# QFX WoW Addon UI Codex Skill

Version: 1.17.0

This package contains a Codex plugin with one skill:

- `qfx-wow-addon-ui`

It is designed for World of Warcraft addon UI design, architecture review, API-safe refactoring, and release packaging with QFX conventions.

## What v1.17.0 changes

- Updates the current WoW 12.1.0 baseline to **Live 12.1.0.69497** and **PTR 12.1.0.69587** (verified 2026-09-01).
- Separates **Live production contracts** from **PTR-only warnings**, so preview APIs are not treated as Retail-ready by default.
- Records the Live 69404 `HookScript` / `SetScript` change for `SimpleAnimAPI`, `SimpleAnimGroupAPI`, and `SimpleScriptRegionAPI`: `SecretArguments = NotAllowed` became `AllowedWhenUntainted`, while assignable-script and `ForbiddenAspect.ScriptBindings` checks remain.
- Records the Live 69465 `UnitCanAssist` signature extension, the new `UnitIsPlayerControlledOrGroupMember(unit)` API, and Blizzard's updated Aura identity-filter behavior.
- Records Blizzard Private Aura behavior showing `visualAlert` can be secret because it derives from a secret spell ID; Blizzard's internal secure-environment `secretunwrap` use is explicitly not treated as an addon-accessible bypass.
- Records the Live 69497 TTS contract change: `C_VoiceChat.SpeakText().text` and `VOICE_CHAT_TTS_PLAYBACK_BOOKMARK.bookmarkName` are now `ConditionalSecret`.
- Records CooldownViewer equip-slot GCD filtering and CooldownBroadcaster's separate `InterruptSpellsBySpec` tracking model with six base cooldowns plus up to two interrupt cooldowns.
- Adds the PTR 69587 warning for `C_LFGInfo.IsInMatchmadeRaidWithoutRoleRequirements()` and Blizzard CompactRaidFrames' use of it for Main Tank / Main Assist layout handling.
- Updates `.codex-plugin/plugin.json` to version 1.17.0.

## Earlier API milestones

### v1.16.2

- Re-verified WoW 12.1.0 at build 69299.
- Recorded the PTR Discord catch-up: `C_Discord.GetDiscordUserName(userID)`, removal of `DiscordChatInfo.username`, and the current `GetDiscordUserCommunityLink` signature.

### v1.16.1

- Re-verified Live 69283 / PTR 69273 against the 69214 high-risk API baseline.

### v1.15.0

- Confirmed the 12.0.7 → 12.1 migration details around `RequiresUnitAuraAccess`, `ForbiddenAspect`, `SecretAspect.RadialProgress`, Aura sound API replacement, Unit identity predicates, and CooldownViewer data changes.

## Core design guidance

The skill uses one scalable QFX method for small, medium, and large addons:

- Blizzard-native visuals by default.
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

The skill includes references for:

- QFX UI architecture and modular addon design.
- Refresh/performance and event/OnUpdate rules.
- English-first multilingual layout, typography, visual standards, and accessibility.
- WoW 12.x API source-grounding.
- 12.0.7 → 12.1 migration history.
- Current 12.1 Live/PTR API baseline.
- Secret-value / taint / ForbiddenAspect safety.
- Blizzard-native UI review.
- Plater / DandersFrames / EllesmereUI-inspired architecture patterns.
- Combat-lockdown deferred apply.
- Packaging, SavedVariables migration, version compatibility, and modification traceability.

The authoritative current API file is:

`skills/qfx-wow-addon-ui/references/wow-12.1.0-live-api-final-zhCN.md`
