# Compact Multilingual Layout

Use this reference for QFX addon panels that support English, Simplified Chinese, and Traditional Chinese.

## General rules

- Design for English first because it is usually wider than Chinese.
- Use the full available panel width instead of wasting horizontal space.
- Keep labels and controls vertically centered on the same row.
- Put long explanations in tooltips rather than inline text.
- Avoid tiny fixed-width controls that clip localized strings.

## Button width

Toolbar and dialog buttons should:
- Have a safe minimum width.
- Measure the current localized text.
- Add horizontal padding.
- Re-layout after language changes and on show.

## Language switching

Runtime language switching must:
- Refresh labels, button text, dropdown display text, titles, and tooltips.
- Recalculate widths after text changes.
- Preserve unsaved editor drafts, import/export text, file paths, and selected values.
- Prefer `RefreshLocale()` over destroying and recreating the editor.

## Layout choices

Use two columns only when:
- Both columns have enough room for English.
- Dropdowns and sliders do not clip.
- Tooltip or help text is not forced into a cramped area.

Use full-width rows for:
- Long labels.
- File paths.
- Import/export text.
- Search boxes.
- Large dropdowns.
- Sliders with bottom value labels.
