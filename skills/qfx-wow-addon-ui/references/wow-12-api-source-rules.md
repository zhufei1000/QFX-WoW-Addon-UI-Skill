# WoW 12.x API Source Rules

Use this reference whenever designing, reviewing, or modifying World of Warcraft addons for Retail 12.x / Midnight or a current PTR where API behavior may have changed.

## Current verified baseline

Last verified: **2026-10-18**.

- Retail `live`: **12.1.5.70448** — the working contract for all current addon work.
- Live HEAD: `b9be9379719047977fca4dba1bb1d9988e8840b3`.
- Retail `ptr`: **12.1.7.70424** — the next-version preview branch; its additions are not Live APIs.
- Retail `ptr2`: **12.1.5.70340** — kept only for 12.1.5 historical comparison.
- `live` **70391 → 70448** touched only `version.txt` and `Blizzard_UIPanels_Game/Mainline/GroupLootFrame.lua`; `Blizzard_APIDocumentationGenerated` did not change, so this round carries **no API contract delta**.
- Content-level Blob SHA verification of the high-risk generated API files (UnitAura, AuraContainer,
  CooldownViewer, SecretPredicates, Unit, UnitRole, Spell, ForbiddenAspect, CombatLog,
  SpecializationInfo, generated documentation TOC) confirmed identical between Live 70448 and
  PTR2 70340.
- The 12.1.5 APIs that earlier notes marked PTR2-only have **entered Live**; treat them as the
  formal contract, not as previews. `C_UnitAuras.GetRefreshCarryOverDuration` is the clearest
  example and is already used by shipping addons.

For the current Live verification matrix, read `wow-12.1.0-live-api-final-zhCN.md`.
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

> **Local availability.** `Blizzard_APIDocumentationGenerated` ships inside the CASC store, so a
> normal client install does **not** expose `Interface\AddOns\Blizzard_APIDocumentationGenerated`.
> When that dump is absent, do not stall — fall back in this order:
> 1. grep the addons actually installed on this machine for real call sites of the symbol
>    (`Get-ChildItem <AddOns> -Recurse -Filter *.lua | Select-String '<Symbol>'`), which proves what
>    the live client accepts today;
> 2. the Warcraft Wiki `API:<Name>` page (signature, game-type badges, secret predicates);
> 3. the `Gethe/wow-ui-source` branch matching the target build.
>
> Treat "no local dump" as a sourcing change, never as permission to recall a signature.

Recommended public references:

- `Gethe/wow-ui-source`: current WoW UI source with separate `live`, `ptr`, `ptr2`, and `beta` branches.
- `Ketho/BlizzardInterfaceResources`: extracted globals, templates, mixins, atlas data, enums, and build resources.
- Blizzard PTR/UI Engineering posts: intended behavior and migration direction.
- Warcraft Wiki API pages: signatures, patch history, examples, and consolidated diffs.
- `wago.tools`: DB2/global string/resource lookups when required by extracted resources.

### Why generated API docs come first

Wiki and PTR summaries can lag behind the actual extracted client build. During 12.1, the public PTR source advanced through several late builds before Live switched to 12.1.5. Current Retail work must now use **Live 12.1.5.70448** generated docs as the primary source of truth.

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
