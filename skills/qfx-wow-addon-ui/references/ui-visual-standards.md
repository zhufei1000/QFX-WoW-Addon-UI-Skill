# UI Visual Standards

Use this reference when creating or reviewing QFX addon panels: settings pages, dialogs, toolbars, lists, and editors. The pixel-level baseline is the QFXWidgets factory itself: `W.Theme` (layout tokens) and the QFXUI `W.Skin` (colors and control sizes). Do not hardcode sizes or colors that exist as tokens, and never override a token per row.

Read `qfxwidgets-factory.md` for the factory contract; this file covers the visual rules that apply on top of it.

## 1. Layout tokens (`W.Theme`)

| Token | Value | Use |
|---|---|---|
| `rowH` | 32px | compact option row |
| `sliderRowH` | 38px | slider rows (min/max under the track) |
| `wideButtonH` | 34px | full-width buttons |
| `headerH` | 28px | section headers |
| `pad` / `sidePad` / `rightPad` | 10 / 10 / 16px | content, label, and right-edge insets |
| `labelGap` | 8px | label-to-control gap |
| `trackWidth` | 110px | default slider track |
| `controlH` | 20px | compact control height |
| `labelSize` / `sectionSize` | 12 / 11px | row label / section title font size |
| `rowBgOdd` / `rowBgEven` | 4.5% / 1.5% alpha | zebra stripes (restarted by `SectionHeader`) |

Rules:
- Adjust a token with `W:SetTheme{...}` only when an addon truly needs a different density; never inline magic numbers in rows.
- Row heights and spacing stay compact: prefer more rows on screen over tall sparse cards.

## 2. Control sizes (QFXUI `W.Skin`)

| Control | Standard |
|---|---|
| Button | 20px high (row buttons), min width 88px; wide button 34px row with a centered button |
| Toggle switch | 40x20 capsule, 16px knob, 2px pad, 75ms slide |
| Checkbox | 16px box, 3px inner mark, label right with 6px gap; box and mark sized with `SnapUI` so both axes land on whole physical pixels (an unsnapped square rounds to 22x23 and reads as wobbly) |
| Slider | track 4px high, thumb 16x16, value box 44x20, stepper column 18px; min/max labels sit beside the track ends at its vertical centre (`labelsBelow` = true stacks them under the rail on a taller row) |
| Dropdown / input | 20px high; dropdown width fits the longest common EN option |
| Segmented pill | min 38px wide plus 16px text padding, 1px gap |
| Color swatch | 22px in rows, 20px in `colorMode`, 16px in grids; no label inside |
| Section title | 14px title centred on a 24px gradient bar (saturated accent blue fading right into the panel, both ends opaque enough to read, 2px bright edge on the left); description 12px muted, left-aligned with the title; 1px divider 6px below the last description line |
| Row label | 12px; notes 12px muted; slider min/max 10px muted |
| Menu row | 20px high, 8px insets, 4px menu padding |

Rules:

- The section title must stay visually above its description: title 14px on the gradient bar, note 12px muted, divider under both. Never let a note outweigh the title.
- The divider closes the whole description block; never leave a description below it.
- Captions that explain how to operate one control go *below* that control (12px muted, 6px gap), not into the section header.
- Gradient fills: `SetGradient` filters the texture's own colour, so set a white base (`SetColorTexture(1,1,1,1)`) before calling it or the bar renders dark. EllesmereUI uses the same `SetColorTexture` + `SetGradient` pairing.

Marks that show an active state use the warm accent sparingly: the check-mark fill is warm, the dropdown arrow only warms up on hover, and the toggle knob plus slider thumb stay neutral (white). A permanently warm knob or thumb read as noisy at this compact size.

## 3. Colors (`W.Skin` QFXUI tokens)

| Token | Purpose |
|---|---|
| `accent` `#4a9cfa` | active/selected marks, focus fills, highlights |
| `controlBg` / `controlBgHi` | control fill / hover fill |
| `border` / `borderHi` | resting / hover border for controls and windows |
| `trackBg` / `trackFill` / `knob` | slider track / fill / thumb; toggle track/knob |
| `warmAccent` / `warmAccentHi` | active ochre/orange: tab underline, logo arc, `checkFill`, hovered dropdown arrow |
| `checkFill` / `thumb` / `arrow` / `arrowHi` | optional overrides for the check-mark fill, slider thumb tint, and dropdown arrow (rest / hover) |
| `selectedFill` / `selectedLine` / `selectedText` | selected pill, tab underline, selected text |
| `text` / `textMuted` | primary / secondary text |
| `danger` / `good` | destructive and success accents |
| `buttonBg` / `buttonBgHi` / `buttonBorder` | button surfaces |
| `menuBg` / `rowHover` | menu background / row hover wash |
| `sectionText` / `line` | section headings / separator lines |
| `sectionBarFrom` / `sectionBarTo` / `sectionBarEdge` | gradient title bar (left→right fade) and its 2px left edge |

Rules:
- The section title must stay visually above its description: title 14px on the gradient bar, note 12px muted, divider under both. Never let a note outweigh the title.
- Never convey state with color alone; pair it with text, a check mark, or a tooltip.
- Use semantic tokens (`danger`, `good`, `textMuted`) rather than literal RGB values.
- Delete/confirm actions use `W:Confirm` with `danger = true`; warning text uses `danger` or `textMuted`, not custom colors.

## 4. Typography

- One font: `W.Theme.font` (`STANDARD_TEXT_FONT` by default). Do not load or set per-panel fonts outside the token.
- Three text levels plus menu/helper text: section title (11px), row label (12px), note/description (12px muted), slider min/max (10px muted).
- Do not shrink font sizes to make English fit; the factory ellipsizes labels and shows the full text on hover instead.
- Do not create a 5-level scale inside one panel.

## 5. Row layout and alignment

Standard option row anatomy (QFXWidgets `DualRow`):

```text
[ label (left, ellipsized) ] [ control lane, right-anchored ]   <- 32px row
[ label                ] [ ===== slider track ===== ][ ... ]    <- 38px slider row
                                 min              max
```

Rules:
- Left label + right control is the default; `DualRow` splits the row into two equal lanes when both slots are used (1px divider between them).
- Labels clamp with `...` and show full text plus tooltip on hover; the clamp retries one frame later when the row was not sized yet.
- Numeric values right-align (slider value box, inputs); display text left-aligns.
- Long explanations go to `tooltip`, or to a `Note`; never push the control off-row.
- Full-width rows for: notes/banners, multiline import/export boxes, `Slider` rows with long labels, scroll pages, `StatusRow`, `ResetRow`.
- Two-column rows only when both English labels and control content fit; otherwise use a full-width row.

## 6. Sections, stripes, and chrome

- Use `W:SectionHeader` for section titles; it resets the zebra stripes at each section start. Call `W:ResetRows(parent)` at page start if the first stripe must be deterministic.
- Zebra stripes are subtle alpha washes; do not add card borders, gradients, or shadows.
- Host windows use `W:SkinFrame` (factory background + border), `W.Surface`, and `W:Border`. Do not use `SetBackdrop` or hand-built borders for QFXUI panels.
- 1px lines and borders must disable pixel snapping (`W.NoSnap` semantics) so they never round away at fractional UI scales.

## 7. Dialog and popup sizing

| Surface | Standard |
|---|---|
| `W:Confirm` | 360px wide by default; title, wrapped text, cancel + accept (danger for destructive) |
| Host editor dialogs | Clamp to screen minus a 40px margin; min usable width 560px before falling back to full-width rows |
| Menus / dropdowns | Width matches the dropdown by default (min 170px; searchable 220px+); clamp to screen |
| Cog popup | 250px wide by default; rows use `DualRow` |
| Tooltips | Native `GameTooltip`; keep text short |

Rules:
- Menus and dropdowns sit on `FULLSCREEN_DIALOG` level 200 with a full-screen click catcher; they close on outside click, Esc, or parent hide.
- Long menus scroll (`maxH` / `maxVisible`); the scrollbar is self-drawn (4px) and matches menu scale.
- Do not stack dialogs; `W:Confirm` is modal and closes before the next action.

## 8. Scroll areas

- Use `W:ScrollPage`; the scrollbar is self-drawn (4px bar, wheel plus thumb drag) and hides when everything fits.
- Preserve scroll offset across tab switches and reopen; use `page:ScrollTo(0)` only when a page switch should start at the top.
- `reserveBar = true` keeps row widths stable when the bar appears; prefer it for pages that alternate between fitting and scrolling.
- After search/jump, scroll the target row into view with `page:ScrollTo(offset)`.

## 9. Interaction states

Every interactive control shows: default -> hover -> pressed/selected -> focus (edit boxes) -> disabled.

- Hover: `controlBgHi` fill plus `borderHi` border (factory default). Do not invent per-control hover art.
- Selected: accent mark for toggles/checkboxes; `selectedFill` for pills; `selectedLine` underline for tabs.
- Focus: edit boxes switch to the `borderHi` border; sliders commit on release and on Enter in the value box.
- Disabled: 0.35 alpha plus an input blocker; `disabledTooltip` explains why. `blockInCombat` applies the same treatment during combat lockdown with `combatTooltip`.
- Errors: inline text near the control, paired with color; success confirmations stay quiet.

## 10. Review checklist

- Are all controls built by QFXWidgets with token values (no hardcoded sizes/colors, no Blizzard templates or AceGUI mixed in)?
- Do rows use `DualRow`/full-width helpers instead of custom placement, with labels that ellipsize and show full text on hover?
- Do sliders use the standard anatomy, commit-on-release, and clamped steppers?
- Are menus/dropdowns clamped, scrollable, and closed on outside click/Esc?
- Are sections separated by `SectionHeader`, with zebra stripes restarted per section?
- Is scroll position preserved, and is `reserveBar` used where the bar toggles?
- Are disabled and combat-blocked controls dimmed and explained by tooltip, then restored via `W:Refresh()`?
- Are destructive actions routed through `W:Confirm` with a danger accept button?
