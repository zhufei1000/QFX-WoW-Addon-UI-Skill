# Refresh Performance Rules

Use this reference when UI changes cause lag, repeated rebuilds, or import/expand stutter.

## RequestRefresh pattern

Use `RequestRefresh(reason)` or an equivalent queue:

- If a refresh is already pending, merge the new reason.
- `full` overrides weaker reasons.
- Defer heavy refresh to the next frame when possible.
- Do not rebuild the entire panel for every small value change.

## Targeted refresh

Prefer targeted refresh for:
- Button enabled/disabled state.
- One row visual update.
- Slider value text.
- Dropdown display text.
- Selected row highlight.

Use full refresh only for:
- Data structure changes.
- Filter/sort changes.
- Locale-wide relayout.
- Missing or invalid cache.

## Sliders

While dragging:
- Update current value text immediately.
- Save or apply value as needed.
- Defer expensive relayout or full list refresh.

## Bulk import/export

During bulk import:
- Parse all data first.
- Apply changes in memory.
- Refresh once at the end.
- Avoid one full list rebuild per imported item.
