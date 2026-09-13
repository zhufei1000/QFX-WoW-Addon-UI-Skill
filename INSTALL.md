# Install QFX WoW Addon UI Skill v1.18.0

This package contains one skill, `qfx-wow-addon-ui`, usable from opencode, Codex, or any agent that reads `SKILL.md` frontmatter:

```text
skills/qfx-wow-addon-ui/SKILL.md
skills/qfx-wow-addon-ui/references/*.md
```

## Install in opencode

Copy the skill folder into a scanned skill path:

```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\.config\opencode\skills" | Out-Null
Copy-Item -Recurse -Force ".\skills\qfx-wow-addon-ui" "$env:USERPROFILE\.config\opencode\skills\qfx-wow-addon-ui"
```

Alternatively use the auto-loaded external path:

```bash
mkdir -p ~/.agents/skills
cp -R skills/qfx-wow-addon-ui ~/.agents/skills/qfx-wow-addon-ui
```

Restart opencode after copying. Skills are loaded at startup from `SKILL.md` frontmatter and are not hot-reloaded.

## Install as a Codex plugin

Copy the whole plugin folder into a plugin location and register it in a local marketplace. The `README.md` shows an example marketplace entry.

## Install as a raw skill only (Codex)

Copy only the skill folder:

```bash
mkdir -p ~/.agents/skills
cp -R qfx-wow-addon-ui-plugin/skills/qfx-wow-addon-ui ~/.agents/skills/qfx-wow-addon-ui
```

Restart Codex if it does not show up.

## How to invoke

In opencode, the skill appears automatically when your request matches its description. You can also name it explicitly:

```text
Use qfx-wow-addon-ui to review this WoW addon UI before release.
```

In Codex, use `$` and select `qfx-wow-addon-ui`, or mention it in your prompt.

For architecture-heavy work:

```text
Use qfx-wow-addon-ui to apply the primary QFX design method: choose small/medium/large scale, preserve native Blizzard visuals, size layout from English first, defer heavy options, use page cache and widget refresh where useful, centralize high-frequency events, coalesce refreshes, avoid permanent OnUpdate, and keep combat-safe applies.
```

For multilingual layout work:

```text
Use qfx-wow-addon-ui to review this settings UI with English as the base layout language, then verify Simplified Chinese and Traditional Chinese for overflow, clipping, row balance, and runtime language switching.
```
