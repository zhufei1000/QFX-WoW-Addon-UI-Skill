# Event and OnUpdate Rules

Use this reference when reviewing addon performance and event handling.

## Event registration

Rules:
- Register events once.
- Unregister events when a feature is disabled if safe to do so.
- Keep handlers idempotent.
- Avoid duplicate handlers across modules.
- Centralize shared event dispatch when practical.

## OnUpdate discipline

Do not use permanent idle polling for UI that only changes on events.

If OnUpdate is needed:
- Start it only while active.
- Stop it when no longer needed.
- Throttle expensive work.
- Avoid scanning all rows every frame.

## UI refresh from events

Event handlers should usually request refresh instead of doing full UI rebuild immediately.

Prefer:

```text
OnEvent -> update safe state -> RequestRefresh(reason)
```

## Combat and taint

Event handlers must respect combat lockdown and secret-value rules.
Do not mutate protected frames or branch on secret values during combat.
