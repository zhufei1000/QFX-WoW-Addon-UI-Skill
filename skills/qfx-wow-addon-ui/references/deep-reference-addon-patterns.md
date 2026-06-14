# Deep Reference Addon Patterns

This reference captures additional architecture and UI lessons found after a deeper review of the uploaded Plater and DandersFrames reference addons.

Use these patterns selectively. They are valuable for larger QFX addons, but they can over-engineer small addons. Do not copy reference addon assets, bundled libraries, private code, or complete custom frameworks unless the user explicitly requests it and licensing is verified.

## 1. Controlled extension and scripting system

Plater's strongest advanced architecture is its controlled extension model: user scripts, mods, hooks, triggers, import/export metadata, and explicit hook points.

QFX should not add user scripting by default. But if an addon needs presets, user packs, or external extensions, use a controlled extension system instead of letting random code patch internals.

Rules:

- Define a fixed hook catalog with stable names such as `OnAlertStart`, `OnAlertStop`, `OnProfileChanged`, `OnModuleEnabled`, or `OnFrameRefresh`.
- Store extension metadata: name, author, version, addonVersion, description, trigger type, enabled state, and required features.
- Validate imported extensions before saving them.
- Compile or initialize extensions in a dedicated loader, not inside the options page.
- Run extension callbacks through a guarded dispatcher with `pcall` or equivalent error isolation.
- If an extension errors repeatedly, disable or quarantine only that extension instead of breaking the whole addon.
- Keep user extension state separate from built-in presets.
- Give every extension a stable ID so triggers, imports, and errors can reference it.
- Do not expose raw DB tables to extensions; provide a small API surface.

Good for:

- MCDVoiceCooldown preset packs;
- class/spec alert packs;
- advanced trigger packs;
- user-customizable text formatting;
- integration callbacks for other addons.

Avoid for:

- small one-purpose addons;
- settings that can be represented as normal SavedVariables;
- anything that would run untrusted code in combat-sensitive paths.

## 2. Hook catalog and trigger registry

A hook or trigger system should be table-driven.

Example shape:

```lua
QFX.ExtensionHooks = {
  ALERT_START = { args = {"alert", "context"}, safeInCombat = true },
  ALERT_STOP = { args = {"alert", "reason"}, safeInCombat = true },
  PROFILE_CHANGED = { args = {"profileName"}, safeInCombat = false },
}
```

Rules:

- Hook names are internal constants, not localized strings.
- Document expected arguments and combat safety.
- Validate trigger type and trigger ID before adding it to an extension.
- Prevent duplicate triggers when only one extension can own a trigger.
- Provide migration for old hook names when the hook catalog changes.
- Use a dispatcher so modules do not directly call user extensions.

## 3. Adapter / Resolver / Renderer pipeline

DandersFrames' designer systems are strong because they separate data collection, resolution, and rendering.

Use this pattern when UI output is computed from several data sources.

Recommended pipeline:

```text
Adapter -> Resolver -> Model -> Renderer -> Preview -> Commit
```

Definitions:

- Adapter: reads external game/addon/API data and normalizes it into stable internal records.
- Resolver: chooses the final value from DB, defaults, profile overrides, runtime state, and adapter data.
- Model: plain table describing what should be displayed.
- Renderer: updates frames from the model.
- Preview: renders from proxy/draft data without committing.
- Commit: writes validated changes to the real DB.

Rules:

- Do not let renderers call many game APIs directly.
- Do not let option pages duplicate resolver logic.
- Adapter outputs should be safe, normalized, and version-aware.
- Resolver should handle missing values and fallback paths.
- Renderer should be dumb and idempotent: same model produces same frame state.
- Preview mode should reuse the same renderer where possible.

Good for:

- text designers;
- aura/alert designers;
- unit frame layout rendering;
- minimap provider detection;
- sound/media picker previews;
- cooldown alert previews.

## 4. Capability gates and feature flags

Both reference addons gate features based on version, available libraries, game APIs, combat state, or known taint risk.

Rules:

- Define capability checks once, for example `Compat:HasSafeAuraAPI()` or `Media:HasSharedMedia()`.
- Feature files ask the capability layer instead of repeating version checks.
- If a feature is disabled, expose a clear reason for options UI and diagnostics.
- For temporary disabled files or features, leave a short reason and re-enable condition near the TOC or compat file.
- Do not silently ignore a missing dependency if the user can fix it.

Example:

```lua
QFX.Capabilities = {
  hasTTS = C_VoiceChat and C_VoiceChat.SpeakText ~= nil,
  hasSharedMedia = LibStub and LibStub("LibSharedMedia-3.0", true) ~= nil,
  canEditProtectedFrames = not InCombatLockdown(),
}
```

## 5. Self-healing configuration and missing asset fallback

DandersFrames includes strong handling for imported profiles that reference missing textures or assets.

Rules:

- Validate configured font, texture, sound, and icon paths before using them.
- Resolve logical media names to real file paths before `SetFont`, `SetTexture`, or playback.
- If a media asset is missing, replace it with a known stock fallback and show a one-time warning.
- Track which warning has already been shown so chat is not spammed.
- Add diagnostics that report missing media keys and fallback choices.
- Imported profiles should not break the UI just because the sender had extra SharedMedia files.

## 6. Object pools with explicit reset rules

Both references use reusable frame ideas, but DandersFrames also documents when pooling can cause stale state.

Rules:

- Use pools for many similar rows, preview icons, test frames, and repeated list items.
- Every pooled object must have a `Reset` or `Release` path that clears anchors, scripts, text, textures, alpha, shown state, selected state, parent, and stable keys.
- Never rely on previous frame state being correct.
- If stale state bugs are likely and object count is small, prefer rebuilding that small component instead of pooling it.
- Keep the item identity in data, not only in the frame.
- Diagnostic mode can expose pool size, active count, and release count.

Reset checklist:

```text
Hide -> ClearAllPoints -> clear parent if needed -> clear scripts -> clear text/texture -> reset alpha/color -> clear data keys -> mark inactive
```

## 7. Post-load validation pass

Large addons benefit from a final load pass after all files are loaded.

Rules:

- Keep `LoadFinished.lua`, `Bootstrap.lua`, or a final init phase for post-load validation.
- Verify required modules registered successfully.
- Verify critical DB paths exist after migrations.
- Verify optional library capability flags.
- Register slash commands and public API after internals are ready.
- Run lightweight self-tests only; do not scan the whole world or create heavy UI during final bootstrap.
- Report serious missing pieces once, with actionable text.

## 8. Category-scoped import/export and merge strategy

Profile import/export should not always be all-or-nothing.

Rules:

- Allow category-scoped export when the addon has distinct setting groups.
- Include category metadata in exported data.
- On import, show detected categories and let users choose what to apply.
- Validate and migrate imported categories independently.
- Merge imported category data into existing profile only through known category keys.
- For destructive full-profile imports, create a backup or confirmation step.
- After import, run a targeted refresh for touched categories.

Good categories:

```text
appearance | sound | text | cooldowns | conditions | profiles | layouts | media | advanced
```

## 9. Auto profile and context switching

DandersFrames uses auto-profile ideas for specialization/content/layout changes.

Rules:

- Auto-switch profiles only when the rule is explicit and visible in options.
- Store auto-profile assignment per character when it depends on that character's spec or role.
- Validate target profile exists before switching.
- Avoid switching during combat if it changes protected frames; defer and show pending state.
- If profile switching changes enabled frame modes or secure headers, prompt for `/reload` when required.
- Add diagnostics for last auto-switch reason, source rule, and target profile.

Useful context keys:

```text
spec | class | role | instanceType | arena | battleground | mythic | raid | party | openWorld
```

## 10. Safe performance probes and ownership filters

The DandersFrames profiler demonstrates an important safety lesson: instrumentation can taint foreign frames if it wraps scripts it does not own.

Rules:

- Profilers and debug hooks must be opt-in and easy to disable.
- Only instrument frames owned by the addon.
- Determine ownership by name prefix, parent chain, explicit marker, or registry membership.
- Cache ownership checks.
- Restore original scripts when profiling stops.
- Do not wrap Blizzard secure frames or other addons' frames.
- Track call count, total time, max time, and optionally memory delta.
- Keep profiling UI hidden from normal users.

## 11. Foreign attachment and compatibility scanner

Large frame addons can be affected by other addons anchoring to their frames.

Rules:

- Provide an optional scanner that reports foreign frames anchored to your frames.
- Run the scanner only on demand.
- Report frame name, parent, anchor target, and owning addon if possible.
- Do not automatically detach foreign frames unless the user explicitly asks.
- This is diagnostic only; compatibility fixes should be intentional and scoped.

Useful for minimap and unit-frame addons where other addons attach widgets to owned frames.

## 12. Safe runtime state machines for alerts

Alert engines should model state explicitly rather than using scattered timers.

Rules:

- Track state per alert key: inactive, pendingDelay, active, repeating, coolingDown, muted.
- Store active timers/tickers by alert key and cancel them on stop, profile switch, spec change, logout, or module disable.
- Avoid duplicate sound/TTS playback from repeated events in the same state.
- Use one cleanup path for all stop reasons.
- Test buttons should route through the same playback path when possible, but mark context as test.
- Diagnostics should show last alert key, last playback path, channel, and stop reason.

## 13. Option dependency graph

Complex option pages often have dependent controls.

Rules:

- Define parent/child relationships explicitly instead of scattering `SetEnabled` calls.
- When a parent setting changes, refresh only affected children or group.
- Disabled child controls should show why they are disabled in tooltip or banner.
- Hidden/disabled child values should not be lost unless the user explicitly resets them.
- Dependencies should be stable keys, not localized labels.

Example:

```lua
Dependencies:Register("sound.enabled", {
  children = {"sound.tts.enabled", "sound.customPath", "sound.channel"},
  refresh = "soundGroup",
})
```

## 14. Design tokens without copying visual skin

Reference addons often have consistent visual systems. QFX can absorb the token idea without copying the skin.

Rules:

- Define spacing, row height, card padding, section gap, label width, control width, and disabled alpha as constants.
- Define semantic colors by purpose, not by copied brand palette: normal, muted, warning, danger, success, accent.
- Use Blizzard-native textures and fonts unless the project explicitly owns custom assets.
- A Skin layer may apply tokens to native controls, but should not own business logic.

## 15. Documentation as part of architecture

Popular addons usually include user-facing docs, changelog, and internal comments for risky load-order choices.

Rules:

- Keep public changelog separate from development trace notes.
- Document TOC load order when it matters.
- Document disabled files/features with the technical reason.
- Keep API docs close to `API.lua`.
- Include example prompts or usage flows for Skill/plugin packages.
- Do not include noisy AI/date markers in runtime code.

## 16. Deep architecture review checklist

When deeply reviewing a QFX addon, additionally check:

- Does the addon need controlled extension hooks, or would normal settings be safer?
- Are data adapters, resolvers, and renderers separated for complex previews?
- Are capability gates centralized and visible in diagnostics?
- Do imported profiles self-heal missing media?
- Are pools reset completely, and are small stale-prone components rebuilt instead?
- Is there a final post-load validation pass?
- Can import/export work by category instead of all-or-nothing?
- Are auto-profile switches explicit, validated, and combat-safe?
- Are profilers ownership-filtered and opt-in?
- Is there an on-demand foreign attachment scanner for owned frames?
- Are alert timers/tickers state-machine based and cleaned up reliably?
- Are option dependencies centralized?
- Are design tokens used without copying another addon's skin?
- Is architecture documentation present where load order or compatibility is non-obvious?
