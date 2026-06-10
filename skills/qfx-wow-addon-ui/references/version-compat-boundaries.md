# Version Compatibility Boundaries

Use this reference when adapting addons for Retail, Classic, MoP Classic, TBC Classic, or custom season/titan variants.

## General rule

Do not add compatibility code for UI providers or game versions unless the addon actually interacts with those frames or APIs.

Avoid unnecessary ElvUI/NDui/SexyMap compatibility in addons that do not move or skin their frames.

## Version checks

Keep version detection centralized in `Compat/Version.lua` or an existing equivalent.

Do not scatter build checks across unrelated UI files.

## API differences

When APIs differ by version:
- Wrap them behind a compatibility helper.
- Use safe fallback behavior.
- Keep UI options disabled or hidden only when unsupported.
- Document what behavior differs.

## Reference addons

When using another addon as a reference:
- Copy design ideas, not unrelated dependencies.
- Do not add a compatibility layer just because the reference addon has one.
- Preserve the target addon's existing architecture.

## Testing

For each claimed supported version, test:
- Login with no errors.
- Open settings panel.
- Toggle each option.
- Reload UI.
- Enter combat if combat-sensitive.
