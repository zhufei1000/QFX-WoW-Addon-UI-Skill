# UI Factory, Dialog, and Mode Rules

Use this reference when building or refactoring settings panels, popups, and editor dialogs.

## UI factory rules

Centralize repeated control creation:
- Buttons
- Checkboxes
- Dropdowns
- Sliders
- Input boxes
- Section headers
- Card frames
- Font and color helpers
- Tooltip helpers

Do not place addon business rules in the UI factory.

## Dialog rules

Dialogs must:
- Use consistent width and padding.
- Align labels and controls.
- Keep controls inside the card/module boundary.
- Clamp to screen where needed.
- Hide dropdowns and child popups when closing.
- Avoid rebuilding unsaved editor state during language changes.

## Dropdown popup rules

For long dropdowns:
- Prefer a singleton popup shared by all dropdown controls.
- Match popup width to the control width by default.
- Use a maximum visible row count.
- Add scrolling for overflow.
- Keep popup strata above normal dialogs.
- Close on outside click and parent dialog close.
- Reopen near the selected item when possible.

## Slider wrapper rules

For native sliders:
- Prefer native slider templates.
- If using `OptionsSliderTemplate`, hide or clear default `Text`, `Low`, and `High` labels.
- Use custom QFX min/current/max labels below the track.
- Update current value text immediately while dragging.
- Defer heavy refresh work until drag stop or next frame.

## Mode-specific controls

If the UI supports multiple display modes:
- Show controls only in the relevant mode.
- Hide irrelevant controls instead of leaving disabled clutter.
- Keep per-mode settings separate when behavior differs.
- When an item is disabled/hidden, remove it from related sorting lists if appropriate.
