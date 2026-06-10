# Safe Font and Media Rules

Use this reference when an addon exposes font, texture, sound, or LibSharedMedia options.

## Font safety

Before calling `FontString:SetFont(path, size, flags)`, ensure `path` is a real valid font asset path.

Do not pass symbolic presets such as:
- `AUTO`
- `DEFAULT`
- `BLIZZARD`
- empty string
- nil

Resolve presets through a media helper first.

## Fallback order

Recommended font fallback:
1. User selected LibSharedMedia font if available.
2. Addon bundled font if included.
3. Known Blizzard font path.
4. Final safe fallback.

## Media files

Check:
- TOC references existing files only.
- Sounds/textures/fonts exist in the package.
- Paths use WoW-compatible separators.
- Missing LibSharedMedia does not break the UI.

## User paths

For custom sound paths:
- Explain that paths are relative to WoW install or addon media conventions.
- Do not validate through expensive repeated file checks in combat.
- Keep invalid path failure non-fatal.
