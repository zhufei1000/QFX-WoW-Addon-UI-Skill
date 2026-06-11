# Blizzard Native UI Checklist

Use this checklist when reviewing or refactoring World of Warcraft addon settings panels.

## Native control preference

Prefer Blizzard-native controls and templates:
- `UIPanelButtonTemplate`
- `UICheckButtonTemplate`
- `OptionsSliderTemplate` or equivalent native slider
- `InputBoxTemplate`
- `BackdropTemplateMixin`
- Blizzard dropdown behavior or a local wrapper that visually matches it

Avoid mixing native controls, AceGUI controls, and custom self-drawn controls in the same panel unless the addon already uses that system and the user requests preservation.

## Visual consistency

Check:
- Buttons have consistent height, padding, hover, disabled, and pushed states.
- Checkboxes use the same template and alignment.
- Sliders use the QFX min/current/max value layout.
- Dropdown popup width matches the closed dropdown width unless there is a clear reason.
- Text colors follow enabled/disabled state.
- Tooltips are used for long explanations instead of crowding the layout.

## Color selectors

For color picker controls, use a compact textless swatch instead of a normal labeled button.

Required behavior:
- The visible control should be the selected color itself, inside a small bordered frame.
- Do not put `Color`, `颜色`, or other label text inside the color swatch.
- Put any explanation in the row label, section hint, or tooltip/help text.
- Left-click should open the color picker.
- Right-click may reset to default only when the UI clearly documents that behavior.
- Update the swatch color immediately after pick, cancel/restore, or reset.
- Keep the control compact enough for multilingual rows, usually around 24-32 px wide and one row high.
- Preserve hover/pressed feedback with border or highlight changes so the swatch still feels clickable.
- Centralize swatch creation in the local UI factory/helper when more than one color selector exists.

Avoid:
- A full `UIPanelButtonTemplate` labeled `Color`/`颜色` beside every row.
- Separate text labels inside the swatch frame.
- Recreating multiple color picker implementations in the same addon.
- Changing unrelated layout or SavedVariables when replacing a labeled color button with a swatch.

## Dropdowns

Long dropdowns must:
- Clamp to screen.
- Stay above dialogs.
- Limit visible row count.
- Scroll for additional items.
- Show clear hover and selected states.
- Close when the parent dialog closes.

## Sliders

QFX slider standard:

```text
[ Label                ][ ======= slider ======= ]
                         min      current     max
```

If `OptionsSliderTemplate` is used, hide or clear built-in `Low`, `High`, and `Text` labels and use the unified QFX labels instead.

## Do not over-skin

A native-looking addon should not become a web-style interface. Keep frames, controls, spacing, and behavior close to Blizzard settings panels unless the user asks for a different style.
