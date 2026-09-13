# Lists, Collections, Sound, and Media UI

Use this reference for saved voice lists, sound collections, addon/module lists, any UI with many rows, and any UI exposing font, texture, or LibSharedMedia options.

## Row reuse

Large lists should reuse row frames instead of recreating all rows every refresh.

Separate:

- Data building.
- Row creation.
- Row rendering.
- Selection state.
- Drag/drop state.
- Refresh scheduling.

## Collections

- Collection rows must remain selectable even when empty if edit/delete applies to the collection itself.
- Expand/collapse should update cached visible rows when possible rather than rebuilding the entire list.
- If an enabled/visible checkbox controls list membership, sorting rows must update immediately when an item is hidden/shown.
- During import or bulk edits, update the data model first and refresh once at the end.

## Drag/drop

Drag start must record stable source identity:

- `sourceKey`
- `sourceType`
- `sourceGroup`
- `sourceIndex` when useful

Drop targets should use stable keys instead of relying only on row frame references. Dragging an item out of a collection must preserve item identity until drop completes or is cancelled.

## Sound and TTS picker

Built-in sound and LibSharedMedia lists can be long.

- Use a scrollable dropdown or searchable list.
- Do not let dropdowns fill the whole screen.
- Reopen near the selected item when possible.
- LibSharedMedia must not break the UI if missing.
- Test buttons should use the same playback path as real alerts when possible.
- TTS channel controls should not be disabled unless the WoW API truly prevents it.
- Do not assume every client locale has the same TTS voice behavior.
- Preserve values during language switching.

## Font safety

Before calling `FontString:SetFont(path, size, flags)`, ensure `path` is a real valid font asset path.

Do not pass symbolic presets such as `AUTO`, `DEFAULT`, `BLIZZARD`, an empty string, or nil. Resolve presets through a media helper first.

Recommended font fallback order:

1. User-selected LibSharedMedia font if available.
2. Addon bundled font if included.
3. Known Blizzard font path.
4. Final safe fallback.

## Media files

Check:

- TOC references existing files only.
- Sounds, textures, and fonts exist in the package.
- Paths use WoW-compatible separators.
- Missing LibSharedMedia does not break the UI.

## User paths

For custom sound paths:

- Explain that paths are relative to the WoW install or addon media conventions.
- Do not validate through expensive repeated file checks in combat.
- Keep invalid-path failure non-fatal.
