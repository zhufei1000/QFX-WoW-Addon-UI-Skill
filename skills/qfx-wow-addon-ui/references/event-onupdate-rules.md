# Event and OnUpdate Rules

Use this reference when reviewing addon performance, event handling, OnUpdate usage, taint risk, or high-frequency UI/runtime updates.

## Primary event model

Use the EllesmereUI-style event model as the default for QFX addons when events are shared, bursty, or high-frequency:

```text
One dispatcher owns event registration
  -> listeners register by owner/module
  -> handler updates safe state
  -> RequestRefresh / RequestApply is queued
  -> UI/runtime refresh happens once after burst
```

Small addons with only one or two simple events may use one local event frame instead. Do not over-engineer trivial addons.

## Central event dispatcher

Avoid every module, row, or button registering and filtering the same high-frequency event independently.

Bad pattern:

```text
40 buttons each RegisterEvent("ACTIONBAR_UPDATE_COOLDOWN")
40 buttons each run OnEvent and filter independently
```

Preferred pattern:

```lua
local dispatcher = CreateFrame("Frame")
local listeners = {}

function QFX.Events:Register(event, owner, callback)
    listeners[event] = listeners[event] or {}
    listeners[event][owner] = callback
    dispatcher:RegisterEvent(event)
end

function QFX.Events:Unregister(event, owner)
    local bucket = listeners[event]
    if not bucket then return end
    bucket[owner] = nil
    if not next(bucket) then
        listeners[event] = nil
        dispatcher:UnregisterEvent(event)
    end
end

dispatcher:SetScript("OnEvent", function(_, event, ...)
    local bucket = listeners[event]
    if not bucket then return end
    for owner, callback in pairs(bucket) do
        if owner.enabled ~= false then
            callback(owner, event, ...)
        end
    end
end)
```

Use this for:
- action bar events;
- unit aura/state events;
- bag updates;
- quest tracker updates;
- nameplate/unit frame updates;
- cooldown/timer updates;
- global UI scale/profile changes;
- repeated settings-panel refresh events.

## Event registration rules

Rules:
- Register events once where practical.
- Unregister events when a feature is disabled if safe to do so.
- Keep handlers idempotent.
- Avoid duplicate handlers across modules.
- Centralize shared high-frequency event dispatch.
- Do not mutate UI layout directly inside bursty event handlers.
- Event handlers should usually update safe state and request refresh/apply.

Prefer:

```text
OnEvent -> update safe state -> RequestRefresh(reason)
```

## Coalescing burst events

Many WoW events fire several times in the same frame or same short burst.

Use a pending flag and next-frame queue:

```lua
local pending

local function QueueApply()
    if pending then return end
    pending = true
    C_Timer.After(0, function()
        pending = false
        ApplyQueuedChanges()
    end)
end
```

Use this for bag, quest, aura, spellbook, actionbar, profile, and options refresh bursts.

## OnUpdate discipline

Do not use permanent idle polling for UI that only changes on events.

Allowed temporary OnUpdate cases:
- dragging;
- smooth scrolling;
- short highlight or glow animation;
- resize capture;
- one or two frame layout resnap;
- visible progress animation.

If OnUpdate is needed:
- start it only while active;
- stop it when no longer needed;
- throttle expensive work;
- avoid scanning all modules or rows every frame;
- clear it on panel close, module disable, profile switch, and logout.

Example:

```lua
frame:SetScript("OnUpdate", function(self, elapsed)
    progress = progress + elapsed
    if progress >= duration then
        self:SetScript("OnUpdate", nil)
        FinishAnimation()
        return
    end
    UpdateAnimation(progress / duration)
end)
```

## Weak-table frame state

Do not attach many addon-specific fields directly to Blizzard frames or foreign addon frames when a side table can store state.

Preferred:

```lua
local frameData = setmetatable({}, { __mode = "k" })

local function Data(frame)
    local d = frameData[frame]
    if not d then
        d = {}
        frameData[frame] = d
    end
    return d
end
```

Use weak-table state for:
- skin metadata;
- temporary hook state;
- border/pixel metadata;
- foreign frame ownership markers;
- diagnostic counters;
- cached safe values.

Direct fields are fine for frames fully owned by the addon when there is no taint, lifecycle, or ownership concern.

## Combat and taint

Event handlers must respect combat lockdown and secret-value rules.

Rules:
- Do not mutate protected frames in combat.
- Do not branch on protected/secret values during combat.
- Save safe DB values immediately.
- Queue protected applies for `PLAYER_REGEN_ENABLED`.
- Avoid wrapping Blizzard secure frames or foreign addon secure frames with debug/profiler hooks.
