# Combat Lockdown Deferred Apply

Use this reference when UI options may affect protected frames or combat-sensitive behavior.

## Core pattern

When a setting is changed:

1. Save the setting immediately.
2. If not in combat, apply it immediately.
3. If in combat, mark apply pending and apply after `PLAYER_REGEN_ENABLED`.

## Do not

- Do not mutate protected frames in combat.
- Do not spam chat for every deferred setting change.
- Do not lose the user's setting just because apply is delayed.
- Do not rebuild protected frame layouts during combat.

## Good user feedback

If useful, show one small status line:

```text
This change will apply after combat.
```

Avoid repeated warnings.

## Testing

Test:
- Change setting out of combat.
- Change setting in combat.
- Leave combat and verify pending apply happens once.
- Reload after deferred setting and verify saved state remains correct.
