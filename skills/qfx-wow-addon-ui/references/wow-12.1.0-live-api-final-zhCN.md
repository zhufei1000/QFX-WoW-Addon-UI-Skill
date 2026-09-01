# WoW 12.1.0 当前 API 基线（Live 69497 / PTR 69587）

用于 Retail 12.1.0 正式服插件开发、兼容性审查，以及对 PTR 后续 API 变化进行预警。

> 本文件区分 **Live 正式合同** 与 **PTR 预警**。除非明确写明已进入 Live，否则 PTR API 不应直接作为正式服可用接口。

## 当前基线

最后核实：**2026-09-01**。

- Retail `live`：**12.1.0.69497**
- Live HEAD：`027d26c3406d3de2cbd2b1f67d468fe033a1bcd4`
- Retail `ptr`：**12.1.0.69587**
- PTR HEAD：`a89e9d0ceb7f6cd31e8fc5ca7df1a338ac0b1b58`
- `ptr2`：12.0.7.68887（当前不作为 12.1 主参考）
- `beta`：12.0.1.66220（当前不作为 12.1 主参考）

Gethe 当前版本：

```text
live  = 12.1.0.69497
ptr   = 12.1.0.69587
```

---

# 1. 当前结论

截至 Live 69497：

- 12.1 的 Aura 访问限制、Secret Predicate、ForbiddenAspect、CooldownViewer/CDM 数据结构、Unit Identity Secret、Spell/Cooldown 与 CombatLog 基础规则继续有效；
- Live 69404 放宽了部分 `HookScript` / `SetScript` 的 Secret 参数接收条件；
- Live 69465 新增 Unit 辅助判断参数与 `UnitIsPlayerControlledOrGroupMember`；
- Live 69497 正式把 TTS 文本与书签名纳入 `ConditionalSecret`；
- Blizzard 原生 CooldownBroadcaster 已开始独立维护专精打断技能；
- PTR 69587 新增 `C_LFGInfo.IsInMatchmadeRaidWithoutRoleRequirements()`，目前仍为 PTR-only。

因此，正式开发默认基线必须是：

```text
Live 12.1.0.69497
```

PTR 69587 只用于兼容预警与提前设计。

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

# 13. Aura Sound 当前路径

12.0.7 的：

```lua
C_UnitAuras.AddPrivateAuraAppliedSound
C_UnitAuras.RemovePrivateAuraAppliedSound
C_UnitAuras.TriggerPrivateAuraShowDispelType
```

在 12.1 generated docs 中已移除。

当前路径：

```lua
C_UnitAuras.AddAuraSound
C_UnitAuras.RemoveAuraSound
```

`AddAuraSound` 带 restrictions，不是读取 Secret Aura 原始数据的后门。

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

当前没有发现 Live 69497 对核心 CombatLog API 进行新的重大合同重构。

已有 restriction 继续遵守，但普通战斗日志统计仍不是本轮最高风险迁移区。

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

# 17. PTR 69587 预警：LFG 新 API

> **PTR-only：不要在 Live 69497 直接调用。**

PTR 69587 新增：

```lua
C_LFGInfo.IsInMatchmadeRaidWithoutRoleRequirements()
    -> result: bool
```

目前未看到额外 Secret / Restriction 标记。

Blizzard CompactRaidFrames 已实际使用该 API：

- 注册 `LFG_UPDATE`；
- 在无角色要求的自动匹配团队中停止单独显示 Main Tank / Main Assist；
- 避免匹配团队产生大量自动标记主坦导致布局异常。

### 对插件的影响

如果插件实现团队框架中的 Main Tank / Main Assist 独立分组，应预留兼容层：

```lua
if C_LFGInfo.IsInMatchmadeRaidWithoutRoleRequirements then
    -- PTR/未来 Live：根据该结果决定是否显示 flagged members
end
```

正式服启用前必须再次确认该 API 已进入 `live`。

---

# 18. 正式服插件审查优先级

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

# 19. 后续维护规则

从现在起：

- Retail 正式开发以 `live` **12.1.0.69497** 为当前基线；
- `ptr` **12.1.0.69587** 仅作为预警和兼容设计来源；
- PTR-only API 必须明确标记，不能默认写进 Live 代码路径；
- 如果 `live` build 继续增加，即使仍叫 12.1.0，也必须重新比较 `Blizzard_APIDocumentationGenerated`；
- 不要用 build number 写业务 feature flag，build 只作为文档 provenance；
- 所有 Aura、Unit、Spell/Cooldown、TTS、secure/forbidden API 决策必须读取当前目标 build 的 restriction metadata；
- Blizzard FrameXML 内部可用能力不自动等于普通 AddOn 可调用能力；
- 对 Secret 值的正确策略是重新设计数据流，而不是通过 side channel 或 secure 内部函数绕过限制。

## 相关参考

- `wow-12.0.7-to-12.1-api-migration-zhCN.md`：12.0.7 → 12.1 的历史迁移差异与 PTR build 演进。
- `wow-12-api-source-rules.md`：API 来源和核实规则。
- `wow-12-secret-value-taint.md`：Secret / Taint / Forbidden Object 设计规则。

**当前结论：Live 12.1.0.69497 是正式开发基线；PTR 12.1.0.69587 只用于预警。69404、69465、69497 已产生实际 API/安全合同变化，PTR 69587 新增 LFG API。Aura、Secret、Unit、TTS、CooldownViewer 与 secure/forbidden 仍是 WoW 12.1 插件开发最需要持续核实的高风险区域。**
