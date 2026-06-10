# Large List, Collection, and Sound UI

Use this reference for saved voice lists, sound collections, addon lists, module lists, and any UI with many rows.

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

Collection rows must remain selectable even when empty if edit/delete applies to the collection itself.

Expand/collapse should update cached visible rows when possible rather than rebuilding the entire list.

## Drag/drop

Drag start must record stable source identity:
- `sourceKey`
- `sourceType`
- `sourceGroup`
- `sourceIndex` when useful

Drop targets should use stable keys instead of relying only on row frame references.

Dragging an item out of a collection must preserve item identity until drop completes or is cancelled.

## Sound picker

Built-in sound and LibSharedMedia lists can be long.

Rules:
- Use a scrollable dropdown or searchable list.
- Do not let dropdowns fill the whole screen.
- Reopen near the selected item when possible.
- LibSharedMedia must not break the UI if missing.
- Test buttons should use the same playback path as real alerts when possible.

## TTS fields

TTS UIs should:
- Keep test playback grounded in real alert logic.
- Keep voice/channel/rate controls enabled unless the WoW API truly prevents it.
- Explain valid custom text and sound path usage.
- Preserve values during language switching.
