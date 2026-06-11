# Install QFX WoW Addon UI Skill v1.6.2

This package contains a Codex plugin folder:

```text
qfx-wow-addon-ui-plugin/
```

The plugin contains this skill:

```text
skills/qfx-wow-addon-ui/SKILL.md
```

## Recommended simple install

Copy only the skill folder:

```bash
mkdir -p ~/.agents/skills
cp -R qfx-wow-addon-ui-plugin/skills/qfx-wow-addon-ui ~/.agents/skills/qfx-wow-addon-ui
```

Then restart Codex if it does not show up.

## Plugin install

Copy the whole plugin folder into a plugin location and register it in a local marketplace. The included `README.md` inside the plugin shows an example marketplace entry.

## How to invoke

In Codex, use `$` and select:

```text
qfx-wow-addon-ui
```

Or mention it in your prompt:

```text
Use qfx-wow-addon-ui to review this WoW addon UI before release.
```
