# WoW API 检索、快照和版本差异

需要查函数签名、事件参数、结构体、枚举、控件方法，或更新 API 基线时读取本文件。开发规则仍以 `wow-12-api-source-rules.md` 为入口；日常功能分类见 `wow-api-common-topics.md`。

## 范围与来源

`api-index/manifest.json` 和 `api-index/symbols.jsonl` 是同一份、可离线检索的机器索引。只读取 manifest 或运行查询，不把整个 JSONL 加载到模型上下文。

- 来源：同一不可变提交中的 `version.txt` 与 `Interface/AddOns/Blizzard_APIDocumentationGenerated/`。
- 覆盖该目录全部 Lua 文档表：全局函数、`C_*` 函数、ScriptObject 方法、事件及 Payload、结构体及 Fields、枚举及取值、常量、回调类型、precondition / secret 谓词，以及所属系统的元数据。
- 保留 Arguments、Returns、Nilable、MayReturnNothing、全部 Secret / Restriction 元数据和来源行号；未知标记不会被白名单过滤。
- `manifest.json` 记录客户端、分支、Build、提交、各类数量、每个源文件的 Git Blob / SHA-256，以及索引自身的 SHA-256。
- 这不是运行时全部能力清单：手写 FrameXML 的 `Settings.*`、模板、Mixin、部分全局（例如 `CreateFrame`）可能不在生成文档中。未命中不等于已移除；去同提交 UI 源码或已提取资源继续查。
- 收录不代表第三方插件获准调用；检查 Environment、系统记录、调用者限制、Secret 元数据和同版本 Blizzard 使用方式。

来源仓库：[Gethe/wow-ui-source](https://github.com/Gethe/wow-ui-source)。API 定义来自 Blizzard 生成文档，索引为静态提取；脚本不执行下载的 Lua。索引是核验时的快照，不会随网络源自动变化。

## 离线查询

要求 Python 3.10+；查询和 diff 只用标准库，不需要游戏运行、网络或 Git。以下命令从技能目录运行（包含 `SKILL.md` 的目录），其他工作目录应使用脚本的绝对路径。

```powershell
python scripts/wow_api.py search C_Container.GetContainerItemInfo --exact
python scripts/wow_api.py search UNIT_COMBAT --kind event --exact
python scripts/wow_api.py search SimpleFrameAPI:RegisterEvent --exact
python scripts/wow_api.py search Enum.BagIndex.Backpack --exact
python scripts/wow_api.py search ContainerItemInfo --kind structure --exact
python scripts/wow_api.py search GetSpellCooldown --namespace C_Spell --exact
python scripts/wow_api.py search RequiresUnitAuraAccess --details --limit 5
```

`--exact` 接受完整或短符号名；结构体、枚举和常量的字段名也可精确检索，返回包含该字段的整条类型记录。ScriptObject 以文档中的类型名加冒号标识（例如 `SimpleFrameAPI:RegisterEvent`），不是名为 `SimpleFrameAPI` 的可调用全局对象。

默认返回完整合同，省略自然语言 Documentation；`--details` 同时显示这些说明，并搜索嵌套参数、字段和限制标记。每条结果包含固定提交的 `source_url`；需要解释生命周期或内部权限时，继续读取其所属系统及同提交 FrameXML。

退出码：`0` 成功，`1` 查询无匹配，`2` 参数、来源或完整性错误。输出为 UTF-8 JSON。无匹配时先核对客户端和命名空间，再查源码；不要凭记忆补签名。

## 获取新快照

`refresh` 需要 Git 和网络，使用独立稀疏源码缓存。它获取一次分支提交，然后从同一提交读取版本与所有文档，避免扫描期间分支更新造成混版。已有缓存必须来源正确且没有本地修改；不会强制覆盖改动。

```powershell
$apiCache = Join-Path ([Environment]::GetFolderPath('UserProfile')) '.cache/qfx-wow-api'
python scripts/wow_api.py refresh --branch live --out "$apiCache/snapshots/live-next"
python scripts/wow_api.py search UNIT_COMBAT --exact --index "$apiCache/snapshots/live-next"
python scripts/wow_api.py diff references/api-index "$apiCache/snapshots/live-next" --out "$apiCache/reports/live-next.json"
```

输出目录必须为空或不存在；再次核验时选择新的快照目录和报告名。缓存默认位于用户目录 `.cache/qfx-wow-api/source`，可通过 `--cache` 改成其他专用路径。`refresh` 会更新该干净缓存的稀疏检出，不能把正在开发的源码仓库当缓存。

PTR 另存并明确按预警处理：

```powershell
python scripts/wow_api.py refresh --branch ptr --out "$apiCache/snapshots/ptr-next"
python scripts/wow_api.py diff "$apiCache/snapshots/live-next" "$apiCache/snapshots/ptr-next" --out "$apiCache/reports/live-to-ptr-next.json"
```

`refresh` 的 `live/ptr/ptr2/beta` 均指该来源的 Retail 分支。Classic / MoP / TBC 等需要先核对来源仓库、实际分支和 Build，再使用显式客户端标签的 `snapshot`；不能把 Retail 快照改个标签就作为 Classic 证据。

## 固定提交和历史比较

已有目标分支的 Git 源码时，`snapshot` 不修改工作树，直接读取指定提交；来源需要 GitHub origin 才能生成可追溯链接。

```powershell
python scripts/wow_api.py snapshot --source "$apiCache/source" --ref b9be9379719047977fca4dba1bb1d9988e8840b3 --branch live --client retail --out "$apiCache/snapshots/live-70448-history"
```

历史提交须已存在于源码缓存；浅克隆可先执行：

```powershell
git -C "$apiCache/source" fetch --depth=1 origin b9be9379719047977fca4dba1bb1d9988e8840b3
```

diff 同时检查新增、删除和合同变化，包括嵌套 `Payload[].SecretValue`、返回值、参数、字段、枚举值，以及 owner-level 元数据。默认忽略自然语言 Documentation 和行号变化，`--include-documentation` 可纳入说明变化；原始文件变化始终列在 `files_changed`。

- 身份由 kind / owner / name / file 组成；跨文件移动会显示为删除与新增，需结合 Git diff 判断。
- JSON 数组路径使用从 0 开始的索引；对照元素的 Name 阅读，不把数组下标当 Lua 参数编号。
- 符号重命名显示为删除与新增，不猜测替代关系。
- diff 拒绝跨客户端、跨来源仓库比较；同客户端跨分支比较会标明 `cross_branch`，不代表 PTR 功能已进入 Live。
- 未识别的 Lua 文档语法会报错，不跳过源文件或输出看似完整的部分索引。符号表达式保留为 `lua_expression`，不求值，不把其字符串当枚举数值。
- 文档 diff 不覆盖 FrameXML 行为变化，也不能证明实际战斗行为；必要时继续比较 UI 源码并在游戏内验证。

## 维护已安装索引

1. 刷新目标分支到新目录，核对 manifest 的分支、客户端、Build 和提交。
2. 对旧索引运行 diff；阅读发生变化的源文件及相关同提交 FrameXML。
3. 将新快照的 **manifest.json 和 symbols.jsonl 一起**复制到 `references/api-index/`；保持校验和配套，不手改 JSONL。
4. 更新现有 Live 基线、API 来源规则和 Secret 参考，保留历史比较的原始 Build 含义。
5. 同步入口、参考、脚本和索引到实际安装技能；验证哈希与至少一条离线查询。只有正式发布才更新技能版本；不自动提交或推送。

可运行脚本行为检查：

```powershell
python -m unittest discover -s scripts -p test_wow_api.py -v
```
