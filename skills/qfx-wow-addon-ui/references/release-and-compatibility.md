# Release, Compatibility, and Reporting

Use this reference before returning a release zip, publishing a WoW addon, adapting it to another game version, changing SavedVariables structure, or reporting any addon code/package change.

## Package structure

Check:

- Zip root folder name matches the addon folder.
- `.toc` file exists at the addon root.
- TOC references only files that exist.
- All referenced Lua/XML files are included.
- All referenced media files are included.
- Required libraries are included or declared correctly.
- Sub-addons are included when the user expects a complete package.
- SavedVariables are declared in the TOC if used.
- Changelog documents are excluded: `CHANGELOG.md`, `CHANGELOG*.md`, `docs/CHANGELOG*`, release notes, dev logs. QFX release zips never carry a changelog; it stays in the dev workspace/repo as the release-notes source.

## Versioning

Check:

- TOC version is updated.
- README/changelog version matches when present in the workspace (the changelog file itself is updated in the repo but never zipped).
- Zip name follows the requested naming style.
- Use three-part decimal addon versions: `MAJOR.MINOR.PATCH`, for example `1.1.1`.
- Treat each part as a decimal integer, not a floating-point number: `1.1.10` is newer than `1.1.9`.
- Bug fixes, UI polish, localization changes, and small compatibility fixes increment PATCH: `1.1.1 -> 1.1.2`.
- New user-facing features, new modules, or meaningful upgrades increment MINOR and reset PATCH: `1.1.9 -> 1.2.0`.
- Major rewrites, architecture changes, or intentionally incompatible SavedVariables changes increment MAJOR and reset MINOR/PATCH: `1.9.9 -> 2.0.0`.
- Release zip names use only the addon name and official version, for example `QFXToolBox_0.44.20.zip`. Keep notes like `secret_value_fix` or `ui_optimized` in the changelog, not the filename.

## Localization

If the addon claims EN/zhCN/zhTW support:

- All locale files are included.
- New UI strings are localized.
- Default language follows the client unless a force-language setting exists.

## Release cleanliness

Do not include:

- Temporary files.
- Debug dumps.
- Old backup folders.
- Changelog documents of any kind: `CHANGELOG.md`, `CHANGELOG*.md`, `docs/CHANGELOG*`, release notes. Update them in the workspace before packaging, then exclude them from the zip.
- OS metadata like `__MACOSX`.

## Version compatibility boundaries

Use this section when adapting addons for Retail, Classic, MoP Classic, TBC Classic, or custom season/titan variants.

- Do not add compatibility code for UI providers or game versions unless the addon actually interacts with those frames or APIs.
- Avoid unnecessary ElvUI/NDui/SexyMap compatibility in addons that do not move or skin their frames.
- Keep version detection centralized in `Compat/Version.lua` or an existing equivalent; do not scatter build checks across unrelated UI files.
- When APIs differ by version: wrap them behind a compatibility helper, use safe fallbacks, disable/hide options only when unsupported, and document what differs.
- When using another addon as a reference: copy design ideas, not unrelated dependencies. Do not add a compatibility layer just because the reference addon has one.

For each claimed supported version, test: login with no errors, open the settings panel, toggle each option, reload the UI, and enter combat if combat-sensitive.

## SavedVariables migration

Use this when changing settings structure or adding new per-module / per-mode options.

- Never wipe existing user settings during a UI refactor.
- Add defaults without overwriting user values.
- Version migrations must be idempotent.
- Old profile keys must be copied or translated safely.
- Keep migration separate from UI layout code.

Per-module settings:

- Each module owns its defaults.
- Core DB merges module defaults once.
- Missing module tables are created lazily and safely.

Per-mode settings:

- Keep separate tables when behavior differs by mode.
- Do not reuse one global setting if each mode needs independent persistence.
- When migrating from a single old value, copy it into each relevant mode unless user intent is clear.

Report for DB migration changes: new SavedVariables keys, removed/renamed keys, migration path, rollback risk, and `/reload` test steps.

## Deploying to the game client

Use this when copying built addon files into the game or syncing a modified module to a running install.

- After any WoW addon code change, check the game client before finishing: look for the addon folder (and its sub-addon folders) under the game's `Interface/AddOns/`. If the addon is installed there, sync the changed files immediately without waiting for a request; if it is not installed, do not create it and sync only when the user explicitly asks.
- Locate the game installation from the Blizzard registry key (`InstallPath`) or the known `_retail_` / `_classic_` folders, and match the addon folder names exactly — a differently named folder is not the same addon.
- Back up the files being overwritten to a local workspace folder first (for example `archive/<Addon>_client_backup_YYYYMMDD/`). Never place backups inside the game installation directory or inside `Interface/AddOns/` — those locations must stay clean so the game only sees loadable addon files, and wide `*.lua`/`*.bak` sweeps or addon managers can otherwise pick up stray files.
- Sync only the files that actually changed; do not overwrite player-generated client files (companion-app config such as rule/config Lua files, SavedVariables, `.wtf` data) unless the task explicitly requires it.
- When syncing an embedded `QFXWidgets.lua`, replace the whole file with the canonical copy; never merge diverging versions by hand.
- After copying, verify each synced file by hash against the release payload or source; report which files were synced and where the backup lives.
- Update the installed `.toc` only when its contents (file list, interface version) changed; a version-line-only difference does not require touching the client copy.

## Modification traceability and minimal diff

Use this for every addon code/package change.

Final report:

- Files changed.
- Files added.
- Files deleted.
- TOC impact.
- SavedVariables impact.
- API or branch/build assumptions.
- Risk level.
- Rollback notes.
- In-game test steps.

Minimal diff when fixing a focused issue:

- Do not reformat unrelated files.
- Do not rename unrelated functions.
- Do not rewrite architecture unless requested.
- Do not change feature behavior during UI-only work.

Runtime comments: do not add `modified by AI`, date-stamped edit markers, or noisy trace comments. Comments should explain real WoW API behavior, taint risk, migration logic, compatibility, or performance decisions. If the user wants edit traces, put them in a dev changelog such as `docs/CHANGELOG_DEV.md`, never shipped in release zips.

Rollback notes should say which files to restore and whether SavedVariables migration makes rollback risky.
