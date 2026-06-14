# Modular Addon Architecture

Prefer Core, DB, Migration, Localization, UI, Modules, Media, Compat, Debug, ImportExport, and optional API boundaries.

Use the architecture at the right scale:

- Small addon: one root namespace, Core, DB/defaults, Localization, Options.
- Medium QFX addon: Core, UI, Modules, Media, Compat, Debug.
- Large addon: add Profile, Migration, ImportExport, Designer, API, and lazy diagnostics.

Rules:

- Do not create duplicate module registries, DB layers, locale tables, UI factories, media resolvers, or event buses.
- Child addons should not become independent unless explicitly requested.
- Runtime modules should not depend on options pages being opened.
- Defaults must load before DB initialization.
- Localization must load before UI creation.
- Compatibility checks should live in one boundary instead of being scattered through every file.
- High-frequency events should use targeted dispatchers when possible.
- Public APIs should be documented and separate from private internals.
- Import/export should validate and migrate data before applying it.
- Debug/profiling should be lazy-loaded or explicitly enabled, not always active.

For large addon architecture derived from the reference addons, read `references/reference-addon-architecture-patterns.md`.
