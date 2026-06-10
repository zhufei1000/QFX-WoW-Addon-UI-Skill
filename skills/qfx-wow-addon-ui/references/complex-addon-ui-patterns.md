# Complex Addon UI Patterns

These patterns are reusable for complex World of Warcraft addon configuration UIs. They were extracted from real MCDVoiceCooldown UI work, but they are not MCD-specific.

Use this reference for addons with saved entries, collections, drag-and-drop sorting, sound/TTS pickers, long dropdowns, import/export panels, or language-switchable editor dialogs.

## 1. Lightweight Skin layer

A Skin layer may normalize the look of native controls, but it must not become a business-logic layer.

Rules:
- Keep business logic in modules/controllers.
- Keep widget creation in UIFactory or layout helpers.
- Keep Skin focused on fonts, borders, highlight textures, checkbox/button/dropdown visual normalization, and Blizzard-native compatibility.
- Do not forcefully redraw every control if Blizzard templates are already good enough.
- Allow external skins such as ElvUI/NDui to skin native controls naturally when the addon does not own those frames.

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

## 9. Native slider wrapper

For QFX sliders:
- Prefer native slider templates.
- If using `OptionsSliderTemplate`, hide or clear the template's default `Low`, `High`, and `Text` labels.
- Create min/current/max labels through the UI factory or layout helper.
- Put min under the left end, max under the right end, and current value centered under the track.
- Use one helper to enable/disable slider labels and update disabled colors.

## 10. Editor dialog grid constants

Complex editor dialogs should define layout constants first.

Rules:
- Define columns, row height, gaps, label widths, control widths, and module/card bounds in one place.
- Use layout helpers such as `PlaceModule`, `PlaceControl`, and `CreateFieldLabel`.
- Do not scatter magic coordinates in business logic files.
- Three-column rows such as ID / Name / Cooldown must use named constants.
