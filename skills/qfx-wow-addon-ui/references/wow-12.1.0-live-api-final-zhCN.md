# WoW 12.1.0 Live API 最终核实（69283）

用于 Retail 12.1.0 正式服插件开发、兼容性审查和 12.0.7 → 12.1.0 迁移后的最终 API 基线确认。

## 当前正式服基线

最后核实：**2026-08-13**。

- Retail `live`：**12.1.0.69283**
- Live HEAD：`710f59e457317676c0f699e6addaf2c405c2a1a4`
- Retail `ptr`：**12.1.0.69273**
- PTR HEAD：`6e348870ed8f93d95f0cd16d299b51dbce500296`

Gethe `live/version.txt` 当前为：

```text
12.1.0.69283
```

Gethe `ptr/version.txt` 当前为：

```text
12.1.0.69273
```

## Live 与 PTR 69214 的最终结论

`live` 与 `ptr` Git 历史分叉，因此不能直接把 branch compare 中的大量 added/modified 文件当成真实 API 差异。

本次采用 **generated API 文件 Blob SHA 内容级核对**。

以下高风险 API 文件在 Live / PTR 中 Blob SHA 完全一致：

| 文件 | Blob SHA | 结论 |
|---|---|---|
| `UnitAuraDocumentation.lua` | `e53a0aede84d369f78f63e8afde886421eab7cf4` | 完全一致 |
| `CooldownViewerDocumentation.lua` | `ec05eb25cef1b3ec6870e78a95d470d5ff4eda7e` | 完全一致 |
| `SecretPredicatesDocumentation.lua` | `97af2eb71809da82a1dfcdc6cccb147812bcc1fc` | 完全一致 |
| `UnitDocumentation.lua` | `a0d34f0e5379af2bb4fc6399684d51eaf0c00d57` | 完全一致 |
| `UnitRoleDocumentation.lua` | `194cc3ad91a328ce81491d77d732e49a920bd7fa` | 完全一致 |
| `SpellDocumentation.lua` | `096033af83dee399c1c6eb2b805a339b6e6da535` | 完全一致 |
| `ForbiddenAspectConstantsDocumentation.lua` | `434f6f61a487b471772387e88c128db2cb685718` | 完全一致 |
| `CombatLogDocumentation.lua` | `7b5db6fcd30cfcf8e3ff2b5c1d67843232aaf84c` | 完全一致 |
| `AuraContainerSharedDocumentation.lua` | `066832ee25b75f2924a887f60409b8104fc26a00` | 完全一致 |
| `AuraContainerUtilDocumentation.lua` | `6eac23d2f2c8a6b6f711e22de8e682e3aac05b43` | 完全一致 |
| `SpecializationInfoDocumentation.lua` | `2bd552e09e5d924610f22b18ba6d209d32b943e9` | 完全一致 |
| `Blizzard_APIDocumentationGenerated.toc` | `bdd65e77ef8b1426e028a9a5c1ffef0a8f102d20` | generated API 清单一致 |

因此：

> **没有发现 PTR 12.1.0.69214 → Live 12.1.0.69214 的高风险 API 临时改动。**

此前在 PTR 69214 中确认的 Aura、CooldownViewer/CDM、Secret Predicate、Unit Identity、ForbiddenAspect、Spell/Cooldown、CombatLog、Inspect specialization 等规则，可以正式视为 **12.1.0 Live 69214 当前 API 合同**。

## 69214 → 69283 / 69273 复查结论（2026-08-13）

Live 推进到 **12.1.0.69283**、PTR 推进到 **12.1.0.69273** 后，按同样的 generated API 文件 Blob SHA 内容级核对方法复查。

以下高风险 API 文件在 Live 69283 与 PTR 69273 中 Blob SHA 与 69214 完全相同：

| 文件 | Blob SHA（与 69214 一致） |
|---|---|
| `UnitAuraDocumentation.lua` | `e53a0aede84d369f78f63e8afde886421eab7cf4` |
| `CooldownViewerDocumentation.lua` | `ec05eb25cef1b3ec6870e78a95d470d5ff4eda7e` |
| `SecretPredicatesDocumentation.lua` | `97af2eb71809da82a1dfcdc6cccb147812bcc1fc` |
| `UnitDocumentation.lua` | `a0d34f0e5379af2bb4fc6399684d51eaf0c00d57` |
| `UnitRoleDocumentation.lua` | `194cc3ad91a328ce81491d77d732e49a920bd7fa` |
| `SpellDocumentation.lua` | `096033af83dee399c1c6eb2b805a339b6e6da535` |
| `ForbiddenAspectConstantsDocumentation.lua` | `434f6f61a487b471772387e88c128db2cb685718` |
| `CombatLogDocumentation.lua` | `7b5db6fcd30cfcf8e3ff2b5c1d67843232aaf84c` |
| `AuraContainerSharedDocumentation.lua` | `066832ee25b75f2924a887f60409b8104fc26a00` |
| `AuraContainerUtilDocumentation.lua` | `6eac23d2f2c8a6b6f711e22de8e682e3aac05b43` |
| `SpecializationInfoDocumentation.lua` | `2bd552e09e5d924610f22b18ba6d209d32b943e9` |
| `Blizzard_APIDocumentationGenerated.toc` | `bdd65e77ef8b1426e028a9a5c1ffef0a8f102d20` |

因此：

> **没有发现 69214 → 69283（live）与 69214 → 69273（ptr）之间的高风险 API 改动。**
> 此前确认的 Aura、CooldownViewer/CDM、Secret Predicate、Unit Identity、ForbiddenAspect、Spell/Cooldown、CombatLog、Inspect specialization 等规则，继续作为 **12.1.0 Live 当前 API 合同**。

---

# 1. Aura：12.1 正式服最重要的兼容变化

12.1 Live 中大量 `C_UnitAuras` API 已带：

```text
RequiresUnitAuraAccess = true
```

重点包括：

```lua
C_UnitAuras.CancelAuraByInstanceID
C_UnitAuras.DoesAuraHaveExpirationTime
C_UnitAuras.GetAuraApplicationDisplayCount
C_UnitAuras.GetAuraBaseDuration
C_UnitAuras.GetAuraDataByAuraInstanceID
C_UnitAuras.GetAuraDataByIndex
C_UnitAuras.GetAuraDataBySlot
C_UnitAuras.GetAuraDispelTypeColor
C_UnitAuras.GetAuraDuration
C_UnitAuras.GetAuraSlots
C_UnitAuras.GetBuffDataByIndex
C_UnitAuras.GetDebuffDataByIndex
C_UnitAuras.GetRefreshExtendedDuration
C_UnitAuras.GetUnitAuraInstanceIDs
C_UnitAuras.GetUnitAuras
C_UnitAuras.IsAuraFilteredOutByInstanceID
```

同时：

```text
UNIT_AURA
SecretWhenAurasRestricted = true
```

以及：

```text
UNIT_AURA_BLOCKED.auraInstanceID
SecretValue = true
```

### 实际影响

高风险：

- 单位框架 Buff/Debuff；
- 姓名板 Aura；
- Boss Debuff；
- 队友 Debuff；
- 根据 Aura 层数/持续时间触发提醒；
- 根据 Aura 是否存在做战斗逻辑。

如果功能只是显示 Aura，应优先使用：

```text
AuraContainer
ManagedAuraContainer
CustomAuraButton
C_AuraContainerUtil
```

不要尝试通过 nil、Lua error、table 长度、frame Show/Hide、child count 或其他 side channel 还原 Secret Aura。

---

# 2. Aura Sound 正式替换路径

12.0.7 的：

```lua
C_UnitAuras.AddPrivateAuraAppliedSound
C_UnitAuras.RemovePrivateAuraAppliedSound
C_UnitAuras.TriggerPrivateAuraShowDispelType
```

在 12.1 generated docs 中已移除。

当前正式路径：

```lua
C_UnitAuras.AddAuraSound
C_UnitAuras.RemoveAuraSound
```

`AddAuraSound` 带 restrictions；它不是读取 Secret Aura 原始数据的后门。

---

# 3. CooldownViewer / CDM 正式结构

12.1 Live 的 `CooldownViewerCooldown`：

```text
cooldownID
spellID
spellCategoryID
overrideSpellID
overrideTooltipSpellID
equipSlot
buffSlot
linkedSpellIDs
selfAura
hasAura
charges
isKnown
isInvisible
flags
category
```

关键类型：

```text
spellID: number | nil
spellCategoryID: number | nil
equipSlot: luaIndex | nil
buffSlot: luaIndex | nil
```

因此插件不能再假设每个 CooldownViewer 条目都一定有 `spellID`。

推荐来源判定：

```text
spellID
→ spellCategoryID
→ equipSlot
→ buffSlot
```

同时正式保留：

```lua
C_CooldownViewer.GetGroupBuffItems()
```

这会影响：

- CDM 配置读取；
- 技能/语音映射；
- 饰品/装备冷却；
- Buff Slot；
- Group Buff；
- 专精预设。

---

# 4. Unit Identity Secret 正式生效

12.1 Live 需要重点检查：

```text
UnitClass
UnitClassBase
UnitGroupRolesAssigned
UnitGroupRolesAssignedEnum
UnitGetAvailableRoles
UnitIsGroupAssistant
UnitIsGroupLeader
UnitIsRaidOfficer
UnitLeadsAnyGroup
UnitIsOwnerOrControllerOfUnit
UnitIsPVP
UnitPhaseReason
UnitHonorLevel
```

这些 API 在对应受限上下文中受 `SecretWhenUnitIdentityRestricted` 影响。

`UnitName` 使用更细粒度的：

```text
SecretWhenUnitNameIdentityRestricted
```

`UnitIsCharmed` / `UnitIsPossessed` 使用：

```text
SecretWhenUnitPossessionRestricted
```

不要对任意 nameplate / enemy / PvP unit 默认执行 Secret 值比较或分支。

---

# 5. Inspect 专精正式 namespaced API

推荐：

```lua
C_SpecializationInfo.GetInspectSpecialization(unit)
```

并遵守：

```text
SecretWhenUnitIdentityRestricted
SecretArguments = "AllowedWhenUntainted"
```

旧全局兼容入口不应继续作为新代码首选。

---

# 6. ForbiddenAspect 正式进入 Mainline 12.1

12.1 Live 已正式包含 `ForbiddenAspect` 模型。

不要只依赖：

```lua
frame:IsForbidden()
```

判断一个对象是否可以 Hook、RegisterEvent、SetParent、QueryFocus 等。

特别是 AuraButton / AuraContainer，不要通过：

```text
OnShow / OnHide
OnSizeChanged
IsShown
child count
anchor/layout 变化
事件注册状态
```

推断隐藏 Aura。

---

# 7. Spell / Cooldown

核心：

```lua
C_Spell.GetSpellCooldown
C_Spell.GetSpellCharges
```

其 Cooldown Secret 规则并不是 12.1 才新增，12.0.7 已经存在。

12.1 正式新增/变化包括：

```lua
C_Spell.GetLastCategoryCooldownSource(spellCategory)
```

以及：

```lua
iconID, originalIconID, conditionalIconID = C_Spell.GetSpellTexture(spellID)
```

不要把既有 Cooldown Secret 规则错误归因为“12.1 新封锁”。

---

# 8. CombatLog

Live 69214 与 PTR 69214 的 `CombatLogDocumentation.lua` Blob SHA 完全一致。

当前没有发现 12.1 上线当天对核心 CombatLog API 再做临时重构。

已有 restriction 仍需遵守，但普通战斗日志统计不是这次最高风险迁移区。

---

# 9. 69214 最后新增的低风险 API

69214 相对 69189 的 generated API 变化仍是：

```lua
C_HousingBlueprint.UpdateBlueprintStringFromInput(inputShareCode)
```

以及：

```text
RecentAlliesSearchInfo.searchText
cstring → string
```

这些已经进入 Live 69214，没有看到正式服撤回或再次改签名。

---

# 10. 正式服插件审查优先级

| 功能类型 | 风险 |
|---|---|
| Aura/Buff/Debuff 扫描与战斗判断 | 🔴 极高 |
| Aura 显示 / 单位框架 / 姓名板 | 🔴 极高 |
| CDM/CooldownViewer 数据读取与语音映射 | 🟠 高 |
| UnitName/Class/Role/GUID 类判断 | 🟠 高 |
| Blizzard AuraButton/受保护 UI Hook | 🟠 高 |
| Spell/Cooldown 一般显示 | 🟡 中 |
| CombatLog 统计 | 🟢 较低 |
| Housing/RecentAllies | 🟢 低 |

---

# 11. 后续维护规则

从现在起：

- Retail 正式开发以 `live` **12.1.0.69283** 为当前基线；
- PTR 文件只用于追踪后续 hotfix / 12.1.x / 12.1.5 / 12.2 预发布变化；
- 如果 `live` build 继续增加，即使仍叫 12.1.0，也必须重新比较 generated docs；
- 不要用 build number 写业务 feature flag，build 只作为文档 provenance；
- 所有 Aura、Unit、Spell/Cooldown、secure/forbidden API 决策必须读取当前目标 build 的 restriction metadata。

## 相关参考

- `wow-12.0.7-to-12.1-api-migration-zhCN.md`：12.0.7 → 12.1 的历史迁移差异与 PTR build 演进。
- `wow-12-api-source-rules.md`：API 来源和核实规则。
- `wow-12-secret-value-taint.md`：Secret / Taint / Forbidden Object 设计规则。

**当前结论：PTR 69214 中已经确认的关键 12.1 API 规则，已被 Live 69214 正式保留；Live 69283 / PTR 69273 复查未发现任何高风险 API 改动，上述规则继续作为 12.1.0 当前 API 合同有效。**