# 常用 WoW API 专题入口

按功能选择查询方向；具体签名、空返回、事件参数及限制从 `wow_api.py search` 读取。下表入口已在所附 Retail Live 快照中核对，不将这些签名套用于 Classic。索引版本见 `api-index/manifest.json`，刷新方法见 `wow-api-lookup.md`。

## 功能索引

| 功能 | 优先检索 | 生成文档文件 | 实现时核对 |
|---|---|---|---|
| 背包、银行、物品格 | `C_Container.GetContainerItemInfo`、`C_Container.GetContainerNumSlots`、`Enum.BagIndex`、`BAG_UPDATE_DELAYED` | `ContainerDocumentation.lua`、`BagIndexConstantsDocumentation.lua` | 空格子/空返回；背包类型使用目标版本枚举；物品操作及银行访问限制；合并批量背包刷新 |
| 物品资料、缓存加载 | `C_Item.GetItemInfo`、`C_Item.GetItemInfoInstant`、`C_Item.RequestLoadItemDataByID`、`ITEM_DATA_LOAD_RESULT` | `ItemDocumentation.lua` | 完整物品资料可能尚未缓存；区分即时静态信息与异步完整资料；按 itemID 合并请求并处理失败 |
| 任务日志、目标 | `C_QuestLog.GetInfo`、`C_QuestLog.GetQuestObjectives`、`QUEST_LOG_UPDATE` | `QuestLogDocumentation.lua` | 任务日志索引与 questID 不同；标题行不是任务；重建日志后旧索引可能失效 |
| 地图、玩家位置 | `C_Map.GetBestMapForUnit`、`C_Map.GetPlayerMapPosition`、`PLAYER_ENTERING_WORLD` | `MapDocumentation.lua`；事件单独检索 | 地图查询可无结果；返回坐标所属地图、地下城/副本限制和单位可见性；不推断隐藏单位位置 |
| 插件通信、聊天 | `C_ChatInfo.RegisterAddonMessagePrefix`、`C_ChatInfo.SendAddonMessage`、`CHAT_MSG_ADDON`、`C_ChatInfo.SendChatMessage` | `ChatInfoDocumentation.lua` | 前缀注册、消息长度、节流和发送结果；收到的文本按外部数据验证；发送聊天仍受消息及 Secret 限制 |
| CVar、原生设置衔接 | `C_CVar.GetCVar`、`C_CVar.SetCVar`、`CVAR_UPDATE`；手写 Lua 的 `Settings.*` 另查 FrameXML | `CVarDocumentation.lua`、`ConsoleDocumentation.lua`；Settings 系统查同提交 UI 源码 | CVar 的文本值与默认值；区分用户偏好和插件 DB；QFX 设置控件仍使用 QFXWidgets，只有原生设置入口需要接入时才研究 Settings 注册方式 |
| 计时、事件、生命周期 | `C_Timer.NewTimer`、`C_Timer.NewTicker`、`SimpleFrameAPI:RegisterEvent`、`ADDON_LOADED`、`PLAYER_LOGIN`、`PLAYER_REGEN_ENABLED` | `UITimerDocumentation.lua`、`SimpleFrameAPIDocumentation.lua`；事件单独检索 | 保存并取消需要取消的计时器；只在工作期间保留 ticker；高频事件合并刷新；受保护设置脱战应用 |
| 加载状态、插件元数据 | `C_AddOns.GetAddOnMetadata`、`C_AddOns.IsAddOnLoaded`、`C_AddOns.LoadAddOn`、`ADDON_LOADED` | `AddOnsDocumentation.lua` | LoadOnDemand 和失败原因；版本在自己 ADDON_LOADED 后缓存；不要让运行时依赖打开设置页 |
| 技能、冷却、光环、单位 | `C_Spell.GetSpellInfo`、`C_Spell.RequestLoadSpellData`、`C_Spell.GetSpellCooldown`、`C_UnitAuras`、`UNIT_AURA`、`UNIT_COMBAT` | `SpellDocumentation.lua`、`UnitAuraDocumentation.lua`、`UnitDocumentation.lua` | 阅读全部限制元数据；区分安全显示和 Lua 可读数据；优先沿现有 Live / Secret 专题执行 |
| 控件、材质、文本 | `SimpleFrameAPI`、`SimpleTextureBaseAPI`、`SimpleFontStringAPI`；`CreateFrame`、模板、Mixin 查源码/资源 | 相应 `*APIDocumentation.lua` 与同提交 FrameXML | 方法继承、Environment、受保护和 Forbidden Aspects；文档类型名不是可调用的全局对象；QFXWidgets 已封装的控件不重复实现 |

文件列表示在 `Blizzard_APIDocumentationGenerated/` 中的检索入口，不保证某功能只出现在一个文件。`CVAR_UPDATE` 的 Payload 在 `ConsoleDocumentation.lua`；不要只搜同名命名空间文件就判定事件不存在。

## 按任务选择正确资料

### 异步资料与刷新

物品、技能、任务显示优先确定所需资料是否已就绪。未就绪时显示本地化加载状态，通过目标 API 对应的完成事件或同提交官方加载助手更新；避免每帧重试和无上限的请求队列。回调触发后重新检查所显示对象是否还是原来的 itemID / spellID / questID，防止旧请求覆盖新选择。

### 地图和日志的身份

持久状态保存稳定 ID。日志行索引、列表选中行、地图当前层级属于临时展示状态；收到更新后重新解析。先检查 API 的 Nilable / MayReturnNothing，再访问返回结构，不把“暂时没有结果”直接记成永久不存在。

### 聊天与插件通信

先检索目标 Build 的发送函数及事件 Payload，再决定分包、节流和重试上限。插件通信需要 schema / 长度 / 版本校验，不执行收到的 Lua。普通聊天、插件消息、TTS 是不同能力，不能互相假定权限或长度规则；现行限制参考 `wow-12-secret-value-taint.md`。

### 设置、控件和运行时能力

`Settings.*`、模板和 Mixin 可由手写 Lua/XML 提供，生成文档未命中时去同提交 FrameXML 搜索定义和使用处。示例插件只是使用线索。控件继承或 Blizzard 内部使用也不自动赋予普通插件调用权限；检查战斗、保护和 Secret/Forbidden 约束。

### Secret 数据

从 `UNIT_COMBAT`、Unit、Spell 或 Aura 取得数据时，检查事件 Payload 和结构体字段本身的标记，不能只查函数顶层。当前 Live 的 `UNIT_COMBAT.amount` 标有 `SecretValue = true`。允许不透明传递的值仍不可被普通 Lua 分支、算术或持久化消费；具体可用 setter 和调用者权限以目标 Build 合同为准。

## 维护专题时的边界

这里保留用途、入口和容易出错的决策，不复制整套签名手册。新增功能先用机器索引找声明，再阅读原始源文件；确实缺少生成声明时才使用同提交源码/资源及游戏内验证。每个常用领域逐步补充经过实际项目验证的规则，不把所有版本的接口堆进 `SKILL.md`。
