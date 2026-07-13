# Versioned WoW API Snapshots

Use this reference whenever an addon is created, reviewed, fixed, or packaged for a named WoW client version.

## Mandatory rule

Verify every WoW API, event payload, enum, mixin, template, widget method, and FrameXML symbol touched by the work against the exact target version. Do not write version-specific code from memory or from a different patch's documentation.

## Bundled snapshots

| Target | Client build | Channel | Archive |
|---|---:|---|---|
| 12.0.7 | 12.0.7.68453 | Retail pinned tag | `api-snapshots/wow-addon-api-docs-12.0.7-build-68453.zip` |
| 12.1.0 | 12.1.0.68629 | PTR pinned tag | `api-snapshots/wow-addon-api-docs-12.1.0-PTR-build-68629.zip` |

Each archive contains:

- `version.txt` for build verification;
- `Interface/AddOns/Blizzard_APIDocumentation/`;
- `Interface/AddOns/Blizzard_APIDocumentationGenerated/`.

The files come from the matching fixed tag in [Gethe/wow-ui-source](https://github.com/Gethe/wow-ui-source), a Git mirror of Blizzard's client UI source.

The 12.1.0 archive is a PTR snapshot. Recheck the newest matching PTR or live client source before releasing a 12.1.0 addon because signatures and restrictions may change after build 68629.

## Verification workflow

1. Identify the requested patch, channel, build, and TOC/interface number.
2. Extract the matching snapshot to a temporary directory.
3. Search for every affected symbol in `Blizzard_APIDocumentationGenerated`.
4. Search the matching full Blizzard UI source for real usage when the generated signature is insufficient.
5. Read the patch API-change page for additions, removals, payload changes, secret-value behavior, secure restrictions, and deprecations.
6. Record the result in an API verification record before implementation or release.
7. Put confirmed version differences behind `Compat` wrappers or capability gates.

Example searches after extraction:

```powershell
rg "C_UnitAuras|AuraData" Interface/AddOns/Blizzard_APIDocumentationGenerated
rg "SetOnUpdateMode" Interface/AddOns/Blizzard_APIDocumentationGenerated
rg "EVENT_NAME" Interface/AddOns/Blizzard_APIDocumentationGenerated
```

## API verification record

Use this compact record in work notes and final reporting:

```text
Target: 12.0.7 Retail / build 68453 / TOC 120007
Sources: bundled API snapshot; target patch API changes; matching Blizzard UI source usage
Checked: C_Namespace.Function, EVENT_NAME payload, TemplateName, MixinName
Decision: direct use / Compat wrapper / capability gate / unsupported
Unknowns: none, or list exact unresolved behavior
```

For multi-version packages, create one record per claimed version. Passing on one patch does not establish compatibility with another.

## Online change indexes

- 12.0.7: <https://warcraft.wiki.gg/wiki/Patch_12.0.7/API_changes>
- 12.1.0: <https://warcraft.wiki.gg/wiki/Patch_12.1.0/API_changes>
- 12.1 PTR development notes: <https://us.forums.blizzard.com/en/wow/t/midnight-curse-of-ulatek-ptr-development-notes/2317811>

## Integrity

```text
3A8B5A1FF4018EF203C7EA523767FFD8B9E92DA31C74FB5ED140F683A26B1576  wow-addon-api-docs-12.0.7-build-68453.zip
604A9E1F571E3E2AAC02BB0D8EC08BD48FD70A1E496CBF73CF4081DC353538FA  wow-addon-api-docs-12.1.0-PTR-build-68629.zip
```
