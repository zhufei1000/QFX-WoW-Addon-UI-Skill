# WoW 12.x API Source Rules

Use this reference whenever designing, reviewing, or modifying World of Warcraft addons for Retail 12.x / Midnight or a current PTR where API behavior may have changed.

## Current verified baseline

Last verified: **2026-08-11**.

- Retail `live`: **12.1.0.69214**.
- Live HEAD: `057e2e1429765a2b9e9eb100889f2b7e50317307`.
- Retail `ptr`: **12.1.0.69214**.
- PTR HEAD: `9eb0468a36ff0fd9f51d74ae179b201f5b2e8326`.
- `live/version.txt` and `ptr/version.txt` both report `12.1.0.69214`.
- Content-level Blob SHA verification confirms the high-risk generated API files are identical between Live and PTR 69214: UnitAura, AuraContainer, CooldownViewer, SecretPredicates, Unit, UnitRole, Spell, ForbiddenAspect, CombatLog, SpecializationInfo, and the generated documentation TOC.
- Therefore the previously verified PTR 69214 rules in those areas are now treated as the **current Retail 12.1.0 Live API contract**.

For the final Live verification matrix, read `wow-12.1.0-live-api-final-zhCN.md`.
For historical 12.0.7 → 12.1 migration details and PTR build evolution, read `wow-12.0.7-to-12.1-api-migration-zhCN.md`.

Do not copy the build numbers above into addon runtime logic. They are documentation provenance only. When doing future work, re-check the target branch `version.txt` and generated API documentation first.

## 1. Preferred API source order

When API correctness matters, use this order:

1. **Generated API documentation from the exact target branch/build**, especially `Interface/AddOns/Blizzard_APIDocumentationGenerated/`.
2. Current FrameXML/UI source from that same branch, to see how Blizzard actually consumes the API.
3. Current extracted interface resources/API dumps.
4. Blizzard UI Engineering / PTR addon API notes.
5. Warcraft Wiki API pages and patch-change summaries.
6. Existing addon examples only after checking they target the same client branch.
7. Memory/internal knowledge last, and never as the only source for changed APIs.

Recommended public references:

- `Gethe/wow-ui-source`: current WoW UI source with separate `live`, `ptr`, `ptr2`, and `beta` branches.
- `Ketho/BlizzardInterfaceResources`: extracted globals, templates, mixins, atlas data, enums, and build resources.
- Blizzard PTR/UI Engineering posts: intended behavior and migration direction.
- Warcraft Wiki API pages: signatures, patch history, examples, and consolidated diffs.
- `wago.tools`: DB2/global string/resource lookups when required by extracted resources.

### Why generated API docs come first

Wiki and PTR summaries can lag behind the actual extracted client build. During 12.1, the public PTR source advanced through several late builds before Live switched to 12.1.0. Current Retail work must now use **Live 12.1.0.69214** generated docs as the primary source of truth.

Therefore:

- Use the wiki to understand *why* and *when* behavior changed.
- Use current generated documentation to determine current signatures and restriction metadata.
- Use current FrameXML to confirm how Blizzard expects the API/object to be used.
- Use direct PTR commit diff only for future pre-release changes after the current Live baseline.

## 2. Branch and build discipline

Always match the client branch before trusting an API.

Rules:

- For live Retail, use the `live` branch.
- For PTR/Beta, use the matching `ptr`, `ptr2`, or `beta` branch.
- Never treat an older PTR weekly note as newer than the current extracted branch.
- Do not mix Retail 12.x assumptions with Classic, MoP Classic, TBC Classic, Titan, or other clients.
- Record the branch and build in review notes when a decision is API-sensitive.
- Keep build checks out of feature modules unless a real runtime compatibility requirement exists.

PTR behavior can reverse between weekly builds. A concrete 12.1 example: an earlier PTR build intentionally errored when addons created an AuraContainer in combat, while a later PTR build changed the design to allow addon AuraContainer creation during combat. Re-verify the current branch instead of preserving an older PTR workaround forever.

## 3. Read restriction metadata as part of the API contract

In 12.x, the function name and Lua return type are not enough. Generated documentation contains restriction metadata that must be reviewed before using a value in addon logic.

Pay special attention to fields such as:

- `HasRestrictions`
- `SecretArguments`
- `SecretReturns`
- `SecretValue`
- `ConditionalSecret`
- `ConditionalSecretContents`
- `SecretWhenUnitAuraRestricted`
- `SecretWhenAurasRestricted`
- `SecretWhenUnitIdentityRestricted`
- `SecretWhenUnitNameIdentityRestricted`
- `SecretWhenUnitComparisonRestricted`
- `SecretWhenUnitPossessionRestricted`
- `SecretWhenUnitHealthRestricted`
- `SecretWhenUnitPowerRestricted`
- `RequiresUnitAuraAccess`
- `RequiresValidUnitAuraInstance`
- `RequiresNonSecretAura`
- `RequiresUnitIdentityAccess`
- `RequiresComparableUnitTokens`
- `NeverSecret` / `NeverSecretContents`

Treat these annotations as functional API behavior, not as documentation decoration.

A table marked `ConditionalSecretContents = true` may be a normal Lua table whose contents become secret under a restricted context. Do not assume that receiving the table means addon code may inspect, count, compare, sort, serialize, or make gameplay decisions from its contents.

## 4. High-risk API categories

Before using an API in these areas, verify it in the current generated docs/source first:

- auras and aura payloads;
- spell cooldown/usability and action state;
- unit identity, GUID/name/class/race/role/group-state APIs;
- unit health/power/stats;
- cast/interruptibility data;
- tooltip aura/unit access;
- `C_` namespace APIs with restriction annotations;
- secure/protected/forbidden script objects;
- frame creation, reparenting, anchors, scripts, events, and visibility in combat;
- addon compartment/minimap APIs;
- TTS/voice/channel APIs;
- templates, mixins, widget methods, and removed globals.

## 5. Patch 12.1 aura refactor: source-grounding rule

Patch 12.1 introduces Aura Containers / Aura Buttons and tighter aura secrecy. Blizzard's direction is to let addons customize **display** without exposing underlying aura data that can be used for combat automation.

For current 12.1 Live work:

- Treat `C_UnitAuras` index/slot/aura-instance access as restricted when `RequiresUnitAuraAccess` / `SecretWhenUnitAuraRestricted` applies.
- `C_UnitAuras.GetUnitAuras` returns a table whose aura contents are marked `ConditionalSecretContents = true` and the call requires UnitAura access.
- Spell-ID/name lookup APIs such as `GetUnitAuraBySpellID`, `GetPlayerAuraBySpellID`, and `GetAuraDataBySpellName` carry `RequiresNonSecretAura = true`; they are not a general bypass around aura restrictions.
- `UNIT_AURA` is marked `SecretWhenAurasRestricted = true`.
- `UNIT_AURA_BLOCKED.auraInstanceID` is a secret value.
- Prefer AuraContainer/ManagedAuraContainer display architecture when the addon only needs to present filtered auras.
- Do not rebuild a 12.1 aura display around manual enumeration, diffing, or hidden-state inference merely because an older Retail implementation did so.
- Keep Classic `SecureAuraHeaderTemplate` code behind a version boundary; it was removed from Mainline during the 12.1 aura migration.

For direct **12.0.7 → 12.1 Live** migration or compatibility review, read `wow-12.0.7-to-12.1-api-migration-zhCN.md` together with `wow-12.1.0-live-api-final-zhCN.md`.

Read `wow-12-secret-value-taint.md` before implementing or repairing any aura display or aura-driven combat logic.

## 6. Secret value / taint / forbidden-object discipline

For modern Retail 12.x:

- Do not compare, arithmetic, serialize, persist, unwrap, or deliberately leak secret values.
- Do not branch gameplay logic on protected/secret booleans or numbers.
- Do not use error behavior, table length, iteration success, frame visibility, script callbacks, timing, or other side channels to infer protected information.
- Do not treat `pcall` as a way to make a restricted API safe.
- Do not install scripts/hooks/events on objects whose Forbidden Aspects disallow those operations.
- Prefer Blizzard-provided safe display objects, safe formatting APIs, events with non-secret payloads, fixed/static metadata, and explicit user configuration.

Errors containing `a secret boolean value`, `a secret number value`, `execution tainted by`, `forbidden`, or a restricted-script-object failure require an API/design review, not just a nil guard.

## 7. Compatibility wrapper pattern

Do not scatter version-sensitive APIs through feature modules.

Use intent-based compatibility helpers, for example:

```lua
QFX.Compat = QFX.Compat or {}

function QFX.Compat.GetSpellCooldownSafe(spellID)
  -- Implement only from the verified target branch API contract.
  -- Return normalized data only when addon code is allowed to consume it.
end
```

Rules:

- Wrapper names describe addon intent, not merely mirror a Blizzard API name.
- Document nil/unsupported behavior.
- A wrapper must not attempt to declassify or infer secret data.
- Keep version/feature capability checks inside `Compat` or a capability module.
- UI test/preview data should be explicit fake data, not extracted restricted live data.

For 12.1 aura displays, a compatibility layer should select the correct display architecture by client family/version rather than trying to normalize restricted AuraData back into the pre-12.1 model.

For 12.1 CooldownViewer/CDM, never assume `CooldownViewerCooldown.spellID` is always non-nil; inspect `spellCategoryID`, `equipSlot`, and `buffSlot` as applicable.

## 8. Deprecation and replacement discipline

When an API appears deprecated, renamed, removed, or replaced:

- Search current generated docs for the old and new names.
- Search same-branch FrameXML for current Blizzard usage.
- Compare restriction metadata, not just arguments/returns.
- Check whether the replacement is a data API, display API, secure action, or script-object API; these are not interchangeable.
- Add a fallback only for client versions the addon really supports.
- Remove stale PTR workarounds after verifying they are no longer required.

## 9. Source-grounded review checklist

Before packaging a Retail 12.x addon update:

- What exact branch/build was checked?
- Was every changed risky API verified against generated docs from that branch?
- Were restriction annotations checked as well as signatures?
- Was same-branch FrameXML checked when object lifecycle or secure behavior matters?
- Is any wiki/blue-post guidance older than the current extracted branch?
- Are aura displays using the supported 12.1 display path instead of secret-data enumeration?
- Are Unit identity/comparison restrictions handled without secret branching?
- Are protected/forbidden frame mutations deferred or avoided correctly?
- Are Mainline/Classic template differences isolated?
- Are TTS, sound, tooltip, minimap, and secure-action APIs verified if touched?
- Does the final report state API assumptions and in-game test requirements?
- For PTR work, was the previous PTR HEAD compared directly to the current PTR HEAD for late-build changes?

## 10. What to do when unsure

If there is uncertainty about a WoW API:

1. Read target branch `version.txt`.
2. Search the target branch generated API documentation.
3. Search same-branch FrameXML for Blizzard usage.
4. Read the latest Blizzard addon/PTR notes for intent.
5. Use Warcraft Wiki for history and consolidated diffs, checking its documented build.
6. For PTR work, compare the previous known PTR commit against current `ptr` HEAD.
7. Isolate uncertain behavior behind a capability/compatibility boundary.
8. Mark PTR-only assumptions explicitly; do not apply them to Live without verification.

Never invent a 12.x API signature or secrecy rule from memory.
