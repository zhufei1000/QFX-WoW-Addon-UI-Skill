# Plater-Inspired Options UI Patterns

This reference is extracted from the uploaded Plater addon as a reusable UI design model for QFX-style World of Warcraft addon settings panels.

Use it as a design reference only. Do not copy Plater bundled fonts, textures, icons, sounds, third-party libraries, or brand-specific assets into QFX addons unless the user explicitly asks and licensing is verified.

## 1. What to copy conceptually

The useful UI ideas are structural:

- many settings are split into stable tab categories;
- heavy pages can be created only when the tab is opened;
- option rows are described as data tables with `type`, `name`, `desc`, `get`, `set`, `values`, `min`, `max`, and `step`;
- shared templates keep fonts, buttons, sliders, switches, and dropdowns visually consistent;
- a global callback applies DB refresh and live UI refresh after a setting changes;
- search indexes existing option metadata instead of creating a separate second options system;
- scroll lists separate row creation from row refresh so rows can be reused.

## 2. Tab container for large settings panels

Use a tabbed layout when a single scroll page mixes unrelated settings or becomes hard to scan.

Rules:

- Define tab metadata in one table with stable internal names and localized display labels.
- Keep tab order stable because users build muscle memory around it.
- Group by user task, not by Lua file name.
- Use short tab labels; long labels should move to tooltips or section headers.
- For heavy tabs, define a `createOnDemandFunc`-style function and create content only when needed.
- Store selected tab independently from frame lifetime so refreshes do not jump the user back to page one.

Good QFX categories often look like:

```text
General | Sound | Image | Text | Conditions | Profiles | Import/Export | Advanced
```

For toolboxes, prefer module tabs or a module list on the left with a settings area on the right.

## 3. Table-driven option rows

For large option pages, prefer option-row tables over hand-placing every control.

Recommended fields:

```lua
{
  type = "toggle",      -- label, toggle, range, select, color, execute, textentry, blank
  key = "enableSound",  -- stable local id for search and testing
  name = L.ENABLE_SOUND,
  desc = L.ENABLE_SOUND_DESC,
  get = function() return db.enableSound end,
  set = function(_, value) db.enableSound = value end,
  disabled = function() return not db.enabled end,
}
```

Rules:

- `get` and `set` should be small and predictable.
- Avoid business logic inside the row builder; call module/controller functions from `set` when needed.
- Use stable `key` or `id` for search, testing, and lookup.
- Keep user-facing text localized.
- Use `blank` or section labels for spacing instead of scattered magic Y offsets.
- Put tooltip detail in `desc`; do not make rows too tall to explain everything inline.

## 4. Shared templates and UI factory

The reference addon normalizes controls through shared templates. For QFX addons, do the same with native controls:

- one button helper;
- one checkbox/switch helper;
- one dropdown helper;
- one slider helper;
- one editbox helper;
- one section/card helper;
- one tooltip helper;
- one color swatch helper.

Rules:

- Templates define visual defaults only: size, font, padding, borders, highlight, disabled colors.
- Business logic stays in modules/controllers.
- Do not create several button styles in the same page unless each style has a clear meaning.
- Avoid copying DetailsFramework if the addon is otherwise lightweight and Blizzard-native.
- If an addon already has a local UIFactory, extend it instead of creating another parallel factory.

## 5. Global option change callback

Large UIs should not make every row invent its own refresh path.

Use one global callback such as:

```lua
local function OnOptionChanged(reason)
  DB:RefreshCache()
  UI:RequestRefresh(reason or "option")
  Modules:ApplyChangedSettings(reason)
end
```

Rules:

- All option rows route through the shared callback unless the change is purely visual and local.
- The callback must not always rebuild every frame.
- Let modules expose targeted apply methods.
- For live protected frame changes, save immediately but defer protected apply until combat ends.
- Avoid chat spam when several settings are changed quickly.

## 6. Searchable settings without duplicate controls

The reference addon builds search from existing option tables. For QFX addons:

- Collect `name`, `desc`, `tags`, parent tab, and parent section from option metadata.
- Search should display matching rows grouped by tab and section.
- Search rows may either jump to the real option or render a temporary copy of the option table.
- If rendering a temporary copy, it must call the same `get`, `set`, and global callback as the real option.
- Do not create a second independent control that writes to a different path.
- If a setting cannot safely be edited from search, show a jump button instead.

Useful metadata:

```lua
{
  key = "ttsChannel",
  name = L.TTS_CHANNEL,
  desc = L.TTS_CHANNEL_DESC,
  tags = {"tts", "voice", "sound", "channel"},
  tab = "Sound",
  section = "TTS",
}
```

## 7. Load-on-demand pages

Use delayed creation for pages that are heavy, rarely used, or depend on other pages being ready.

Good candidates:

- search pages;
- profile import/export pages;
- media browser pages;
- designer/preview pages;
- long spell lists;
- advanced debugging pages.

Rules:

- Keep a loaded-state table.
- Make the create function idempotent.
- If a search page needs all option metadata, load missing tabs in short delayed chunks rather than freezing the UI.
- Show a small loading indicator for long creation work.
- Never rebuild a loaded heavy page just because the parent frame re-opened.

## 8. Reusable scroll rows

For long spell, aura, media, saved voice, or module lists, split row creation from row refresh.

Pattern:

```lua
local function CreateLine(parent, index)
  local line = CreateFrame("Button", nil, parent, BackdropTemplateMixin and "BackdropTemplate")
  line.icon = line:CreateTexture(nil, "ARTWORK")
  line.name = line:CreateFontString(nil, "ARTWORK", "GameFontNormal")
  line.remove = CreateFrame("Button", nil, line, "UIPanelCloseButton")
  return line
end

local function RefreshLine(line, data, index)
  line.key = data.key
  line.name:SetText(data.name)
  line.icon:SetTexture(data.icon)
  line.remove:SetEnabled(data.canRemove)
end
```

Rules:

- Create visible line frames once and reuse them.
- Store stable identity on the line (`key`, `type`, `group`) during refresh.
- Do not store important state only in row object references.
- Hide or clear unused rows after filtering.
- Do not call full rebuild for each row during import or search.

## 9. Combat state in options UI

When a settings panel controls live frames:

- register `PLAYER_REGEN_DISABLED` and `PLAYER_REGEN_ENABLED` only while the panel is alive or visible;
- show a clear combat note or subtle overlay if changes will be deferred;
- save settings immediately when safe, but defer protected frame updates;
- apply pending changes once combat ends;
- do not block unrelated safe settings just because the player is in combat.

## 10. Profile, import/export, and external update pages

Large addons often need profile and import/export pages. Keep these separate from everyday settings.

Rules:

- Put import/export in its own tab or dialog.
- Use large editboxes for serialized text, not narrow one-line inputs.
- Protect unsaved text from language refresh and tab refresh.
- Show loading/progress state for heavy imports.
- Validate imported content before overwriting existing profile data.
- Keep rollback/backup guidance visible when profile operations are destructive.

## 11. QFX adaptation checklist

When applying this pattern to a QFX addon:

- Preserve the addon’s existing architecture; do not introduce DetailsFramework unless already used.
- Add or extend a native `UIFactory.lua` instead of hand-copying Plater widgets.
- Convert repeated controls into table-driven rows gradually.
- Keep small addons simple; do not add a tab framework for three settings.
- Use Plater-style delayed creation only for genuinely heavy pages.
- Add search only when the addon has enough options to justify it.
- Keep EN/zhCN/zhTW widths in mind when setting tab and button sizes.
- Keep final packages free of copied reference fonts, textures, and libraries.
