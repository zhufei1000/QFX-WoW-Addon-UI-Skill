# QFX UI Architecture

Use this reference when structuring or refactoring QFX-style WoW addon UI code.

## Primary design method

Use the EllesmereUI-style design method as the default architecture model for QFX addon UI work, scaled to addon size.

This means:
- one root namespace;
- one DB/default/migration boundary;
- one localization boundary;
- one QFXWidgets factory copy for all settings controls (never a second local factory);
- one module registry when modules exist;
- one settings shell when the addon has more than a trivial options page;
- runtime modules that do not depend on options pages being opened;
- deferred creation of heavy options UI;
- page caching when useful;
- widget refresh callbacks instead of full rebuilds;
- central dispatch for repeated or high-frequency events;
- coalesced refresh/apply queues;
- temporary OnUpdate only while active;
- weak-table side state for Blizzard or foreign frames when ownership or taint risk exists.

Previous QFX, Plater-inspired, DandersFrames-inspired, native-UI, and WoW 12.x rules are supplements to this base method. Use them when they improve the result, but if they conflict with this method on UI lifecycle, refresh strategy, event dispatch, or runtime performance, prefer this method.

Settings UI visuals come from QFXWidgets/QFXUI (see `qfxwidgets-factory.md`), not from this architecture model. Do not copy reference-addon assets or custom skins.

## Scale by addon size

### Small addon

Use the simplified form:

```text
AddonName.lua or Core.lua
Localization.lua      if multilingual
Options.lua           if settings exist
Compat.lua            if version/API wrappers are needed
```

Rules:
- Do not over-engineer.
- One event frame is usually enough.
- A full settings shell is optional.
- Build settings rows with an embedded `QFXWidgets.lua` (add it to the Config `.toc`; in a core + load-on-demand Config host, load it lazily there — see `qfxwidgets-factory.md`); do not write local widget helpers.
- Add `RequestRefresh` only when repeated refresh is visible or likely.
- Avoid permanent OnUpdate.

### Medium addon

Use the normal QFX structure:

```text
Core/
  Init.lua
  Events.lua
  DB.lua
  Migration.lua
  Localization.lua
UI/
  QFXWidgets.lua      -- shared controls, skin, menus, lists (copy verbatim)
  MainFrame.lua
  Options.lua
  Dialogs.lua         -- host-specific dialogs only; confirms use W:Confirm
Modules/
  ModuleName.lua
Media/
  Media.lua
Compat/
  Version.lua
  Blizzard.lua
```

Rules:
- Register modules into one settings shell.
- Runtime modules expose `Enable`, `Disable`, `Apply`, `Refresh`, and optional `GetStatus` functions.
- Options pages call module APIs; they do not own runtime state.
- Heavy options, lists, media pickers, previews, and import/export pages are lazy-created.
- Use widget refresh callbacks for value/status updates.

### Large addon or addon suite

Add boundaries only when the addon needs them:

```text
UI/
  ModuleRegistry.lua
  PageCache.lua
  RefreshRegistry.lua
  SearchRegistry.lua
Core/
  Dispatcher.lua
  RefreshQueue.lua
Debug/
  Diagnostics.lua
ImportExport/
  ImportExport.lua
API.lua                 if external access is needed
```

Rules:
- Use one shared settings shell for module navigation.
- Use cached pages with explicit invalidation.
- Use searchable setting metadata instead of duplicate search controls.
- Use central event dispatch for high-frequency shared events.
- Use diagnostics lazily; do not run profilers by default.
- Use public API boundaries only when other addons or child addons need stable integration.

## Settings shell model

For settings-heavy addons, prefer a single shell with:
- left module/category list;
- top title and description area;
- tabs or pages for the selected module;
- scrollable content area;
- footer actions such as reset, close, import/export, or diagnostics;
- one current-page refresh registry.

Each module registers metadata and page builders:

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

The shell owns navigation, scroll behavior, page cache, search, and shared refresh. Modules own settings definitions and business logic.

## Preferred lazy options pattern

Runtime code must load without creating all options widgets.

```lua
QFX.UI._loaded = false
QFX.UI._deferredInits = QFX.UI._deferredInits or {}

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

Do not defer DB migration, localization required at startup, compatibility wrappers required by runtime modules, or module event setup.

## QFXWidgets factory

QFXWidgets is the standard settings-control factory for QFX addons. Read `qfxwidgets-factory.md` for the full contract (tokens, cfg types, extra controls, refresh/page model, combat rules, media helpers).

It may create and style:
- Buttons, toggle switches, sliders, dropdowns, segmented pills, inputs, keybind capture
- Color swatches and color-mode rows, color grids
- Section headers, notes, spacers, wide buttons, status and reset rows
- Tabs and tab panels, checkbox grids, multiline boxes, confirm dialogs
- Scrollable pages, searchable dropdowns, icon pickers, list and reorder rows
- Menus, shared skin tokens, tooltip and refresh helpers

The factory must not contain addon business logic; `getValue`/`setValue` closures own meaning.

## Option row definitions

Describe rows with QFXWidgets cfgs and keep the metadata that search and diagnostics need:

```lua
-- metadata (for search/jump and docs)
-- id = "chatbar.scale", desc = "Adjust the chat bar scale."

local row, h = W:DualRow(parent, y,
    { type = "label", text = L["Scale"] },
    { type = "slider",
      min = 0.7, max = 1.5, step = 0.05,
      getValue = function() return db.chatBar.scale end,
      setValue = function(value)
          db.chatBar.scale = value
          QFX.Modules.ChatBar:RequestApply("scale")
      end,
      tooltip = L["Adjust the chat bar scale."] })
```

The factory creates the control; the module handles meaning.

## Skin layer responsibilities

The QFXUI skin ships inside QFXWidgets; hosts do not own a skin layer.
- Override tokens globally with `W:SetSkin{...}` / `W:SetTheme{...}` when an addon truly needs a variation; restore with `W:SetSkin()`.
- Use `W:SkinFrame`, `W.Surface`, and `W:Border` for host window chrome instead of `SetBackdrop` or custom border code.
- Never restyle individual factory controls outside the skin, and never take ownership of business behavior.

Do not move alert logic, saved-list logic, drag/drop logic, cooldown logic, or module runtime logic into the skin tokens or the factory.

## Dialog grid constants

Complex dialogs should define layout constants first:
- Dialog width and height.
- Card/module widths.
- Column x positions.
- Label widths.
- Control widths.
- Row heights and gaps.

Use helpers such as `PlaceModule`, `PlaceControl`, and `CreateFieldLabel` instead of scattering magic coordinates.

## No duplicate architecture

Do not create a second:
- Database layer
- Localization table
- Module registry
- Widget factory or skin (embed QFXWidgets verbatim; do not fork it)
- Media resolver
- Event dispatcher
- Refresh queue
- Search registry

Extend the existing architecture unless a full rewrite is explicitly requested.
