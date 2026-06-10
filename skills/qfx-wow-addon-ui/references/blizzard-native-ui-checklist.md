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
