# Complex Addon UI Patterns

These patterns are reusable for complex World of Warcraft addon configuration UIs. They were extracted from real MCDVoiceCooldown UI work, but they are not MCD-specific.

Use this reference for addons with saved entries, collections, drag-and-drop sorting, sound/TTS pickers, long dropdowns, import/export panels, or language-switchable editor dialogs.

## 1. Factory and skin boundaries

QFXWidgets owns settings-control creation and the QFXUI look; hosts own logic.

Rules:
- Keep business logic in modules/controllers.
- Keep widget creation in QFXWidgets (`W:DualRow` and the documented helpers), not in page files.
- Skin tokens belong to `W.Skin`/`W.Theme`; override globally with `W:SetSkin`/`W:SetTheme` only when an addon needs a variation.
- Do not redraw factory controls per addon, and do not mix Blizzard templates or AceGUI into a QFXUI panel.
- Host windows use `W:SkinFrame`, `W:Surface`, and `W:Border`; external skins such as ElvUI/NDui are not expected to skin QFXUI controls.

## 2. Singleton scrollable dropdown popup

Complex addons often need dropdowns with many entries, especially sound/media lists.

Prefer one shared dropdown popup instead of one popup frame per dropdown.

Rules:
- All dropdown controls reuse the same popup frame.
- Popup width should match the dropdown control by default.
- Popup must be clamped to screen.
- Popup frame strata must be above ordinary dialogs.
- The parent dialog must hide child popups when it closes.
- Use a blocker or outside-click handler to close the popup.
- Long lists must show a maximum of about 8-10 visible rows and scroll the rest.
- Reopening a dropdown should position the current selected option near the visible middle when possible.
- Hover state and selected/check state must be clear.

## 3. Large list responsibility split

Do not put building, rendering, selection, drag/drop, and refresh in one giant file.

Recommended split:
- `Builder`: generates visible row data from saved settings.
- `Renderer`: controls overall list rendering.
- `RowFactory`: creates and reuses row frames.
- `RowRenderer`: updates one row's visual state.
- `Selection`: stores selected key/type independently from row frame lifetime.
- `DragDrop`: manages drag start, drag ghost, and drop execution.
- `DropTarget`: computes valid drop targets.
- `Geometry`: mouse-position and row-boundary math.
- `Refresh`: coalesces refresh requests.

## 4. Batched refresh

Complex UI should use `RequestRefresh(reason)` or an equivalent pending queue.

Rules:
- If a refresh is already pending, do not immediately refresh again.
- Merge repeated `list`, `buttons`, `locale`, or `layout` requests.
- Let `full` refresh override weaker reasons.
- Defer heavy UI work to the next frame when possible.
- Sliders may update text immediately while deferring expensive layout or database refresh.
- Import/export and bulk changes must not call full rebuild for every item.

## 5. Collection expand/collapse

For saved collections or grouped lists:
- Expanding one collection should update only the affected cached area when possible.
- Collapsing one collection should remove only its child rows from the visible row cache.
- Full rebuild is allowed only when cache is missing, filters changed, sort order changed, or the underlying saved data changed structurally.
- Empty collections must still be selectable if edit/delete applies to the collection itself.

## 6. Stable drag/drop identity

Drag logic must not rely only on current row frame references.

Record stable values at drag start:
- `sourceKey`
- `sourceType`
- `sourceGroup`
- optional `sourceIndex`

Drop targets should use stable values too:
- `dropKey`
- `dropType`
- `dropGroup`
- `dropMode` such as before/after/inside/root

Do not destroy the source identity during a full list refresh. If a refresh cannot be avoided, preserve the drag ghost and source identity until the drop ends or is cancelled.

## 7. Language-safe editor refresh

Language switching must not wipe unsaved user work.

Rules:
- Refresh labels, tooltips, dropdown display text, button text, and title text.
- Recalculate button widths after locale changes.
- Do not recreate the whole editor unless unavoidable.
- Do not clear draft text, file paths, import/export content, selected sound, TTS custom text, or unsaved cooldown fields.
- Prefer `RefreshLocale()` on open dialogs.

## 8. Toolbar width auto-fit

Toolbar buttons must handle English/zhCN/zhTW text.

Rules:
- Use a minimum button width.
- Measure current localized text and add padding.
- Re-run layout on `OnShow` and after language changes.
- Avoid hardcoding widths based only on Chinese text.

## 9. Slider rows

For QFX sliders, use the QFXWidgets row slider (`{ type = "slider" }`) or full-width `W:Slider`:
- Track on the row; min under the left end and max under the right end (10px muted), value box (44px) at the right edge, `+`/`-` steppers flush right of the box.
- Dragging commits once on release and refreshes the page once; steppers nudge one clamped step and dim at the ends; `steppers = false` drops the column.
- Value formatting follows `step` (one decimal, or two below 0.1) with optional `valueSuffix`; Esc in the value box reverts, Enter commits.
- For media sliders with previews, pair the slider with a `StatusRow` or `SearchableDropdown` action instead of a second value display.

## 10. Editor dialog grid constants

Complex editor dialogs should define layout constants first.

Rules:
- Define columns, row height, gaps, label widths, control widths, and module/card bounds in one place.
- Use layout helpers such as `PlaceModule`, `PlaceControl`, and `CreateFieldLabel`.
- Do not scatter magic coordinates in business logic files.
- Three-column rows such as ID / Name / Cooldown must use named constants.

## 11. QFXWidgets boundaries and dialog rules

QFXWidgets centralizes control creation: toggles, sliders, dropdowns, segmented pills, inputs, keybinds, colors, section headers, notes, grids, tabs, lists, scroll pages, menus, and confirms. Do not place addon business rules in the factory; `getValue`/`setValue` closures call module APIs and the factory only builds UI.

Dialogs must:
- Use `W:Confirm` for confirmations and `W:MakeMenu`/`W:SearchableDropdown` for pickers instead of custom popups.
- Use consistent width and padding, aligned labels and controls.
- Keep controls inside the module boundary.
- Clamp to screen where needed.
- Close menus, dropdowns, and cog popups when the dialog closes or the outside is clicked.
- Avoid rebuilding unsaved editor state during language changes; refresh labels through `W:Refresh(owner)` instead.

## 12. Mode-specific controls

If the UI supports multiple display modes:
- Show controls only in the relevant mode.
- Hide irrelevant controls instead of leaving disabled clutter.
- Keep per-mode settings separate when behavior differs.
- When an item is disabled/hidden, remove it from related sorting lists if appropriate.

## 13. Combat lockdown deferred apply

Use this when a setting may affect protected frames or combat-sensitive behavior.

When a setting is changed:

1. Save the setting immediately.
2. If not in combat, apply it immediately.
3. If in combat, mark apply pending and apply after `PLAYER_REGEN_ENABLED`.

Do not:
- Mutate protected frames in combat.
- Rebuild protected frame layouts during combat.
- Spam chat for every deferred setting change.
- Lose the user's setting just because apply is delayed.

Good feedback is one small status line such as `This change will apply after combat.` Avoid repeated warnings.

Test: change the setting out of combat; change it in combat; leave combat and verify the pending apply happens once; reload after a deferred setting and verify the saved state remains correct.
