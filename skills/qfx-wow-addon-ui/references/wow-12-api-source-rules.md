# WoW 12.x API Source Rules

Use this reference whenever designing, reviewing, or modifying World of Warcraft addons for Retail 12.x / Midnight or any current client where API behavior may have changed.

A GitHub search did not find a ready-made `WoW 12.0 API Codex Skill` suitable to depend on directly. Instead, use current API/source repositories and API-documentation sites as grounding sources before writing code.

## 1. Preferred API source order

When API correctness matters, use this order:

1. Current FrameXML/UI source for the target branch.
2. Current extracted interface resources and API dumps.
3. Warcraft Wiki API pages for signatures, notes, and historical behavior.
4. Existing addon examples only after checking they target the same client branch.
5. Memory/internal knowledge last, and never as the only source for changed APIs.

Recommended public references:

- `Gethe/wow-ui-source`: current WoW UI source with separate `live`, `ptr`, `ptr2`, and `beta` comparisons.
- `Ketho/BlizzardInterfaceResources`: extracted global resources, globals, templates, mixins, atlas info, and build metadata.
- Warcraft Wiki API pages: community API documentation and behavior notes.
- `wago.tools`: useful for DB2/global string/resource lookups referenced by extracted resource projects.

## 2. Branch and build discipline

Always match the client branch before trusting an API.

Rules:

- For live Retail, prefer `live` branch resources.
- For PTR/Beta, prefer the matching `ptr`, `ptr2`, or `beta` branch when available.
- Do not mix Retail 12.x API assumptions with Classic, MoP Classic, TBC, or Titan branches.
- Record the build or interface number used for API decisions when the fix is sensitive.
- If a user reports a version-specific bug, ask or infer the exact branch only when necessary; otherwise write guarded compatibility code.

## 3. Verify before using changed or risky APIs

Before using an API that is likely to change, verify it in source/dumps first.

High-risk categories:

- spell cooldown and spell usability APIs;
- aura APIs and aura payload shape;
- interruptibility, cast info, and protected booleans;
- unit health/power/combat state values;
- tooltip scanning APIs;
- C_ namespace APIs;
- map, quest, encounter journal, and LFG APIs;
- secure/protected frame creation and attribute changes;
- addon compartment and minimap APIs;
- TTS/voice APIs and channel routing;
- FrameXML templates, mixins, and widget names;
- deprecated globals replaced by namespaced APIs.

## 4. Retail 12.x secret value and taint checks

For 12.x / Midnight-style clients, treat combat-related API changes as taint-sensitive until proven otherwise.

Rules:

- Do not compare, store, serialize, or arithmetic secret values.
- Do not branch on protected/secret booleans during combat if the result can taint execution.
- Errors containing `a secret boolean value`, `a secret number value`, or `execution tainted by` require redesign, not just nil checks.
- Prefer event-driven safe approximations, fixed timers, cached safe values, or user-configured values.
- Keep all uncertain 12.x API work behind a compatibility wrapper so future changes are localized.

## 5. Compatibility wrapper pattern

Do not scatter raw API calls through feature modules when the API is version-sensitive.

Use a compatibility wrapper:

```lua
QFX.Compat = QFX.Compat or {}

function QFX.Compat.GetSpellCooldownSafe(spellID)
  -- implement using verified branch-specific APIs
  -- return normalized, non-secret values only if safe
end
```

Rules:

- Wrapper names should describe intent, not one Blizzard function name.
- Return normalized values with documented nil behavior.
- Keep branch checks inside Compat, not in every module.
- Add comments only when explaining real API changes, taint, compatibility, or migration.
- Test mode should call the same wrapper where possible, with explicit fake data support.

## 6. Deprecation and replacement discipline

When an API appears deprecated or renamed:

- Search source for both old and new names.
- Check if Blizzard code still uses the old API.
- Check whether the replacement has different return values, payload shape, or combat restrictions.
- Add a fallback only when the old branch still needs it.
- Do not keep unnecessary fallback layers for versions the addon no longer supports.

## 7. Source-grounded code review checklist

Before packaging an addon update for 12.x:

- Did every changed WoW API call get checked against a current source/dump/wiki page?
- Are branch-specific calls isolated in `Compat/Version.lua`, `Compat/Blizzard.lua`, or equivalent?
- Are protected frame changes deferred out of combat?
- Are secret-value errors avoided by design rather than patched with boolean/nil tests?
- Are FrameXML templates and mixins available in the target branch?
- Are TTS, sound, and media APIs verified for the target client?
- Are Classic/MoP/TBC/Titan branches kept separate from Retail 12.x logic?
- Does final reporting mention any API assumptions or branch limitations?

## 8. What to do when unsure

If there is uncertainty about a WoW API:

1. Search current source/dumps.
2. Search Warcraft Wiki API documentation.
3. Search the target branch of Blizzard UI source for Blizzard's own usage.
4. Put the call behind a compatibility wrapper.
5. Add a guarded fallback or explicit unsupported note.
6. Include the API uncertainty in the final risk/test report.

Never invent a 12.x API signature from memory.
