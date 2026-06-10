# WoW 12.x Secret Value and Taint Rules

Use this reference when fixing Retail 12.x errors that mention secret values or taint.

## Recognize secret value errors

Treat these as taint/secret-value issues, not ordinary Lua type errors:

```text
a secret boolean value
a secret number value
execution tainted by
```

## Do not do these

Do not:
- Compare secret booleans or numbers.
- Store secret values in SavedVariables.
- Serialize secret values.
- Use secret values in arithmetic.
- Branch directly on protected results in combat.
- Hook protected functions in a way that taints Blizzard execution.

## Safer approaches

Prefer:
- Event-driven state.
- Fixed cooldown timers.
- Cached safe values.
- User-configured fallback values.
- Delayed application after combat.
- Avoiding protected frame mutation during combat.

## Common risky areas

Be careful with:
- Spell availability.
- Cooldown APIs.
- Unit health/power.
- Aura internals.
- Interruptibility flags.
- Action button state.
- Protected frame visibility and anchoring.

## Reporting

When fixing a secret-value issue, final notes should state:
- Which protected/secret API pattern was avoided.
- What safe approximation or event path replaced it.
- Whether functionality changed.
- In-game test steps for combat and non-combat.
