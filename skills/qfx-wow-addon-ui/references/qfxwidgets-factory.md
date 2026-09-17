# QFXWidgets Factory Standard

QFXWidgets is the single settings-control factory for QFX addons. When a task involves addon settings rows, option pages, editors, pickers, or dialogs, build them with QFXWidgets instead of a local `UIFactory.lua`, Blizzard option templates, or AceGUI.

This file is the factory contract. If it disagrees with a host addon's older widget code, QFXWidgets wins; migrate the host.

The factory source of truth is `QFXWidgets.lua` (one file, kept in the QFXWidgets addon folder and embedded in consumer Config addons). Re-read that file before changing a host, and update this reference when its `VERSION` changes.

## 1. What it is

- One drop-in file, `QFXWidgets.lua`, global `QFXWidgets` plus `ns.QFXWidgets`.
- Pure library: no SavedVariables, no events, no permanent `OnUpdate`. It only builds frames. All state lives in the host's `getValue` / `setValue` closures.
- One custom-drawn renderer (the QFXUI blue/navy skin). Every control is drawn with solid color textures. Blizzard assets are used only for `ColorPickerFrame` and the options gear glyph; the dropdown arrow is the drawn white V and the rounded-control art (switch capsule, circle knob, slider thumb) ships in `QFXWidgets\Media\` with drawn fallbacks.
- Rounded-control media ships in two formats: the `.blp` twins are the default and carry 2x resolution plus a pre-baked mip chain sampled with `TRILINEAR`, so the capsule/knob/thumb stay crisp at fractional UI scales; the PNG twins of the same names are the explicit fallback (`W:SetMediaFormat("png")`) and for hosts that ship only the PNG art.
- When the media is unavailable (the library addon is not installed and nothing else ships it), the factory falls back to white textures masked with Blizzard's portrait alpha mask: correct but visibly rougher at compact sizes, so ship or require the media wherever the QFXUI skin matters.
- Version-guarded singleton: the file keeps a `VERSION` number and reuses a newer already-loaded copy, so embedding it in several addons never duplicates tables or frames.
- No AceGUI, no external libraries, no external media required.

## 2. Loading and integration

- Copy `QFXWidgets.lua` into the addon (or its Config sub-addon, for example `QFXSystemBar_Config\QFXWidgets.lua`), add it to the `.toc` before the page files, and keep the copy verbatim.
- A standalone `QFXWidgets` addon may provide it instead; the embedded-copy pattern must still work when that addon is absent.
- In a core addon plus load-on-demand Config host, prefer lazy loading over putting the factory in the core `.toc` (see "Lazy factory loading" below).
- Hosts may keep a legacy UI during migration and switch rows over in phases:

```lua
local addonName, ns = ...
local W = _G.QFXWidgets
local USE_QFX = type(W) == "table" and type(W.DualRow) == "function" and ns.useQFXWidgets ~= false
```

- Missing factory must degrade gracefully (print a reinstall hint or fall back), never error at load.
- The factory builds into any parent frame; runtime modules must not depend on a settings page being open.

### Lazy factory loading (core addon + load-on-demand Config)

The factory is startup weight: a verbatim copy is a few hundred KB of loaded code, and most sessions never open a dialog or a settings page. Keep it out of the core addon's startup path:

- Put `QFXWidgets.lua` first in the **Config** (load-on-demand) `.toc`, not in the core addon's `.toc`. The core addon keeps only the global reference, which may be nil at load time: `local W = rawget(_G, "QFXWidgets")`.
- Resolve the factory at use time, never at load time. Call this right before building any dialog or page and degrade gracefully when it fails:

```lua
local function EnsureDialogWidgets()
    W = rawget(_G, "QFXWidgets") or ns.QFXWidgets
    if W then return true end
    if not ns.EnsureConfigLoaded() then return false end   -- LoadAddOn("..._Config")
    W = rawget(_G, "QFXWidgets") or ns.QFXWidgets
    return W ~= nil
end
```

- A standalone `QFXWidgets` addon, when installed and enabled, is found by `rawget` and nothing extra loads at startup; when it is absent or disabled, loading the Config child supplies the embedded copy. The version guard makes the embedded copy a no-op when the standalone one already loaded, so the worst case is one extra file compile.
- Configure skin and media at the layer that actually loaded the factory (the Config addon's factory bootstrap), applied to whichever copy won (`_G.QFXWidgets or ns.QFXWidgets`). The core addon must not call `W:SetMediaFormat` / `W:SetBrand` at startup.
- Core dialogs that would otherwise force the factory early (first-run wizard, module notices) should run on a short post-login delay, so a standalone factory addon has already loaded and the Config child stays unloaded for players who never open settings.
- Only the first dialog or settings open pays the load cost; every later open reuses the loaded Config. Runtime modules must never require the factory (they stay independent of the settings UI).

## 3. Standard page build

```lua
local page = W:ScrollPage(rightPanel)          -- parent must already be sized
local content = page.content
W:BeginPage(content)                           -- drops this page's old refresh callbacks
W:ResetRows(content)                           -- restart zebra stripes
local y = -W.Theme.pad
local row, h = W:SectionHeader(content, L["GENERAL"], y); y = y - h
row, h = W:DualRow(content, y,
    { type = "toggle", text = L["Enable"], getValue = ..., setValue = ... },
    { type = "slider", text = L["Size"], min = 10, max = 40, step = 1,
      getValue = ..., setValue = ... })
y = y - h
y = W:Note(content, y, L["Some hint text."])
row, h = W:WideButton(content, L["Open Full Settings"], y, onClick); y = y - h
W:EndPage()
page:SetContentHeight(-y + W.Theme.pad)
```

- On page refresh or reopen call `W:Refresh(owner)` (or `W:Refresh()`); callbacks re-read every `getValue` and re-apply disabled states.
- `W:Refresh()` errors are counted in `W.lastRefreshError` instead of being swallowed.
- Call `W:Refresh()` on `PLAYER_REGEN_ENABLED` so combat-blocked controls come back.

### Window chrome

- `W:SkinFrame(frame, opts)`, `W:Perimeter(frame, opts)` (the warm-into-accent gradient frame border: warm at the top-left, accent blue body, warm return in the bottom-right corner; re-fits on resize; `opacity = 0.72` for inner panels), `W:CloseButton(parent, opts)`, `W:Border`, `W:Surface` draw host windows; never `SetBackdrop` for QFXUI panels.
- `W:Banner(frame, opts)` is the brand header for a host main window: a left logo plus an optional faded right watermark and glow. It draws on the **host frame's own layers** (watermark on `BACKGROUND` sub 2, logo/glow on `ARTWORK` sub 1) so the host's `OVERLAY` labels and buttons stay on top, and it re-lays out on the host's `OnSizeChanged`, so the art always fits the header area the host reserves. Options: `height`, `logo` / `logoSize` / `logoX` / `logoY` / `logoGap`, `watermark` / `watermarkFit` (`"right"` height-driven mark, `"width"` edge-to-edge strip) / `watermarkHeight` / `watermarkRatio` / `watermarkX` / `watermarkY` / `watermarkTint` / `watermarkFade`, `glow` / `glowSize` / `glowX` / `glowY` / `glowTint` / `glowBlend`. Use `banner.textLeft` for the title x so the logo is never covered, and `banner:SetWatermarkTint(color)` for a theme-driven mark.
- One brand for every QFX addon: `W:SetBrand{ logo = path, watermark = path, watermarkTint, watermarkFit, glow }` declares the shared art once, and `W:Banner` inherits whatever the caller does not pass. Ship the brand art with the factory (`QFXWidgets\Media\`) so hosts only pass `height`.
- The watermark fade uses `SetGradient` over the art, so the same rule applies as for the section bar: a base colour/vertex colour must exist first or the fade shows nothing.

## 4. Theme and skin (the QFX visual standard)

`W.Theme` (layout tokens, overridable with `W:SetTheme(t)`):

| Token | Value | Use |
|---|---|---|
| `rowH` | 32 | compact option row |
| `sliderRowH` | 38 | slider rows only when `cfg.labelsBelow` stacks the min/max under the track |
| `wideButtonH` | 34 | full-width buttons |
| `headerH` / `sectionBarH` | 28 / 24 | fallback header row (bar disabled) / gradient title bar |
| `labelSize` / `sectionSize` / `noteSize` | 12 / 14 / 12 | row labels / section title / description |
| `pad` / `sidePad` / `rightPad` | 10 / 10 / 16 | content insets |
| `labelGap` | 8 | label-to-control gap |
| `trackWidth` | 110 | default slider track |
| `controlH` | 20 | compact control height |
| `rowBgOdd` / `rowBgEven` | 7% / 1.8% alpha washes | zebra stripes |

`W.Skin` (QFXUI tokens; override with `W:SetSkin{...}` which merges over the stock skin, `W:SetSkin()` restores):

- accent `#4a9cfa` (0.290, 0.610, 0.980); `controlBg` dark blue fill, `controlBgHi` hover; `border` / `borderHi` steel-blue frame; `trackBg` / `trackFill` / `knob`; `selectedFill` / `selectedLine` / `selectedText`; `danger` / `good`; `buttonBg` / `buttonBgHi` / `buttonBorder`; `text` / `textMuted`; `menuBg` / `rowHover`; `sectionText`; `line`; `warmAccent` / `warmAccentHi` (the orange used by the check mark, tab underline, logo arc and perimeter).
- Stock section title bars use the warm amber hand-off (`sectionBarFrom` 0.62/0.32/0.07, `sectionBarTo` 0.10/0.05/0.02, `sectionBarEdge` 0.86/0.52/0.16) and the zebra rows a raised blue wash (`rowBgOdd` 7% / `rowBgEven` 1.8%); both are plain skin tokens a host may override.
- The dropdown arrow defaults to the drawn white V (legible at the compact row height); `W:SetArrowTexture(path)` installs PNG art, `W:SetArrowTexture(false)` restores the V.
- Warm accents: the check-mark fill (`checkFill`) resolves to `warmAccent`, and the dropdown arrow (`arrowHi`) turns warm only while hovered. The toggle knob and slider thumb stay neutral (`toggleKnobOn/Off`, `thumb` / `knob`) because a permanently warm knob read as noisy in the compact QFXUI skin. All of these are `W:SetSkin{...}` overrides; a host wanting the blue mark sets `checkFill = S.accent`.
- Control sizes: toggle 40x20 (knob 16, 2px pad, 75ms slide, `toggleAnim = false` to disable), track height 4, thumb 16x16, value box 44 wide, row control height 20, button height 20 / min width 88, stepper column 18, segmented pill min width 38 + 16 text padding, menu row 20.
- Rounded shapes come from the media above and are never combined with a second mask; a mask path is only for clients without the art. Knobs and thumbs stay white/gray art tinted through `SetVertexColor`, so a skin change needs no new files.
- Host window chrome uses `W:SkinFrame(frame)`, `W.Surface`, and `W.Border`; never `SetBackdrop` for QFXUI panels.
- Do not restyle individual controls outside the skin, and never mix QFXWidgets with Blizzard templates or AceGUI in the same settings panel.

## 5. Option rows — `W:DualRow(parent, y, leftCfg, rightCfg)`

Returns `frame, height`. One row has a left label column and an optional right slot; a slider in either slot raises the row to `sliderRowH`. `cfg` types:

| `type` | Fields |
|---|---|
| `label` | `text` |
| `toggle` | `text`, `getValue`, `setValue`, `tooltip` |
| `slider` | `text`, `min`, `max`, `step`, `getValue`, `setValue`, `trackWidth`, `valueSuffix`, `steppers` (off by default: the value box takes direct input; `steppers = true` adds the `+`/`-` column only where click nudging is needed), `stepperWidth`, `tooltip` |
| `dropdown` | `text`, `values`, `order`, `getValue`, `setValue`, `width`, `menuWidth`, `tooltip` |
| `segmented` | `text`, `values`, `order`, `getValue`, `setValue`, `minWidth`, `onSelect`, `tooltip` |
| `button` | `text`, `onClick`, `width` |
| `buttonRow` | `gap`, `buttons = { { text, onClick, width, tooltip, disabled, disabledTooltip }, ... }` (right-aligned cluster) |
| `color` | `text`, `getValue -> r,g,b[,a]`, `setValue`, `alpha = true`, `tooltip` |
| `colorMode` | `text`, `modes`, `order`, `customKey`, `getMode`, `setMode`, `getColor`, `setColor`, `defaultColor`, `defaultMode`, `alpha`, `resetTooltip` |
| `keybind` | `text`, `getValue`, `setValue`, `width`, `noneText`, `captureText`, `conflicts(key) -> name`, `clearOnRightClick` |
| `input` | `text`, `getValue`, `setValue`, `width`, `numeric`, `tooltip` |

All cfgs also accept `disabled = function() return true end`, `disabledTooltip` (string or function), and `blockInCombat` / `combatTooltip`.

Standalone helpers return raw controls:

- `W:CheckboxDropdown(parent, width, frameLevel, items, getFn, setFn, opts)` — multi-select summary dropdown; `items = { { key, label, tooltip }, ... }`; `opts.summaryFn`, `opts.noneText`.
- `W:ColorSwatch(parent, frameLevel, getFn, setFn, opts)` — returns swatch and update function.
- `W:Segmented(parent, frameLevel, values, order, getValue, setValue, opts)` — returns `region, refresh, firstButton`; caller anchors the region.

## 6. Extra controls

- `W:SectionHeader(parent, text, y, opts)` / `W:Note(parent, y, text, opts)` / `W:Spacer(parent, y, height)` — returns `frame, height` (Note returns `y, frame`); SectionHeader restarts zebra stripes.
- `SectionHeader` draws a gradient title bar (the stock warm-amber hand-off fading into the panel, 2px bright edge, `opts.bar = false` for the old plain row) with the 14px title anchored to the bar so it stays vertically centred, and `opts.note` (string or list) renders the description inside the same block; the divider then lands below every description line with `lineGap`. Other opts: `barHeight` / `height`, `from` / `to`, `size`, `noteSize`, `noteGap`, `line`, `lineGap`.
- A page hint that answers "how do I operate this control" is a **caption**: place it with `W:Note` directly *below* the control it explains (strip, list, grid). Section-level descriptions belong in `SectionHeader{ note = ... }` above the divider. Never place a caption above the control or a description below the divider.
- A late-arriving section description folds into its section with `local hdr, flowY = W:LastSectionHeader(parent)` then `if hdr and math.abs(flowY - y) < 0.5 then y = y - hdr:AddNote(text) end`.
- The divider marks the end of the section header block: title bar, all description lines, then the rule, then the controls of that section.
- `W:WideButton(parent, text, y, onClick, opts)` — full-width button row.
- `W:Tabs(parent, y, items, getActive, onSelect, opts)` — text tabs with an underline; `items = { { key, label }, ... }`.
- `W:NavList(parent, opts)` — the vertical sidebar standard, one control with two named modes:
  - **fixed** (`mode = "fixed"`, the QFXSystemBar standard): every item is a top row, clicking selects the page; no groups, no indicators.
  - **expandable** (default, the QFXToolBox standard): a group row carries a `+` / `-` expand indicator and toggles its children; children render as sub-tabs — no frame, the factory zebra wash carries the row (renumbered on every re-layout) and the active one gets a `W:Tabs`-style underline.
  In both modes top/group rows are chrome buttons (Surface + Border + sheen; the active row keeps the warm orange, hover stays electric blue). `opts = { mode, x, y, width, rowH, childH, indent, gap, expanded, getActive, onSelect(key), onToggle(key, expanded), items }`; items are `{ key, label, group = true }` for groups and `{ key, label, parent = groupKey }` for children. API: `nav:SetItems(items)`, `nav:SetExpanded(key | nil)`, `nav:GetExpanded()`, `nav:Toggle(key)`, `nav:Refresh()`, `nav.buttons[key]`.
- `W:TabPanel(parent, y, opts)` — tabs plus per-tab content built once then shown/hidden; `tabs = { { key, label, build(content, key) -> height }, ... }`; returns `frame, height, api` with `api.Show(key)`, `api.GetContent(key)`, `api.Refresh()`.
- `W:CheckGrid(parent, y, columns, entries, opts)` — checkbox grid; `entries` may carry `group`, `icon`, `help`; `opts.maxSelected` (number or function) dims and blocks extras with `opts.limitTooltip`; returns `frame, height` and `frame.Count()`.
- `W:ColorGrid(parent, y, columns, entries, opts)` — per-cell color swatches.
- `W:SearchableDropdown(parent, width, frameLevel, items, getValue, setValue, opts)` — search box, groups, optional per-row action button (`items[n].action = { text | icon, tooltip, onClick(key) }`), items re-read on every open (table or function); Enter picks the first match; returns `dd, refresh`.
- `W:IconPicker(parent, frameLevel, getValue, setValue, opts)` — icon button plus searchable menu; combine with `W:SpellIconItems({ id | { id, label }, ... })`.
- `W:ListRows(parent, y, opts)` — data-driven rows; `items` (table or function), `rowH`, `columns`, `header`, `rowBuilder(row, item, index, api)` runs once per row frame, `rowUpdate(row, item, index, api)` runs per `api.Render()`; `api.GetRow`, `api.GetCount`, `api.ColumnX`, `api.ColumnW`.
- `W:ReorderList(parent, y, opts)` — drag-to-reorder rows with the shared QFX drag language (3px pickup threshold, orange insertion line, cursor ghost, locked rows cannot be picked up). Rows may carry an icon (with `coords`), a `sub` label and an inline `edit = { getValue, setValue }` box: `items = { { key, label, sub, icon, coords, locked, tooltip, edit }, ... }`, `onChange(keys)`, `rowH`, `gap`, `editWidth`, `disabled`. Returns `frame, height, api` (`api.Render()` re-reads items). Used by the Chat Bar button order and the Raid Marker Panel button order.
- `W:Cog(anchor, opts)` — gear button plus popup settings; `opts.rows` are DualRow left cfgs, optional `onReset`, `title`, `width`; returns `cog, openFn`.
- `W:ScrollPage(parent, opts)` — self-drawn scrollbar (wheel plus thumb drag); `opts = { width, height, point, relPoint, x, y, barWidth, scrollStep, reserveBar, onScroll }`; returns `page` with `frame`, `content`, `viewport`, `scrollBar`, `thumb`, `ScrollTo`, `GetOffset`, `GetMaxOffset`, `SetContentHeight`, `Refresh`.
- `W:MultilineBox(parent, y, cfg)` — import/export and long text; `label`, `hint`, `height`, `rows`, `getValue`, `setValue`, `readOnly`, `maxLetters`, `commitOnEnter`, `onCommit`; `frame:GetText/SetText/Commit`.
- `W:Confirm(opts | text)` — modal confirm dialog; `title`, `text`, `acceptText`, `cancelText`, `onAccept`, `onCancel`, `width`, `danger = true`; Esc or backdrop cancels.
- `W:StatusRow(parent, y, opts)` — dynamic label plus value line; `label`, `getText`, `color`, `wrap`; `frame:Update()` forces one refresh.
- `W:ResetRow(parent, y, opts)` — right-aligned reset buttons; per-button `confirm = true` routes through `W:Confirm`.
- `W:Slider(parent, y, cfg)` — full-width slider (label above the track) for long labels; same cfg as the row slider plus `label`, `height`.
- `W:MakeMenu(anchor, spec)` — custom menu for pickers the factory does not cover; `spec = { items (table | function), width, maxH, maxVisible, multi, dynamic, checked(key), disabled(key), disabledTooltip(key), labelFor(key), onPick(key), refresh() }`; `anchor._invalidateMenu()` rebuilds rows with `spec.dynamic`.
- Media helpers: `W:LSM()`, `W:MediaList(kind)`, `W:MediaValues(kind)`, `W:FetchMedia(kind, name)`, `W:PreviewSound(name, channel)`. Feed `MediaList` output straight into `SearchableDropdown` or `dropdown` values. Missing LibSharedMedia must return empty lists, never error.
- Bundled-art overrides: `W:SetCircleTexture(path | false)`, `W:SetPillTexture(path | false)`, `W:SetSliderThumbTexture(path | false)`, `W:SetArrowTexture(path | false)`, and `W:SetMediaFormat("png" | "blp")` for the switch capsule, knob circle, slider thumb, and dropdown arrow.

## 7. Refresh and page model

- `W:RegisterRefresh(fn)` registers a widget refresher; the factory does this automatically for its own controls.
- `W:BeginPage(owner)` drops that owner's old callbacks and scopes new ones; `W:EndPage()` closes the scope.
- `W:Refresh(owner)` refreshes one page's callbacks; `W:Refresh()` refreshes everything; `W:ClearRefreshes(owner)` clears one owner or all.
- Rebuilds of a page use BeginPage/EndPage instead of firing `ClearRefreshes` by hand.

## 8. Combat and disabled model

- `disabled()` dims the control to 0.35 alpha and blocks mouse input; `disabledTooltip` explains why on hover.
- `blockInCombat = true` makes a control read-only during lockdown; `combatTooltip` overrides the default reason. The host calls `W:Refresh()` on `PLAYER_REGEN_ENABLED`.
- `W:IsCombatLocked()` / `W:InCombatLocked()` expose the state; `W:IsDisabled(cfg)` reports explicit or combat disablement.
- Never mutate protected frames from the factory; settings that touch them follow the combat deferred-apply rules in `complex-addon-ui-patterns.md`.

## 9. Behavior standards

- English-first labels live in the left column; controls are right-anchored. Long labels ellipsize with `...` (the clamp retries one frame later if the row was not sized yet) and show the full text plus tooltip on hover. Never shrink fonts to fix overflow.
- Sliders: track on the row, min/max labels beside the track ends sharing its vertical centre (so a slider row keeps the normal `rowH`), value box at the right edge. The `+`/`-` stepper column is off by default (the value box takes direct input; the standard dropped the redundant nudgers); `steppers = true` adds it flush right of the box, clamped and dimmed at the ends. `cfg.labelsBelow = true` restores the older stacked layout and the taller `sliderRowH` row. Dragging commits the value once on release and refreshes the page once; typing commits on Enter or focus loss; Esc reverts.
- Segmented pills: 2-4 mutually exclusive options, measured from label text, active pill uses the selected fill.
- Menus and dropdowns sit on `FULLSCREEN_DIALOG` level 200 with a full-screen click catcher; long lists scroll with a self-drawn bar; the menu matches the dropdown's scale.
- Scroll pages preserve offset across tabs/rebuilds; call `page:ScrollTo(0)` when a page switch should start at the top.
- Confirmation dialogs are non-stacking modals (`W:Confirm`), Esc cancels, destructive actions use the red accept button.
- Secret values (WoW 12.x): measured text uses `W.IsSecret` / `W.TruncateToFit` guards; never compare, store, serialize, or do arithmetic on secret values. The factory skips measurement instead of erroring.

## 10. Engineering rules

- One factory. Do not create a second `UIFactory.lua`, a parallel skin, or per-row custom controls. Extend QFXWidgets itself when a control is missing.
- Keep business rules out of the factory: `getValue`/`setValue` closures call the module's apply APIs; the factory never writes the DB directly.
- Embed the factory file verbatim and keep its `VERSION` bump discipline; when updating the factory, bump `VERSION` and re-check hosts.
- Do not fork the skin per addon; override tokens through `SetSkin`/`SetTheme` only.
- Migration order: keep the legacy UI behind a flag, migrate generic option rows first, then custom editors (grids, pickers, lists), then dialogs.

## 11. Review checklist

- Is every settings control drawn by QFXWidgets (no leftover AceGUI, Blizzard templates, or hand-drawn twins in the same panel)?
- Are rows built with `DualRow` and registered refreshers instead of rebuilt per change?
- Is `BeginPage`/`EndPage` used around page rebuilds, and `Refresh(owner)` on value changes and `PLAYER_REGEN_ENABLED`?
- Do sliders use the standard anatomy and commit-on-release behavior?
- Do long labels clamp with a hover tooltip in EN/zhCN/zhTW instead of clipping or wrapping?
- Are destructive actions routed through `W:Confirm`, and combat-blocked controls through `blockInCombat` + `combatTooltip`?
- Is the factory copy unmodified except for its `VERSION` when a real factory update is intended?
- Are the rounded controls rendering from the bundled media (library addon installed or media shipped) instead of the mask fallback, and is the loaded factory copy the highest `VERSION`?
