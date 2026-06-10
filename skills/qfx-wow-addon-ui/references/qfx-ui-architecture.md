# QFX UI Architecture

Use this reference when structuring or refactoring QFX-style WoW addon UI code.

## Preferred structure

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
  Dialogs.lua
  Dropdown.lua
  Lists.lua
Modules/
  ModuleName.lua
Media/
  Media.lua
Compat/
  Version.lua
```

## UIFactory responsibilities

UIFactory may create and style:
- Buttons
- Checkboxes
- Sliders
- Dropdowns
- Input boxes
- Section cards
- Tooltip helpers
- Font/color helpers
- Shared spacing constants

UIFactory must not contain module-specific business logic.

## Skin layer responsibilities

Skin should be a lightweight visual normalization layer:
- Apply Blizzard-native look consistently.
- Normalize button/dropdown/slider/checkbox visuals.
- Keep external skin friendliness.
- Avoid taking ownership of business behavior.

Do not move alert logic, saved-list logic, drag/drop logic, or cooldown logic into Skin.

## Dialog grid constants

Complex dialogs should define layout constants first:
- Dialog width and height.
- Card/module widths.
- Column x positions.
- Label widths.
- Control widths.
- Row heights and gaps.

Use helpers such as `PlaceModule`, `PlaceControl`, and `CreateFieldLabel` instead of scattering magic coordinates.

## No duplicate architecture

Do not create a second:
- Database layer
- Localization table
- Module registry
- UI factory
- Media resolver
- Event dispatcher

Extend the existing architecture unless a full rewrite is explicitly requested.
