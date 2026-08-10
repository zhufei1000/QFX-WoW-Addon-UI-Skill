# WoW 12.0.7 → 12.1.0 PTR API 迁移参考

用于把 Retail 12.0.7 插件迁移、审查或适配到 12.1.0 PTR。

## 当前核实基线

最后核实：**2026-08-10**（当日基于 `Gethe/wow-ui-source` live/ptr 分支 generated docs 逐条复核，live 与 ptr 全部关键 API 已做 diff）。

- 正式服 `live`：**12.0.7.68974**
- PTR `ptr`：**12.1.0.69189**（截至 2026-08-10 仍是最新 PTR build，无 692xx 后续 build 公开）
- PTR 当前 HEAD：`a520b6c27bb897e6be2333b6cc2be36d52c7c11b`

截至本次核实，Gethe `live` 分支仍未切换到 12.1.0。本文描述的是 **12.1.0.69189 PTR 相对 12.0.7.68974 live 的当前差异**，不是对最终正式服 API 冻结状态的承诺。

正式服上线后必须重新做一次：

```text
12.0.7 live → 12.1.0 live
```

最终 diff；只有那次结果才可以标记为“12.1.0 正式服最终 API”。

主要事实来源：

1. `Gethe/wow-ui-source` 对应 `live` / `ptr` 分支的 `version.txt`。
2. 同分支 `Interface/AddOns/Blizzard_APIDocumentationGenerated/`。
3. 同分支 FrameXML/UI source，用于确认 Blizzard 自己如何消费这些 API。
4. PTR build 之间直接比较 commit，不只依赖 wiki 汇总或旧 PTR 周报。

> 不要仅根据 GitHub branch compare 中“某文件 added/modified”就判断 API 是新增。`live` 与 `ptr` 历史可能分叉，必须比较实际 generated documentation 内容和 restriction metadata。

---

# 一、上线前最后 PTR build 链路

当前已经核对：

```text
12.1.0.68914
→ 12.1.0.69027
→ 12.1.0.69111
→ 12.1.0.69189
```

## 69027

`68914 → 69027` 基本是 WorldMap `.zmp` 资源从 UI code list 中移除，没有新的 generated API 文档变化。

因此不要把 69027 当成一次 API 大改。

## 69111

`69027 → 69111` 是最后阶段真正值得插件作者注意的一轮，主要包括：

- AuraContainer 增加 Stealable / NotStealable 显示过滤；
- `SecondsFormatter` 增加秒数取整策略；
- 新增 `SecretWhenUnitPossessionRestricted`；
- `UnitIsCharmed` / `UnitIsPossessed` 改用新的 Possession Secret predicate；
- Texture Script Object 增加 SVG API；
- Housing UI 少量新增查询接口。

## 69189

`69111 → 69189` 是当前 PTR 最新提交。生成 API 的主要变化：

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

因此 **69189 没有再次重写 Aura / Spell / Cooldown 核心架构**，主要是补充少量 API，并继续细化 Unit identity secrecy。

---

# 二、12.0.7 → 12.1 核心结论

这次变化不是“所有 WoW API 全部重做”，核心是进一步强化敏感战斗数据边界，并提供由 Blizzard 承载敏感数据的显示对象。

最重要的变化顺序：

1. **Aura 原始数据访问进一步收紧**：大量 `C_UnitAuras` 查询增加 `RequiresUnitAuraAccess`。
2. **`UNIT_AURA` 本身进入 Aura restriction 模型**。
3. **AuraContainer / ManagedAuraContainer / CustomAuraButton 成为 12.1 的重点显示路径**。
4. **Unit 身份、职业、职责、荣誉等级、控制/附身关系的 Secret domain 扩大或细分**。
5. **Forbidden Object 进一步细分为 Forbidden Aspects**。
6. **CooldownViewer / CDM 数据结构实际扩展**，`spellID` 不再保证存在，并增加 category / equipment / buff slot 等来源。
7. **Spell/Cooldown 核心 API 在最后几个 PTR build 没有再次大改**；已有 Cooldown Secret 规则继续存在。
8. **CombatLog 不是当前 12.1 迁移最高风险区**。

## 风险优先级

| 领域 | 12.0.7 → 12.1 变化 | 风险 |
|---|---|---|
| Aura / Buff / Debuff | 数据访问门禁、事件 Secret、新显示框架 | 🔴 极高 |
| 团队/姓名板 Aura 显示 | 旧式手动枚举应优先迁移显示架构 | 🔴 极高 |
| Unit 身份/职业/职责/控制关系 | Secret domain 扩大/细分 | 🟠 高 |
| AuraButton / Blizzard Script Object | Forbidden Aspect 粒度更细 | 🟠 高 |
| CooldownViewer / CDM | 条目来源和结构字段扩展 | 🟠 高 |
| Spell / Cooldown | 小量新增 API/返回值；原有限制继续存在 | 🟡 中 |
| SecondsFormatter / Texture | UI 显示辅助能力扩展 | 🟡 中低 |
| Browser / Delves / Housing | 少量独立新增接口 | 🟢 低 |
| CombatLog | 当前核心 generated API 基本未重做 | 🟢 低 |

---

# 三、Aura：从“结果可能 Secret”升级为“访问本身有前置条件”

12.0.7 中，很多 Aura API 已经存在：

```text
SecretWhenUnitAuraRestricted = true
```

因此 Aura Secret 并不是 12.1 才第一次出现。

12.1 当前 PTR 进一步在大量查询上加入：

```text
RequiresUnitAuraAccess = true
```

当前 69189 中带 `RequiresUnitAuraAccess = true` 的完整列表（16 个，经 live 12.0.7 与 ptr 12.1.0 生成文档逐条比对确认，live 中该标记数量为 0）：

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

注意：`GetAuraDuration` / `GetAuraBaseDuration` / `GetAuraApplicationDisplayCount` / `DoesAuraHaveExpirationTime` / `GetRefreshExtendedDuration` / `GetAuraDispelTypeColor` / `CancelAuraByInstanceID` 这类"读时长 / 读层数 / 取消光环"函数在 12.0.7 时**没有** `RequiresUnitAuraAccess`，12.1 全部纳入门禁。

## 既有 precondition：`RequiresValidUnitAuraInstance`

`RequiresValidUnitAuraInstance`（`FailureMode = "ReturnNothing"`）在 12.0.7 已存在，**不是** 12.1 新增。

它和 `RequiresUnitAuraAccess` 是两层不同检查：

- `RequiresUnitAuraAccess`：决定当前调用者/环境是否有 Aura 数据访问权；
- `RequiresValidUnitAuraInstance`：决定传入的 `auraInstanceID` 是否是合法有效的 Aura 实例（无效时函数直接返回 nil，而不是抛错）。

迁移时不要把这两个 precondition 混为一谈：前者是访问门禁，后者是参数合法性校验。

## 迁移含义

12.0.7 更接近：

```text
允许调用
→ 某些返回值在受限场景成为 Secret
```

12.1 进一步变为：

```text
先满足 UnitAura access
→ 再允许访问这类 Aura 数据
```

因此不要把旧代码简单包一层：

```lua
if aura then
    ...
end
```

或者：

```lua
pcall(...)
```

就当成 12.1 兼容方案。

如果功能目标只是**显示 Aura**，优先评估 AuraContainer / ManagedAuraContainer / CustomAuraButton，而不是继续维护旧式 Aura scanner。

---

# 四、`GetUnitAuras()`：`ConditionalSecretContents` 不是新变化，但访问门禁是

12.0.7 的：

```lua
C_UnitAuras.GetUnitAuras(...)
```

已经存在：

```text
ConditionalSecretContents = true
```

所以外层返回 Lua table 并不代表内容一定可以安全读取。

12.1 当前 PTR 在此基础上继续加入：

```text
RequiresUnitAuraAccess = true
```

`GetUnitAuras()` 的参数签名（`maxCount` / `sortRule` / `sortDirection`）在 12.0.7 已经存在，**不是** 12.1 新增，不要错误归因：

```text
unit: UnitTokenRestrictedForAddOns (NeverSecret)
filter: AuraFilters
maxCount: number | nil
sortRule: UnitAuraSortRule = "Unsorted"
sortDirection: UnitAuraSortDirection = "Normal"
```

`UnitAuraSortRule` 当前枚举值（7 个，12.0.7 已存在）：

```text
Unsorted
Default
BigDefensive
Expiration
ExpirationOnly
Name
NameOnly
```

`UnitAuraSortDirection` 当前枚举值（2 个，12.0.7 已存在）：

```text
Normal
Reverse
```

因此以下操作都不能默认安全：

```lua
#auras
ipairs(auras)
table.sort(auras)
aura.spellId == spellID
```

也不要：

- 序列化/保存受限 Aura 内容；
- 通过 table 长度推断隐藏 Aura；
- 通过遍历是否成功推断隐藏 Aura；
- 通过错误/无错误行为推断 Aura 是否存在。

`GetUnitAuras()` 不是绕过单个 Aura API restriction 的后门。

---

# 五、`UNIT_AURA` 事件本身也进入 restriction 模型

## 12.0.7

`UNIT_AURA` 没有当前 12.1 的：

```text
SecretWhenAurasRestricted
```

`UNIT_AURA_BLOCKED.auraInstanceID` 也没有当前的显式 `SecretValue` 标记。

## 12.1 PTR 69189

当前 generated docs：

```text
UNIT_AURA
SecretWhenAurasRestricted = true
```

同时：

```text
UNIT_AURA_BLOCKED
auraInstanceID
SecretValue = true
```

旧插件常见链路：

```text
UNIT_AURA
→ updateInfo
→ auraInstanceID
→ AuraData
→ 比较 spellID / duration / stacks
→ 决定提示或动作
```

在 Restricted 场景中不能再默认整条链路都可供 addon 消费。

尤其不要把以下行为当 side channel：

```text
事件是否触发
updateInfo 是否可迭代
auraInstanceID 是否出现
API 是否报错
AuraButton 是否 Show/Hide
子框体数量
布局尺寸变化
```

---

# 六、按 SpellID / SpellName 查询不是 Secret Aura 绕过方案

以下 API 在 12.0.7 就已经带 `RequiresNonSecretAura` 等约束，12.1 继续保留：

```lua
C_UnitAuras.GetUnitAuraBySpellID
C_UnitAuras.GetPlayerAuraBySpellID
C_UnitAuras.GetAuraDataBySpellName
```

因此不要通过一组已知 SpellID 做探针：

```lua
for _, spellID in ipairs(importantAuras) do
    local aura = C_UnitAuras.GetUnitAuraBySpellID(unit, spellID)
    -- 不要把 nil / 非 nil 当作 Secret aura presence probe
end
```

`RequiresNonSecretAura` 是安全边界，不是普通 nil 条件。

---

# 七、AuraContainer / CustomAuraButton：12.1 的受支持显示路径

12.1 PTR 有独立 generated docs：

```text
AuraContainerSharedDocumentation.lua
AuraContainerUtilDocumentation.lua
```

`C_AuraContainerUtil` 当前提供多种显示配置处理器，例如：

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

当前重要枚举：

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
```

## 69111 新增 Stealable 显示过滤

当前 69189 已包含：

```text
CustomAuraButtonDispelTypeStealableFilter
- Stealable
- NotStealable
```

`CustomAuraButtonDispelTypeTextureOptions` 当前完整字段（经 69189 生成文档逐条核实）：

```text
showAlways: bool = false            -- 忽略其他条件强制显示
showWhenHarmful: bool = true
showWhenHelpful: bool = false
showWithoutDispelType: bool = false
stealableFilter: CustomAuraButtonDispelTypeStealableFilter | nil
style: CustomAuraButtonDispelTypeTextureStyle = "BorderWithIcon"
customDispelAssetMap: table<string, CustomAuraButtonDispelTypeTextureAsset> | nil
customDispelColorMap: table<string, colorRGB> | nil
customDispelColorCurve: LuaColorCurveObject | nil
```

含义要点：

- `showAlways = true` 时忽略其他显示条件，强制显示 dispel type texture；
- `stealableFilter` 可以限制只对可偷取或不可偷取 Aura 显示相应驱散/偷取视觉；
- `style` 控制纹理风格（Border / BorderWithIcon / Icon / PreserveAsset / CustomAsset）；
- `customDispelAssetMap` / `customDispelColorMap` / `customDispelColorCurve` 允许自定义各驱散类型的资产与着色曲线（仅 `CustomAsset` 风格生效）。

这说明 Blizzard 继续增加“插件可以控制怎样显示”的能力，而不是恢复“插件任意读取原始 Aura 再自己判断”的模式。

## 推荐架构

旧式：

```text
Addon 读取 AuraData
→ 自己筛选
→ 自己排序
→ 自己计算持续时间/层数
→ 自己创建图标
```

12.1 推荐方向：

```text
Blizzard 跟踪/过滤/Assignment
→ AuraContainer / AuraButton 承载数据
→ Addon 配置允许的样式、过滤和布局
```

---

# 八、Aura Sound API 发生替换/扩展

12.0.7 生成文档中存在：

```lua
C_UnitAuras.AddPrivateAuraAppliedSound
C_UnitAuras.RemovePrivateAuraAppliedSound
C_UnitAuras.TriggerPrivateAuraShowDispelType
```

当前 12.1 PTR 中这三个旧 API **已从生成文档移除**（不是 Deprecated 别名，而是删除）：

```lua
C_UnitAuras.AddAuraSound
C_UnitAuras.RemoveAuraSound
```

并使用新的 Aura sound trigger/info 结构（`AddAuraSound` 带 `HasRestrictions = true`，`SecretArguments = "AllowedWhenUntainted"`）。

迁移注意：

- **不要继续调用 12.0.7 的 `AddPrivateAuraAppliedSound` / `RemovePrivateAuraAppliedSound` / `TriggerPrivateAuraShowDispelType`**，这些在 12.1 PTR 已不存在；
- 声音/TTS 功能应按目标 build 重新确认结构和限制；
- Aura Sound API 不代表 addon 重新获得受限 Aura 原始数据访问权。

---

# 九、Group Buff：Aura 与 CooldownViewer 两边都扩展

## `C_UnitAuras`

当前 PTR 提供：

```lua
C_UnitAuras.GetGroupBuffVisualAlerts
C_UnitAuras.SetGroupBuffVisualAlerts
C_UnitAuras.GetHiddenGroupBuffs
C_UnitAuras.SetHiddenGroupBuffs
```

`GetGroupBuffVisualAlerts` 返回 `GroupBuffVisualAlertInfo[]`（12.1 新增结构，字段以目标 build 生成文档为准）；`SetGroupBuffVisualAlerts` / `SetHiddenGroupBuffs` 带 `HasRestrictions = true`。

对应事件：

```text
GROUP_BUFF_VISUAL_ALERTS_CHANGED
HIDDEN_GROUP_BUFFS_CHANGED
```

## `C_CooldownViewer`

当前 69189 提供：

```lua
C_CooldownViewer.GetGroupBuffItems()
```

返回：

```text
GroupBuffItem[]
```

`GroupBuffItem` 当前字段：

```text
spellID
name
iconID
flags
isKnown
```

这说明 Blizzard 正把 Group Buff 的展示/配置能力放进受支持 API，而不是要求插件自己扫描所有 Aura。

---

# 十、CooldownViewer / CDM 数据结构是 12.1 的实际迁移点

当前 12.1 PTR 69189 的：

```text
CooldownViewerCooldown
```

准确字段如下：

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

其中当前 generated docs 明确（经 69189 逐字段核实）：

```text
spellID: number | nil
spellCategoryID: number | nil
equipSlot: luaIndex | nil
buffSlot: luaIndex | nil
isInvisible: bool
charges: bool            -- 注意：是 bool（是否带充能层数显示），不是充能数值
flags: CooldownSetSpellFlags
  - HideAura = 1
  - HideByDefault = 2
category: CooldownViewerCategory（9 个值，含 GroupBuff = 4）
```

注意：`GetCooldownViewerCategorySet` 的 `allowUnlearned: bool = false` 参数在 12.0.7 已存在，不是 12.1 新增，不要错误归因。

这意味着 12.1 不能再假设每个 CooldownViewer 条目都一定对应一个 `spellID`。

错误假设：

```lua
local info = C_CooldownViewer.GetCooldownViewerCooldownInfo(id)
local spellID = info.spellID
-- 默认一定存在
```

正确迁移方向：

```text
先判断 spellID
再判断 spellCategoryID / equipSlot / buffSlot
再决定条目来源和显示逻辑
```

对于：

- CDM 配置读取；
- CDM 技能映射；
- 饰品/装备冷却；
- Buff 槽；
- Group Buff；
- 语音绑定；

这是比普通 `C_Spell.GetSpellCooldown()` 更直接的 12.1 迁移点。

---

# 十一、Unit Identity Secret 范围继续扩大

注意：Unit Identity Secret 并不是 12.1 才出现。

12.0.7 已经有很多函数带：

```text
SecretWhenUnitIdentityRestricted
```

12.1 的变化是更多 API 被纳入，或改成更细粒度 predicate。

## 2026-08-10 复核结论

本次用 live 12.0.7 与 ptr 12.1.0 的 `UnitDocumentation.lua` / `UnitRoleDocumentation.lua` 生成文档逐条 diff，确认下列函数在 12.0.7 **没有** `SecretWhenUnitIdentityRestricted`，12.1 全部新增该标记（live 仅有 `SecretArguments`，ptr 额外带 `SecretWhenUnitIdentityRestricted`）：

```text
UnitClass
UnitClassBase
UnitGroupRolesAssigned
UnitGroupRolesAssignedEnum
UnitGetAvailableRoles        -- 位于 UnitRoleDocumentation.lua
UnitIsGroupAssistant
UnitIsGroupLeader
UnitIsRaidOfficer
UnitLeadsAnyGroup
UnitIsOwnerOrControllerOfUnit
UnitIsPVP
UnitPhaseReason
UnitHonorLevel
```

`UnitIsCharmed` / `UnitIsPossessed` 则从 Aura secrecy 切到 `SecretWhenUnitPossessionRestricted`（详见第十四节）。`UnitIsUnit` 的限制（`RequiresComparableUnitTokens` / `SecretWhenUnitComparisonRestricted`）在 12.0.7 已存在，不是 12.1 新增。

## 职业

当前 PTR：

```lua
UnitClass(unit)
UnitClassBase(unit)
```

加入/带有：

```text
SecretWhenUnitIdentityRestricted = true
```

因此不要默认对任意敌方/受限 unit 都可以安全：

```lua
local _, class = UnitClass(unit)
if class == "MAGE" then
    ...
end
```

## 角色职责

当前 PTR 需要考虑 identity restriction 的函数包括：

```lua
UnitGroupRolesAssigned(unit)
UnitGroupRolesAssignedEnum(unit)
UnitGetAvailableRoles(unit)
```

## 团队身份/控制关系

当前 PTR 需要重点检查：

```lua
UnitIsGroupAssistant
UnitIsGroupLeader
UnitIsRaidOfficer
UnitLeadsAnyGroup
UnitIsOwnerOrControllerOfUnit
UnitIsPVP
UnitPhaseReason
```

## 69189：`UnitHonorLevel`

当前最新 PTR：

```lua
UnitHonorLevel(unit)
```

增加：

```text
SecretWhenUnitIdentityRestricted = true
```

这是 69189 相对 69111 的真实 restriction 变化之一。

---

# 十二、`UnitName()` 使用更细的 Name Identity predicate

12.0.7：

```text
UnitName
SecretWhenUnitIdentityRestricted
```

当前 12.1 PTR：

```text
UnitName
SecretWhenUnitNameIdentityRestricted
```

新的 predicate 与普通 Unit Identity 规则相似，但对 PvP 中查询玩家单位存在专门例外。

结论：不要假设 `UnitName()` 与所有其他 identity API 永远拥有完全相同的 Secret 条件。

---

# 十三、Inspect 专精迁入 `C_SpecializationInfo`

12.1 当前 PTR 有正式 namespaced API：

```lua
C_SpecializationInfo.GetInspectSpecialization(unit)
```

当前 generated docs 带：

```text
SecretWhenUnitIdentityRestricted = true
SecretArguments = "AllowedWhenUntainted"
```

Blizzard 自己的 Inspect UI 也已从旧写法：

```lua
GetInspectSpecialization(unit)
```

迁移为：

```lua
C_SpecializationInfo.GetInspectSpecialization(unit)
```

旧全局目前仍作为 Deprecated 兼容入口存在；新代码应优先使用 namespaced API。

---

# 十四、69111：Possession Secret 被独立成新 predicate

69111 新增：

```text
SecretWhenUnitPossessionRestricted
```

同时：

```lua
UnitIsCharmed(unit)
UnitIsPossessed(unit)
```

从更通用的 Aura secrecy 规则切换为：

```text
SecretWhenUnitPossessionRestricted
```

这是**规则细分**，不是简单“所有情况都更严格”。

做宠物、魅惑、控制、附身状态相关功能时，应按当前 predicate 设计，而不是只判断普通 Aura restriction。

---

# 十五、`UnitIsUnit()` 限制不是 12.1 新增

12.0.7 已经存在：

```text
RequiresComparableUnitTokens = true
SecretWhenUnitComparisonRestricted = true
```

所以不要错误写成“12.1 新增封锁”。

也不要通过大量：

```lua
UnitIsUnit(a, b)
```

建立身份比较矩阵去推断 Secret unit。

---

# 十六、Forbidden Object → Forbidden Aspects

## ForbiddenAspect 是 12.1 全新引入

12.0.7 live 生成文档中**不存在** `ForbiddenAspectConstantsDocumentation.lua`（live 分支该文件 404）；当前 PTR 新增该枚举，共 11 个取值（1..1024，bitmask 语义）：

```text
SetToDefaults            = 1     -- 限制重置对象默认状态（设置其他 aspect 时隐含）
ScriptBindings           = 2     -- 限制查询/替换/hook 对象脚本
UntrustedScriptExecution = 4     -- 限制执行全部脚本，传播到子对象
UntrustedLayoutScriptExecution = 8  -- 限制 layout script（如 OnSizeChanged），传播到子对象与 anchor 对象
EventRegistrations       = 16    -- 限制查询/修改已注册事件
AlwaysPropagateInput     = 32    -- 强制鼠标/按键输入传播，传播到子对象
ScriptedInput            = 64    -- 限制从 Lua 触发 synthetic input
QueryFocus               = 128   -- 限制查询 input focus 状态
ChangeAnimationTarget    = 256   -- 限制修改动画目标对象
RemoveSecretAspects      = 512   -- 限制清除对象 secret aspects
ChangeParent             = 1024  -- 限制修改对象 parent
```

## 12.1 SecretAspect 枚举扩展

`SecretAspect` 枚举在 12.0.7 已存在（29 个取值），12.1 新增：

```text
RadialProgress = 8388608
```

（live 29 个 → ptr 30 个，`MaxValue` 从 4194304 提到 8388608。）

## 与旧式 forbidden 思维的区别

不要再把对象安全性简单理解成：

```text
Forbidden / Not Forbidden
```

而应该理解为：

```text
某一类操作被禁止
其他操作可能仍允许
```

例如一个对象可能禁止：

- Script hook/query；
- Event registration；
- reparent；
- synthetic input；
- focus query；
- layout script；

但仍允许部分视觉配置。

同样：

```lua
frame:IsForbidden() == false
```

不能作为“所有操作都安全”的充分条件。

## AuraButton / AuraContainer side channel 禁止思路

不要通过：

```text
OnShow / OnHide
OnSizeChanged
child count
IsShown
focus/input query
事件注册状态
anchor/layout 变化
reparent 结果
```

推断受限制 Aura。

---

# 十七、Spell / Cooldown：最后 PTR build 没有再次大翻修

先明确：Cooldown Secret 化不是 12.1 新变化。

12.0.7 已经存在：

```text
C_Spell.GetSpellCooldown
    SecretWhenCooldownsRestricted

C_Spell.GetSpellCharges
    SecretWhenCooldownsRestricted

C_Spell.GetSpellCastCount
    SecretWhenCooldownsRestricted

C_Spell.GetSpellDisplayCount
    SecretWhenCooldownsRestricted
```

不要把这些写成“12.1 新封锁”。

## 当前 12.1 PTR 新增：`GetLastCategoryCooldownSource`

```lua
C_Spell.GetLastCategoryCooldownSource(spellCategory)
```

返回：

```text
spellID
itemID
```

并带：

```text
SecretWhenCooldownsRestricted = true
```

## `GetSpellTexture()` 新增第三返回值

12.0.7：

```lua
iconID, originalIconID = C_Spell.GetSpellTexture(spellID)
```

12.1 PTR：

```lua
iconID, originalIconID, conditionalIconID = C_Spell.GetSpellTexture(spellID)
```

只取第一个返回值的旧代码通常不受影响；如果依赖固定返回值数量，应更新。

## ItemLocation 技能描述

当前 PTR 新增：

```lua
C_Spell.GetSpellDescriptionForItemLocation(spellIdentifier, itemLocation)
```

## 68914 → 69189 最后阶段

最后三个 PTR commit 没有再次修改 `SpellDocumentation.lua` 的核心 cooldown 签名。

因此不要写成：

```text
69189 又重新改变 C_Spell.GetSpellCooldown
```

当前更值得关注的是：

```text
既有 Cooldown Secret 规则
+
CooldownViewer/CDM 数据结构扩展
```

---

# 十八、69111：`SecondsFormatter` 增加取整策略

`SecondsFormatter` Script Object API 新增：

```text
GetRounding()
SetRounding(rounding)
```

新增枚举：

```text
SecondsFormatterRounding
- RoundUp
- Truncate
```

含义：

- `RoundUp`：不显示毫秒时，小数秒向上取整；
- `Truncate`：不显示毫秒时，直接截断。

这对 Aura duration、Cooldown countdown、状态条文字等 UI 有用。

如果当前场景能使用 Blizzard formatter，不必自己用互不一致的 `math.ceil` / `math.floor` 模拟官方时间显示。

---

# 十九、69111：Texture 增加 SVG API

`SimpleTextureBase` Script Object 新增：

```text
ClearSVG()
SetSVG(svgAsset) -> success: bool
```

其中 `SetSVG` 当前带：

```text
SecretArguments = "AllowedWhenTainted"
```

这是一般 UI 能力扩展，不是战斗信息 API。

---

# 二十、69189：Browser / Delves 新增接口

## Browser

```lua
C_Browser.CloseFullscreenBrowser()
```

新增同步事件：

```text
FULLSCREEN_BROWSER_SPINNER_SHOW
FULLSCREEN_BROWSER_SPINNER_HIDE
```

Blizzard 同时新增 `Blizzard_FullscreenBrowser` UI 模块消费这些事件。

## Delves / Lair

```lua
C_DelvesUI.HasActiveLFGLair()
C_DelvesUI.IsInLair()
```

Blizzard 自己已经在相关 Delves / InstanceDifficulty UI 中使用新接口。

这类 API 与 Aura/Secret 主迁移无关，但属于 69189 的真实新增。

---

# 二十一、69111：低风险 Housing 新增接口

当前 generated docs 还新增：

```text
HousingBlueprintUI.CanExportRoom(roomGUID) -> canExport
HousingLayoutUI.RoomHasStairs(roomGUID) -> hasStairs
```

与一般战斗插件关系较低，可记录但不用进入高优先级迁移清单。

---

# 二十二、CombatLog 当前不是 12.1 迁移重点

当前检查没有发现 12.1 相对 12.0.7 对核心 CombatLog generated API 做同等级别的重构。

`C_CombatLogSecure` 也不是 12.1 才新增；12.0.7 已经存在。

所以以下功能目前优先级低于 Aura / Unit / CDM：

- `COMBAT_LOG_EVENT_UNFILTERED` 统计；
- 施法成功历史统计；
- 打断次数统计；
- 非 Secret 战斗日志文本处理。

仍然必须遵守 12.0.7 已经存在的 CombatLog restriction。

---

# 二十三、不要错误归因的项目

以下内容不要写成“12.1 新增”：

```text
canaccessvalue / canaccessallvalues / canaccesstable / canaccesssecrets
UnitIsUnit 的 comparable-token restriction
C_Spell.GetSpellCooldown 的 Cooldown Secret 规则
C_CombatLogSecure
```

另外：

```text
69027 删除 WorldMap .zmp
```

是资源清理，不等于 API 删除。

真正值得记录的 12.1 核心是：

```text
Aura access boundary
AuraContainer display architecture
Unit identity predicate 扩展/细分
Possession predicate
ForbiddenAspect
CooldownViewer/CDM 数据扩展
最后 PTR build 的少量新 UI API
```

---

# 二十四、迁移设计建议

## 1. 不要把 AuraContainer 还原成旧 AuraData scanner

错误方向：

```text
12.1 AuraContainer
→ 想办法恢复旧 AuraData
→ 继续旧 scanner
```

正确方向：

```text
12.0.7：旧数据/显示路径
12.1：AuraContainer / ManagedAuraContainer / 支持的显示路径
```

Compat 层应该按“能力/显示架构”分流，而不是试图 declassify Secret 数据。

## 2. 版本敏感 API 集中到 Compat

推荐：

```lua
QFX.Compat = QFX.Compat or {}

function QFX.Compat.GetSpellTextureInfo(spellID)
    -- target-build verified implementation
end

function QFX.Compat.SupportsAuraContainer()
    -- capability/client-family check
end
```

不要在多个业务模块散落：

```lua
if build >= 120100 then
    ...
end
```

文档 build number 是 provenance，不应直接变成永久 feature flag。

## 3. Restriction metadata 是 API 签名的一部分

审查 API 时除了：

```text
Arguments
Returns
```

还必须看：

```text
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

## 4. CooldownViewer 不要假设 `spellID` 永远存在

12.1 当前必须允许：

```text
spellID == nil
```

并检查：

```text
spellCategoryID
equipSlot
buffSlot
```

再决定条目来源。

## 5. Preview 使用明确假数据

设置界面的：

- Aura 图标；
- 层数；
- 持续时间；
- 队友；
- Boss Debuff；

应该使用明确 preview/fake data，不要为了预览读取受限实战数据。

---

# 二十五、迁移测试清单

任何使用 Aura / Unit / CDM / protected frame 的插件至少测试：

- 登录；
- `/reload`；
- 非战斗；
- 普通战斗；
- 副本战斗；
- Mythic+ / 团本 encounter；
- PvP（如果功能涉及）；
- `target`；
- `focus`；
- `mouseover`；
- `party1..4`；
- `raid1..40`；
- `nameplateX`；
- 宠物/守护者/魅惑/附身单位；
- CooldownViewer spell 条目；
- equipSlot 条目；
- buffSlot / Group Buff 条目；
- 多次进入/离开战斗；
- 与其他修改 Blizzard Frame 的插件共同运行。

重点观察：

```text
a secret boolean value
a secret number value
execution tainted by
forbidden
```

以及来自下列 restriction 的 Lua error：

```text
RequiresUnitAuraAccess
RequiresNonSecretAura
SecretWhenUnitIdentityRestricted
SecretWhenUnitNameIdentityRestricted
SecretWhenUnitPossessionRestricted
ForbiddenAspect
```

---

# 二十六、给 Codex 的核对顺序

当需要把插件从 12.0.7 适配到 12.1 时：

1. 读取目标分支 `version.txt`。
2. 读取目标 build 的 generated API documentation。
3. 对比 **restriction metadata**，不只比较函数名。
4. 先判断某限制是不是 12.0.7 已存在，避免错误归因。
5. Aura 显示优先检查 AuraContainer / CustomAuraButton。
6. Unit API 检查 Identity / NameIdentity / Possession 等对应 Secret domain。
7. Blizzard Script Object 检查 Forbidden Aspect，而不是只看传统 combat lockdown。
8. CooldownViewer 检查 `spellID` nilability、`spellCategoryID`、`equipSlot`、`buffSlot`、Group Buff。
9. Spell/Cooldown 先确认是不是旧 Secret 规则延续。
10. CombatLog 只有实际 diff 才重写，不因版本号变化盲改。
11. 检查最后几个 PTR commit，避免文档停在旧周 build。
12. 最终结论分成：**已确认 / PTR-only / 待正式服 live 验证**。

---

# 二十七、当前上线前结论

截至 **2026-08-10 / PTR 12.1.0.69189**：

- `live` 仍是 **12.0.7.68974**；
- 当前公开 PTR UI/API 源码 HEAD 是 **12.1.0.69189**，且 69189 之后截至本日无更新 build；
- 68914 后没有再次发生 Aura / Spell / Cooldown 核心架构大翻转；
- 69111 补充了 Stealable Aura 显示过滤、Possession predicate、SecondsFormatter rounding、SVG 等；
- 69189 补充 Browser / Delves API，并让 `UnitHonorLevel` 进入 Unit Identity Secret；
- 2026-08-10 复核确认：`RequiresUnitAuraAccess` 全量 16 个 API（live 为 0）、`ForbiddenAspect` 11 值全为 12.1 新增、`SecretAspect` 新增 `RadialProgress`、`UNIT_AURA` Secret 标记与 `UNIT_AURA_BLOCKED` SecretValue 均与文档一致、Aura Sound 旧 API 在 12.1 移除；
- 对一般战斗插件影响最大的仍是 **Aura access boundary + AuraContainer + Unit Identity Secret + CooldownViewer 数据结构扩展**。

**正式服上线后必须重新以新的 `live` build 做最终全量 diff。**
