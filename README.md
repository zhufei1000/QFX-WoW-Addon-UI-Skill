# QFX WoW Addon UI Codex Skill

Version: 1.6.0

A reusable Codex skill for World of Warcraft addon UI design, review, and refactoring.

This skill focuses on:

- Blizzard-native UI style
- Compact multilingual layouts for English, 简体中文, and 繁體中文
- Complex settings panels
- Large saved lists and collection UIs
- Scrollable dropdowns
- Slider value layout standards
- Drag-and-drop list behavior
- Safe UI refresh and performance patterns
- Retail 12.x secret-value / taint awareness
- Release packaging and traceable change reports

## v1.6 highlights

- Added complex addon UI patterns extracted from real MCDVoiceCooldown UI work.
- Added singleton scrollable dropdown rules.
- Added large-list Builder / Renderer / RowFactory / RowRenderer split.
- Added batched `RequestRefresh(reason)` rules.
- Added stable drag/drop sourceKey and dropKey model.
- Added language switching rules that do not wipe editor drafts.
- Added toolbar button width auto-fit for localized text.
- Added native slider wrapper details for min/current/max labels.
- Added editor dialog grid constant rules.

## Repository structure

```text
.codex-plugin/plugin.json
INSTALL.md
LICENSE
README.md
skills/qfx-wow-addon-ui/SKILL.md
skills/qfx-wow-addon-ui/references/
```

## Usage example

```text
Use qfx-wow-addon-ui to review this WoW addon UI for Blizzard-native style, multilingual layout overflow, long dropdowns, list refresh performance, drag/drop behavior, taint risk, and release packaging completeness.
```

## License

MIT License.
