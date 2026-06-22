# Refresh Performance Rules

Use this reference when UI changes cause lag, repeated rebuilds, import/expand stutter, page switching delay, or settings-panel memory growth.

## Primary refresh model

Use the EllesmereUI-style refresh model as the default for QFX addons:

```text
Event / user edit / import
  -> update DB or safe runtime state
  -> RequestRefresh(reason, scope)
  -> next frame coalesced refresh
  -> widget refresh callbacks for value/status changes
  -> full rebuild only for structural changes
```

Do not rebuild the entire settings panel for every small value change.

## RequestRefresh pattern

Use `RequestRefresh(reason, scope)` or an equivalent queue:

```lua
local pending
local reasons = {}

function QFX:RequestRefresh(reason, scope)
    reasons[reason or "unknown"] = scope or true
    if pending then return end
    pending = true
    C_Timer.After(0, function()
        pending = false
        self:Refresh(reasons)
        wipe(reasons)
    end)
end
```

Rules:
- If a refresh is already pending, merge the new reason.
- `full` overrides weaker reasons.
- Defer heavy refresh to the next frame when possible.
- Keep the last refresh reason for diagnostics when useful.
- Do not do immediate full rebuilds inside bursty events.

## Widget refresh callbacks

When a page is built, each control should register a small refresh function when useful.

Use widget refresh callbacks for:
- checkbox checked state;
- slider value text;
- dropdown display text;
- button enabled/disabled state;
- selected row highlight;
- dependency visibility;
- warning/banner text;
- preview swatches;
- one row visual update.

Example:

```lua
QFX.UI:RegisterWidgetRefresh(function()
    checkbox:SetChecked(db.enabled)
    slider.ValueText:SetText(FormatValue(db.scale))
    dropdown:SetDisplayText(GetCurrentLabel(db.mode))
end)
```

## Page cache rules

For settings-heavy addons, cache pages when switching tabs or modules would otherwise rebuild many controls.

Cache key:

```text
moduleName .. "::" .. pageName
```

Cached page should store:
- wrapper frame;
- content height;
- refresh callbacks;
- optional search metadata;
- optional scroll position.

When revisiting a cached page:
- show the wrapper;
- restore the relevant refresh callbacks;
- refresh values in place;
- do not recreate all child frames.

Limit cache size when memory becomes a problem:
- small addon: no page cache needed;
- medium addon: cache current module pages while panel is open;
- large addon: cache current page plus recent pages, or invalidate heavy editor pages aggressively.

## Targeted refresh vs full rebuild

Prefer targeted refresh for:
- button state;
- one row visual update;
- slider current value text;
- dropdown display text;
- selected row highlight;
- dependency enable/disable;
- warning/banner content;
- preview display.

Use full refresh only for:
- rows added or removed;
- data structure changes;
- filter or sort changes;
- locale-wide relayout;
- page layout changes;
- control type changes;
- missing or invalid cache.

## Sliders

While dragging:
- update current value text immediately;
- save or apply lightweight values as needed;
- defer expensive relayout or full list refresh;
- do not rebuild a page on every slider tick.

## Large lists

For saved sounds, voice collections, addon lists, module lists, spell lists, aura lists, bag categories, and search results:
- create row frames once;
- refresh visible row contents from data;
- keep selection state in data, not in row frame lifetime;
- refresh only visible rows while scrolling;
- rebuild the visible data model only when filter, sort, import, delete, or add changes the list structure.

## Bulk import/export

During bulk import:
- decode and validate all data first;
- apply changes in memory;
- migrate and self-heal missing data if needed;
- refresh once at the end;
- avoid one full list rebuild per imported item.

During export:
- gather data from DB/runtime state, not from visible row widgets;
- do not require the options page to be open.

## Combat-aware refresh

If a refresh would touch protected frames:
- update DB immediately;
- update safe UI values immediately;
- if in combat, mark protected apply pending;
- apply on `PLAYER_REGEN_ENABLED`;
- show one compact note or banner if useful;
- do not spam chat for repeated deferred changes.
