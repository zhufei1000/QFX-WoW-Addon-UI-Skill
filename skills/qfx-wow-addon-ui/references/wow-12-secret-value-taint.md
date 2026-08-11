# WoW 12.x Secret Value, Forbidden Object, and Taint Rules

Use this reference when fixing Retail 12.x errors involving secret values, taint, forbidden script objects, auras, unit identity, protected frames, or combat-sensitive data.

## Current verified baseline

Last verified: **2026-08-11**.

- Retail `live`: **12.0.7.68974**.
- Retail `ptr`: **12.1.0.69214**.
- PTR HEAD: `9eb0468a36ff0fd9f51d74ae179b201f5b2e8326`.
- The 12.1.0 aura/forbidden-object rules below are PTR behavior at this verification point. Re-check the current `ptr` generated API documentation before coding against them.
- `69189 → 69214` did **not** change `UnitAuraDocumentation.lua`, AuraContainer docs, `SecretPredicatesDocumentation.lua`, `UnitDocumentation.lua`, `UnitRoleDocumentation.lua`, ForbiddenAspect docs, Spell/Cooldown docs, or CombatLog docs. Therefore the Secret/Taint rules in this document remain valid for 69214.

For a focused live-to-PTR change list, read `wow-12.0.7-to-12.1-api-migration-zhCN.md`. It distinguishes **new 12.1 restrictions** from Secret/Restriction behavior that was already present in 12.0.7.

## Recognize restriction errors

Treat messages like these as API/security design problems, not ordinary Lua type errors:

```text
a secret boolean value
a secret number value
execution tainted by
forbidden
```

Also treat a Lua error from an API documented with restriction metadata such as `RequiresUnitAuraAccess`, `SecretWhenUnitAuraRestricted`, or `SecretWhenUnitIdentityRestricted` as a signal to redesign the data flow rather than wrapping the same call in more guards.

## Secret values are not ordinary values

Do not:

- compare secret booleans, numbers, strings, GUIDs, IDs, or enum values;
- perform arithmetic on secret numbers;
- concatenate/format secret strings unless the API explicitly supports secret formatting for that purpose;
- store secrets in SavedVariables;
- serialize or export secrets;
- sort, count, hash, key, or classify secret data to infer its value;
- branch gameplay logic on a secret result;
- use `pcall`, error/no-error behavior, timing, frame visibility, table length, or iteration success as a side channel to infer secret information;
- copy secret values into another table/frame/object in an attempt to make them non-secret.

A secret value is intentionally unreadable addon state. The correct fix is normally to stop requiring the protected information.

## Read generated restriction annotations literally

Modern generated API documentation carries security behavior in metadata. Important annotations include:

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
- `RequiresUnitAuraAccess`
- `RequiresValidUnitAuraInstance`
- `RequiresNonSecretAura`
- `RequiresComparableUnitTokens`
- `HasRestrictions`

These are part of the API contract.

For example, a returned table marked `ConditionalSecretContents = true` is not automatically safe to inspect simply because the outer table is a Lua table.

# Patch 12.1 Aura Rules

Blizzard's 12.1 design goal is to let addons customize **how filtered auras are displayed** while preventing addons from reading the underlying aura state for combat automation.

## C_UnitAuras is no longer a general-purpose combat aura database

In the current 12.1 PTR generated documentation:

- `C_UnitAuras.GetAuraDataByAuraInstanceID` requires UnitAura access and is secret when UnitAura access is restricted.
- `C_UnitAuras.GetAuraDataByIndex` requires UnitAura access and is secret when restricted.
- `C_UnitAuras.GetAuraDataBySlot` requires UnitAura access and is secret when restricted.
- `C_UnitAuras.GetBuffDataByIndex` and `GetDebuffDataByIndex` carry the same restriction model.
- `C_UnitAuras.GetUnitAuras` requires UnitAura access and returns an aura table with `ConditionalSecretContents = true`.
- `C_UnitAuras.GetUnitAuraInstanceIDs` requires UnitAura access.
- `UNIT_AURA` is marked `SecretWhenAurasRestricted = true`.
- `UNIT_AURA_BLOCKED` explicitly marks `auraInstanceID` as a secret value.

Do not build combat logic by enumerating these APIs and then trying to distinguish restricted from unrestricted results.

## Spell ID/name lookup is not a bypass

Current PTR APIs such as:

- `C_UnitAuras.GetUnitAuraBySpellID`
- `C_UnitAuras.GetPlayerAuraBySpellID`
- `C_UnitAuras.GetAuraDataBySpellName`

carry `RequiresNonSecretAura = true` together with aura restriction metadata.

Use them only for cases where the queried aura is legitimately exposed as non-secret. Do not use a list of spell IDs/names as a probe to discover whether secret combat auras are present.

## Prefer AuraContainer / ManagedAuraContainer for display

For an addon whose goal is to **show** buffs/debuffs:

- use the 12.1 AuraContainer/ManagedAuraContainer architecture;
- let Blizzard handle aura tracking, filtering, assignment, and refresh;
- use AuraGroups/AuraSlots and supported filters/options for presentation;
- style aura buttons only through supported initialization/configuration paths;
- do not rebuild the old `UNIT_AURA -> enumerate -> diff -> decide -> render` model for restricted contexts.

This is a display boundary, not a new way to recover AuraData.

## Aura filters changed in 12.1

Current 12.1 PTR notes include:

- support for negating most filters with `!`, for example `!PLAYER`;
- `NOT_CANCELABLE` removed in favor of `!CANCELABLE`;
- `DISPELLABLE` added;
- `IMPORTANT` restored after its 12.0.7 removal;
- `RAID_PLAYER_DISPELLABLE` expanded to include helpful enemy auras that a raid member can dispel/steal.

Re-check the current filter enum/docs before hardcoding a filter set.

## SecureAuraHeaderTemplate boundary

`SecureAuraHeaderTemplate` was removed from Mainline during the 12.1 aura migration and remains relevant to Classic branches.

Rules:

- Mainline 12.1 aura displays should migrate to AuraContainers.
- Classic support must stay behind a version/client boundary.
- Do not keep Mainline code dependent on `SecureAuraHeaderTemplate` just because a Classic implementation still uses it.

## AuraContainer combat creation changed during PTR

PTR behavior changed during testing:

- an earlier PTR build intentionally rejected addon AuraContainer creation in combat;
- a later PTR build changed this and allows addons to create AuraContainers during combat.

This is exactly why old PTR workarounds must not be treated as permanent API truth. Verify the current build before preserving a workaround.

# Forbidden Script Objects and Forbidden Aspects

Patch 12.1 adds Private Script Objects, a Forbidden Partition, and Forbidden Aspects.

A **secret** aspect hides/obfuscates data. A **forbidden** aspect blocks addon access to functionality on the object.

Important 12.1 Forbidden Aspects include:

- `UntrustedScriptExecution`
- `UntrustedLayoutScriptExecution`
- `EventRegistrations`
- `AlwaysPropagateInput`
- `ScriptedInput`
- `QueryFocus`

The enum also contains additional generic restrictions such as script binding, parent-change, animation-target, and secret-aspect operations. Always inspect current generated docs when interacting with a constrained script object.

## AuraButton restrictions

Aura Buttons are deliberately designed so addon code cannot use their lifecycle as a combat-information side channel.

Do not rely on:

- `OnShow` / `OnHide` / `OnSizeChanged` callbacks to discover aura state;
- hooking AuraButton mixins to detect assignments;
- registering events on AuraButtons when forbidden;
- `IsShown` or focus/input queries to infer an aura's presence;
- reparenting AuraButtons;
- child-frame hooks that attempt to bypass the parent restrictions.

Calls through tainted code can Lua-error in restricted contexts even if similar calls worked outside combat.

## AuraContainer restrictions

AuraContainers use forbidden-object mechanics too. Their intended role is controlled presentation.

Do not install logic whose purpose is to infer hidden aura assignments from:

- child count;
- child visibility;
- layout/size changes;
- event registration;
- anchor changes;
- tooltip/focus/input behavior.

Use supported container configuration APIs only.

# Unit Identity and Comparison Restrictions

12.1 also expands secret handling beyond auras.

Current generated Unit documentation marks many identity-sensitive APIs with `SecretWhenUnitIdentityRestricted`, including examples such as:

- `UnitClass` / `UnitClassBase`
- `UnitCreatureFamily` / `UnitCreatureID` / `UnitCreatureType`
- `UnitFullName` / `UnitGUID` / `UnitNameFromGUID` / `UnitNameUnmodified`
- `UnitGroupRolesAssigned` / `UnitGroupRolesAssignedEnum`
- `UnitIsOwnerOrControllerOfUnit`
- `UnitIsPVP`
- `UnitIsRaidOfficer`
- `UnitLeadsAnyGroup`
- `UnitOwnerGUID`
- `UnitPVPName`
- `UnitPhaseReason`
- `UnitRace`
- `UnitSexBase`

This list is not exhaustive. Trust the current generated annotation on the function you are actually using.

`UnitName` has its own `SecretWhenUnitNameIdentityRestricted` rule.

`UnitIsUnit` currently has both:

- `RequiresComparableUnitTokens = true`
- `SecretWhenUnitComparisonRestricted = true`

Do not use a matrix of `UnitIsUnit` calls to identify secret units.

`UnitIsCharmed` and `UnitIsPossessed` are marked `SecretWhenUnitPossessionRestricted` in the current PTR docs.

PTR notes also changed `GetGuildInfo` so addons should not rely on compound unit tokens there.

# Common Risk Areas

Be especially careful with:

- aura state and aura payloads;
- spell availability/cooldowns;
- unit identity/GUID/name/class/race/role;
- unit health/power/stats;
- interruptibility/cast state;
- action button state;
- tooltip scanning;
- frame visibility/focus/input;
- protected/forbidden frame scripts and events;
- secure attributes and protected frame mutation during combat.

# Safer Design Patterns

Prefer:

- Blizzard-provided display objects that consume restricted data internally;
- non-secret events whose payload is explicitly documented as consumable;
- static spell metadata where the addon only needs labels/icons/configuration;
- fixed cooldown timers when the timing is legitimately known from the player's own action/event path;
- cached values only when those values were originally non-secret and remain valid for the use case;
- user-configured fallback values;
- explicit preview/fake data in settings UI;
- delayed protected-frame application after combat;
- version/capability wrappers that return `nil`/unsupported rather than probing a restriction.

## Important distinction: visual customization vs combat decision logic

A 12.1 AuraContainer may allow rich visual customization without granting addon code access to the actual aura identity/state.

That means this can be valid:

```text
Blizzard tracks filtered aura -> AuraContainer displays button -> addon styles supported visual properties
```

while this design is invalid/unreliable in restricted contexts:

```text
addon reads secret aura -> identifies mechanic -> branches logic -> selects target/action/alert
```

Do not try to convert the first model back into the second through hooks or side channels.

# Testing Checklist

For any secret/taint/forbidden-object fix, test at minimum:

- login/reload with no Lua errors;
- out of combat;
- ordinary combat;
- encounter or Mythic+ combat if the feature is used there;
- PvP restricted contexts if applicable;
- target/focus/mouseover/nameplate/party/raid unit-token paths used by the addon;
- entering and leaving combat repeatedly;
- UI reload followed by `PLAYER_LOGIN` for AuraButton initialization behavior;
- taint/forbidden errors with other addons enabled if the feature touches shared Blizzard frames.

Do not mark a fix complete merely because it works on a target dummy out of combat.

# Reporting

When fixing a secret-value or forbidden-object issue, final notes should state:

- target branch/build verified;
- which API/restriction annotation caused the old design to be unsafe;
- what supported display/event/configuration path replaced it;
- whether any feature behavior was intentionally reduced because the underlying information is no longer available to addons;
- Mainline vs Classic differences if relevant;
- in-game test steps for both unrestricted and restricted contexts.
