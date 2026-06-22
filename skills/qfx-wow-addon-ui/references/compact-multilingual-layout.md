# Compact Multilingual Layout

Use this reference for QFX addon panels that support English, Simplified Chinese, and Traditional Chinese.

## Primary rule: English-first layout baseline

Design addon UI layout from English text first.

English labels, button text, dropdown values, section titles, and descriptions are usually longer than Simplified Chinese and Traditional Chinese. If a layout is sized safely for English with padding, the Chinese UI will usually fit without overflow. If a layout is designed around Chinese first, the English version often clips, wraps badly, or forces later layout changes.

Therefore:
- Treat English as the base layout language.
- Size labels, buttons, dropdowns, tabs, column widths, and card widths against the English strings first.
- Then verify Simplified Chinese and Traditional Chinese.
- Do not design a tight Chinese layout and translate it to English afterward.
- Do not solve English overflow by shrinking fonts below the QFX standard unless there is no better layout option.
- If English does not fit, fix the layout structure: wider control, full-width row, shorter label, tooltip description, or fewer columns.

## Layout workflow

Use this workflow for QFX settings panels:

1. Write or inspect the English strings first.
2. Build the row width, label width, control width, and button width for the English text.
3. Add safe horizontal padding.
4. Check Chinese and Traditional Chinese after the English layout passes.
5. If Chinese still overflows, fix that specific text or row without shrinking the whole design.
6. Re-check after runtime language switching.

## General rules

- Use the full available panel width instead of wasting horizontal space.
- Keep labels and controls vertically centered on the same row.
- Put long explanations in tooltips rather than inline text.
- Avoid tiny fixed-width controls that clip localized strings.
- Avoid two narrow columns when English labels or dropdown values are long.
- Prefer shorter visible labels plus tooltip explanations over long inline sentences.
- Avoid mixing one row designed for Chinese width with another row designed for English width.

## Label and control sizing

Rules:
- Label columns must be wide enough for the English label plus padding.
- Dropdown buttons must fit the longest common English option, not only the current default option.
- Slider rows should reserve enough room for English labels and bottom min/current/max values.
- Tab buttons should be measured from English tab labels first.
- Section headers may be English-long; use full-width headers and tooltips for detailed help.
- For cramped panels, use full-width rows before reducing font size.

## Button width

Toolbar and dialog buttons should:
- Have a safe minimum width.
- Measure the English text first.
- Measure the current localized text.
- Use the larger measured width plus horizontal padding.
- Re-layout after language changes and on show.

Recommended logic:

```lua
local function GetLocalizedButtonWidth(fontString, englishText, localizedText, minWidth, padding)
    fontString:SetText(englishText or "")
    local englishWidth = fontString:GetStringWidth() or 0
    fontString:SetText(localizedText or englishText or "")
    local localizedWidth = fontString:GetStringWidth() or 0
    return math.max(minWidth or 80, englishWidth, localizedWidth) + (padding or 28)
end
```

## Language switching

Runtime language switching must:
- Refresh labels, button text, dropdown display text, titles, and tooltips.
- Recalculate widths after text changes.
- Preserve unsaved editor drafts, import/export text, file paths, and selected values.
- Prefer `RefreshLocale()` over destroying and recreating the editor.
- Re-run English-width-sensitive layout checks where buttons, tabs, and dropdowns auto-size.

## Layout choices

Use two columns only when:
- Both columns have enough room for English.
- Dropdowns and sliders do not clip.
- Tooltip or help text is not forced into a cramped area.
- The row still looks balanced in Chinese.

Use full-width rows for:
- Long English labels.
- File paths.
- Import/export text.
- Search boxes.
- Large dropdowns.
- Sliders with bottom value labels.
- Explanatory warnings or semantic banners.
- Any control that would force English wrapping in a two-column layout.

## Review checklist

When reviewing a multilingual QFX UI, check:

- Was the row width designed from English first?
- Do English labels clip, wrap, or overlap controls?
- Do English dropdown values fit the closed dropdown button?
- Do English tab labels fit without cramped spacing?
- Are long explanations moved into tooltips?
- Does Chinese still look compact and not overly sparse?
- Does switching language recalculate widths without rebuilding the entire page unnecessarily?
- Are buttons sized from the larger of English and current localized text?
