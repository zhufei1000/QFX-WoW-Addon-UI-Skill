# WoW 12.0.7 → 12.1.0 PTR API 迁移参考

用于把 Retail 12.0.7 插件迁移、审查或适配到 12.1.0 PTR。

## 当前核实基线

最后核实：**2026-08-08**。

- 正式服 `live`：**12.0.7.68974**
- PTR `ptr`：**12.1.0.69189**

当前 12.1.0 仍是 PTR。本文描述的是 **69189 相对 12.0.7.68974 的当前差异**，不是对最终正式服 API 冻结状态的承诺。后续 PTR build 或正式上线 build 仍可能继续调整。

主要事实来源：

1. `Gethe/wow-ui-source` 对应 `live` / `ptr` 分支的 `version.txt`。
2. 同分支 `Interface/AddOns/Blizzard_APIDocumentationGenerated/`。
3. 必要时再用同分支 FrameXML 验证 Blizzard 自己如何消费这些 API。

不要仅根据 GitHub 的 branch file diff 判断“新增 API”。`live` 与 `ptr` 分支历史存在分叉，某些文件会显示为 added/modified，但实际 API 内容可能在两个分支完全相同。

---

# 一、迁移结论

12.0.7 → 12.1 的核心变化不是“所有 WoW API 全部重做”，而是进一步强化了战斗数据边界：

1. **Aura 原始数据访问进一步收紧**：大量 `C_UnitAuras` 查询增加 `RequiresUnitAuraAccess`。
2. **`UNIT_AURA` 本身进入 Aura restriction 模型**：受限时事件被标记为 Secret。
3. **Blizzard 提供新的 Aura 显示层**：AuraContainer / CustomAuraButton / `C_AuraContainerUtil`，鼓励“暴雪管理数据，插件管理显示”。
4. **Unit 身份、职责、控制/附身关系的 Secret 范围继续扩大**。
5. **Forbidden Object 进一步细分为 Forbidden Aspects**。
6. **Spell/Cooldown 只有少量接口和返回值变化**；Cooldown Secret 化本身并不是 12.1 才出现。
7. **CombatLog 当前主要公开文档与 12.0.7 基本一致**，不是这次迁移最高风险区。

## 风险优先级

| 领域 | 12.0.7 → 12.1 变化 | 迁移风险 |
|---|---|---|
| Aura / Buff / Debuff | 数据访问门禁、事件 Secret、新显示框架 | 🔴 极高 |
| 团队/姓名板 Aura 显示 | 旧式手动枚举应迁移到 AuraContainer 路径 | 🔴 极高 |
| Unit 身份/职责/控制关系 | Secret domain 继续扩大 | 🟠 高 |
| Blizzard Frame / AuraButton | Forbidden Aspect 粒度更细 | 🟠 高 |
| Spell / Cooldown | 小量新增 API/返回值，既有限制继续存在 | 🟡 中 |
| CombatLog | 当前核心 API 基本未变 | 🟢 低 |
| AddOnProfiler / EncounterTimeline | 当前生成文档无实质迁移差异 | 🟢 低 |

---

# 二、最重要变化：Aura 访问从“可能返回 Secret”升级为“访问本身有前置条件”

12.0.7 中，很多 Aura API 已经带：

```text
SecretWhenUnitAuraRestricted = true
```

这意味着 12.0.7 本来就已经存在 Aura Secret 机制。

当前 12.1 PTR 进一步在大量 Aura 查询上加入：

```text
RequiresUnitAuraAccess = true
```

当前 69189 中需要重点检查的例子包括：

```lua
C_UnitAuras.GetAuraDataByAuraInstanceID
C_UnitAuras.GetAuraDataByIndex
C_UnitAuras.GetAuraDataBySlot
C_UnitAuras.GetBuffDataByIndex
C_UnitAuras.GetDebuffDataByIndex
C_UnitAuras.GetAuraSlots
C_UnitAuras.GetUnitAuraInstanceIDs
C_UnitAuras.GetUnitAuras
C_UnitAuras.IsAuraFilteredOutByInstanceID
```

## 迁移含义

12.0.7 更接近：

```text
可以调用 API
→ 某些结果在受限场景下成为 Secret
```

12.1 进一步变为：

```text
先判断调用者是否具有 UnitAura access
→ 再决定是否允许这一组 Aura 数据访问
```

因此不要把旧代码简单包一层 `if aura then` 或 `pcall` 当作 12.1 兼容方案。

错误方向：

```lua
local aura = C_UnitAuras.GetAuraDataByIndex(unit, index, filter)
if aura then
    -- 继续读取 spellId / duration / applications / sourceUnit
end
```

正确迁移思路取决于插件目的：

- 如果目的是 **显示 Aura**：优先使用 Blizzard 支持的 AuraContainer / CustomAuraButton 显示路径。
- 如果目的是 **依据 Aura 做战斗判断**：先确认该信息在当前环境是否仍被允许给 addon；不能通过 side channel 还原 Secret 数据。

---

# 三、`GetUnitAuras()`：`ConditionalSecretContents` 不是 12.1 新增，但 12.1 增加了访问门禁

需要明确区分“旧限制”和“新限制”。

12.0.7 的：

```lua
C_UnitAuras.GetUnitAuras(...)
```

已经返回：

```text
ConditionalSecretContents = true
```

所以“外层是 Lua table”从 12.0.7 开始就不代表内容一定可读。

12.1 当前 PTR 继续保留 `ConditionalSecretContents = true`，并新增：

```text
RequiresUnitAuraAccess = true
```

因此以下操作都不能默认安全：

```lua
#auras
ipairs(auras)
table.sort(auras)
aura.spellId == spellID
把 aura 数据序列化/保存
通过表长度或遍历成功与否推断隐藏状态
```

迁移时不要把 `GetUnitAuras()` 当成绕过单个 Aura API 限制的后门。

---

# 四、`UNIT_AURA` 事件在 12.1 发生实质变化

## 12.0.7

`UNIT_AURA` 事件没有 `SecretWhenAurasRestricted` 标记。

`UNIT_AURA_BLOCKED` 的 `auraInstanceID` 在 12.0.7 也不是显式 `SecretValue`。

## 12.1 PTR 69189

当前生成文档中：

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

## 对旧架构的影响

旧插件常见链路：

```text
UNIT_AURA
→ 读取 updateInfo
→ 获取 auraInstanceID
→ 查询 AuraData
→ 比较 spellID / duration / stacks
→ 决定提示、目标、动作或 UI
```

在 12.1 Restricted 场景中，不能再默认这条链路可消费。

尤其不要通过：

- 事件是否触发；
- `updateInfo` 是否可迭代；
- auraInstanceID 是否存在；
- API 是否报错；
- 子框体是否显示；
- 布局尺寸是否变化；

来推断受保护 Aura。

---

# 五、SpellID / SpellName 查询 Aura 不是 12.1 绕过方案

这些接口在 12.0.7 就已经有 `RequiresNonSecretAura` 约束，12.1 继续保持：

```lua
C_UnitAuras.GetUnitAuraBySpellID
C_UnitAuras.GetPlayerAuraBySpellID
C_UnitAuras.GetAuraDataBySpellName
```

典型元数据：

```text
RequiresNonSecretAura = true
SecretWhenUnitAuraRestricted = true
```

所以不要通过一组已知 SpellID 探测某个 Secret Aura 是否存在：

```lua
for _, spellID in ipairs(importantAuras) do
    local aura = C_UnitAuras.GetUnitAuraBySpellID(unit, spellID)
    -- 不要把返回 nil / 非 nil 当成 Secret Aura presence probe
end
```

结论：**`RequiresNonSecretAura` 是明确的安全边界，不是普通 nil 条件。**

---

# 六、12.1 新增 AuraContainer / CustomAuraButton 显示体系

当前 PTR 新增生成文档：

```text
AuraContainerSharedDocumentation.lua
AuraContainerUtilDocumentation.lua
```

其中 `C_AuraContainerUtil` 提供大量用于安全显示的配置处理器，例如：

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

还新增/扩展 Aura Button 显示配置类型，例如：

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

## 架构方向

旧式：

```text
Addon 读取 AuraData
→ Addon 自己筛选
→ Addon 自己排序
→ Addon 自己计算持续时间/层数
→ Addon 自己创建图标
```

12.1 推荐方向：

```text
Blizzard 负责 Aura 跟踪/过滤/Assignment
→ AuraContainer / AuraButton 负责承载受控数据
→ Addon 在允许范围内配置样式和布局
```

如果插件功能本质只是“显示 Buff/Debuff”，优先迁移显示架构，不要继续复制 12.0.7 的原始 Aura 数据管线。

---

# 七、Aura Sound API 当前发生替换/扩展

12.0.7 生成文档中存在：

```lua
C_UnitAuras.AddPrivateAuraAppliedSound
C_UnitAuras.RemovePrivateAuraAppliedSound
```

当前 12.1 PTR 已出现新的通用 Aura Sound 路径：

```lua
C_UnitAuras.AddAuraSound
C_UnitAuras.RemoveAuraSound
```

并使用新的 Aura sound trigger/info 结构。

迁移时：

- 不要继续假设 12.0.7 PrivateAura sound API 是 12.1 唯一/最终入口；
- 对声音/TTS 类功能必须按目标 build 重新核实函数和结构；
- Aura Sound API 并不意味着插件重新获得 Secret Aura 原始数据读取权限。

---

# 八、12.1 新增团队 Buff 显示管理接口

当前 PTR `C_UnitAuras` 新增：

```lua
C_UnitAuras.GetGroupBuffVisualAlerts
C_UnitAuras.SetGroupBuffVisualAlerts
C_UnitAuras.GetHiddenGroupBuffs
C_UnitAuras.SetHiddenGroupBuffs
```

对应事件包括：

```text
GROUP_BUFF_VISUAL_ALERTS_CHANGED
HIDDEN_GROUP_BUFFS_CHANGED
```

这进一步说明 Blizzard 的方向是：

```text
允许 addon 配置“怎样显示/隐藏/提示”
而不是把全部原始 Aura 状态交给 addon 自己判断
```

对于团队 Buff 辅助 UI，应优先评估这些受支持接口，而不是先写 Aura scanner。

---

# 九、Unit API：12.1 继续扩大 Identity / Possession Secret Domain

注意：**Unit Identity Secret 并不是 12.1 才出现。**

12.0.7 已经有多种身份 API 带：

```text
SecretWhenUnitIdentityRestricted
```

例如 `UnitGUID`、`UnitFullName`、`UnitOwnerGUID`、`UnitPVPName` 等本来就不能当作 12.1 新限制。

12.1 的重要变化是：更多 API 被纳入这些 Secret domain。

## 当前确认在 12.1 新增/扩大的例子

### 角色职责

12.0.7：

```lua
UnitGroupRolesAssigned(unit)
UnitGroupRolesAssignedEnum(unit)
```

当前 PTR 进一步标记：

```text
SecretWhenUnitIdentityRestricted = true
```

### 团队身份

当前 PTR 对以下函数加入/强化 `SecretWhenUnitIdentityRestricted`：

```lua
UnitIsGroupAssistant
UnitIsGroupLeader
UnitIsRaidOfficer
UnitLeadsAnyGroup
```

### 控制/所有权

```lua
UnitIsOwnerOrControllerOfUnit
```

当前 PTR 纳入 Unit Identity restriction。

### PVP 身份

```lua
UnitIsPVP
```

当前 PTR 纳入 Unit Identity restriction。

### 魅惑/附身

当前 PTR：

```lua
UnitIsCharmed
UnitIsPossessed
```

增加：

```text
SecretWhenUnitPossessionRestricted = true
```

## `UnitName()` Secret domain 进一步细分

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

这说明 Blizzard 正在把 Secret 范围拆成更具体的 domain，而不是只用一个总的 Unit Identity 开关。

---

# 十、`UnitIsUnit()` 的限制不是 12.1 新增

不要错误归因。

12.0.7 已经有：

```text
RequiresComparableUnitTokens = true
SecretWhenUnitComparisonRestricted = true
```

当前 PTR 继续保持。

所以这种代码本来就需要遵守 comparable token 限制：

```lua
UnitIsUnit("mouseover", "party1")
```

不要通过大量 `UnitIsUnit` 比较建立“身份矩阵”去推断 Secret unit。

---

# 十一、12.1 新增更细粒度的 ForbiddenAspect 模型

当前 PTR 新增：

```text
ForbiddenAspect
```

当前生成文档定义 11 个 Aspect：

```text
SetToDefaults
ScriptBindings
UntrustedScriptExecution
UntrustedLayoutScriptExecution
EventRegistrations
AlwaysPropagateInput
ScriptedInput
QueryFocus
ChangeAnimationTarget
RemoveSecretAspects
ChangeParent
```

## 与旧式 forbidden 思维的区别

不要再把对象安全性简单理解成：

```text
Forbidden / Not Forbidden
```

12.1 更接近：

```text
这个对象的某一类操作被禁止
但其他允许的操作仍可能存在
```

例如一个对象可能：

- 禁止 Hook/查询 script；
- 禁止事件注册；
- 禁止改 parent；
- 禁止 synthetic input；
- 禁止 focus 查询；
- 禁止 layout script；

但这不自动等于所有视觉属性都不可配置。

反过来也一样：`frame:IsForbidden() == false` 不能作为“所有 API 操作都安全”的充分条件。

## AuraButton 特别注意

AuraButton / AuraContainer 的生命周期不能当成 Secret Aura side channel。

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

推断隐藏 Aura。

---

# 十二、Spell / Cooldown：迁移量较小，但有几个实际变化

## 先明确：Cooldown Secret 化不是 12.1 新变化

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

所以不要把这些限制在迁移报告中误写成“12.1 新封锁”。

## 当前 PTR 新增 `GetLastCategoryCooldownSource`

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

适合确认某个 cooldown category 最近由哪个 spell/item 触发，但受限场景仍不能拿它做 Secret combat branching。

## `GetSpellTexture()` 新增第三个返回值

12.0.7：

```lua
iconID, originalIconID = C_Spell.GetSpellTexture(spellID)
```

当前 PTR：

```lua
iconID, originalIconID, conditionalIconID = C_Spell.GetSpellTexture(spellID)
```

旧代码如果只取第一个返回值通常不受影响；如果自己 unpack 或做返回值数量假设，应更新兼容层。

## 新增按 ItemLocation 获取技能描述

当前 PTR 新增：

```lua
C_Spell.GetSpellDescriptionForItemLocation(spellIdentifier, itemLocation)
```

适用于物品位置影响技能描述的场景。

---

# 十三、CombatLog 当前不是 12.1 迁移重点

当前核实的：

```text
CombatLogDocumentation.lua
```

在 live / ptr 的核心生成文档内容一致；`C_CombatLog` 主要函数、事件和 Restriction 模型没有看到此次 12.1 对 12.0.7 的实质迁移变化。

`C_CombatLogSecure` 也并不是 12.1 才新增；12.0.7 已经存在。

所以以下类型功能目前优先级低于 Aura/Unit：

- `COMBAT_LOG_EVENT_UNFILTERED` 统计；
- 施法成功后的历史统计；
- 打断次数统计；
- 非 Secret 的战斗日志文本处理。

但仍需遵守原本已经存在的 CombatLog restriction。

---

# 十四、这些东西“看起来新增”，但当前并不是 12.1 实质 API 差异

不要仅依赖 GitHub branch compare 的 added/modified 文件数量。

当前逐文件核实后，以下生成文档在 live / ptr 中没有实质变化，或核心内容一致：

```text
C_AddOnProfiler
C_EncounterTimeline
C_CombatLog
C_CombatLogSecure
UnitAuraSortRule
部分 Action / FrameScript secret helper
```

例如 `canaccessvalue`、`canaccessallvalues`、`canaccesstable`、`canaccesssecrets` 等 Secret helper 在 12.0.7 已经存在，不能写成 12.1 新 API。

真正值得记录的是 12.1 **新增了更细的 restriction annotation / ForbiddenAspect / Aura display architecture**。

---

# 十五、12.0.7 → 12.1 兼容设计建议

## 1. Aura 功能不要做统一“旧 AuraData 兼容层”

错误方向：

```text
12.1 AuraContainer
→ 想办法重新还原成 12.0.7 AuraData
→ 继续运行旧 scanner
```

正确方向：

```text
12.0.7：旧数据/显示路径
12.1：AuraContainer/受支持显示路径
```

在 `Compat` 层按“能力/显示架构”分流，不要试图 declassify Secret 数据。

## 2. 版本敏感 API 集中到 Compat

推荐：

```lua
QFX.Compat = QFX.Compat or {}

function QFX.Compat.GetSpellTextureInfo(spellID)
    -- target-build verified implementation
end

function QFX.Compat.SupportsAuraContainer()
    -- capability check / client-family check
end
```

不要在多个模块中散落：

```lua
if build >= 120100 then
    ...
end
```

尤其不要把文档 build number 当成永久 runtime feature flag。

## 3. Restriction annotation 必须当成签名的一部分

审查 API 时，不只看：

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
ConditionalSecretContents
RequiresUnitAuraAccess
RequiresNonSecretAura
RequiresUnitIdentityAccess
RequiresComparableUnitTokens
SecretWhen...
```

## 4. Preview / 设置界面使用假数据

如果设置 UI 需要展示：

- Aura 图标；
- 层数；
- 持续时间；
- 队友角色；
- Boss Debuff；

应使用明确的 preview/fake data，不要为了预览去读取受限实战数据。

---

# 十六、迁移测试清单

任何使用 Aura / Unit / protected frame 的插件至少测试：

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
- 宠物/守护者/魅惑单位（如果涉及）；
- 多次进入/离开战斗；
- 与其他修改 Blizzard Frame 的插件共同运行。

重点观察：

```text
a secret boolean value
a secret number value
execution tainted by
forbidden
```

以及任何来自 `RequiresUnitAuraAccess`、`RequiresNonSecretAura`、ForbiddenAspect 的 Lua error。

---

# 十七、给 Codex 的迁移判定顺序

当用户要求“把 12.0.7 插件适配 12.1”时：

1. 先读取目标分支 `version.txt`。
2. 再读取目标 API 的 generated documentation。
3. 对比 12.0.7 与当前 PTR 的 **restriction metadata**。
4. 判断旧限制是否 12.0.7 已经存在，避免错误归因。
5. Aura 显示优先查 AuraContainer / CustomAuraButton。
6. Unit API 检查对应 Secret domain。
7. Blizzard Script Object 检查 Forbidden Aspect，而不是只看传统 combat lockdown。
8. Spell/Cooldown 先确认是否只是已有 Secret 规则继续存在。
9. CombatLog 不要因为版本升级就无理由重写；只有实际 API diff 才改。
10. 最后给出：已确认、PTR-only、待游戏内验证三类结论。

---

# 十八、最终一句话规则

**12.0.7 的核心是“数据仍可暴露，但越来越多结果会成为 Secret”；12.1 的方向进一步变成“对敏感战斗数据设置显式访问边界，同时提供 Blizzard 管理的数据展示对象，让插件定制显示而不是自由读取原始状态”。**

迁移时优先重构“数据获取架构”，不要只修 nil、boolean 或 Lua error。
