# Packaging and Release Checklist

Use this reference before returning a release zip or publishing a WoW addon.

## Package structure

Check:
- Zip root folder name matches the addon folder.
- `.toc` file exists at the addon root.
- TOC references only files that exist.
- All referenced Lua/XML files are included.
- All referenced media files are included.
- Required libraries are included or declared correctly.
- Sub-addons are included when the user expects a complete package.

## Versioning

Check:
- TOC version is updated.
- README/changelog version matches when present.
- Zip name follows the requested naming style.
- Use three-part decimal semantic-style addon versions: `MAJOR.MINOR.PATCH`, for example `1.1.1`.
- Treat each version part as a decimal integer, not as a floating-point number: `1.1.10` is newer than `1.1.9`.
- For bug fixes, UI polish, localization text changes, and small compatibility fixes, increment PATCH: `1.1.1 -> 1.1.2`.
- For new user-facing features, new modules, or meaningful feature upgrades, increment MINOR and reset PATCH: `1.1.9 -> 1.2.0`.
- For major rewrites, architecture changes, or intentionally incompatible SavedVariables changes, increment MAJOR and reset MINOR/PATCH: `1.9.9 -> 2.0.0`.
- Release zip names should use only the addon name and official version, for example `QFXToolBox_0.44.20.zip`; keep notes like `secret_value_fix` or `ui_optimized` in the changelog instead of the package filename.

## Localization

If the addon claims EN/zhCN/zhTW support:
- All locale files are included.
- New UI strings are localized.
- Default language follows client unless a force-language setting exists.

## Release cleanliness

Do not include:
- Temporary files.
- Debug dumps.
- Old backup folders.
- Unrequested dev changelogs.
- OS metadata like `__MACOSX`.

## Final report

Report:
- Changed files.
- Added files.
- Deleted files.
- TOC impact.
- SavedVariables impact.
- Risk level.
- Rollback notes.
- In-game test steps.
