# DandersFrames-Inspired Complex Settings UI Patterns

This reference is extracted from the uploaded DandersFrames addon as a reusable design model for complex QFX-style World of Warcraft addon settings panels.

Use it as a structural reference only. DandersFrames uses a custom modern dark UI and bundled assets; QFX addons should normally remain Blizzard-native, lightweight, compact, and multilingual. Do not copy its fonts, textures, icons, libraries, brand assets, or full custom visual system unless the user explicitly asks and licensing is verified.

## 1. What to absorb

The useful ideas are not the skin. They are the workflow patterns:

- persistent collapsible settings groups;
- semantic information and warning banners;
- cross-page `See Also` navigation;
- a searchable settings registry instead of plain text filtering;
- guided setup wizards for first-run or bulk configuration;
- profile override indicators and reset behavior;
- preview-safe designers that edit proxy data before committing;
- advanced diagnostic pages for large addons.

These patterns are especially useful for QFXToolBox, MCDVoiceCooldown, unit-frame addons, minimap tools, and any addon with many modules or visual editors.

## 2. Persistent collapsible groups

Large settings pages should not force the user to scroll through every option every time.

Rules:

- Provide a shared `CreateCollapsibleSection` or equivalent helper.
- Store collapsed/expanded state in SavedVariables using stable group IDs.
- Do not store collapse state by localized title; localized strings can change.
- Collapsing a group should remove or hide its children and recalculate parent layout height.
- Expanding should restore child controls without rebuilding unrelated groups.
- Group headers may show a small status summary, preview icon, enabled state, or warning badge.
- Empty but configurable groups should still be selectable or expandable if edit/delete/reset actions apply.

Good stable IDs:

```lua
"sound.tts"
"cooldown.conditions"
"chatbar.mode.colorBlocks"
"minimap.provider.leatrix"
```

Avoid:

```lua
L["声音"]
sectionTitle
frame:GetName()
```

## 3. Semantic banners instead of long inline text

Complex explanations should not be squeezed into labels or repeated tooltips.

Use semantic banners for:

- combat lockdown and deferred-apply notices;
- destructive profile/import actions;
- secret-value or API limitation explanations;
- TTS channel limitations or locale behavior;
- missing optional libraries or media;
- compatibility notes for ElvUI, NDui, SexyMap, Leatrix Plus, or Classic branches.

Recommended banner variants:

```text
info | warning | caution | danger | success
```

Rules:

- Banner text must wrap and auto-size vertically.
- When banner text changes, the parent layout must be refreshed.
- Use one compact icon or severity marker, not large decorative art.
- Do not spam multiple banners when one section-level banner is enough.
- A banner should never replace the actual control label or tooltip; it explains context.

## 4. See Also cross-page navigation

When related settings live on different pages, do not duplicate the same control in every page.

Use a compact `See Also` row:

```text
See also: TTS Settings · Custom Sounds · Import/Export
```

Rules:

- `See Also` should navigate to the real setting page and optionally highlight the target group.
- Keep labels short and localized.
- Do not create a second control that writes to the same DB key unless scope is clearly different.
- Use this for relationships such as Sound ↔ TTS, Text ↔ Preview, Profiles ↔ Import/Export, Minimap Provider ↔ Compatibility.

## 5. Searchable settings registry

Search should be based on registered setting metadata, not just visible text scanning.

Each real control should register searchable metadata when created:

```lua
Search:Register({
  id = "sound.tts.channel",
  tab = "Sound",
  section = "TTS",
  label = L.TTS_CHANNEL,
  desc = L.TTS_CHANNEL_DESC,
  keywords = {"tts", "voice", "sound", "channel", "voice channel"},
  dbKey = "ttsChannel",
  widgetType = "dropdown",
  jump = function() UI:OpenTab("Sound", "sound.tts") end,
})
```

Rules:

- Use stable IDs for search entries.
- Include `tab`, `section`, `label`, `desc`, optional `keywords`, `dbKey`, and `widgetType`.
- Search results should display a breadcrumb such as `Sound > TTS`.
- Results may either jump to the real control or render a safe proxy that uses the same `get`, `set`, and global callback.
- If editing from search is unsafe, show a jump/highlight button instead.
- Add useful aliases: `opacity` ↔ `alpha`, `voice` ↔ `tts`, `cooldown` ↔ `cd`, `image` ↔ `texture`, `buff` ↔ `aura`.
- Avoid scanning every frame every keystroke; index metadata once and throttle search updates.

## 6. Highlight target setting after navigation

When search, wizard, or `See Also` jumps to a setting, the user needs to see where they landed.

Rules:

- Open the target tab.
- Expand the target collapsible group.
- Scroll the target row into view if the page is scrollable.
- Temporarily highlight the target row or group header.
- Remove highlight automatically after a short time or when another target is selected.
- Do not use heavy animations; a simple border/highlight pulse or color change is enough.

## 7. Guided setup wizard

A wizard is useful when the user must make several related choices before the addon feels usable.

Good candidates:

- first-run setup;
- choosing a minimap provider or compatibility mode;
- choosing chat bar display mode;
- choosing cooldown alert categories;
- importing a class/spec preset;
- setting up sound/TTS/image/text alert behavior.

Rules:

- Wizard steps should write to the same SavedVariables and module APIs as the full settings page.
- A wizard initializes or batch-configures; it must not replace the full settings UI.
- Provide Back, Next, Cancel, and Finish where appropriate.
- Let the final screen summarize what will change.
- After Finish, optionally jump to and highlight the real settings section.
- Store incomplete wizard draft state separately from committed settings when possible.
- Do not run protected frame changes in combat; save choices and apply after combat if needed.

Recommended step types:

```text
intro | singleChoice | multiChoice | textInput | mediaChoice | previewChoice | confirm | done
```

## 8. Profile override indicators

When a setting can come from multiple layers, the UI must show where the active value comes from.

Common layers:

```text
Default < Global < Profile < Character < Spec < Mode < Runtime override
```

Rules:

- Mark overridden settings with a compact icon such as a star, dot, or badge.
- Tooltip should explain the source: `Overridden by Profile`, `Using Global Default`, or `Spec-specific value`.
- Provide a reset action to return to the parent value when safe.
- Do not silently write profile-specific values when the user thinks they are editing global settings.
- If an entire tab has overrides, the tab may show a small badge.
- Destructive reset actions should show a warning banner or confirmation.

This is important for QFX addons that add per-character, per-class, per-spec, per-mode, or per-profile configuration.

## 9. Preview-safe visual editors

For visual settings such as images, text, alerts, unit frames, minimap position, or aura indicators, editing should not immediately corrupt the real saved configuration.

Rules:

- Use proxy/draft data while the editor is open.
- Preview changes live from the proxy data.
- Commit to real DB only on Save/Apply.
- Cancel must discard proxy changes.
- Language refresh must not wipe draft text, paths, selected media, positions, or imported data.
- Heavy preview refresh should be throttled.
- Position editors should start away from the settings controls so draggable preview frames do not block checkboxes or dropdowns.
- If the preview frame overlays the options panel, provide a temporary move/lock toggle or move it outside the panel bounds.

## 10. Diagnostic and debug pages

Large QFX addons benefit from a hidden or advanced diagnostic page.

Useful diagnostics:

- recent errors captured by the addon;
- registered events and whether they are active;
- active OnUpdate loops and their throttle interval;
- refresh counters and last refresh reason;
- frame anchors and provider detection;
- optional library/media availability;
- combat lockdown pending changes;
- current profile/language/version branch;
- last played sound/TTS path and channel;
- import/export validation results.

Rules:

- Diagnostic pages should be hidden under Advanced/Debug and not shown as normal settings.
- Do not keep expensive scanners running unless the page is visible or the user starts a test.
- Provide copyable diagnostic text for bug reports.
- Never include account-private data unless the user explicitly chooses to copy it.

## 11. QFX adaptation checklist

When applying these patterns to QFX addons:

- Keep Blizzard-native visual style unless the user asks for custom skinning.
- Add collapsible sections before adding more tabs if the page is already category-specific.
- Add search only when the addon has enough settings to justify it.
- Use banners for warnings and compatibility notes instead of oversized descriptions.
- Use `See Also` links instead of duplicate controls.
- Use wizard only for first-run or multi-step setup, not for every option.
- Add override indicators only when settings truly have multiple source layers.
- Keep preview editors draft-safe and language-safe.
- Keep diagnostic pages lazy-loaded and advanced-only.
- Do not copy DandersFrames bundled fonts, textures, libraries, color picker, or custom skin.
