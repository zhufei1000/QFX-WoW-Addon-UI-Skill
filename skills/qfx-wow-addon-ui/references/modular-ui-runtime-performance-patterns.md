# Modular UI Runtime Performance Patterns

Use this reference when a WoW addon has a large settings panel, many modules, action buttons, saved lists, visual editors, or repeated refresh lag.

This reference is extracted from an EllesmereUI / EllesmereUIActionBars case study. Apply the architecture and runtime patterns that fit QFX addons. Do not copy its bundled fonts, textures, icons, sounds, libraries, brand-specific art, or complete visual skin unless the user explicitly requests it and licensing is verified.

## Priority rule

When this reference conflicts with older generic QFX guidance about UI lifecycle, page refresh, event dispatch, or runtime performance, prefer this reference.

The priority override applies to architecture and performance behavior:
- deferred options loading;
- module registration;
- page caching;
- widget refresh callbacks;
- centralized event dispatch;
- coalesced refresh;
- temporary OnUpdate;
- weak-table state storage;
- combat-safe deferred apply.

It does not require QFX addons to copy a modern custom-drawn visual style. If the user wants Blizzard-native appearance, keep the QFX native visual style while using these runtime patterns.

## 1. Register modules into one settings shell

Large QFX addons should not let every module create its own independent settings frame.

Prefer one settings shell with:
- left module list or category list;
- top title and description area;
- tab or page bar for the selected module;
- scrollable content area;
- footer actions such as reset, close, import/export, or diagnostics;
- a single module registry.

Each module should register metadata and page builders:

```lua
QFX.UI:RegisterModule("ChatBar", {
    title = L["Chat Bar"],
    description = L["Configure chat input shortcuts and buttons."],
    pages = { "General", "Buttons", "Advanced" },
    buildPage = function(pageName, parent, y)
        return QFX.Options.ChatBar:BuildPage(pageName, parent, y)
    end,
    refresh = function(pageName)
        QFX.Modules.ChatBar:RefreshOptions(pageName)
    end,
    reset = function()
        QFX.Modules.ChatBar:ResetOptions()
    end,
})
```

The shell owns navigation, scroll behavior, search, cached pages, and shared refresh. Modules own settings definitions and business logic.

## 2. Runtime modules must not depend on options UI

Runtime code must work even if the settings panel has never been opened.

Recommended separation:

```text
Core/      load at addon startup
Modules/   runtime features and event handlers
UI/        shared UI shell and widget factory, created lazily
Options/   page builders, created lazily
Debug/     optional diagnostics, lazy-loaded or hidden
```

A module may expose `Apply`, `Refresh`, `Enable`, `Disable`, and `GetStatus` functions. The options page calls these functions; it must not become the owner of runtime state.

## 3. Defer heavy options initialization

Do not build all settings pages during `ADDON_LOADED` or `PLAYER_LOGIN`.

Use a lazy gate:

```lua
QFX.UI._deferredInits = QFX.UI._deferredInits or {}
QFX.UI._loaded = false

function QFX.UI:EnsureLoaded()
    if self._loaded then return end
    self._loaded = true
    for i, fn in ipairs(self._deferredInits) do
        fn()
        self._deferredInits[i] = nil
    end
end

function QFX.UI:Open()
    self:EnsureLoaded()
    self:CreateMainFrame()
    self.MainFrame:Show()
end
```

Use this for:
- large widget files;
- searchable setting metadata;
- import/export editors;
- media pickers;
- diagnostics;
- preview panels;
- heavy dropdown/list construction.

Do not defer core runtime modules, localization needed at startup, DB migration, or compatibility wrappers required by running features.

## 4. Cache pages, but refresh widgets in place

For large settings panels, rebuilding a full page on every tab switch or every checkbox change causes lag and layout drift.

Preferred model:

```text
cache key = moduleName .. "::" .. pageName
cached value = {
  wrapper = frame,
  totalHeight = number,
  refreshList = table,
  metadata = optional,
}
```

When a cached page is revisited:
- show the cached wrapper;
- restore its refresh callback list;
- call each refresh callback to re-read DB values;
- do not recreate every child frame.

When layout really changes:
- invalidate only the affected page cache;
- rebuild that page;
- preserve scroll position if appropriate;
- avoid orphaning other cached pages.

For very large QFX addons, limit cached pages if memory becomes an issue:
- default: cache current page and recent pages;
- heavy visual editors: cache only while the panel remains open;
- diagnostic pages: rebuild on demand unless repeatedly used.

## 5. Use widget refresh callbacks instead of full rebuilds

Every reusable control should be able to register a refresh function.

```lua
local refreshList = {}

function QFX.UI:RegisterWidgetRefresh(fn)
    refreshList[#refreshList + 1] = fn
end

function QFX.UI:RefreshPage(force)
    if not force and #refreshList > 0 then
        for i = 1, #refreshList do
            refreshList[i]()
        end
        return
    end
    self:RebuildCurrentPage()
end
```

Use refresh callbacks for:
- checkbox checked state;
- slider value text;
- dropdown display text;
- enabled/disabled state;
- row selection highlight;
- dependency visibility;
- warning/banner text;
- preview swatches.

Use full rebuild only for:
- new rows added or removed;
- filter/sort result changes;
- locale change requiring relayout;
- page structure changes;
- corrupted or missing cached page;
- control type changes.

## 6. Describe option rows with data where practical

For repeated settings, prefer table-driven row definitions over ad-hoc widget construction.

A row definition should include:

```lua
{
    id = "chatbar.scale",
    type = "slider",
    label = L["Scale"],
    desc = L["Adjust the chat bar scale."],
    min = 0.7,
    max = 1.5,
    step = 0.05,
    get = function(db) return db.chatBar.scale end,
    set = function(db, value)
        db.chatBar.scale = value
        QFX.Modules.ChatBar:RequestApply("scale")
    end,
    refresh = "targeted",
}
```

The widget factory creates the frame; the module handles meaning.

This improves:
- localization coverage;
- search indexing;
- dependency graph handling;
- import/export mapping;
- consistent layout;
- future UI refactors.

## 7. Use a central event dispatcher for high-frequency events

Avoid registering the same high-frequency event in many modules or many row/button frames.

Bad pattern:

```text
40 buttons each RegisterEvent("ACTIONBAR_UPDATE_COOLDOWN")
40 buttons each run OnEvent and filter independently
```

Better pattern:

```lua
local dispatcher = CreateFrame("Frame")
local listeners = {}

function QFX.Events:Register(event, owner, callback)
    listeners[event] = listeners[event] or {}
    listeners[event][owner] = callback
    dispatcher:RegisterEvent(event)
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

Use central dispatch for:
- action bar events;
- unit aura/state events;
- bag updates;
- quest tracker updates;
- nameplate/unit frame updates;
- cooldown/timer updates;
- global UI scale/profile changes.

Keep simple one-off modules simple. Do not add a large dispatcher to a tiny addon with two events.

## 8. Coalesce repeated refreshes into one next-frame apply

Many WoW events fire in bursts. Do not rebuild immediately for every event.

Use a pending flag:

```lua
local pending
local reasons = {}

function QFX:RequestRefresh(reason)
    reasons[reason or "unknown"] = true
    if pending then return end
    pending = true
    C_Timer.After(0, function()
        pending = false
        self:Refresh(reasons)
        wipe(reasons)
    end)
end
```

Use this for:
- bag item changes;
- quest watch updates;
- aura updates;
- spellbook updates;
- profile changes;
- multi-control UI edits;
- bulk import;
- resize/scale cascades.

If the update touches protected frames, combine this with combat-safe deferred apply.

## 9. OnUpdate must be temporary and owned

Permanent idle polling is a release risk unless the addon truly needs continuous animation or measurement.

Allowed temporary OnUpdate cases:
- dragging;
- smooth scrolling;
- short highlight/glow animation;
- resize capture;
- one or two frame layout resnap;
- progress animation while visible.

Rules:
- set `OnUpdate` only when the behavior starts;
- clear it immediately when the behavior ends;
- do not scan all modules or rows every frame;
- throttle expensive work;
- clean it up on panel close, module disable, profile switch, and logout.

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

## 10. Store external frame state in weak tables

Do not attach lots of custom fields directly to Blizzard frames or foreign addon frames if a weak side table can hold the state.

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
- pixel-perfect border data;
- temporary hook state;
- external frame ownership markers;
- diagnostic counters;
- cached safe values.

Still keep direct fields when the frame is fully owned by the addon and there is no taint or lifecycle concern.

## 11. Avoid duplicate architecture systems

Before adding a new helper, check whether the addon already has:
- UI factory;
- module registry;
- event dispatcher;
- refresh queue;
- DB/profile layer;
- media resolver;
- localization loader;
- diagnostic logger.

Extend the existing system unless the user explicitly requests a full rewrite.

Do not mix Ace, custom event systems, and extra callback routers in the same addon without a reason. If an old addon already depends on Ace, do not remove Ace only for style; first isolate runtime and UI refresh costs.

## 12. Combat-safe apply remains mandatory

A cached UI page or refresh callback must not bypass combat lockdown safety.

If a setting touches protected frames:
- save the DB value immediately;
- show the new value in the UI;
- if in combat, mark an apply as pending;
- apply on `PLAYER_REGEN_ENABLED`;
- show one compact warning/banner if useful;
- do not spam chat for every deferred setting.

## 13. Search should index settings, not duplicate controls

For searchable settings:
- register metadata from the same option definitions that create controls;
- include stable setting ID, localized label, aliases, module, page, section, and jump/highlight callback;
- search result click should navigate to the real page and highlight the real control;
- do not create a second copy of the setting inside search results.

## 14. Large-list rows should separate create and refresh

For saved voices, spell pickers, bag categories, module lists, or aura lists:
- create a fixed number of row frames;
- refresh row contents from visible data;
- keep selection state in data, not row object lifetime;
- refresh only visible rows for scroll changes;
- rebuild the data model only when filters/sorts/imports change.

## 15. QFX adoption tiers

Small addon:
- keep one file or simple modules;
- use native controls;
- add `RequestRefresh` only if repeated refresh is visible;
- do not add page cache unless options are large.

Medium addon:
- use module registry;
- lazy options panel;
- UI factory;
- refresh callbacks;
- coalesced apply;
- targeted event dispatch.

Large addon / addon suite:
- shared settings shell;
- page cache with invalidation;
- searchable setting registry;
- central event dispatcher;
- diagnostics page;
- import/export validation;
- profile/schema migration;
- weak-table state for foreign frames;
- explicit public API if other addons integrate.

## 16. Review checklist

When reviewing a QFX addon against this reference, check:

- Does runtime load without opening settings?
- Are heavy options created only on first open?
- Are pages cached or rebuilt repeatedly?
- Do widgets refresh in place where possible?
- Are option rows table-driven or at least factory-driven?
- Are high-frequency events centrally dispatched?
- Are repeated event bursts coalesced?
- Are OnUpdate scripts temporary and cleaned up?
- Is foreign frame state stored safely?
- Are protected frame changes deferred in combat?
- Are imports and bulk edits refreshed once at the end?
- Are old architecture systems reused instead of duplicated?
- Are visual assets and libraries not copied from the reference addon?
