# docdev CLI 契约

`docdev` 接管项目目录、文档模板、文件名、时间、landing revision、索引和交叉引用。Agent 通常只提交正文 `content`；标题可省略，由 CLI 从正文第一行推断。

## 命令

```bash
docdev init [project-dir] [--name name]
docdev doc <index|idea|landing|exp|decision|lesson> [--id id] [--append] [--input file|-]
docdev read <id> [--quiet]
docdev search [query] [--type type] [--ref id] [--limit n] [--verbose] [--archived|--all]
docdev board [--max-nodes n] [--no-graph]
docdev archive [--days n] [--apply]
docdev unarchive <id>
docdev rm <id> [--dry-run] [--force]
docdev clean [--dry-run]
docdev validate [--fix]
```

除 `--help` 外，成功和失败都输出 JSON。命令位于 Skill pack 的 `bin/docdev`；运行 `install.sh` 后可从 PATH 调用。

## 初始化

```bash
docdev init /path/to/project --name project-name
```

CLI 自动创建固定的 8 个顶层目录、源码子目录、项目 index，以及三份 landing：

- dataset landing：数据路径、格式、统计、切分、预处理和数据版本；
- model landing：模型结构、参数、关键模块和预训练权重；
- pipeline landing：预处理、训练、推理、评测的入口、顺序和使用方法。

初始化结果返回 `index_id` 和三个 `landing_ids`。重复执行保持幂等。

## 写文档

### 最小输入

所有类型使用相同输入：

```json
{
  "content": "要写入的正文"
}
```

可选标题：

```json
{
  "title": "简短标题",
  "content": "要写入的正文"
}
```

`content` 是唯一必填字段。CLI 不接受 status、owner、priority、time、revision、path 等额外 slot。

### 创建

```bash
printf '%s' '{"content":"研究一个新的条件编码方法。"}' |
  docdev doc idea --project /path/to/project
```

创建支持 `idea`、`exp`、`decision`、`lesson`。index 和 landing 由 init 创建。

### 更新

```bash
printf '%s' '{"content":"更新后的完整正文。"}' |
  docdev doc idea --id idea-20260813-条件编码 --project /path/to/project
```

更新替换正文，不改文档 ID、创建时间或文件名。landing 可用 domain 代替 ID：

```bash
printf '%s' '{"content":"路径：data/train；格式：parquet。"}' |
  docdev doc landing --id dataset --project /path/to/project
```

landing 正文发生变化时 revision 自动加 1；no-op 更新不增加。

### 追加实验日志

```bash
printf '%s' '{"content":"loss 正常下降，未发现 NaN。","title":"启动检查"}' |
  docdev doc exp --id exp-20260813-baseline --append --project /path/to/project
```

CLI 自动添加时间，并把日志追加到实验正文末尾。

## 文档类型的用途

Agent 只需判断内容应放入哪一类，不需要遵循 Markdown 模板：

- `index`：当前在做的实验与 idea、阻塞和下一步。不含文档目录（清单直接 `ls docs/*`）。
- `idea`：研究问题、假设、动机、最小验证想法和当前结论。
- `landing dataset`：数据集的稳定事实。
- `landing model`：模型及权重的稳定事实。
- `landing pipeline`：训练、推理、评测和预处理流程的稳定事实。
- `exp`：一个实验变体的目标、baseline、指标、运行记录、模型输出、失败案例和结论。
- `decision`：技术选择、方向否决、用户批评及其证据和影响。
- `lesson`：踩坑或用户纠正，包含现象、根因、正确做法和复发信号。

这些是内容范围，不是必填小节。正文可以按当前研究需要自由组织。

## 自动命名和时间

文档名称统一为：

```text
<type>-YYYYMMDD-<docname>.md
```

CLI 从 title 或正文第一行生成 docname；同名时自动追加 `-2`、`-3`。创建和更新时间来自系统时钟，Agent 不传时间。

## 交叉引用

在正文任意位置写：

```text
[[idea-20260813-条件编码]]
[[exp-20260813-baseline|baseline 实验]]
```

CLI 会：

1. 写入前检查目标文档存在；
2. 在 Markdown 中渲染为正确的相对链接；
3. 在搜索结果中提供正向和反向引用；
4. 文档标题变化时重新渲染依赖链接；
5. 在 `docdev board` 生成的看板里汇总整个引用网络。

获取文档 ID：

```bash
docdev search "条件编码" --type idea --project /path/to/project
```

## 搜索

```bash
docdev search "条件 编码" --project /path/to/project
docdev search "NaN" --type lesson --project /path/to/project
docdev search "" --ref idea-20260813-条件编码 --project /path/to/project
docdev search "" --type exp --project /path/to/project
docdev search "NaN" --verbose --project /path/to/project
```

关键词采用 Unicode case-insensitive AND 搜索，**索引覆盖 ID、标题、正文与实验日志全文**。

为控制上下文开销，结果默认只返回 `id`、`type`、`title`、`updated_at`。
需要片段、路径和引用列表时加 `--verbose`，会补上 `snippet`、`path`、`created_at`、
`revision`、`references` 和 `referenced_by`。

`--verbose` 只影响输出字段，不影响命中范围：正文里提到但标题没写的关键词，默认模式同样能搜到。

默认只搜活跃文档。`--archived` 搜归档区，`--all` 搜全部；归档结果带 `archived: true` 标记。

## 文档看板

```bash
docdev board --project /path/to/project
docdev board --max-nodes 60 --project /path/to/project
docdev board --no-graph --project /path/to/project
```

生成 `docs/board.md`，一份全局只读视图，包含九个小节：

1. 标题头：项目名、生成时间、文档总数与各类型计数、交叉引用条数；
2. 项目脉搏：index 正文摘要（引用已展开为链接）；
3. 交叉引用图谱：mermaid `graph LR`，按文档类型分类；
4. 交叉引用明细：`文档 / 引用 → / ← 被引用` 表格，不依赖 mermaid 渲染器；
5. 孤立文档：已写正文但双向都没有交叉引用的文档，空白占位文档不计入；
6. 实验看板：每个 exp 的日志数和最后活动时间；
7. Landing 状态：三个领域的 revision 和更新时间；
8. 决策与经验速查；
9. 最近活动：按更新时间倒序前 10 篇。

图谱在三种情况下降级为纯表格，并在该小节写明原因：文档数超过 `--max-nodes`（默认 40）、显式 `--no-graph`、项目暂无交叉引用。

看板只在显式运行 `docdev board` 时生成，其他命令不会刷新它。看板不是 record：不参与 `validate`，不影响 `search`，也不修改任何文档的正文或时间。每次生成整体覆盖 `docs/board.md`，不要手工编辑，正文改动写回对应文档后重新生成。

返回 JSON 包含 `path`、`generated_at`、`documents`、`counts`、`edges`、`graph`、`orphans`。

## 读文档（会刷新未读计时）

```bash
docdev read <id> --project /path/to/project
docdev read <id> --quiet --project /path/to/project    # 只记录读取，不回正文
```

**读文档一律用这个命令，而不是直接读 Markdown 文件。** 它把 `last_read` 更新为当前时间，
自动归档据此判断文档是否还在用。直接用编辑器或 Read 工具看文件，CLI 无从得知，
文档会在 5 天后被误归档（虽然可以 `unarchive` 恢复）。

`read` 只改 record 里的 `last_read`，不改 `updated_at`，也不重写任何 Markdown ——
所以它不会让 `validate` 报差异，也不产生 git 噪音。

## 自动归档

超过 5 个**活跃日**未被 `read` 读取、也未被 `doc` 修改的 `exp`、`decision`、`lesson` 会被归档：
文件移动到 `docs/archive/<type>s/`，从活跃目录消失，`search` 默认不再返回它。

`index`、`landing`、`idea` 是常驻文档，永不归档。

### 活跃日，不是自然日

每次运行 docdev 命令，当天日期就被记入 `docs/.docdev/calendar.json` 的活跃日历
（同一天多次调用只记一次）。归档数的是**这份日历里的天数**，不是日历日之差：

- 休假两周没碰过项目 → 期间零活跃日 → **一篇都不会被归档**；
- 回来后每天工作 → 第 6 个活跃日到来时，那些一直没读的文档才到期。

这样"很久没来干活"不会导致文档被成批误归档。`archive` 的返回里
`idle_active_days` 是该文档积压的活跃日数，`active_days_recorded` 是日历里的总天数。

日历文件可以安全删除（会被重新累积），但删除等于把所有文档的计时归零。

```bash
docdev archive --project /path/to/project              # 只列候选与未读天数，不动文件
docdev archive --apply --project /path/to/project      # 执行移动
docdev archive --days 14 --apply --project /path/to/project
docdev unarchive <id> --project /path/to/project       # 恢复到活跃目录
```

`docdev doc` 写文档时会顺手归档到期文档，被归档的 ID 出现在返回的 `auto_archived` 里。
设 `DOCDEV_NO_AUTO_ARCHIVE=1` 可关闭这个行为。

归档**不会破坏交叉引用**：链接按实际位置重新计算，指向归档文档的链接变成
`../archive/lessons/xxx.md` 且真实可解析。`unarchive` 后又变回来。

## index 只写当前焦点

index 不再包含文档目录。它只写当前在做的实验、当前的 idea、阻塞和下一步，
末尾由 CLI 附一行固定指引（去哪找文档）。

文档清单直接看目录，文件名即标题：

```bash
ls docs/ideas docs/landing docs/exps docs/decisions docs/lessons
ls docs/archive/exps docs/archive/decisions docs/archive/lessons
```

这比在 index 里维护目录省很多上下文：目录会随文档数无限增长，而 `ls` 的输出不含
markdown 链接语法，同样的信息更短。需要按内容查找时用 `docdev search`，
需要看引用关系时用 `docdev board`。

## 交互式看板服务

```bash
python3 <skill-base>/scripts/docboard_server.py --project /path/to/project --port 8600
```

浏览器打开后提供：交叉引用力导向图谱（点节点看正文、可按类型过滤、可聚焦邻居）、
Markdown 与 LaTeX 渲染（`$...$` 行内、`$$...$$` 独立）、以及编辑 / 新建 / 追加实验日志 / 删除。

服务端所有写操作都通过 `docdev` CLI 执行，不直接改 records 或生成的 Markdown，
因此正文校验、引用完整性、landing revision、时间戳与索引刷新的行为与命令行完全一致。
前端依赖（cytoscape / marked / KaTeX / DOMPurify）本地托管在 `assets/board/`，不依赖 CDN。

删除走两步：先请求影响面（哪些文档引用了它），确认后才执行强制删除。

## 删除文档

```bash
docdev rm <id> --dry-run --project /path/to/project    # 只报告影响面，不删除
docdev rm <id> --project /path/to/project              # 被引用时拒绝删除（退出码 5）
docdev rm <id> --force --project /path/to/project      # 强制删除并清理引用
```

只能删除 `idea`、`exp`、`decision`、`lesson`；`index` 和 `landing` 由 init 管理，拒绝删除。

默认情况下，只要还有文档引用目标就拒绝删除，并在 `referenced_by` 里列出这些文档。
`--force` 会删除文档，并把其他文档正文（含 exp 日志）里指向它的 `[[引用]]`
替换为纯文本：有别名时保留别名，否则用被删文档的标题。这样不会留下悬空引用，
删除后 `validate` 仍然通过。被改写的文档列在返回的 `rewritten` 里。

## 清理 smoke/debug 实验产物

先保存有价值的诊断 lesson，再执行：

```bash
docdev clean --dry-run --project /path/to/project
docdev clean --project /path/to/project
```

CLI 只扫描项目 `exp/` 下的目录，并删除目录名中包含 `smoke` 或 `debug`（不区分大小写）的目录。`--dry-run` 只显示候选目录。

## 校验和恢复

```bash
docdev validate --project /path/to/project
docdev validate --fix --project /path/to/project
```

records 是权威数据。`--fix` 只重建 Markdown、index、缺失目录和 `.gitignore`，不会猜测或改写正文。

升级本 CLI 后跑一次 `docdev validate --fix`：它会把 records 从 schema v2 迁移到 v3
（补 `last_read` 与 `archived`），并重建 index（目录已移除）。正文不受影响。

**迁移把 `last_read` 设为迁移时刻，不追溯历史 `updated_at`** —— 所以升级当天不会有文档
因为"历史上很久没动过"而被立刻归档，归档计时从升级开始。
