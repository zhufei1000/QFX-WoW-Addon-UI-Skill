# SavedVariables Migration

Use this reference when changing settings structure or adding new per-module/per-mode options.

## Migration rules

- Never wipe existing user settings during UI refactor.
- Add defaults without overwriting user values.
- Version migrations should be idempotent.
- Old profile keys should be copied or translated safely.
- Keep migration separate from UI layout code.

## Per-module settings

For modular addons:
- Each module should own its defaults.
- Core DB should merge module defaults once.
- Missing module tables should be created lazily and safely.

## Per-mode settings

For mode-specific UI options:
- Keep separate tables when behavior differs by mode.
- Do not reuse one global setting if each mode needs independent persistence.
- When migrating from a single old value, copy it into each relevant mode unless user intent is clear.

## Reporting

When DB migration changes are made, report:
- New SavedVariables keys.
- Removed or renamed keys.
- Migration path.
- Rollback risk.
- `/reload` test steps.
