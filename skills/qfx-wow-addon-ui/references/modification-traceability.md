# Modification Traceability

Use this reference for every addon code/package change.

## Final report requirements

Report:
- Files changed.
- Files added.
- Files deleted.
- TOC impact.
- SavedVariables impact.
- Risk level.
- Rollback notes.
- In-game test steps.

## Minimal diff

When fixing a focused issue:
- Do not reformat unrelated files.
- Do not rename unrelated functions.
- Do not rewrite architecture unless requested.
- Do not change feature behavior during UI-only work.

## Runtime code comments

Do not add comments like:
- `modified by AI`
- date-stamped edit markers
- noisy trace comments

Comments should explain real WoW API behavior, taint risk, migration logic, compatibility, or performance decisions.

## Dev changelog

If the user wants edit traces, put them in a dev changelog such as:

```text
docs/CHANGELOG_DEV.md
```

Keep dev-only notes out of release zips unless requested.

## Rollback notes

Rollback notes should say which files to restore and whether SavedVariables migration makes rollback risky.
