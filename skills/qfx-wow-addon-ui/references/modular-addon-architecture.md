# Modular Addon Architecture

Use this reference when reorganizing a WoW addon without changing feature behavior.

## Preferred modules

Recommended structure:

```text
Core/
  Init.lua
  Events.lua
  DB.lua
  Migration.lua
  Localization.lua
UI/
  UIFactory.lua
  Skin.lua
  MainFrame.lua
  Options.lua
Modules/
  FeatureName.lua
Media/
  Media.lua
Compat/
  Version.lua
```

## Rules

- Keep Core small and stable.
- Keep feature logic in modules.
- Keep UI layout in UI files.
- Keep media resolution in Media.
- Keep version checks in Compat.
- Keep migration code separate from runtime logic.

## Do not duplicate systems

Do not create a second:
- DB layer.
- Locale table.
- Module registry.
- UI factory.
- Event dispatcher.
- Media resolver.

## Parent/sub-addon rule

Do not make sub-addons independent unless the user explicitly asks. If the parent addon owns shared libraries, DB, or localization, preserve that relationship.
