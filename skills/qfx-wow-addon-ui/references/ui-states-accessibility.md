# UI States, Feedback, and Accessibility

Use this reference when building or reviewing any QFX addon panel for state feedback (empty, loading, error, success, confirm) and accessibility (keyboard, contrast, focus, motion).

## 1. Empty states

An empty state must explain what is missing and what to do next.

Rules:
- Use a compact layout: one muted icon or small texture, one short line of text, and one clear action button (for example `Add first voice`, `Import a profile`).
- The empty text must be localized; it is a UI string, not debug output.
- If an empty collection is still editable (edit/delete applies to the collection itself), keep it selectable and show the collection row, not a dead empty area (see `large-list-collection-sound-ui.md`).
- Do not show a full-screen placeholder for a small inline list; an inline empty row is enough.
- After the user's first add/import, remove the empty state and show the real list; no flicker between the two.

## 2. Loading states

Long operations (first tab open, import, media scan, search index build) need feedback.

Rules:
- Use the Blizzard spinner/loading template or a compact progress bar; do not invent custom animated logos.
- Show a short localized text next to the indicator: `Loading...`, `Importing profile...`, `Scanning sounds...`.
- Keep the panel interactive where possible; block only the region being loaded.
- After loading completes, refresh only the affected region; never rebuild the whole page (see `refresh-performance-rules.md`).
- If a heavy page loads in chunks (search index, long lists), show incremental progress rather than one long freeze.
- Failure to load must fall back to an error state, not an endless spinner.

## 3. Input validation and error feedback

Rules:
- Validate on blur (leaving the field) and on submit; do not nag while the user is typing unless the error is resolved live.
- Show the error inline: red-ish text under or next to the field, plus a short message (`Path must be relative to Interface\AddOns`).
- Highlight the offending field with a border or background tint; never rely on color alone.
- For invalid custom paths or media names, keep the failure non-fatal: allow focus to move away and offer a reset/clear action.
- Non-fatal errors should never open modal dialogs; use inline errors or a single non-blocking banner.
- Fatal errors (missing library required for the panel) may use a semantic danger banner with an action link (`Install LibSharedMedia`).

## 4. Success and save feedback

Rules:
- Prefer quiet, non-interrupting feedback: briefly flash the row or show a small inline `Saved` text; avoid modal popups for every save.
- Import success shows a summary (`Imported 12 rows from profile X`), not just `Done`.
- After destructive-but-successful operations, offer the rollback/backup location in the same message.
- Do not spam chat or screen messages for repeated saves while the user drags sliders; batch feedback until the interaction ends (see `refresh-performance-rules.md`).

## 5. Confirmation for destructive actions

Use a confirm dialog (narrow, 320-400px) for: reset, delete, clear list, overwrite import, profile switch that loses data.

Rules:
- The confirm title and button use the real verb: `Delete voice?` / `Delete`, not generic `OK`.
- Default focus is on Cancel; Enter confirms the primary action only when the dialog is designed for it.
- Esc closes and cancels.
- If the action is irreversible, the dialog body states what will be lost and where a backup exists.
- Destructive confirmations use the danger color token plus an icon, and the button text repeats the destructive verb.
- Do not add a confirm step for reversible actions (slider changes, toggles) — those are undoable by changing the value back.

## 6. Keyboard navigation

WoW panels are keyboard-reachable; keep them usable without a mouse.

Rules:
- Tab order follows visual order: header → label/control pairs left-to-right, top-to-bottom; focus moves into the content area, then to footer buttons.
- Arrow keys navigate inside lists and dropdown popups; Enter selects; Esc closes the popup.
- Esc hierarchy: close open dropdown → close dialog → return focus to the opener.
- Every interactive control (button, checkbox, dropdown, slider, input) must be reachable by Tab and activate by Enter/Space.
- Keep a visible focus state on the active control (template focus ring or 1px highlight); never remove it.
- When a panel opens, put initial focus on the first useful control or the panel itself, not on a random footer button.
- Sliders: left/right arrows adjust by one step; PageUp/PageDown jump by a larger step; keep the value text updated while adjusting.

## 7. Contrast and readability

Rules:
- Aim for 4.5:1 contrast on normal text and 3:1 on large text where the custom palette allows; Blizzard template text is the fallback baseline and usually passes for primary text.
- Muted/disabled text must stay readable on the panel background; if a gray is too low contrast, lighten it and rely on state, not on color alone.
- Never use color alone to communicate status: pair with icons and/or text (`✔ Saved`, `! Deferred until combat ends`).
- Keep minimum label size at template defaults; do not go below 11px for any user-facing text.
- Test the panel at 150%+ UI scale; layout must not break, only scale.

## 8. Motion and animation discipline

QFX default: no unnecessary animation.

Rules:
- Allowed micro-motion: short hover highlight, focus ring, highlight pulse for searched/jumped settings, fade-in of dialogs (template default), slider thumb movement.
- Keep animations short (150-300ms) and non-essential; content must be readable mid-animation.
- Never loop animation on idle; stop all timers/OnUpdate on panel close, module disable, profile switch, and logout (see `event-onupdate-rules.md`).
- Respect players who disable animations: if the client-level motion setting is available, skip decorative animation.
- Preview editors may animate live preview, but throttle expensive refresh (see `dandersframes-complex-settings-ui.md`).

## 9. Review checklist

- Does every empty list show a localized hint plus one action button?
- Do long operations show progress and refresh only the affected region on completion?
- Are input errors inline, non-modal, and paired with text (not color alone)?
- Are saves quiet and batched; do imports show a summary?
- Do destructive actions use a confirm dialog with a verb-labeled danger button and Esc-to-cancel?
- Is the panel fully navigable by keyboard with a visible focus state?
- Do primary texts meet contrast targets; is state never communicated by color alone?
- Are animations short, non-looping, stoppable, and skipped when the player disables motion?
