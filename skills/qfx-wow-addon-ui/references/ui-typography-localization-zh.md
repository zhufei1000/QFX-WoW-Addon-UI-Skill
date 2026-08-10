# Typography and Trilingual Localization Layout

Use this reference for any QFX addon UI that displays English, Simplified Chinese (zhCN), or Traditional Chinese (zhTW). It complements `compact-multilingual-layout.md` (width safety) by covering font choice and text-quality rules.

## 1. Full-width characters change width math

Chinese characters are full-width: at the same font size, one CJK character is roughly twice as wide as a Latin letter and about 1.5x an English digit/space.

Consequences:

- Never estimate width by character count. A 12-character Chinese label can be wider than a 20-character English label.
- Always measure with `FontString:GetStringWidth()` on the actual localized string, then add padding.
- "English is longer than Chinese" is true for typical option labels, but NOT guaranteed per string. Verify each label, not the language average.
- When mixing, the visual "longest" language decides the column: `math.max(enWidth, zhCNWidth, zhTWWidth)`.

## 2. Font selection and fallback

Rules:

- Prefer Blizzard stock fonts (`STANDARD_TEXT_FONT` and template fonts). Do not bundle CJK fonts unless the addon must guarantee identical glyphs across clients.
- Blizzard handles locale-appropriate fallback for CJK glyphs automatically when using stock fonts; do not hardcode `Fonts\\ARKai_T.TTF`-style paths unless the project deliberately owns them.
- Never call `FontString:SetFont` with symbolic presets such as `AUTO`, `DEFAULT`, `BLIZZARD`, empty string, or nil (see `safe-font-media-rules.md`).
- If the addon exposes a font picker (LibSharedMedia), missing fonts must fall back safely and never break the panel.
- For custom-drawn text (rare), test the same string in all three locales; CJK glyphs can shift metrics between zhCN and zhTW fonts.

## 3. Mixed-language composition

Rules:

- Insert a space between CJK text and adjacent Latin letters/digits for readability: `播放 30 秒` rather than `播放30秒` when the addon builds strings at runtime. Keep the space out of localized source strings where possible.
- Keep units and numbers together: `50%`, `1.5x`, `3 秒`. Do not let wrapping split a number from its unit.
- Do not wrap inside localized tokens; wrap at token boundaries or spaces.
- If concatenating labels at runtime, use locale-aware order; do not assume `prefix .. value .. suffix` reads correctly in CJK (it usually does, but keep order flexible).

## 4. Punctuation and symbols

Rules:

- Use locale-correct punctuation in localized strings: Chinese full-width `，。；：「」` for zhCN/zhTW, half-width `, . ; : "` for EN.
- For truncation, use an ellipsis appropriate to the locale: EN `...` or `…`; zhCN/zhTW prefer `…` (single full-width ellipsis) and keep it inside the visible width.
- Avoid mixing full-width and half-width parentheses inconsistently within one string.
- Percent signs, plus/minus, and arrow symbols (`→`) render on all clients; verify them in zhTW where the font differs.
- Do not put decoration symbols in stable IDs or search keywords.

## 5. Truncation rules

When text cannot fit:

1. Shorten the visible label and move the full explanation to the tooltip — never silently drop information.
2. Truncate with the locale-appropriate ellipsis; do not let text clip mid-glyph.
3. Never truncate critical values (numbers, paths, cooldown times, channel names). Give those rows full width or wrap them.
4. Dropdowns: truncate display text in the closed button, but show the full option text in the popup and tooltip.
5. Do not use `SetFixedSize`-style clipping as a substitute for layout fixes; treat clipping as a layout bug (see `compact-multilingual-layout.md`).

## 6. zhCN / zhTW terminology consistency

zhCN and zhTW are different languages with different terms. Maintain a small glossary per addon.

Common examples (verify per addon):

| EN | zhCN | zhTW |
|---|---|---|
| Settings | 设置 | 設定 |
| Addon | 插件 | 附加元件 |
| Options | 选项 | 選項 |
| Profile | 配置 | 設定檔 |
| Import / Export | 导入 / 导出 | 匯入 / 匯出 |
| Reset | 重置 | 重設 |
| Sound / Voice | 声音 / 语音 | 音效 / 語音 |
| General | 常规 | 一般 |

Rules:

- Never machine-translate one locale from the other without a glossary pass.
- Keep zhCN and zhTW as separate locale files with their own keys; do not share a single "Chinese" table.
- If zhCN and zhTW share a string key, each file still gets its own translated value.
- Search keywords and aliases should include terms from all three locales (see `dandersframes-complex-settings-ui.md` search registry).

## 7. Line breaking and wrapping

Rules:

- CJK can break between any two characters; ensure desc/banner text wraps instead of clipping.
- Avoid leaving a single CJK character or a lone punctuation mark as the last item of a wrapped line (widows); tweak copy or use `\n` where it matters.
- Keep inline help under 2 lines in a row; longer explanations move to tooltip or banner.
- For banners: text must wrap and the parent layout must refresh when banner text changes.

## 8. Runtime language switching

Rules (in addition to `compact-multilingual-layout.md`):

- After switching locale, re-measure label, button, dropdown, and tab widths before relayout — CJK glyph metrics can differ between clients.
- Preserve unsaved draft text, file paths, imported text, selected values, and editor scroll positions across the switch.
- Prefer `RefreshLocale()` over recreating dialogs; only rebuild when the widget set or layout structure must change.
- Re-run the English-width baseline check after switching back to EN.

## 9. Review checklist

- Is every fixed-width label/column verified with `GetStringWidth` on the actual EN string plus padding?
- Do zhCN/zhTW strings wrap and ellipsize correctly without mid-glyph clipping?
- Are numbers and units kept together; are critical values never truncated?
- Is punctuation locale-correct, including full-width forms in zhCN/zhTW?
- Does the zhCN/zhTW glossary exist and stay consistent across files, tooltips, and search aliases?
- Do runtime-concatenated strings insert a space between CJK and Latin/digits?
- Does switching locale preserve drafts and re-measure widths?
