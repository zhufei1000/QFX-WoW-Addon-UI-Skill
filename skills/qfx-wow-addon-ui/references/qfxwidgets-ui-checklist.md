# QFXWidgets UI Checklist

Use this checklist when reviewing or refactoring QFX addon settings panels, option pages, editors, and dialogs.

## Factory control preference

Build every settings control with QFXWidgets (`references/qfxwidgets-factory.md`):

- Rows: `W:DualRow` with `toggle`, `slider`, `dropdown`, `segmented`, `button`, `buttonRow`, `color`, `colorMode`, `keybind`, `input`, or `label` cfgs.
- Helpers: `SectionHeader`, `Note`, `Spacer`, `WideButton`, `Tabs`, `TabPanel`, `CheckGrid`, `ColorGrid`, `SearchableDropdown`, `IconPicker`, `ListRows`, `ReorderList`, `Cog`, `ScrollPage`, `MultilineBox`, `Confirm`, `StatusRow`, `ResetRow`, `Slider`, `MakeMenu`.
- Keep the embedded `QFXWidgets.lua` copy verbatim; extend the factory itself when a control is missing instead of adding page-local widgets.

Avoid mixing QFXWidgets, Blizzard option templates, and AceGUI in the same panel. Legacy panels migrate row by row behind a flag, not by stacking two systems in one page.

## Visual consistency

Check:

- All controls of one type use the same cfg/helper across pages (no second button or dropdown style).
- Sizes and colors come from `W.Theme`/`W.Skin` tokens; nothing is hardcoded per row.
- Toggles, checkboxes, and pills show selected state with the accent/selected tokens, not a custom color.
- Sliders use the standard anatomy: track on the row, min/max under the ends, value box right, steppers flush right.
- Dropdown menu width matches the closed dropdown by default; long menus scroll and clamp to screen.
- Text uses `text` / `textMuted`; danger and success use their tokens; state is never color-only.
- Tooltips explain long content instead of crowding rows; disabled and combat-blocked controls show `disabledTooltip` / `combatTooltip`.

## Duplicate controls

Do not show multiple controls with the same effective function on the same page unless there is a clear usability reason.

Required behavior:

- Prefer one obvious primary control per action in a visible scope.
- If two controls reset or apply the same settings, keep the one closest to the setting group and remove the duplicate global/footer control.
- Footer buttons should be reserved for panel-level actions such as close, save, cancel, or truly global actions that are not already present in the page content.
- If a duplicate action is intentionally kept, the labels and tooltips must make the scope different, for example `Reset position` versus `Reset all alert text`.
- Avoid ambiguous pairs such as `Reset Default` and `Reset All` when users can reasonably interpret them as the same action.
- Removing a duplicate button should not change SavedVariables or the underlying behavior of the remaining control.

## Color selectors

Use `W:ColorSwatch`, the `color` / `colorMode` row cfgs, or `W:ColorGrid` instead of a labeled color button.

Required behavior:

- The visible control is the color itself in a small frame; no `Color` / `颜色` text inside the swatch.
- `alpha = true` adds the alpha channel to the picker; `colorMode` shows the swatch only while the mode is `customKey`.
- Hover shows the `borderHi` outline (the factory default); the swatch updates immediately after pick, cancel, or reset.
- Swatch sizes: 22px in rows, 20px in `colorMode`, 16px in grids.
- A reset path exists (`colorMode` reset button or `ResetRow`), not a right-click secret.

## Dropdowns and menus

Long dropdowns must:

- Use `W:SearchableDropdown` (or `W:MakeMenu`) once the list stops fitting — no custom popup code.
- Clamp to screen, sit on `FULLSCREEN_DIALOG` level 200, and limit visible rows with scroll for the rest.
- Re-read items on every open (pass a function when they change), and close on outside click/Esc.
- Show clear hover and selected/checked states; group headings where the list is categorized.
- Offer a per-row action (preview/test/remove) through `items[n].action` instead of a second column of buttons.

## Sliders

QFX slider standard:

```text
[ Label                ][ ===== slider ===== ][ 42 ][+]
                         min               max     [-]
```

- Use row sliders for compact pages and `W:Slider` for long labels; never build a custom slider.
- Dragging commits once on release; steppers nudge one clamped step; `steppers = false` drops the column.
- Esc reverts the value box, Enter commits, and formatting follows `step`/`valueSuffix`.

## Confirmations and destructive actions

- Use `W:Confirm` for destructive or irreversible actions with `danger = true`.
- Provide verb-labeled accept text (`Delete`, `Reset`) and localized cancel text; Esc and backdrop cancel.
- Never stack confirms, and never apply a destructive change before the confirm callback.

## Do not over-skin

Do not add per-panel textures, gradients, shadows, animations, or custom borders. QFXUI is flat by design; visual variation comes only from global `W:SetSkin`/`W:SetTheme` tokens.
