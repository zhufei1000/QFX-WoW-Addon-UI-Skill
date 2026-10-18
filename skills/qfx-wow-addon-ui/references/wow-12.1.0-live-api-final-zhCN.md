# WoW 12.1 当前 API 基线（Live 12.1.5.70448 / PTR 12.1.7.70424）

用于 Retail 12.1.5 正式服插件开发、兼容性审查，以及对 PTR / PTR2 后续 API 变化进行预警。

> 本文件严格区分 **Live 正式合同** 与 **PTR / PTR2 预警**。除非明确写明已进入 Live，否则 PTR / PTR2 API 不应直接作为正式服可用接口。

## 当前基线

最后核实：**2026-10-18**。

- Retail `live`：**12.1.5.70448**
- Live HEAD：`b9be9379719047977fca4dba1bb1d9988e8840b3`
- Retail `ptr`：**12.1.7.70424**（新版本预警分支；其新增接口不能当作 Live API）
- Retail `ptr2`：**12.1.5.70340**
- PTR2 HEAD：`12380f8cdc541b7f0963f74cbe0874c21a857fbb`
- `beta`：12.0.1.66220（当前不作为 12.1 主参考）

Gethe 当前版本：

```text
live  = 12.1.5.70448
ptr   = 12.1.7.70424
ptr2  = 12.1.5.70340
beta  = 12.0.1.66220
```

关键判断：

- Live 已正式进入 **12.1.5**；
- Live **70391 → 70448** 的最新提交只调整 `GroupLootFrame.lua` 与 `version.txt`，**没有修改 `Blizzard_APIDocumentationGenerated`**；
- 当前重点高风险 generated API 文档（UnitAura / Unit / Spell / CombatLog / CooldownViewer / ForbiddenAspect / SecretPredicates / PvP / SocialRestrictions / VoiceChat / RaidMarkers）在 Live 70448 与 PTR2 70340 内容一致；
- 因此此前 69952 / 70077 阶段标记为 PTR2-only 的主要 12.1.5 API，现在应按 **Live 正式合同**处理。

---

# 1. 当前结论

截至 **Live 12.1.5.70448**：

- 12.1 的 Aura 访问限制、Secret Predicate、Unit Identity Secret、Spell/Cooldown、TTS、CombatLog 与 ForbiddenAspect 基础规则继续有效；
- `C_UnitAuras.GetRefreshCarryOverDuration(unit, auraInstanceID, spellID?)` 已进入 Live，可作为 Pandemic / Aura 刷新继承时间的正式接口；
- `CooldownSetSpellFlags.SelectHighestLevelLinkedSpell = 4` 已进入 Live，CDM / CooldownViewer 解析器不能再默认只认基础 `spellID` 或 `linkedSpellIDs[1]`；
- 全局 `GetArenaOpponentSpec(index)` 已进入 Live，但 `SecretReturns = true`，不能当普通 specializationID 做 Lua 比较、查表、缓存或自动决策；
- `ForbiddenAspect` 正式包含 `SetTexture`、`QueryRotation`、`QueryAnimationProgress`、`AddAnimations`，Texture / Animation 状态不能再被当作稳定 side channel；
- `C_SocialRestrictions.CanSendChat()`、Age Verification 相关 API 与 VoiceChat Chat Messaging Lockdown 限制均已进入 Live；
- `C_UnitAuras.AddAuraSound` 正式文档明确：声音最多播放 5 秒，`throttleSeconds` 必须位于 0～5 秒（含）；
- Live 70448 与 PTR2 70340 的重点高风险 generated API 合同当前一致；70391 → 70448 不存在新增/删除/签名/Secret/Restriction 合同变更。

正式开发默认基线：

```text
Live 12.1.5.70448
```

PTR2 目前主要用于后续变化预警，而不是当前 12.1.5 API 的“更先进版本”。**PTR 12.1.7.70424** 则已经有一批新增接口，必须单独按预警处理。

### Live 70448：额外拾取 UI 行为变化（非 API 合同）

Gethe 的 Live 70448 提交只修改 `version.txt` 与 `Blizzard_UIPanels_Game/Mainline/GroupLootFrame.lua`：

- `BonusRollFrame_StartBonusRoll()` 新增一个 5 秒间隔的 `C_Timer.NewTicker`，只在 `frame.state == "prompt"`（等待玩家选择）时刷新 `GroupLootContainer_Update()` 并保持窗口显示；
- `BonusRollFrame_CloseBonusRoll()` 取消刷新 ticker；
- **不是** Aura / Unit / Spell / CombatLog / CooldownViewer 或 Secret 合同变化；
- QFXBeggar 等插件只有直接 Hook `BonusRollFrame`、`GroupLootContainer` 或额外拾取窗口状态时才需要做对应 UI 兼容性核查；普通掉落 / Roll 不应被混为一谈。

### PTR 12.1.7.70424：新 API 预警（未进入 Live）

以下来自 PTR `Blizzard_APIDocumentationGenerated`，**不能直接用于 Live 12.1.5**：

1. `GroupBuffItem.displaySpellID`（CooldownViewer）：`spellID` 是各技能等级共享的持久化 key；`displaySpellID` 代表用于名称、图标、Tooltip 的技能——已学最高等级，若都未学则为最低等级。CDM / 语音映射应该区分持久化标识与显示技能 ID，不能把它们混为同一含义。
2. `C_ActionBar.EnableActionCombatActionRangeCheck(actionID, enable)` 与同步事件 `ACTION_COMBAT_ACTION_RANGE_CHECK_UPDATE(slot, isInRange, checksRange)`：用于订阅当前目标下的动作战斗范围变化。`checksRange=false` 时不要采用 `isInRange` 作结论。该函数 `SecretArguments = "AllowedWhenUntainted"`。这是动作可用距离事件，不是任意敌方单位的精确距离接口。
3. `C_Spell.IsActiveSpell(spellIdentifier, targetUnit?)`：检查切换型技能当前是否处于激活状态，目标可选，默认玩家或宠物；带 `SecretWhenUnitAuraRestricted=true`、`SecretWhenUnitIdentityRestricted=true` 与 `SecretArguments="AllowedWhenTainted"`，不得把返回 bool 无条件视为普通值。
4. `C_Spell.GetItemCooldown(itemID)`：返回 `SpellCooldownInfo`，`MayReturnNothing=true`，`SecretArguments="AllowedWhenTainted"`；按文档应处理找不到物品/冷却中的空返回，不能无条件解包。
5. `C_SpellBook.IsSpellBookItemLowRank(slotIndex, spellBank)`：识别已学更高等级技能对应的低等级技能书条目。与 `displaySpellID` 一起有助于 CDM / MCD 技能等级映射。
6. `UnitIsInInteractRange(unit)`、`UnitHasLootInteraction(unit)`：用于交互距离状态和拾取交互状态判断；均有 `SecretArguments="AllowedWhenUntainted"`。
7. `UnitHasEffectivelyTankAura(unit?)`：查看有效坦克 Aura 状态，带 `SecretWhenUnitIdentityRestricted=true` 和 `SecretArguments="AllowedWhenUntainted"`，不可据此绕过 unit identity 限制。

以上仅是 **12.1.7 PTR** 合同预览。当前正式服仍以 Live 70448 为准。相关来源：
- `Gethe/wow-ui-source` `ptr/Interface/AddOns/Blizzard_APIDocumentationGenerated/CooldownViewerDocumentation.lua`
- `ActionBarFrameDocumentation.lua`、`SpellDocumentation.lua`、`SpellBookDocumentation.lua`、`UnitDocumentation.lua`

---

# 2. Aura：12.1 正式服核心限制

12.1 Live 中大量 `C_UnitAuras` API 带：

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
C_UnitAuras.GetRefreshCarryOverDuration
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

### 插件设计规则

高风险功能包括：

- 单位框架 Buff / Debuff；
- 姓名板 Aura；
- Boss Debuff；
- 队友 Debuff；
- Aura 层数 / 持续时间战斗判断；
- 根据 Aura 是否存在触发逻辑。

如果需求只是显示 Aura，优先使用：

```text
AuraContainer
ManagedAuraContainer
CustomAuraButton
C_AuraContainerUtil
```

禁止通过 nil、Lua error、table 长度、frame Show/Hide、child count、anchor/layout 变化等 side channel 还原 Secret Aura。

---

# 3. Live 69465：Unit 与 Aura 身份过滤更新

`UnitCanAssist` 由：

```lua
UnitCanAssist(unit, target)
```

扩展为：

```lua
UnitCanAssist(
    unit,
    target,
    canAssistImmunePC,
    canAssistUninteractable
)
```

新增两个可选布尔参数，默认均为 `false`：

```text
canAssistImmunePC
canAssistUninteractable
```

同时新增：

```lua
UnitIsPlayerControlledOrGroupMember(unit)
```

其合同包含：

```text
SecretArguments = "AllowedWhenUntainted"
```

Blizzard generated documentation 明确说明，它会对以下单位返回 true：

```text
player
pet
vehicle
partyn
partypetn
raidn
raidpetn
```

### Blizzard 原生使用方式

69465 的 `AuraContainerUtil.CanApplyIdentityCandidateFilters()` 已改为：

- Helpful Aura 对玩家本人、小队/团队成员及其宠物可直接通过身份过滤；
- 对 `UnitCanAssist` 判断时，可忽略 immune / uninteractable 限制；
- 这样可避免载具、传送、Mind Control 等边界状态导致 Aura 身份过滤错误。

### 对插件的影响

不要再假设：

```lua
UnitCanAssist("player", unit)
```

在所有状态下都能代表稳定的身份关系。

涉及队伍 Aura、单位框架、辅助目标、可交互性与载具状态时，应优先参考 Blizzard 当前调用方式，并在必要时通过兼容层封装。

---

# 4. Private Aura：`visualAlert` Secret 行为

Live 69465 的 Blizzard PrivateAurasUI 明确记录：

```text
visualAlert is secret due to the spell ID it is based on being secret.
```

Blizzard 在 secure environment 内部使用：

```lua
secretunwrap(visualAlert)
```

再决定对象池模板。

### 插件设计规则

这不是普通 AddOn 可依赖的公开解密路径。

普通插件不得尝试复制 Blizzard secure environment 的 `secretunwrap` 用法来绕过 Secret 限制。

---

# 5. Live 69404：HookScript / SetScript SecretArguments 放宽

以下 generated API：

```text
SimpleAnimAPI.HookScript
SimpleAnimAPI.SetScript
SimpleAnimGroupAPI.HookScript
SimpleAnimGroupAPI.SetScript
SimpleScriptRegionAPI.HookScript
SimpleScriptRegionAPI.SetScript
```

其：

```text
SecretArguments = "NotAllowed"
```

改为：

```text
SecretArguments = "AllowedWhenUntainted"
```

但仍保留：

```text
RequiresAssignableScript = true
ChecksForbiddenAspects = ScriptBindings
```

### 对插件的影响

这是兼容性放宽，但不是解除安全限制。

仍然必须遵守：

- taint 规则；
- ForbiddenAspect；
- secure / protected frame 限制；
- ScriptBindings 检查。

不要把 `AllowedWhenUntainted` 理解成“Secret 值可以被读取或任意参与 Lua 逻辑”。

---

# 6. Live 69497：TTS 正式进入 ConditionalSecret

`C_VoiceChat.SpeakText()` 的 `text` 参数已正式变成：

```lua
{ Name = "text", Type = "cstring", Nilable = false, ConditionalSecret = true }
```

同时：

```text
VOICE_CHAT_TTS_PLAYBACK_BOOKMARK.bookmarkName
```

也变成：

```text
ConditionalSecret = true
```

### 对插件的影响

所有使用：

```lua
C_VoiceChat.SpeakText(...)
```

的 TTS 模块都应假设文本可能带 Secret 传播属性。

不要对可能为 Secret 的文本做：

- 比较；
- 拼接；
- 序列化；
- 日志打印；
- 作为普通 Lua 条件分支来源。

如果来源值允许直接传入支持 ConditionalSecret 的 API，应优先“直接传递”，而不是先在 Lua 层加工。

---

# 7. CooldownViewer / CDM 当前结构

12.1 Live 的 `CooldownViewerCooldown` 仍包含：

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

因此插件不能假设每个 CooldownViewer 条目都一定有 `spellID`。

推荐来源判定：

```text
spellID
→ spellCategoryID
→ equipSlot
→ buffSlot
```

正式保留：

```lua
C_CooldownViewer.GetGroupBuffItems()
```

---

# 8. CooldownViewer 原生 GCD 过滤

在 12.1.0.69323 的原生 CooldownViewer 实现中，暴雪增加了装备槽冷却的 GCD 过滤逻辑：

当一个 CooldownViewer 条目来源于 `equipSlot`，且：

```text
spellCooldownInfo.isOnGCD == true
```

时，不把这次 GCD 当作装备本身的真实冷却显示。

### 对插件的影响

处理饰品、装备槽、物品技能冷却时，不应把 GCD 误判为装备真实 CD。

建议兼容逻辑：

```lua
if equipSlot and spellCooldownInfo.isOnGCD then
    -- 忽略本次 GCD，不作为装备真实冷却
end
```

---

# 9. CooldownBroadcaster：专精打断技能独立追踪

Live 69404 的 Blizzard CooldownBroadcaster 从：

```text
MAX_COOLDOWNS = 6
```

调整为：

```text
MAX_BASE_COOLDOWNS = 6
MAX_INTERRUPT_COOLDOWNS = 2
MAX_COOLDOWNS = 8
```

并新增：

```text
InterruptSpellsBySpec
```

用于按专精维护打断技能。

### 对插件的影响

做小队打断监控、CD 同步、专精打断库时，可以参考 Blizzard 的官方数据组织方式：

```text
specID → interrupt spell IDs
```

普通大技能与打断技能应视为不同类别管理，而不是全部混在同一个固定容量列表中。

---

# 10. Unit Identity Secret

12.1 Live 需要持续重点检查：

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

这些 API 在对应受限上下文中受：

```text
SecretWhenUnitIdentityRestricted
```

影响。

`UnitName` 使用：

```text
SecretWhenUnitNameIdentityRestricted
```

`UnitIsCharmed` / `UnitIsPossessed` 使用：

```text
SecretWhenUnitPossessionRestricted
```

不要对任意 nameplate / enemy / PvP unit 默认执行 Secret 值比较或分支。

---

# 11. Inspect 专精 API

推荐：

```lua
C_SpecializationInfo.GetInspectSpecialization(unit)
```

并遵守：

```text
SecretWhenUnitIdentityRestricted
SecretArguments = "AllowedWhenUntainted"
```

旧全局兼容入口不应作为新代码首选。

---

# 12. ForbiddenAspect

12.1 Live 正式包含 `ForbiddenAspect` 模型。

不要只依赖：

```lua
frame:IsForbidden()
```

来判断对象是否可：

- Hook；
- RegisterEvent；
- SetParent；
- QueryFocus；
- 修改 ScriptBindings。

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

# 13. Aura Sound 当前正式路径

12.0.7 的：

```lua
C_UnitAuras.AddPrivateAuraAppliedSound
C_UnitAuras.RemovePrivateAuraAppliedSound
C_UnitAuras.TriggerPrivateAuraShowDispelType
```

在 12.1 generated docs 中已移除。

当前 Live 12.1.5 路径：

```lua
C_UnitAuras.AddAuraSound
C_UnitAuras.RemoveAuraSound
```

`AddAuraSound` 当前合同包含：

```text
HasRestrictions = true
SecretArguments = "AllowedWhenUntainted"
```

并明确规定：

```text
声音播放最多 5 秒；
throttleSeconds 必须在 0～5 秒（含）范围内。
```

### 对插件的影响

适合：

- 短提示音；
- “驱散”“危险”“宠物死亡”“技能好了”等短语音；
- 由 Aura 事件直接驱动的短声音提醒。

不适合：

- 超过约 5 秒的长 TTS；
- 依赖 Aura Sound 播完整说明句；
- 试图通过 Aura Sound 读取或还原 Secret Aura。

`AddAuraSound` 仍不是读取 Secret Aura 原始数据的后门。

---

# 14. Spell / Cooldown

核心仍为：

```lua
C_Spell.GetSpellCooldown
C_Spell.GetSpellCharges
```

Cooldown Secret 规则并不是 12.1 才新增，12.0.7 已经存在。

12.1 已确认变化包括：

```lua
C_Spell.GetLastCategoryCooldownSource(spellCategory)
```

以及：

```lua
iconID, originalIconID, conditionalIconID = C_Spell.GetSpellTexture(spellID)
```

不要把既有 Cooldown Secret 规则错误归因为“12.1 新封锁”。

---

# 15. CombatLog

12.1.5 的 generated API 已明确拆分出 CombatLog 普通、Shared、Internal、Secure 等合同层。

截至 Live 70391 / PTR2 70340：

- 重点 CombatLog generated API 内容在两个分支当前一致；
- 最近的 70340 → 70391 推进没有新增 CombatLog 合同变化；
- 普通战斗日志统计仍可继续，但不能把 Internal / Secure 能力视为普通 AddOn 可用；
- 涉及 Secret / Restricted 数据时，仍必须逐函数读取当前 metadata，而不是仅凭“CombatLog 以前能用”推断安全性。

因此 CombatLog 当前不是本轮需要大规模重写的区域，但仍应保持高版本核验习惯。

---

# 16. Discord 当前合同

Live 12.1 已包含：

```lua
C_Discord.GetDiscordUserName(userID)
```

合同：

```text
HasRestrictions = true
SecretArguments = "AllowedWhenUntainted"
```

返回：

```text
userName : KStringDiscordUserName
```

`DiscordChatInfo.username` 已移除。

`GetDiscordUserCommunityLink` 当前签名不再包含旧 `username` 参数。

---

# 17. Live 69587：无角色要求的自动匹配团队

Live 69587 已正式加入：

```lua
C_LFGInfo.IsInMatchmadeRaidWithoutRoleRequirements()
    -> result: bool
```

Blizzard CompactRaidFrames 已实际使用该 API：

- 注册 `LFG_UPDATE`；
- 在无角色要求的自动匹配团队中停止单独显示 Main Tank / Main Assist；
- 避免匹配团队产生大量自动标记主坦导致布局异常。

### 对插件的影响

如果插件实现团队框架中的 Main Tank / Main Assist 独立分组，现在可以在 Live 使用该 API。仍建议保留 capability check，以兼容旧 build：

```lua
local fn = C_LFGInfo and C_LFGInfo.IsInMatchmadeRaidWithoutRoleRequirements
if fn and fn() then
    -- 不单独显示 Main Tank / Main Assist flagged members
end
```

---

# 18. Live 69933：ForbiddenAspect 扩展到 Texture

Live 69933 新增：

```text
Enum.ForbiddenAspect.SetTexture    = 2048
Enum.ForbiddenAspect.QueryRotation = 4096
```

并开始由 `SimpleTextureBaseAPI` 实际检查：

```text
ClearSVG()        -> SetTexture
SetColorTexture() -> SetTexture
SetSVG()          -> SetTexture
GetRotation()     -> QueryRotation
```

### 作用

这两个值不是普通插件主动调用的函数，而是 Blizzard 安全系统给 UI 对象附加的“禁止能力”。

- `SetTexture`：对象被标记后，相关 API 不能替换/清除该纹理内容；
- `QueryRotation`：对象被标记后，不能读取其旋转状态。

### 可以用于什么

对插件开发者来说，它们主要用于判断旧代码是否需要安全降级：

- Hook Blizzard Aura / 姓名板纹理后再强制改色或换 SVG；
- 用 `GetRotation()` 观察受保护纹理状态；
- 通过纹理改变、旋转角度、显示状态推断 Secret 数据。

这类代码以后都必须按 ForbiddenAspect 失败路径设计，而不能假设拿到 Texture 对象就一定能读写。

---

# 19. Live 69933：Raid Marker 进入 Chat Messaging Secret

`IsRaidMarkerActive(index)` 当前合同新增：

```text
SecretInChatMessagingLockdown = true
SecretArguments = "AllowedWhenUntainted"
```

### 作用

正常情况下它仍然用于查询世界标记（Raid Marker）是否处于激活状态；但在 Chat Messaging Lockdown 环境中，返回值受 Secret 规则保护。

### 可以用于什么

普通状态下仍可用于：

- 世界标记 UI；
- 标记按钮状态同步；
- 非受限环境下判断某个 Raid Marker 是否已放置。

但不要在受限聊天环境里依赖它自动决定发言内容、拼接聊天文本或以普通 bool 做分支。

---

# 20. Live 12.1.5：C_UnitAuras.GetRefreshCarryOverDuration

新增合同：

```lua
C_UnitAuras.GetRefreshCarryOverDuration(
    auraInstanceUnit,
    auraInstanceID,
    spellID -- optional
) -> newDuration | nil
```

限制：

```text
RequiresUnitAuraAccess = true
RequiresValidUnitAuraInstance = true
SecretWhenUnitAuraRestricted = true
SecretArguments = "AllowedWhenTainted"
```

### 它返回什么

它返回的不是“刷新后的总持续时间”，而是：

> 如果现在重新施放同一个 Aura，旧 Aura 剩余时间中有多少秒会被继承到新 Aura。

这正是 Pandemic / 提前刷新窗口最需要的量。

例如一个 DoT 基础持续时间 18 秒，当前剩余 4 秒，而客户端判定这 4 秒可以全部继承，则该 API 返回约 4 秒。

`GetRefreshExtendedDuration()` 更偏向回答“现在刷新后，新 Aura 的总持续时间会是多少”；`GetRefreshCarryOverDuration()` 则直接回答“其中有多少是旧 Aura 带过去的时间”。

### Blizzard 已经怎么用

Live 12.1.5 CooldownViewer 已直接使用：

```lua
local carriedOverDuration =
    C_UnitAuras.GetRefreshCarryOverDuration(
        unit,
        auraData.auraInstanceID,
        spellID
    ) or 0

local pandemicStartTime =
    auraData.expirationTime - carriedOverDuration
```

AuraContainer 也直接按：

```text
Pandemic Start = expirationTime - carriedOverDuration
Pandemic End   = expirationTime
```

计算安全刷新窗口。

### 对你的插件最有价值的用途

非常适合：

- DoT / HoT Pandemic 刷新提示；
- “现在刷新不会浪费持续时间”的视觉提醒；
- CDM PandemicTime 语音提示；
- 技能推荐系统判断刷新窗口；
- Aura 图标安全刷新区；
- 不同天赋/技能等级改变基础持续时间时，让客户端自己算 carry-over。

### 为什么比自己算更好

以前常见做法是：

```text
GetRefreshExtendedDuration - GetAuraBaseDuration
```

或自己按“基础持续时间 × 某个比例”计算。

新 API 的优势：

- 客户端按真实规则预测；
- 不必硬编码天赋、被动、技能覆盖；
- 对特殊 Aura 更稳；
- Blizzard 自己已经改用它。

### 风险

它仍属于 Aura Secret 体系。如果当前 unit 的 Aura 访问受限，结果可能受 Secret 规则约束。不要因为返回类型是 number，就假设所有环境都能安全做 `carry > 0` 之类判断。

---

# 21. Live 12.1.5：GetArenaOpponentSpec(index)

新增全局 API：

```lua
specializationID, gender = GetArenaOpponentSpec(index)
```

合同：

```text
MayReturnNothing = true
SecretReturns = true
SecretArguments = "AllowedWhenUntainted"
```

### 作用

按竞技场对手槽位索引读取：

- 对手专精 ID；
- gender。

### 从功能意义上可以做什么

它对应的场景包括：

- 竞技场敌方专精显示；
- 对手专精头像/文本；
- PvP 队伍面板。

### 但普通插件最大的限制

**返回值是 Secret。**

所以不能把它理解成普通专精查询：

```lua
local specID = GetArenaOpponentSpec(1)
if specID == 71 then
    -- 武器战
end
```

这种 Lua 判断不是 Secret-safe 的设计。

也不要默认可以：

- 把 specID 作为 table key；
- 写入 SavedVariables；
- 序列化；
- 比较；
- 根据 specID 自动选择策略或技能提示。

因此它更像 Blizzard/安全 UI 管线的数据源，而不是重新向普通插件开放了可自由处理的竞技场敌方专精 ID。

---

# 22. Live 12.1.5：CooldownSetSpellFlags.SelectHighestLevelLinkedSpell

`CooldownSetSpellFlags` 新增：

```text
SelectHighestLevelLinkedSpell = 4
```

已有值：

```text
HideAura      = 1
HideByDefault = 2
```

### 作用

这是 CooldownViewer / CDM 的数据语义 flag，不是独立函数。

名称与 generated contract 表明：当一个 cooldown set 关联多个 linked spell 时，该条目可以要求按“最高等级 linked spell”语义选择实际技能，而不是固定使用基础 spell。

### 可以用于什么

对 CDM / 技能语音映射很有价值：

- 基础技能被天赋升级后选中正确版本；
- 同一能力存在多个等级/替代 spellID 时避免映射旧技能；
- linkedSpellIDs 不再简单取第一个；
- 图标、技能名、语音映射可以跟随当前有效的高等级版本。

### 建议

它已经进入 Live。正式服解析器应至少认识这个 flag，不要继续假设：

```text
永远 cooldown.spellID
或永远 linkedSpellIDs[1]
```

至于“最高等级”的具体解析规则，应继续跟随 Blizzard 当时的实现，不要仅凭 spellID 数值大小自行排序。

---

# 23. Live 12.1.5：动画状态也进入 ForbiddenAspect

Live 12.1.5 的 `ForbiddenAspect` 已扩展到 15 项，并包含：

```text
QueryAnimationProgress = 8192
AddAnimations          = 16384
```

### QueryAnimationProgress

会限制读取动画运行状态，例如：

```text
SimpleAnimAPI.GetElapsed
SimpleAnimAPI.GetProgress
SimpleAnimAPI.GetSmoothProgress
SimpleAnimAPI.IsDelaying
SimpleAnimAPI.IsDone
SimpleAnimAPI.IsPaused
SimpleAnimAPI.IsPlaying
SimpleAnimAPI.IsStopped
```

AnimationGroup 的 `GetElapsed`、`GetLoopState`、`GetProgress`、`IsDone`、`IsPaused`、`IsPendingFinish`、`IsPlaying`、`IsReverse` 等也受这一 ForbiddenAspect 检查。

### AddAnimations

例如：

```lua
AnimationGroup:CreateAnimation(...)
```

会检查 `Enum.ForbiddenAspect.AddAnimations`；`SimpleAnim:SetParent(...)` 也会检查目标 AnimationGroup 是否允许添加动画。

### 为什么 Blizzard 要这样做

动画也可能成为 side channel。如果受保护状态让动画开始/停止、进度或循环状态变化，而插件还能自由读取 `IsPlaying()` / `GetProgress()`，就可能间接反推出 Secret 信息。

因此 12.1.5 的方向很明确：不仅保护原始数据，也保护能间接泄露数据的 UI 状态。

---

# 24. Live 12.1.5：SocialRestrictions / VoiceChat / Chat Lockdown

此前 PTR2 70077 阶段出现的社交限制已经进入 Live。

当前可用：

```lua
C_SocialRestrictions.CanSendChat()
C_SocialRestrictions.CanReceiveChat()
C_SocialRestrictions.IsAgeVerificationRestricted()
C_SocialRestrictions.IsAgeVerificationRestrictedMinor()
C_SocialRestrictions.AcknowledgeAgeVerificationRestriction()
```

其中：

```text
C_SocialRestrictions.IsAgeVerificationRestrictedMinor()
HasRestrictions = true
```

### 对聊天/自动密语插件的意义

发送失败不能只判断：

- 是否被禁言；
- 是否 combat/chat lockdown；
- 是否频道本身不允许。

还应考虑账号级：

- Age Verification restriction；
- 其他 SocialRestrictions。

对自动密语、组队喊话、聊天条、Whisper、语音频道类插件，优先使用：

```lua
C_SocialRestrictions.CanSendChat()
```

作为“当前是否具备发送聊天条件”的统一入口之一。

### VoiceChat

Live 12.1.5 中大量 VoiceChat API / Event 已带：

```text
SecretInChatMessagingLockdown = true
```

`C_VoiceChat.SpeakText()` 当前仍允许 tainted 调用链传递文本，但：

```text
text
ConditionalSecret = true
```

因此对可能来源于 Secret 的文本，优先直接传递给支持 ConditionalSecret 的 API，不要先：

- 比较；
- 拼接；
- 打印；
- 序列化；
- 用作普通 Lua 条件分支。

这说明 Blizzard 正在把 Chat / Voice / STT / TTS 统一纳入更严格的消息自动化边界。

---

# 25. 正式服插件审查优先级

| 功能类型 | 风险 |
|---|---|
| Aura/Buff/Debuff 扫描与战斗判断 | 🔴 极高 |
| Aura 显示 / 单位框架 / 姓名板 | 🔴 极高 |
| Secret / secure frame / ScriptBindings | 🔴 极高 |
| CDM/CooldownViewer 数据读取与语音映射 | 🟠 高 |
| UnitName/Class/Role/GUID 类判断 | 🟠 高 |
| TTS / VoiceChat 文本传播 | 🟠 高 |
| Blizzard AuraButton/受保护 UI Hook | 🟠 高 |
| Spell/Cooldown 一般显示 | 🟡 中 |
| CombatLog 统计 | 🟢 较低 |
| Housing/RecentAllies | 🟢 低 |

---

# 26. 后续维护规则

从现在起：

- Retail 正式开发以 `live` **12.1.5.70448** 为当前基线；
- `ptr` **12.1.7.70424** 为下一版本的 API 预警来源；其新增内容未经 Live 确认前不能直接用于正式服；
- `ptr2` **12.1.5.70340** 当前重点高风险 API 合同与 Live 70448 一致，主要用于 12.1.5 历史对照；
- 旧文档中 69952 / 70077 的 PTR2-only 结论已经转为 Live 正式合同；
- 如果 `live` 或 `ptr2` build 继续增加，必须重新比较 `Blizzard_APIDocumentationGenerated`，不能只看版本号；
- 不要用 build number 写业务 feature flag，build 只作为文档 provenance；
- 所有 Aura、Unit、Spell/Cooldown、CombatLog、TTS/Voice、secure/forbidden API 决策必须读取当前目标 build 的 restriction metadata；
- Blizzard FrameXML 内部可用能力不自动等于普通 AddOn 可调用能力；
- 对 Secret 值的正确策略是重新设计数据流，而不是通过 UI side channel、动画、Texture 状态或 secure 内部函数绕过限制。

## 相关参考

- `wow-12.0.7-to-12.1-api-migration-zhCN.md`：12.0.7 → 12.1 的历史迁移差异与 PTR build 演进。
- `wow-12-api-source-rules.md`：API 来源和核实规则。
- `wow-12-secret-value-taint.md`：Secret / Taint / Forbidden Object 设计规则。

**当前结论：Live 12.1.5.70448 是当前正式开发基线；与 70391 相比，本轮只有 GroupLootFrame 额外拾取窗口的 UI 行为变化，没有 generated API 合同变化。PTR 12.1.7.70424 已新增 GroupBuffItem.displaySpellID、ActionBar 距离事件、Spell/SpellBook/Unit 等接口，仍只能预警。PTR2 12.1.5.70340 的重点高风险 generated API 合同与 Live 当前一致；此前 PTR2 的 Aura carry-over、CooldownViewer linked-spell、ArenaOpponentSpec Secret、Texture/Animation ForbiddenAspect、SocialRestrictions、VoiceChat/Chat Lockdown 与 Aura Sound 5 秒规则均已正式进入 Live。Aura、Secret、Unit、CooldownViewer、TTS/Voice、CombatLog 与 secure/forbidden 仍是 WoW 12.1.5 插件开发最需要持续核实的高风险区域。**
