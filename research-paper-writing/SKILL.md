---
name: research-paper-writing
description: Improve academic paper writing quality for ML/CV/NLP-style papers. Use when drafting or revising Abstract, Introduction, Related Work, Method, Experiments, or Conclusion; fixing paragraph or sentence flow; checking grammar (articles, tenses, agreement); consulting phrase banks for academic phrasing; choosing better wording; or performing self-review before submission. Supports four task types - structure revision, section drafting, flow polishing, and grammar checking - each routed to the matching reference and closed by a scored review agent.
agent_created: true
---

# Research Paper Writing

## Overview

把论文改到 reviewer 友好。四种任务类型，每种有自己的参考文件与工作流，**任何修改都必须通过评分审查才算结束**。

## 任务路由（先做这一步）

用户请求进来后，先判断类型（可以是混合，比如"改 Introduction 第 2 段并检查语法"）：

| 用户要什么 | 任务类型 | 读什么参考文件 |
|---|---|---|
| 改某个章节（Abstract / Introduction / Related Work / Method / Experiments / Conclusion）的内容、逻辑、架构安排 | **结构指导** | 对应的 `references/{section}.md` |
| 全文架构安排（章节顺序、段落布局、故事线） | **结构指导** | `references/introduction.md` 的 logic map + 所有 section 文件的 skeleton |
| 某一段或某句是否流畅、读不顺、改得更顺 | **语句流畅** | `references/flow/` 下的文件 |
| 用词更学术、句式升级、不知道怎么开头/过渡/转折 | **语句流畅**（查句式库） | `references/phrases/` 下的文件 |
| 语法检查（冠词、时态、单复数、搭配、句法错误） | **语法检查** | `references/grammar-checklist.md` |
| 投稿前的整体审查、找 reject 风险 | **review 指南** | `references/paper-review.md` |

判断不了就问用户一句。混合任务按每种类型分别走流程，最后合并改稿。

## 通用流程（所有任务类型共用）

1. **读任务对应的参考文件**。不要一次加载全部——只读当前任务要用的。
2. **修改前先把原文存下来**（保留修改前后对照的能力）。
3. **按参考文件的规则改**。
4. **启动 review agent 打分**（见下节）。这是硬性步骤，不许跳过。
5. **分数 > 80 才算结束**；不达标就继续改，直到通过或明确报告无法通过的原因。

## 评分审查循环（核心机制）

### 为什么要独立 agent

修改者自己给自己打分会太宽松。评分 agent 必须是**新启动的独立 agent**，它只拿到文本与评分标准，不知道修改过程。

### 怎么启动

每次修改完成后，用 Agent 工具启动一个 general-purpose agent，prompt 模板：

```
你是学术写作评审。对下面【文本】的【维度】打分（0-100），严格按【评分标准】逐条评估。

【维度】= structure / flow / grammar（多维度就多列）

评分标准在 /path/to/skill/references/review-scoring.md，先读它。

【待评文本】：
<修改后的文本>

【修改前原文】（供对照，不计分对象）：
<修改前文本>

输出格式：
- 总分：NN/100
- 各维度分：structure NN / flow NN / grammar NN（只评要求的维度）
- 逐条扣分点：规则编号 + 原文片段 + 扣分理由
- 一句话总评
```

### 通过与不通过

- **总分 > 80**：通过。向用户报告分数和主要修改点。
- **总分 ≤ 80**：不通过。按 review agent 给出的扣分点继续改，再次送审。同时自查一件事：**这次修改是否改变了科学含义**——如果扣分是因为改写引入了不准确的表述，回退该处改写。
- **循环上限 5 轮**。5 轮后仍 ≤ 80，停下来向用户报告：当前分数、剩余扣分点、为什么继续改没有收益（通常是原文本身的逻辑/证据问题，不是文字问题）。

### 评分标准的来源

`references/review-scoring.md` 定义三个维度的评分细则。这个文件**是评分的唯一依据**，review agent 不使用其他标准。

## 结构指导（任务类型 1）

改章节内容、逻辑、全文架构。参考文件：

| 章节 | 文件 |
|---|---|
| Introduction | `references/introduction.md`（含全文 logic map，做全文架构时必读） |
| Abstract | `references/abstract.md` |
| Related Work | `references/related-work.md` |
| Method | `references/method.md` |
| Experiments | `references/experiments.md` |
| Conclusion | `references/conclusion.md` |
| 段落清晰度 | `references/does-my-writing-flow-source.md`（reverse outlining 等） |
| 例文库索引 | `references/examples/index.md` |

工作流：

1. **先逻辑后文字**。按 introduction.md 的 backward reasoning 先想清楚要讲什么，再动笔。
2. 只加载当前章节的 guide；改完一节再看下一节。
3. 每个主要声明必须能对应实验证据；对不上就弱化或删除声明。
4. 写完先跑 reverse outline 检查段落映射，再送审。

## 语句流畅（任务类型 3）

改句子/段落是否流畅、读不顺。参考文件：

| 文件 | 内容 |
|---|---|
| `references/flow/flow-science-of-scientific-writing.md` | 读者期望理论（Gopen & Swan）：主语位/强调位/旧新信息序，含原文正反例与检查动作 |
| `references/flow/flow-williams-style.md` | Williams《Style》的 clarity/grace 原则：动词承载动作、简洁、衔接连贯，含正反例与检查动作 |
| `references/does-my-writing-flow-source.md` | 段落级流畅检查：读者视角、reverse outlining、过渡词表 |
| `references/phrases/phrasebank.md` | 按章节的学术句式库（开头/转折/贡献声明等） |
| `references/phrases/phrasebank-functions.md` | 按语言功能的句式库（hedging、因果、对比等） |

工作流：

1. 先跑 `references/does-my-writing-flow-source.md` 的段落级检查（读者视角三问 + reverse outline）。
2. 句子级问题按 `flow-principles.md` 的法则改：主语位/强调位、旧信息在前、动作放回动词、删冗余。
3. 用词升级时查 `phrases/` 句式库；**语气强度要与证据匹配**（hedging 分级在 phrasebank-functions.md）。
4. 改完送审（flow 维度）。

**硬约束：流畅性修改不得改变科学含义。** 改写前后逐句对照：主张强度、限定范围、因果关系方向都不能变。发现含义漂移立即回退该句。

## 语法检查（任务类型 4）

参考文件：`references/grammar-checklist.md`（80+ 条规则，按出错频率排序）。

工作流：

1. 读 checklist，按「检查顺序」一节逐条扫文本。
2. 每个发现：规则编号 + 原句 + 改后句。**不确定是否符合原意的，列出来问用户，不要替用户改。**
3. 有争议的规则（如 data is/are）选学术出版主流惯例，并在报告里标注该决定。
4. 改完送审（grammar 维度）。

## review 指南（任务类型 5）

投稿前整体审查。完整 checklist 在 `references/paper-review.md`。

1. 五维问题清单（contribution / writing clarity / experimental strength / evaluation completeness / method design soundness）逐条回答。
2. **claim-evidence 对齐是硬约束**：Abstract 和 Introduction 的每个 major claim 必须有实验支撑，对不上就弱化或删除。
3. 挑剔读者视角：假设 reviewer 会戳每个弱点，主动修复。
4. 整体 review 的评分也走「评分审查循环」，维度 = 全部三个（structure + flow + grammar）。

## 执行规则

1. 一段一个 message。
2. 一段只讲一件事，首句点题。
3. 名词自包含；新术语先定义再复用。
4. 术语全文稳定，不要为换词而换词（elegant variation 是陷阱）。
5. 视觉质量（图/表/版式）是内容的一部分，不是装饰。
6. 不把所有 section 指南一次读完，按需加载。
7. 修改前存原文，修改后能给出前后对照。

## 输出契约

改完向用户回报：

1. 改了什么（前后对照，按段落）
2. 评分：总分 + 各维度分
3. review agent 的扣分点及处理（已修复 / 属科学含义问题已回退 / 待用户决定）
4. claim-evidence map：每个 major claim 的 `Claim: ... | Evidence: ... | Status: supported/needs evidence`
