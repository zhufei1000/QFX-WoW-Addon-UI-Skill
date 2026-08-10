# UI Visual Standards

Use this reference when creating or reviewing any QFX addon panel: settings pages, dialogs, toolbars, lists, and editors. It defines the pixel-level visual baseline so repeated work stays consistent.

These standards follow Blizzard-native appearance. If a rule conflicts with a Blizzard template's built-in behavior, prefer the template's behavior and normalize only what the template leaves open.

## 1. Spacing grid

Use a 4px base grid for all spacing decisions. Larger gaps are multiples of 4.

| Token | Value | Typical use |
|---|---|---|
| `gap-xs` | 4px | Between icon and label; checkbox to label |
| `gap-sm` | 8px | Between two controls on the same row |
| `gap-md` | 12px | Between label and control; section body top |
| `gap-lg` | 16px | Card padding; between section header and first row |
| `gap-xl` | 24px | Between cards or major sections |
| `row-sm` | 24px | Single-line option row height |
| `row-md` | 28px | Row with a small desc or larger control |
| `row-lg` | 32px | Row with dropdown/slider stack or warnings |

Do not scatter one-off values like 13px, 17px, or 26px. If a value is not a multiple of 4, justify it (font metrics usually justify 2px offsets; spacing should not).

## 2. Control size baseline

Native Blizzard templates already define most sizes. Standardize the custom parts:

| Control | Standard |
|---|---|
| Button (`UIPanelButtonTemplate`) | Height 22-24px; min width 80px or measured text + 28px padding, whichever is larger |
| Checkbox (`UICheckButtonTemplate`) | 16px box, left-aligned in its cell, label to the right with 4px gap |
| Input box (`InputBoxTemplate`) | Height 20-24px; width from layout or full-width row |
| Slider | Track width from layout; min/current/max labels below track on one line |
| Dropdown | Closed button height 22-24px; width fits longest common EN option + padding |
| Color swatch | 24-32px wide, one row high, bordered frame, no label inside |
| Section title | 14-16px, `GameFontHighlightSmall` or equivalent, with tooltip when helpful |
| Row label | `GameFontNormal` (12-13px); desc text `GameFontDisableSmall` or muted small font |
| Tooltip | Default Blizzard tooltip fonts; keep text short, use `\n` for line breaks |

Buttons: minimum clickable height 22px. If the addon claims touch-friendly support, raise to 32px, but desktop WoW does not require it.

## 3. Typography hierarchy

Use Blizzard stock fonts unless the project owns custom assets. Standard hierarchy:

```text
Panel title        GameFontNormalLarge   16px  white
Section title      GameFontHighlightSmall 14px  white/light
Row label          GameFontNormal       12-13px white
Row desc           GameFontDisableSmall 11-12px muted
Value text         GameFontNormal       same size as row label, right-aligned in controls
Button text        GameFontNormal       inherited from template
Tooltip            GameFontNormal       inherited from Blizzard tooltip
```

Rules:
- Do not create a 5-level font scale in one panel; three text levels (title / label / desc) plus inherited template text are enough.
- Keep the same font size for labels across all pages of one addon.
- Do not shrink fonts below the QFX standard to fix English overflow; fix the layout instead (see `compact-multilingual-layout.md`).

## 4. Semantic color tokens

Define semantic colors by purpose, not by brand palette. Suggested Blizzard-friendly baseline:

| Token | Purpose | Suggested value |
|---|---|---|
| `text-normal` | Primary text | White `#FFFFFF` |
| `text-muted` | Secondary text, disabled descriptions | Light gray `#C0C0C0` (aim ≥ 3:1 against panel bg) |
| `text-disable` | Disabled controls | Gray `#808080` (or `GameFontDisable`) |
| `accent` | Links, active tab, highlight | Blizzard yellow `#FFD100`-style highlight or template default |
| `warning` | Combat notice, deferred apply, caution | Yellow/orange `#FFA500`-ish, plus icon |
| `danger` | Destructive actions, errors | Red `#FF4040`-ish, plus icon |
| `success` | Import/apply success | Green `#20C020`-ish, plus icon |
| `info` | Neutral explanations | Blue/white text with info icon |

Rules:
- Never convey state with color alone; pair color with an icon or text label.
- Keep the base panel background as Blizzard template defaults; do not invent dark/light custom themes unless requested.
- If a custom-drawn skin is explicitly requested, define these tokens in the Skin layer only, never in business modules.

## 5. Row layout and alignment

Standard option row anatomy:

```text
[ label (left, vertical center) ] [ control (right) ]     <- single-line row, 24px
[ label (top)                ] [ control (right) ]
[ desc (below label, wraps)  ]                            <- desc row, 28-32px
```

Rules:
- One row = one concern. Do not stack two unrelated settings in one row.
- Labels and controls are vertically centered on the same row.
- Left label column: 160-200px by default, sized from English text first (`GetStringWidth` + padding). Never exceed 40% of panel width.
- Numeric values align right inside controls; text values align left.
- Long desc goes to the tooltip, or wraps below the label at full row width; never let desc force the control off-row.
- Full-width rows for: file paths, import/export text, search boxes, large dropdowns, sliders with bottom value labels, semantic banners, warnings.
- Two columns only when both columns fit English labels/dropdown values and the row stays balanced in zhCN/zhTW.

## 6. Cards, sections, and groups

- Card: 16px inner padding, 8-12px vertical gap between cards, template backdrop or clean separation line.
- Section header: title + optional tooltip icon; 12px space below before first row.
- Collapsible groups: header row 24-28px with expand arrow on the left; children indented 16px; collapsed state removes children and recalculates height.
- Do not add decorative borders, gradients, or shadows beyond Blizzard templates; native panels stay flat.

## 7. Dialog and panel sizing

| Dialog type | Standard width | Notes |
|---|---|---|
| Narrow confirm / prompt | 320-400px | Single message + 1-2 buttons |
| Standard settings dialog | 640-720px | Left module list + right content, or tabbed |
| Wide editor dialog | 800-960px | Preview editors, import/export, media browsers |

Rules:
- Height: default 480-560px for settings; editors may be taller but must clamp to screen (minus 40px margin).
- Footer: buttons bottom-right (Close / Cancel on the right edge; primary action last), or bottom-center for wizard flows.
- Keep all controls inside the card/module boundary; nothing hangs outside the frame edge.
- Clamp the dialog to screen bounds; respect UI scale — do not assume a specific monitor resolution.
- Minimum usable width for a settings panel: 560px; below that, switch rows to full-width layout instead of shrinking.

## 8. Scroll areas

- Use the Blizzard scroll templates or a local wrapper with the same behavior.
- Mouse wheel scrolls; dragging the scrollbar works; keyboard arrow keys scroll when the panel has focus.
- Preserve scroll position when switching tabs/pages and when reopening the panel, unless content structure changed.
- When navigating to a highlighted setting (search/jump), scroll the target row into view.
- For long lists, refresh only visible rows (see `refresh-performance-rules.md`); show row count or a small progress indicator for heavy first load.

## 9. Interaction states

Every interactive control must show clear states:

```text
default -> hover -> pressed -> focus -> disabled
```

- Hover / pressed / disabled visuals come free from Blizzard templates; do not re-skin them unless asked.
- Focus: keep the template focus ring or add a 1px highlight border; never remove focus indication.
- Disabled: reduce alpha to template default and use `text-disable` color; do not hide the control unless mode rules say so.
- If a control is disabled because of a dependency, the tooltip explains why (see `deep-reference-addon-patterns.md` option dependency graph).

## 10. Review checklist

- Are all spacing values multiples of 4 (except font-metric offsets)?
- Do buttons meet min height 22px and min width from English text + 28px padding?
- Is the left label column sized from English, 160-200px, under 40% of width?
- Is there only one visual style for each control type across all pages?
- Do numeric values right-align and text values left-align?
- Do desc rows wrap without pushing controls off-row?
- Are long dropdowns, sliders, import/export, search, and banners on full-width rows?
- Do dialogs use the standard width tiers and clamp to screen?
- Is scroll position preserved and target rows scrolled into view after jump?
- Are semantic colors paired with icons/text so state is never color-only?
