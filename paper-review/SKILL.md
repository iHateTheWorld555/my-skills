---
name: paper-review
description: "论文深度阅读与结构化 review管线。当用户提供arXiv 链接（或其他论文 PDF链接）并要求 review/分析/总结时触发。完整覆盖：背景动机、贡献、核心设计与故事、方法（逐小节）、实验设置与结果、七维限制审查。输出为一份高信息密度的 Markdown review文件。"
description_zh: "论文深度 Review"
description_en: "Deep Paper Review"
disable: false
agent_created: true
---

# paper-review

## When to use

用户提供一篇或一系列论文（arXiv 链接、PDF 文件路径、或论文标题/DOI）并要求进行 review / 分析 / 总结时触发此skill。典型触发词：
- "review这篇论文"
- "按模板分析论文"
- "帮我读这篇 paper"
- "按之前的格式 review"
- 发送 arXiv 链接 + review 要求

## Steps

### 1. 获取论文全文

1. 若用户给出 arXiv 链接（如 `https://arxiv.org/abs/XXXX.XXXXX`），优先尝试 HTML 全文：
   ```
   curl -sL -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)" "https://arxiv.org/html/{paper_id}v{version}" -o /tmp/paper.html
   ```
2. 用Python 将HTML 转为纯文本（保留 LaTeX alttext、表格分隔符、标题层级）：
   - 替换 `<math alttext="...">` 为 `$alttext$`
   - 移除 script/style
   - 标题 h1-h6 → `###`
   - 段落/列表/表格行 → 换行
   - 去除所有剩余 HTML 标签
   - html.unescape
3. 若HTML 不可用，回退到 Tex 源码下载，解压直接读取 tex 文件
4. 读取全文到上下文。

### 2. 撰写结构化 Review

按照@templates/review-template.md 的完整模板撰写 review

### 3. 输出与呈现

1. 将 review 写入工作目录：`{workspace}/{PaperName}_review.md`
2. 用 `present_files` 呈现给用户
3. 在最终回复中给出 3-5 句话的核心判断摘要

### 4. 清理

- 删除中间文本文件（/tmp/paper.txt 等）
- 保留原始 PDF（用户可能后续需要）

## Pitfalls

- arXiv HTML 版本可能不可用（403/404），必须有 PDF fallback
- pypdf 对双栏 PDF 的文本顺序可能乱，如果方法部分逻辑不连贯需警惕是PDF 解析问题
- 部分论文的 HTML 版本会把表格渲染为图片而非文本，此时表格数据需从 PDF 或 tex 文件中
- 限制部分在作者的 Limitations 章节之上，主动审查并补充
- 不要用代码块包裹数学公式，全部用 $...$ 或 $$...$$
- 减少不必要的换行，提高信息密度
- 不需要英文全称，只需缩写
- 不要为了凑限制写"未来可以优化"这种废话

## Verification

- review 文件是否覆盖了模板的所有一级标题（背景、方法、实验、限制）
- 方法部分是否覆盖了原文的每个技术小节
- 方法是否形成可顺序阅读的因果链：概念先定义、数据/监督先于使用、训练/推理/评估明确分开，而不是机械照搬目录
- 实验结果是否覆盖了所有表格/图的关键结论
- 最终是否调用了 present_files
