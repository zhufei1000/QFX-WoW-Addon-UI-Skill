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
