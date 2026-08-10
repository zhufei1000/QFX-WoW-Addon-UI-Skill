# WoW 12.0.7 → 12.1.0 PTR API 迁移参考

用于把 Retail 12.0.7 插件迁移、审查或适配到 12.1.0 PTR。

## 当前核实基线

最后核实：**2026-08-10**。

- 正式服 `live`：**12.0.7.68974**
- PTR `ptr`：**12.1.0.69189**
- PTR 当前 HEAD：`a520b6c27bb897e6be2333b6cc2be36d52c7c11b`

截至本次核实，`live` 仍未切换到 12.1.0。本文描述的是 **12.1.0.69189 PTR 相对 12.0.7.68974 live 的当前差异**，不是对最终正式服 API 冻结状态的承诺。正式上线 build 仍应重新做一次 `live → live` 最终 diff。

主要事实来源：

1. `Gethe/wow-ui-source` 对应 `live` / `ptr` 分支的 `version.txt`。
2. 同分支 `Interface/AddOns/Blizzard_APIDocumentationGenerated/`。
3. 同分支 FrameXML/UI source，用于确认 Blizzard 自己如何消费这些 API。
4. PTR build 之间直接比较 commit，不只看 wiki 或旧周报。

不要仅根据 GitHub 的 branch file diff 判断“新增 API”。`live` 与 `ptr` 分支历史存在分叉，某些文件会显示为 added/modified，但实际 API 内容可能在两个分支完全相同。

---

# 一、上线前最后 PTR build 链路

当前最后一段 PTR 链路已经核对：

```text
12.1.0.68914
→ 12.1.0.69027
→ 12.1.0.69111
→ 12.1.0.69189
```

## 69027

`68914 → 69027` 基本是 WorldMap `.zmp` 资源从 UI code list 中移除，没有生成 API 文档变化。

因此不要把 69027 当成一次 API 大改。

## 69111

`69027 → 69111` 是最后阶段真正有价值的一轮 API/UI 更新，重点包括：

- AuraContainer 增加可偷取/不可偷取过滤显示能力；
- `SecondsFormatter` 增加秒数取整策略；
- 新增 `SecretWhenUnitPossessionRestricted`；
- `UnitIsCharmed` / `UnitIsPossessed` 从通用 Aura secrecy 切到更精确的 possession secrecy；
- Texture Script Object 增加 SVG API；
- Housing UI 增加少量查询接口。

## 69189

`69111 → 69189` 是当前 PTR 最新提交，生成 API 变化包括：

```lua
C_Browser.CloseFullscreenBrowser()

C_DelvesUI.HasActiveLFGLair()
C_DelvesUI.IsInLair()
```

新增事件：

```text
FULLSCREEN_BROWSER_SPINNER_SHOW
FULLSCREEN_BROWSER_SPINNER_HIDE
```

并且：

```text
UnitHonorLevel
SecretWhenUnitIdentityRestricted = true
```

因此 69189 相比 69111 没有再次重写 Aura/Spell/Cooldown 核心架构，主要是补充 API 与继续细化 Unit identity secrecy。

---

# 二、迁移结论

12.0.7 → 12.1 的核心变化不是“所有 WoW API 全部重做”，而是进一步强化战斗数据边界，并增加由 Blizzard 承载敏感数据的显示对象：

1. **Aura 原始数据访问进一步收紧**：大量 `C_UnitAuras` 查询增加 `RequiresUnitAuraAccess`。
2. **`UNIT_AURA` 本身进入 Aura restriction 模型**：受限时事件被标记为 Secret。
3. **Blizzard 提供新的 Aura 显示层**：AuraContainer / CustomAuraButton / `C_AuraContainerUtil`，方向是“Blizzard 管理敏感数据，插件管理允许的显示”。
4. **Unit 身份、职业、职责、荣誉等级、控制/附身关系等 Secret 范围继续扩大或细分**。
5. **Forbidden Object 进一步细分为 Forbidden Aspects**。
6. **CooldownViewer 的数据模型实际扩展**，增加物品槽、Buff 槽、Group Buff 等信息。
7. **Spell/Cooldown 核心限制没有在最后 PTR build 再次大改**；已有 Cooldown Secret 规则继续存在。
8. **CombatLog 当前主要公开生成文档与 12.0.7 基本一致**，不是这次迁移最高风险区。

## 风险优先级

| 领域 | 12.0.7 → 12.1 变化 | 迁移风险 |
|---|---|---|
| Aura / Buff / Debuff | 数据访问门禁、事件 Secret、新显示框架 | 🔴 极高 |
| 团队/姓名板 Aura 显示 | 旧式手动枚举应迁移到 AuraContainer 路径 | 🔴 极高 |
| Unit 身份/职业/职责/控制关系 | Secret domain 继续扩大/细分 | 🟠 高 |
| Blizzard Frame / AuraButton | Forbidden Aspect 粒度更细 | 🟠 高 |
| CooldownViewer / CDM 数据 | 结构字段和 Group Buff 数据扩展 | 🟠 高 |
| Spell / Cooldown | 少量新增 API/返回值，既有限制继续存在 | 🟡 中 |
| SecondsFormatter / Texture | 新的显示辅助 API | 🟡 中低 |
| Browser / Delves / Housing | 少量独立新增接口 | 🟢 低 |
| CombatLog | 当前核心 API 基本未变 | 🟢 低 |

---

# 三、最重要变化：Aura 访问从“可能返回 Secret”升级为“访问本身有前置条件”

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

- 如果目的是 **显示 Aura**：优先使用 Blizzard 支持的 AuraContainer / ManagedAuraContainer / CustomAuraButton 路径。
- 如果目的是 **依据 Aura 做战斗判断**：先确认该信息在当前环境是否仍允许 addon 消费；不能通过 side channel 还原 Secret 数据。

---

# 四、`GetUnitAuras()`：`ConditionalSecretContents` 不是 12.1 新增，但 12.1 增加了访问门禁

需要明确区分“旧限制”和“新限制”。

12.0.7 的：

```lua
C_UnitAuras.GetUnitAuras(...)
```

已经返回带：

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

# 五、`UNIT_AURA` 事件在 12.1 发生实质变化

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

# 六、SpellID / SpellName 查询 Aura 不是 12.1 绕过方案

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

# 七、12.1 AuraContainer / CustomAuraButton 显示体系

当前 PTR 有独立生成文档：

```text
AuraContainerSharedDocumentation.lua
AuraContainerUtilDocumentation.lua
```

其中 `C_AuraContainerUtil` 提供大量用于受支持显示配置的处理器，例如：

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

核心显示枚举包括：

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

## 69111 又补了一层 Stealable 显示过滤

当前 69189 已包含：

```text
CustomAuraButtonDispelTypeStealableFilter
- Stealable
- NotStealable
```

`CustomAuraButtonDispelTypeTextureOptions` 新增：

```text
showAlways: bool
stealableFilter: CustomAuraButtonDispelTypeStealableFilter | nil
```

含义：

- `showAlways = true` 时忽略其他显示条件，强制显示 dispel type texture；
- `stealableFilter` 可以限制只对可偷取或不可偷取 Aura 显示相应驱散/偷取视觉。

这说明 Blizzard 仍在扩展“让插件控制显示规则，而不是读取原始 Aura 后自己判断”的能力。

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
→ AuraContainer / AuraButton 承载受控数据
→ Addon 在允许范围内配置样式、过滤和布局
```

如果插件功能本质只是“显示 Buff/Debuff”，优先迁移显示架构，不要继续复制 12.0.7 的原始 Aura 数据管线。

---

# 八、Aura Sound API 发生替换/扩展

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

# 九、团队 Buff：`C_UnitAuras` 与 `C_CooldownViewer` 都扩展了

## C_UnitAuras

当前 PTR 新增/提供：

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

## C_CooldownViewer

12.1 当前 PTR 还新增：

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

这进一步说明 Blizzard 正把 Group Buff 展示/管理能力放进受支持 API，而不是要求插件自己扫描所有 Aura。

---

# 十、CooldownViewer / CDM 数据结构有实际变化

12.0.7 的 `CooldownViewerCooldown` 字段比较少。

当前 12.1 PTR 69189 中结构包括：

```text
cooldownID
spellID                 -- 当前变为 Nilable = true
spellCategoryID          -- NEW
omega/overrideSpellID
```

注意：上面不是实际字段名列表中的 `omega`。准确结构应按下列字段使用：

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

相对 12.0.7 明确新增/变化的重点：

```text
spellID: number → number | nil
spellCategoryID: number | nil

equipSlot: luaIndex | nil
buffSlot: luaIndex | nil
isInvisible: bool
```

另外新增 `GroupBuffItem` 数据结构和 `GetGroupBuffItems()`。

## 对 CDM 类插件的意义

不要继续假设：

```lua
local info = C_CooldownViewer.GetCooldownViewerCooldownInfo(id)
local spellID = info.spellID -- 永远存在
```

12.1 必须允许：

```text
spellID == nil
```

并根据：

```text
spellCategoryID
equipSlot
buffSlot
```

判断该 Cooldown 条目可能来自技能类别、装备槽或 Buff 槽。

对于读取暴雪 CDM 配置/语音映射的插件，这是比普通 `C_Spell.GetSpellCooldown()` 更直接的 12.1 迁移点。

---

# 十一、Unit API：12.1 继续扩大 Identity / Possession Secret Domain

注意：**Unit Identity Secret 并不是 12.1 才出现。**

12.0.7 已经有多种身份 API 带：

```text
SecretWhenUnitIdentityRestricted
```

例如 `UnitGUID`、`UnitFullName`、`UnitOwnerGUID`、`UnitPVPName` 等本来就不能当作 12.1 新限制。

12.1 的重要变化是：更多 API 被纳入这些 Secret domain，或改用更细粒度 predicate。

## 当前确认的新增/扩展例子

### 职业

当前 PTR 对以下函数加入：

```text
SecretWhenUnitIdentityRestricted = true
```

```lua
UnitClass(unit)
UnitClassBase(unit)
```

因此不要默认对任意敌方/受限单位都可以安全做：

```lua
local _, class = UnitClass(unit)
if class == "MAGE" then
    ...
end
```

### 角色职责

当前 PTR：

```lua
UnitGroupRolesAssigned(unit)
UnitGroupRolesAssignedEnum(unit)
UnitGetAvailableRoles(unit)
```

都需要考虑：

```text
SecretWhenUnitIdentityRestricted = true
```

### 团队身份

当前 PTR 对以下函数加入/强化 identity restriction：

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

### PvP 身份

```lua
UnitIsPVP
```

当前 PTR 纳入 Unit Identity restriction。

### Phase

```lua
UnitPhaseReason
```

当前 PTR 纳入 Unit Identity restriction。

### Honor Level：69189 最后新增

当前最新 build 中：

```lua
UnitHonorLevel(unit)
```

新增：

```text
SecretWhenUnitIdentityRestricted = true
```

这就是 69189 相对 69111 的真实 Secret 变化之一。

---

# 十二、`UnitName()` Secret domain 进一步细分

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

新的 predicate 说明大意：

```text
按正常 Unit identity secrecy 规则处理，
但 PvP 中被查询单位是玩家时存在例外。
```

这说明 Blizzard 正把 Secret 范围拆成更具体的 domain，而不是只用一个总的 Unit Identity 开关。

不要把：

```lua
UnitName(unit)
```

和所有其他 identity API 假设为完全相同的 Secret 条件。

---

# 十三、Inspect 专精迁入 `C_SpecializationInfo`

12.1 当前 PTR 新增正式 namespaced API：

```lua
C_SpecializationInfo.GetInspectSpecialization(unit)
```

当前生成文档：

```text
SecretWhenUnitIdentityRestricted = true
SecretArguments = "AllowedWhenUntainted"
```

返回：

```text
specializationID: number
```

Blizzard 自己的 Inspect UI 已从旧写法：

```lua
GetInspectSpecialization(unit)
```

迁移到：

```lua
C_SpecializationInfo.GetInspectSpecialization(unit)
```

旧全局目前仍有 Deprecated 兼容别名，但新代码应使用 namespaced API。

---

# 十四、Possession Secret 在 69111 被独立出来

69111 新增 predicate：

```text
SecretWhenUnitPossessionRestricted
```

当前说明的核心含义是：

```text
基于 Aura secrecy 产生 Secret，
但玩家直接控制的 unit token 有例外。
```

同时：

```lua
UnitIsCharmed(unit)
UnitIsPossessed(unit)
```

从：

```text
SecretWhenAurasRestricted
```

改成：

```text
SecretWhenUnitPossessionRestricted
```

这是一次**规则细分**，不是简单“限制加重”。

---

# 十五、`UnitIsUnit()` 的限制不是 12.1 新增

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

# 十六、12.1 ForbiddenAspect 模型

当前 PTR 有：

```text
ForbiddenAspect
```

当前生成文档定义的主要 Aspect 包括：

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

# 十七、Spell / Cooldown：迁移量较小，但有实际变化

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

## 最后 PTR build 没有再重写核心 Cooldown 签名

`68914 → 69189` 的最后三次提交中，没有再次修改 `SpellDocumentation.lua` 的核心 cooldown API。

因此不要写成：

```text
69189 又重新改变了 C_Spell.GetSpellCooldown
```

当前真正需要关注的是既有 Secret 规则 + CooldownViewer/CDM 数据结构扩展。

---

# 十八、69111 新增 SecondsFormatter 取整控制

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

- `RoundUp`：不显示毫秒时，小数秒向上取整到下一秒；
- `Truncate`：不显示毫秒时，直接截断到当前整秒。

这对自定义 Aura duration、Cooldown countdown、状态条文字等 UI 有用。

不要自己用不一致的 `math.ceil` / `math.floor` 逻辑去模拟 Blizzard 的时间显示规则，如果当前场景可以直接使用 `SecondsFormatter`。

---

# 十九、69111 新增 Texture SVG API

`SimpleTextureBase` Script Object API 新增：

```text
ClearSVG()
SetSVG(svgAsset) -> success: bool
```

其中 `SetSVG` 当前带：

```text
SecretArguments = "AllowedWhenTainted"
```

这属于一般 UI 能力扩展，不是战斗信息 API，但做原生风图标/UI 时可以纳入可用能力列表。

---

# 二十、69189 其他新增 API

## Browser

```lua
C_Browser.CloseFullscreenBrowser()
```

新增同步事件：

```text
FULLSCREEN_BROWSER_SPINNER_SHOW
FULLSCREEN_BROWSER_SPINNER_HIDE
```

Blizzard 新增 `Blizzard_FullscreenBrowser` UI 模块来消费这些事件。

## Delves / Lair

```lua
C_DelvesUI.HasActiveLFGLair()
C_DelvesUI.IsInLair()
```

Blizzard 自己已经在 DelvesDifficultyPicker / InstanceDifficulty 中切换到这些新接口。

这些 API 与 Aura/Secret 主迁移无关，但属于 69189 真实新增，做“完整 PTR API 记录”时应保留。

---

# 二十一、69111 低风险 UI/Housing 新增接口

当前生成文档还新增：

```text
HousingBlueprintUI.CanExportRoom(roomGUID) -> canExport
HousingLayoutUI.RoomHasStairs(roomGUID) -> hasStairs
```

这类 API 与一般战斗插件关系较低，可以记录但不需要进入 QFX 战斗功能迁移优先级。

---

# 二十二、CombatLog 当前不是 12.1 迁移重点

当前核实的：

```text
CombatLogDocumentation.lua
```

在 live / ptr 的核心生成文档内容没有看到此次 12.1 对 12.0.7 的实质迁移变化。

`C_CombatLogSecure` 也并不是 12.1 才新增；12.0.7 已经存在。

所以以下类型功能目前优先级低于 Aura/Unit/CDM：

- `COMBAT_LOG_EVENT_UNFILTERED` 统计；
- 施法成功后的历史统计；
- 打断次数统计；
- 非 Secret 的战斗日志文本处理。

但仍需遵守原本已经存在的 CombatLog restriction。

---

# 二十三、这些东西“看起来新增”，但不要错误归因

不要仅依赖 GitHub branch compare 的 added/modified 文件数量。

例如：

- `canaccessvalue` / `canaccessallvalues` / `canaccesstable` / `canaccesssecrets` 等 Secret helper 在 12.0.7 已经存在；
- `UnitIsUnit` 的 comparable-token restriction 在 12.0.7 已存在；
- `C_Spell.GetSpellCooldown` 的 Cooldown Secret 规则不是 12.1 新增；
- `C_CombatLogSecure` 不是 12.1 新增；
- 69027 删除 `.zmp` 文件不代表 API 删除。

真正值得记录的是：

```text
Aura access boundary
Aura display architecture
Unit identity predicate 扩展/细分
Possession predicate
ForbiddenAspect
CooldownViewer/CDM 数据扩展
最后 PTR build 的少量新 UI API
```

---

# 二十四、12.0.7 → 12.1 兼容设计建议

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

## 4. CDM/CooldownViewer 不要假设 spellID 永远存在

12.1 当前结构允许：

```text
spellID == nil
```

需要优先检查：

```text
spellCategoryID
equipSlot
buffSlot
```

再决定条目来源和显示逻辑。

## 5. Preview / 设置界面使用假数据

如果设置 UI 需要展示：

- Aura 图标；
- 层数；
- 持续时间；
- 队友角色；
- Boss Debuff；

应使用明确的 preview/fake data，不要为了预览去读取受限实战数据。

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
- 宠物/守护者/魅惑单位（如果涉及）；
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

以及任何来自：

```text
RequiresUnitAuraAccess
RequiresNonSecretAura
SecretWhenUnitIdentityRestricted
SecretWhenUnitPossessionRestricted
ForbiddenAspect
```

的 Lua error。

---

# 二十六、给 Codex 的迁移判定顺序

当用户要求“把 12.0.7 插件适配 12.1”时：

1. 先读取目标分支 `version.txt`。
2. 再读取目标 API 的 generated documentation。
3. 对比 12.0.7 与当前 PTR 的 **restriction metadata**。
4. 判断旧限制是否 12.0.7 已经存在，避免错误归因。
5. Aura 显示优先查 AuraContainer / CustomAuraButton。
6. Unit API 检查对应 Secret domain，包括 Identity / NameIdentity / Possession。
7. Blizzard Script Object 检查 Forbidden Aspect，而不是只看传统 combat lockdown。
8. CDM/CooldownViewer 检查 `spellID` nilability、`spellCategoryID`、`equipSlot`、`buffSlot`、Group Buff。
9. Spell/Cooldown 先确认是否只是已有 Secret 规则继续存在。
10. CombatLog 不要因为版本升级就无理由重写；只有实际 API diff 才改。
11. 检查最后几个 PTR commit，避免文档停在旧周 build。
12. 最后给出：**已确认、PTR-only、待正式服 live 验证** 三类结论。

---

# 二十七、当前上线前结论

截至 **2026-08-10 / PTR 12.1.0.69189**：

- `live` 仍是 **12.0.7.68974**；
- 当前 PTR API 最新公开源码是 **69189**；
- 68914 之后没有再次发生 Aura/Spell/Cooldown 核心架构大翻转；
- 69111 补了 Aura stealable 显示过滤、Possession predicate、SecondsFormatter rounding、SVG；
- 69189 补了 Browser/Delves API，并让 `UnitHonorLevel` 进入 Unit Identity Secret；
- 对插件开发影响最大的仍然是 **Aura access boundary + AuraContainer + Unit Identity Secret + CooldownViewer 数据扩展**。

**正式服上线后必须再以新的 `live` build 做一次 `12.0.7 live → 12.1.0 live` 最终 diff；只有那次结果才能标记为“12.1.0 正式服最终 API”。**
