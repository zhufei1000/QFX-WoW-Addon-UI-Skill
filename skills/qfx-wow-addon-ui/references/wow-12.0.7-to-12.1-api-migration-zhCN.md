# WoW 12.0.7 → 12.1.0 PTR API 迁移参考

用于把 Retail 12.0.7 插件迁移、审查或适配到 12.1.0 PTR。

## 当前核实基线

最后核实：**2026-08-11**。

- 正式服 `live`：**12.0.7.68974**（Gethe live 当前仍未切到 12.1.0）
- PTR `ptr`：**12.1.0.69214**
- PTR 当前 HEAD：`9eb0468a36ff0fd9f51d74ae179b201f5b2e8326`

本文描述的是 **12.1.0.69214 PTR 相对 12.0.7.68974 live 的当前差异**。PTR 不是最终正式服 API；正式服 `live` 更新到 12.1.0 后仍必须重新做一次 `live → live` 最终 diff。

主要事实来源：

1. `Gethe/wow-ui-source` 的 `live` / `ptr` 分支 `version.txt`。
2. 同分支 `Interface/AddOns/Blizzard_APIDocumentationGenerated/`。
3. 同分支 FrameXML/UI source，用于确认 Blizzard 自己如何使用接口。
4. PTR build 之间直接比较 commit，避免只依赖旧 PTR 周报或 wiki 汇总。

> Restriction metadata 是 API 合同的一部分。比较 API 时必须同时检查 `HasRestrictions`、`SecretArguments`、`SecretReturns`、`SecretValue`、`ConditionalSecretContents`、`Requires*` 和 `SecretWhen*`。

---

# 一、当前 PTR build 链路

已核对的最后阶段 build：

```text
12.1.0.68914
→ 12.1.0.69027
→ 12.1.0.69111
→ 12.1.0.69189
→ 12.1.0.69214
```

## 69027

主要是 WorldMap `.zmp` 资源清理，没有 generated API 文档变化。

## 69111

主要 API/UI 变化：

- AuraContainer 增加 Stealable / NotStealable 显示过滤；
- `SecondsFormatter` 增加取整策略；
- 新增 `SecretWhenUnitPossessionRestricted`；
- `UnitIsCharmed` / `UnitIsPossessed` 改用 Possession Secret predicate；
- Texture Script Object 增加 SVG API；
- Housing UI 少量新增查询接口。

## 69189

主要 generated API 变化：

```lua
C_Browser.CloseFullscreenBrowser()
C_DelvesUI.HasActiveLFGLair()
C_DelvesUI.IsInLair()
```

新增同步事件：

```text
FULLSCREEN_BROWSER_SPINNER_SHOW
FULLSCREEN_BROWSER_SPINNER_HIDE
```

以及：

```text
UnitHonorLevel
SecretWhenUnitIdentityRestricted = true
```

## 69214：当前最新 PTR

`69189 → 69214` 只有 **两个 generated API 文件**发生变化：

```text
HousingBlueprintUIDocumentation.lua
RecentAlliesDocumentation.lua
```

### 新增：Housing Blueprint 输入规范化接口

```lua
C_HousingBlueprint.UpdateBlueprintStringFromInput(inputShareCode)
```

当前签名：

```text
MayReturnNothing = true
SecretArguments = "AllowedWhenUntainted"

Arguments:
  inputShareCode: cstring

Returns:
  updatedShareCode: string
```

用途从 Blizzard 自身 FrameXML 看，是在导入 Blueprint share code 前对用户输入进行更新/规范化。

### 变化：Recent Allies 搜索文本类型

结构：

```text
RecentAlliesSearchInfo
```

字段：

```text
searchText
```

由：

```text
cstring
```

改为：

```text
string
```

其余字段保持：

```text
isOnline: bool
isDND: bool
isAFK: bool
isOffline: bool
interests: RecentAlliesFriendTag[]
```

### 69214 没有变化的高风险领域

这次 build 没有修改下列 generated API 文档，因此此前 69189 的结论继续有效：

```text
UnitAuraDocumentation.lua
AuraContainerSharedDocumentation.lua
AuraContainerUtilDocumentation.lua
CooldownViewerDocumentation.lua
SpellDocumentation.lua
UnitDocumentation.lua
UnitRoleDocumentation.lua
SecretPredicatesDocumentation.lua
CombatLogDocumentation.lua
```

也就是说，**69214 没有再次改变 Aura、CDM/CooldownViewer、Spell Cooldown、Unit Secret、ForbiddenAspect 或 CombatLog 核心规则。**

---

# 二、12.0.7 → 12.1 核心结论

12.1 的核心不是“全部 WoW API 重写”，而是继续收紧敏感战斗数据访问，同时提供 Blizzard 管理的安全显示层。

优先级：

| 领域 | 12.0.7 → 12.1 变化 | 风险 |
|---|---|---|
| Aura / Buff / Debuff | 数据访问门禁、事件 Secret、新显示框架 | 🔴 极高 |
| 团队/姓名板 Aura 显示 | 旧式手动枚举应迁移显示架构 | 🔴 极高 |
| Unit 身份/职责/控制关系 | Secret domain 扩大/细分 | 🟠 高 |
| AuraButton / Script Object | Forbidden Aspect 粒度更细 | 🟠 高 |
| CooldownViewer / CDM | 条目来源和结构字段扩展 | 🟠 高 |
| Spell / Cooldown | 少量新增 API/返回值；既有限制继续存在 | 🟡 中 |
| SecondsFormatter / Texture | UI 显示辅助能力扩展 | 🟡 中低 |
| Housing / RecentAllies / Browser / Delves | 独立低风险接口变化 | 🟢 低 |
| CombatLog | 当前核心 generated API 未重构 | 🟢 低 |

---

# 三、Aura：访问从“结果可能 Secret”升级为“调用有显式门禁”

12.0.7 已存在：

```text
SecretWhenUnitAuraRestricted = true
```

12.1 进一步在大量 Aura API 上加入：

```text
RequiresUnitAuraAccess = true
```

当前 69214 中完整重点列表仍为：

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

12.0.7 live 中上述 `RequiresUnitAuraAccess` 标记不存在；这是 12.1 迁移的核心边界之一。

## `RequiresValidUnitAuraInstance` 不是 12.1 新增

它在 12.0.7 已经存在，作用不同：

```text
RequiresUnitAuraAccess
→ 是否允许访问这类 Aura 数据

RequiresValidUnitAuraInstance
→ 传入的 auraInstanceID 是否有效
```

不要把两者混为一谈。

## 迁移原则

如果功能只是显示 Aura：

```text
优先 AuraContainer / ManagedAuraContainer / CustomAuraButton
```

如果功能需要依据 Aura 做战斗判断：

```text
必须先确认该值在当前上下文是否允许 addon 消费
```

不要依靠 `pcall`、nil、错误行为或 side channel 还原 Secret Aura。

---

# 四、`GetUnitAuras()` 的 table 不代表内容安全

12.0.7 已有：

```text
ConditionalSecretContents = true
```

12.1 又增加：

```text
RequiresUnitAuraAccess = true
```

因此以下行为不能默认安全：

```lua
#auras
ipairs(auras)
table.sort(auras)
aura.spellId == spellID
```

也不要通过：

- table 长度；
- 遍历是否成功；
- nil/非 nil；
- Lua error；
- frame 数量/布局变化；

推断 Secret Aura。

`GetUnitAuras()` 的 `maxCount` / `sortRule` / `sortDirection` 在 12.0.7 已经存在，不应误写为 12.1 新增。

---

# 五、`UNIT_AURA` 事件也进入 Restriction 模型

12.1 当前：

```text
UNIT_AURA
SecretWhenAurasRestricted = true
```

并且：

```text
UNIT_AURA_BLOCKED.auraInstanceID
SecretValue = true
```

旧式链路：

```text
UNIT_AURA
→ updateInfo
→ auraInstanceID
→ AuraData
→ spellID / duration / stacks
→ 战斗判断
```

在 Restricted 场景中不能再默认整条链路可供 addon 消费。

---

# 六、SpellID / SpellName 查询不是 Aura Restriction 绕过方案

以下接口继续受 `RequiresNonSecretAura` 等约束：

```lua
C_UnitAuras.GetUnitAuraBySpellID
C_UnitAuras.GetPlayerAuraBySpellID
C_UnitAuras.GetAuraDataBySpellName
```

不要用已知 spellID/name 列表探测 Secret Aura 是否存在。

---

# 七、AuraContainer / CustomAuraButton

12.1 新显示体系主要由：

```text
AuraContainer
ManagedAuraContainer
CustomAuraButton
C_AuraContainerUtil
```

组成。

常用配置处理器：

```lua
C_AuraContainerUtil.ProcessAuraTooltipBackdropOptions
C_AuraContainerUtil.ProcessAuraTooltipNineSliceOptions
C_AuraContainerUtil.ProcessAuraTooltipTextureSliceOptions
C_AuraContainerUtil.ProcessCustomAuraButtonApplicationBarOptions
C_AuraContainerUtil.ProcessCustomAuraButtonApplicationCountOptions
C_AuraContainerUtil.ProcessCustomAuraButtonDispelTypeTextOptions
C_AuraContainerUtil.ProcessCustomAuraButtonDispelTypeTextureOptions
C_AuraContainerUtil.ProcessCustomAuraButtonDurationBarOptions
C_AuraContainerUtil.ProcessCustomAuraButtonDurationTextOptions
```

重要枚举：

```text
CustomAuraButtonDispelTypeTextureStyle
- Border
- BorderWithIcon
- Icon
- PreserveAsset
- CustomAsset

CustomAuraButtonUpdateMode
- Assignment
- Update

CustomAuraButtonDispelTypeStealableFilter
- Stealable
- NotStealable
```

`CustomAuraButtonDispelTypeTextureOptions` 重点字段：

```text
showAlways
showWhenHarmful
showWhenHelpful
showWithoutDispelType
stealableFilter
style
customDispelAssetMap
customDispelColorMap
customDispelColorCurve
```

推荐思路：

```text
Blizzard 跟踪/过滤/Assignment
→ AuraContainer/AuraButton 承载受控数据
→ Addon 配置允许的样式和布局
```

而不是：

```text
Addon 自己读取全部 AuraData
→ 自己筛选/排序/推断
```

---

# 八、Aura Sound API

12.0.7 存在：

```lua
C_UnitAuras.AddPrivateAuraAppliedSound
C_UnitAuras.RemovePrivateAuraAppliedSound
C_UnitAuras.TriggerPrivateAuraShowDispelType
```

当前 12.1 PTR 中旧接口已从 generated docs 移除，新的路径：

```lua
C_UnitAuras.AddAuraSound
C_UnitAuras.RemoveAuraSound
```

`AddAuraSound` 带 Restrictions；这不是获得 Secret Aura 原始数据的后门。

---

# 九、Group Buff

`C_UnitAuras` 当前提供：

```lua
C_UnitAuras.GetGroupBuffVisualAlerts
C_UnitAuras.SetGroupBuffVisualAlerts
C_UnitAuras.GetHiddenGroupBuffs
C_UnitAuras.SetHiddenGroupBuffs
```

相关事件：

```text
GROUP_BUFF_VISUAL_ALERTS_CHANGED
HIDDEN_GROUP_BUFFS_CHANGED
```

`C_CooldownViewer` 当前提供：

```lua
C_CooldownViewer.GetGroupBuffItems()
```

返回：

```text
GroupBuffItem[]
```

字段：

```text
spellID
name
iconID
flags
isKnown
```

---

# 十、CooldownViewer / CDM

当前 69214 的 `CooldownViewerCooldown` 结构与 69189 相同：

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
charges: bool
isInvisible: bool
```

因此不要假设：

```lua
info.spellID
```

永远存在。

正确流程：

```text
spellID
→ spellCategoryID
→ equipSlot
→ buffSlot
```

按实际来源处理。

这对 CDM 数据读取、饰品/装备冷却、Buff Slot、Group Buff、语音映射都很重要。

---

# 十一、Unit Identity Secret

12.1 相比 12.0.7 新加入/强化 `SecretWhenUnitIdentityRestricted` 的重点函数包括：

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

当前 69214 没有再修改这些规则。

---

# 十二、`UnitName()` 使用独立 Name Identity predicate

12.0.7：

```text
UnitName
SecretWhenUnitIdentityRestricted
```

12.1：

```text
UnitName
SecretWhenUnitNameIdentityRestricted
```

它与普通 Unit Identity predicate 相似，但 PvP 玩家单位存在专门例外。

---

# 十三、Inspect 专精 API 迁入 namespace

推荐：

```lua
C_SpecializationInfo.GetInspectSpecialization(unit)
```

当前带：

```text
SecretWhenUnitIdentityRestricted = true
SecretArguments = "AllowedWhenUntainted"
```

旧：

```lua
GetInspectSpecialization(unit)
```

目前仍有 Deprecated 兼容入口，但新代码应使用 namespaced API。

---

# 十四、Possession Secret

69111 新增：

```text
SecretWhenUnitPossessionRestricted
```

并应用到：

```lua
UnitIsCharmed(unit)
UnitIsPossessed(unit)
```

这是 Secret domain 细分，不是简单的“所有场景限制更严格”。

---

# 十五、`UnitIsUnit()` 限制不是 12.1 新增

12.0.7 已存在：

```text
RequiresComparableUnitTokens = true
SecretWhenUnitComparisonRestricted = true
```

不要通过大量 `UnitIsUnit(a, b)` 建立身份比较矩阵推断 Secret unit。

---

# 十六、ForbiddenAspect / SecretAspect

`ForbiddenAspect` 是 12.1 新增，当前主要值：

```text
SetToDefaults = 1
ScriptBindings = 2
UntrustedScriptExecution = 4
UntrustedLayoutScriptExecution = 8
EventRegistrations = 16
AlwaysPropagateInput = 32
ScriptedInput = 64
QueryFocus = 128
ChangeAnimationTarget = 256
RemoveSecretAspects = 512
ChangeParent = 1024
```

`SecretAspect` 在 12.1 新增：

```text
RadialProgress = 8388608
```

不要只用：

```lua
frame:IsForbidden()
```

判断全部操作是否安全；现在需要考虑对象具体 Forbidden Aspect。

AuraButton / AuraContainer 不得通过以下 side channel 推断隐藏 Aura：

```text
OnShow / OnHide
OnSizeChanged
child count
IsShown
focus/input query
event registration
anchor/layout
reparent
```

---

# 十七、Spell / Cooldown

Cooldown Secret 化不是 12.1 新增。12.0.7 已有：

```text
C_Spell.GetSpellCooldown → SecretWhenCooldownsRestricted
C_Spell.GetSpellCharges → SecretWhenCooldownsRestricted
C_Spell.GetSpellCastCount → SecretWhenCooldownsRestricted
C_Spell.GetSpellDisplayCount → SecretWhenCooldownsRestricted
```

12.1 新增：

```lua
C_Spell.GetLastCategoryCooldownSource(spellCategory)
```

返回：

```text
spellID
itemID
```

并受 Cooldown restriction。

`GetSpellTexture()` 增加第三个返回值：

```lua
iconID, originalIconID, conditionalIconID = C_Spell.GetSpellTexture(spellID)
```

另有：

```lua
C_Spell.GetSpellDescriptionForItemLocation(spellIdentifier, itemLocation)
```

**69214 没有修改 `SpellDocumentation.lua`，因此 `C_Spell.GetSpellCooldown()` 等核心规则相对 69189 无变化。**

---

# 十八、SecondsFormatter

69111 新增：

```text
GetRounding()
SetRounding(rounding)
```

枚举：

```text
SecondsFormatterRounding.RoundUp
SecondsFormatterRounding.Truncate
```

用于让 Aura/Cooldown 等时间显示更贴近 Blizzard 官方格式。

---

# 十九、Texture SVG

69111 新增：

```text
ClearSVG()
SetSVG(svgAsset) -> success: bool
```

这是 UI 能力扩展，不是战斗数据 API。

---

# 二十、Browser / Delves

69189 新增：

```lua
C_Browser.CloseFullscreenBrowser()
C_DelvesUI.HasActiveLFGLair()
C_DelvesUI.IsInLair()
```

事件：

```text
FULLSCREEN_BROWSER_SPINNER_SHOW
FULLSCREEN_BROWSER_SPINNER_HIDE
```

69214 没有再修改这些接口。

---

# 二十一、Housing / Recent Allies

## 69111

新增低风险 Housing 查询：

```text
HousingBlueprintUI.CanExportRoom(roomGUID) -> canExport
HousingLayoutUI.RoomHasStairs(roomGUID) -> hasStairs
```

## 69214

新增：

```lua
C_HousingBlueprint.UpdateBlueprintStringFromInput(inputShareCode)
```

结构变化：

```text
RecentAlliesSearchInfo.searchText
cstring → string
```

这些变化与 Aura/Secret/CDM 主迁移无关，但属于当前 PTR 真实 API 差异，应记录。

---

# 二十二、CombatLog

当前 69214 没有修改 `CombatLogDocumentation.lua`。

`C_CombatLogSecure` 也不是 12.1 才新增，12.0.7 已存在。

因此：

- `COMBAT_LOG_EVENT_UNFILTERED` 统计；
- 施法成功历史统计；
- 打断次数统计；
- 非 Secret combat log 文本处理；

目前优先级低于 Aura / Unit / CDM，但仍必须遵守既有限制。

---

# 二十三、不要错误归因

以下不是 12.1 新增：

```text
canaccessvalue / canaccessallvalues / canaccesstable / canaccesssecrets
UnitIsUnit comparable-token restriction
C_Spell.GetSpellCooldown 的 Cooldown Secret 规则
C_CombatLogSecure
RequiresValidUnitAuraInstance
GetUnitAuras 的 maxCount/sortRule/sortDirection
```

69027 删除 WorldMap `.zmp` 也是资源清理，不等于 API 删除。

---

# 二十四、迁移设计建议

## Aura

不要：

```text
AuraContainer
→ 试图还原旧 AuraData
→ 继续旧 scanner
```

应：

```text
12.0.7：旧数据/显示路径
12.1：AuraContainer/ManagedAuraContainer/受支持显示路径
```

## Compat

版本敏感 API 集中到兼容层：

```lua
QFX.Compat = QFX.Compat or {}

function QFX.Compat.GetSpellTextureInfo(spellID)
    -- target-build verified implementation
end

function QFX.Compat.SupportsAuraContainer()
    -- capability/client-family check
end
```

不要把文档 build number 当永久 runtime feature flag。

## Restriction metadata

审查 API 必须同时看：

```text
Arguments
Returns
HasRestrictions
SecretArguments
SecretReturns
SecretValue
ConditionalSecret
ConditionalSecretContents
RequiresUnitAuraAccess
RequiresNonSecretAura
RequiresUnitIdentityAccess
RequiresComparableUnitTokens
SecretWhen...
```

## CDM

必须允许：

```text
spellID == nil
```

并检查：

```text
spellCategoryID
equipSlot
buffSlot
```

## Preview

设置界面需要 Aura/Boss/队友等演示数据时使用明确的 fake/preview data，不从受限战斗环境提取数据。

---

# 二十五、迁移测试清单

至少测试：

- 登录；
- `/reload`；
- 非战斗；
- 普通战斗；
- 副本战斗；
- Mythic+ / 团本；
- PvP（如果涉及）；
- `target` / `focus` / `mouseover`；
- `party1..4` / `raid1..40`；
- `nameplateX`；
- 宠物/守护者/魅惑/附身单位；
- CooldownViewer spell/category/equipSlot/buffSlot/Group Buff 条目；
- 多次进出战斗；
- 与其他修改 Blizzard Frame 的插件共同运行。

重点观察：

```text
a secret boolean value
a secret number value
execution tainted by
forbidden
```

以及：

```text
RequiresUnitAuraAccess
RequiresNonSecretAura
SecretWhenUnitIdentityRestricted
SecretWhenUnitNameIdentityRestricted
SecretWhenUnitPossessionRestricted
ForbiddenAspect
```

相关 Lua error。

---

# 二十六、给 Codex 的核对顺序

1. 读取目标分支 `version.txt`。
2. 读取目标 build generated API documentation。
3. 比较 restriction metadata，不只看函数名。
4. 判断限制是否在旧 live 已存在，避免错误归因。
5. Aura 显示优先检查 AuraContainer / CustomAuraButton。
6. Unit 检查 Identity / NameIdentity / Possession Secret domain。
7. Script Object 检查 Forbidden Aspect。
8. CooldownViewer 检查 `spellID` nilability、category、equipSlot、buffSlot、Group Buff。
9. Spell/Cooldown 先确认是否只是既有 Secret 规则延续。
10. CombatLog 只有实际 diff 才改。
11. 检查最后 PTR commit，避免停在旧周 build。
12. 输出结论时区分：**已确认 / PTR-only / 待正式服 live 验证**。

---

# 二十七、当前结论

截至 **2026-08-11 / PTR 12.1.0.69214**：

- `live` 镜像当前仍是 **12.0.7.68974**；
- PTR 最新公开 UI/API HEAD 是 **12.1.0.69214**；
- `69189 → 69214` 只有两个 generated API 文档变化：Housing Blueprint 和 Recent Allies；
- Aura、AuraContainer、CooldownViewer/CDM、Spell/Cooldown、Unit Secret、Secret predicates、ForbiddenAspect、CombatLog 相对 69189 **没有新变化**；
- 69214 新增 `C_HousingBlueprint.UpdateBlueprintStringFromInput()`；
- 69214 将 `RecentAlliesSearchInfo.searchText` 从 `cstring` 改为 `string`；
- 对战斗插件影响最大的仍是 **Aura access boundary + AuraContainer + Unit Identity Secret + CooldownViewer 数据结构扩展**。

**正式服 `live` 分支切到 12.1.0 后，必须再做最终 `12.0.7 live → 12.1.0 live` 全量 diff。**
