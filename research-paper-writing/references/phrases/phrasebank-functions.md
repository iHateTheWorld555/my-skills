# ML/CV/NLP 论文写作短语库 —— 按语言功能组织

> 用法：`[...]` 为可替换槽位。按写作时要用到的"语言动作"检索，与按章节组织的 `phrasebank.md` 配合使用。
> 来源见文末。

---

## 1. Hedging（谨慎措辞 / 弱化断言）

### 强度分级表（强 → 弱）

| 强度 | 断言动词/短语 | 适用场景 |
|---|---|---|
| ★★★★★ 最强 | "we demonstrate that..." / "clearly show" / "establish" | 数据压倒性、主结果陈述 |
| ★★★★ 强 | "show" / "indicate that" / "confirm" | 有充分证据但未到碾压级 |
| ★★★ 中 | "suggest (that)" / "provide evidence that" | 结果倾向明确但可能有混杂因素 |
| ★★ 弱 | "appear to" / "seem to" / "may support the hypothesis that" | 初步观察、探索性发现 |
| ★ 最弱 | "may indicate" / "possibly / potentially" / "cannot be ruled out" | 纯推测、需后续工作验证 |

**句式模板：**

1. "Recent research has suggested that [...]." —— 借他人之口弱化命题（Manchester）
2. "There is some evidence to suggest that [...]." —— "一些证据"限定证据量（Manchester）
3. "It is likely / possible / probable that [...]." —— 情态副词分级弱化（Manchester）
4. "[...] may be / could be / might be due to [...]." —— 解释归因时的三级弱化（Manchester）
5. "A possible / likely explanation is that [...]." —— 给解释前先降格为"一种可能"（Manchester）
6. "These data must be interpreted with caution because [...]." —— 主动提醒读者谨慎解读（Manchester）
7. "These results do not rule out the influence of [...]." —— 声明未排除因素，学术诚实（Manchester）
8. "Our findings cannot be extrapolated to [...]." —— 限定结论外推范围（Manchester）
9. "The evidence, while preliminary, suggests that [...]." —— 承认初步性同时给出方向（RhetoriLex 改写）
10. "There is a tendency for X to [...]." —— 规律弱化为"趋势"（Manchester）
11. "X is generally assumed to [...]." —— 命题归为"普遍假设"而非事实（Manchester）
12. "This claim is limited to [...] and may not extend to [...]." —— 显式声明适用边界（RhetoriLex）
13. "Although [...] supports [...], it remains compatible with [...]." —— 声明备择解释仍然成立（RhetoriLex）

---

## 2. Causality（因果关系）

### 强因果（需实验设计支撑）

1. "[...] can lead to / result in / give rise to [...]." —— 因果动词链（Manchester）
2. "[...] is driven by / can be attributed to / stems from [...]." —— 反向归因动词（Manchester）
3. "Removing [...] leads to a drop of [...] in [...], indicating that [...]." —— ML 消融因果三段式（ML 惯用）

### 贡献性因果（只声称部分作用）

4. "[...] contributes to [...]." —— 部分归因（Manchester）
5. "Several factors are known to affect / shape / influence [...]." —— 多因并立（Manchester）
6. "[...] is associated with an increased risk of [...]." —— 关联而非因果的医学式措辞（Manchester）
7. "[...] plays a role in [...]." —— 弱贡献声明（Manchester）

### 名词化与句式因果

8. "[...] is a key / major / dominant / underlying factor in [...]." —— 因素句式（Manchester）
9. "A consequence of [...] is [...]." —— 结果句式（Manchester）
10. "Owing to / Due to / As a result of [...], [...]." —— 介词因果（Manchester）
11. "Therefore, / Consequently, / As a result, [...]." —— 句间因果连接词（Manchester）
12. "[...], thereby [...]ing [...]." —— 分词跟随式因果（Manchester）

### 谨慎的因果（可能相关）

13. "[...] may be an important factor in [...]." —— 弱因果（Manchester）
14. "There is some evidence that [...] may affect [...]." —— 证据限定型因果（Manchester）
15. "It is not yet clear whether [...] is made worse by [...]." —— 明示因果未确证（Manchester）
16. "[...] appears to be linked to [...]." —— 关联措辞，避免因果误读（Manchester）

---

## 3. Contrast / Comparison（对比与比较）

### 引入差异

1. "[...] differs from [...] in a number of important ways." —— 总述差异（Manchester）
2. "There are a number of important differences between [...] and [...]." —— 差异总起句（Manchester）
3. "In contrast to / By contrast / On the other hand, [...]." —— 句间转折三件套（Manchester）
4. "While / Whereas [...], [...]." —— 一句内对仗式对比（Manchester）
5. "Compared with [...], [...] [...]." —— 直接比较（Manchester）
6. "Unlike prior work, our approach [...] rather than [...]." —— ML 方法对比惯用（ML 惯用）
7. "Whereas [...] reports [...], the present analysis finds [...]." —— 与文献结果对比（RhetoriLex）
8. "[...] aligns with [...] but differs from the prediction of [...]." —— 部分吻合部分背离，精细对比（RhetoriLex）

### 引入相似

9. "Both [...] and [...] share a number of key features." —— 共性总述（Manchester）
10. "[...] is similar to / comparable to that of [...]." —— 相似句式（Manchester）
11. "Similarly, / Likewise, / In the same way, [...]." —— 句间平行连接词（Manchester）

### 比较级句式（实验数字用）

12. "[...] achieves [...] more / less [...] than [...]." —— 比较级基础式（Manchester）
13. "[...] tends to perform better / worse than [...] on [...]." —— 趋势比较（Manchester）
14. "[...] outperforms [...] by a large / significant margin." —— ML 结果碾压表述（ML 惯用）
15. "[...] is on par with / comparable to [...], while being [...]." —— 性能持平但有其他优势（ML 惯用）

---

## 4. Emphasis（强调与突出）

1. "Notably, / Importantly, / Strikingly, [...]." —— 句首强调副词三档（ML 惯用）
2. "The most striking result to emerge from the data is that [...]." —— 最惊人发现（Manchester）
3. "What stands out in the table is [...]." —— 引导看表中关键点（Manchester）
4. "It is worth noting that [...]." —— 中等强度提示（Manchester）
5. "Of particular interest is [...]." —— 正式版强调（Manchester 改写）
6. "Notably, our method achieves this without [...]." —— "零代价获得收益"式强调（ML 惯用）
7. "This is a particularly [...] result, given that [...]." —— 结合语境评价结果（Manchester）

---

## 5. Definition（定义术语）

1. "[...] refers to [...]." —— 最简定义（Manchester）
2. "[...] can broadly be defined as [...]." —— 宽泛定义（Manchester）
3. "In this paper, [...] is defined as [...]." —— 本文自定义声明（Manchester）
4. "Throughout this paper, the term '[...]' will refer to [...]." —— 全文术语约定（Manchester）
5. "Here, [...] refers specifically to [...], excluding [...]." —— 定义 + 划界（RhetoriLex）
6. "Following [...], we use [...] to denote [...]." —— 沿用他人定义（ML 惯用）
7. "For clarity, we distinguish between [...] and [...]." —— 消歧声明（ML 惯用）
8. "Several definitions of [...] have been proposed; in this work, we adopt [...]." —— 定义有分歧时先综述后选择（Manchester 改写）
9. "We use the terms [...] and [...] interchangeably." —— 同义声明（Manchester 改写）
10. "A generally accepted definition of [...] is lacking." —— 指出术语未定，适合引言铺垫（Manchester）

---

## 6. Transition（过渡与衔接）

### 章节间过渡

1. "Turning now to [...]." —— 转入下一话题（Manchester）
2. "Having defined [...], we now move on to [...]." —— 承接完成动作再推进（Manchester）
3. "So far, this paper has focused on [...]. The following section will discuss [...]." —— 阶段总结 + 预告（Manchester）
4. "We next investigate / examine [...]." —— ML 短过渡句（ML 惯用）
5. "With the above setup in place, we now turn to [...]." —— 铺垫完成后推进（ML 惯用）

### 段内话题切换

6. "Regarding / In terms of / With respect to [...], [...]." —— 话题限定三件套（Manchester）
7. "As discussed above / As previously stated, [...]." —— 回指前文（Manchester）
8. "In addition, / Furthermore, / Moreover, [...]." —— 递进（Manchester）
9. "Despite this, [...]." —— 让步转折（Manchester）
10. "Returning to the issue of [...], [...]." —— 拉回主线（Manchester）

### 引导后文（图表/公式/章节）

11. "As shown in Figure [...] / Table [...], [...]." —— 图表回指（Manchester）
12. "A detailed description is provided in Section [...] / the Appendix." —— 后文指引（ML 惯用）
13. "This will be discussed in detail in Section [...]." —— 延后讨论声明（ML 惯用）

---

## 7. Example（举例说明）

1. "A well-known example of this is [...]." —— 经典例证（Manchester）
2. "For example, / For instance, [...]." —— 万能举例（Manchester）
3. "[...], such as [...] and [...]." —— 句内嵌例子（Manchester）
4. "[...], including [...], [...] and [...]." —— 多例列举（Manchester）
5. "To illustrate this, consider [...]." —— 构造性举例（ML 惯用）
6. "Take [...] as an example." —— 口语化一点的举例（ML 惯用）
7. "A concrete example is [...]: given [...], [...]." —— 走一个具体算例，方法节常用（ML 惯用）
8. "This can be illustrated briefly by [...]." —— 简短图示式举例（Manchester）

---

## 8. Trend / Quantity Description（趋势与数量描述）

### 趋势

1. "[...] shows a steady / sharp / marked increase / decline in [...]." —— 趋势 + 修饰词（Manchester）
2. "[...] increased / decreased [...] from [...] to [...] over [...]." —— 区间变化（Manchester）
3. "[...] peaked at [...] in [...]." —— 峰值描述（Manchester）
4. "[...] is expected to [...] in the coming [...]." —— 趋势外推（Manchester）
5. "[...] grows [...] as [...] increases, and saturates beyond [...]." —— ML 训练曲线常见叙事（ML 惯用）

### 数量与比例

6. "Over half / Nearly half of [...] [...]." —— 比例句（Manchester）
7. "[...] accounts for [...]% of [...]." —— 占比句（Manchester 改写）
8. "The number of [...] ranges from [...] to [...]." —— 区间句（Manchester）
9. "[...] achieved [...]%, outperforming [...] by [...] points." —— ML 指标 + 增量（ML 惯用）
10. "The improvement is statistically significant (p < 0.05)." —— 统计显著性声明（Manchester 改写）
11. "The mean [...] was [...] (±[...]) across [...] runs." —— 均值 ± 方差报告，ML 多 seed 惯用（ML 惯用）

---

## 9. Criticism（批评与指出不足）

### 指出前人整体不足

1. "Previous studies of [...] have not dealt with [...]." —— 未覆盖面（Manchester）
2. "Most studies in the field of [...] have only focused on [...]." —— 视野过窄（Manchester）
3. "Such approaches, however, have failed to address [...]." —— 失败声明（Manchester）
4. "However, all the previously mentioned methods suffer from [...]." —— 批量否定（Manchester）
5. "Results of previous studies have proved inconclusive." —— 结论不可靠（Manchester / Wordvice）

### 指出单一工作不足

6. "[...] fails to fully define / distinguish between / address [...]." —— 具体缺陷（Manchester）
7. "[...] does not take [...] into account." —— 遗漏因素（Manchester 改写）
8. "The main limitation of this technique, however, is [...]." —— 技术局限（Manchester）
9. "A major problem with the [...] method is that [...]." —— 方法问题（Manchester）
10. "[...] makes the strong assumption that [...], which limits [...]." —— 批评隐含假设（ML 惯用）
11. "[...] was later shown to [...], suggesting that [...]." —— 用后续证据批评（ML 惯用）

### 委婉批评（建设性）

12. "[...] would have been more [...] if it had [...]." —— 假设改进式，最温和（Manchester）
13. "While [...] is effective for [...], it is less suitable for [...]." —— 承认优点再划局限，Related Work 推荐句式（ML 惯用）

---

## 10. Listing / Classification（列举与分类）

1. "[...] can be classified / divided into [...] categories: [...] and [...]." —— 分类骨架（Manchester）
2. "There are two basic approaches currently being adopted in [...]: [...] and [...]." —— 二分法（Manchester）
3. "[...] can be broadly categorized into [...]-based methods and [...]-based methods." —— ML 论文 Related Work 标配二分（ML 惯用）
4. "The key aspects of [...] can be listed as follows: [...], [...] and [...]." —— 列举引导（Manchester）
5. "This topic can best be treated under three headings: [...], [...] and [...]." —— 结构化分主题（Manchester）
6. "Firstly, [...]. Secondly, [...]. Thirdly, [...]." —— 序数列举（Manchester）
7. "First, [...]. Then, [...]. Finally, [...]." —— 过程列举（Manchester 改写）
8. "[...] draws a distinction between [...] and [...]." —— 引用他人的分类（Manchester）
9. "We group existing methods along two axes: [...] and [...]." —— ML 式二维组织法（ML 惯用）

---

## 11. Evidence-safe Claiming（证据分级主张 · RhetoriLex 模式）

> 这一组句式把"主张强度"和"证据类型"显式绑定，适合写 Discussion / Limitations 或回应审稿人质疑。

1. "The available evidence suggests but does not establish that [...]." —— 明示证据不足以确立结论（RhetoriLex）
2. "Given [...], the more defensible interpretation is that [...]." —— 在多解释中选最可辩护者（RhetoriLex）
3. "Because [...] remains imprecise, the evidence does not distinguish between [...] and [...]." —— 声明区分能力不足（RhetoriLex）
4. "Since [...] does not rule out [...], [...] should not be read as causal evidence." —— 声明非因果证据（RhetoriLex）
5. "If [...] holds, [...] is consistent with [...]." —— 条件式主张（RhetoriLex）
6. "Because the sample excludes [...], [...] should be generalized only to [...]." —— 限定外推范围（RhetoriLex）
7. "The measure captures [...] through [...], which may omit [...]." —— 指标覆盖不足的诚实声明（RhetoriLex）
8. "Across [...], the evidence converges on [...], particularly under [...]." —— 多源证据汇合式主张（RhetoriLex）
9. "The literature divides over [...]: [...] supports [...], whereas [...] supports [...]." —— 描述学界分歧（RhetoriLex）
10. "Until [...] is resolved, a proportionate step is to [...]." —— 不确定性下的保守建议（RhetoriLex）

---

## 来源

- **Manchester Academic Phrasebank**（语言功能类 12 页中除 Writing about the past 外均直接抓取）：
  using-cautious-language / being-critical / classifying-and-listing / compare-and-contrast / writing-definitions / describing-trends / describing-quantities / explaining-cause-and-effect / giving-examples / signalling-transition / writing-about-the-past-2
  https://www.phrasebank.manchester.ac.uk/
- **shengmincui/Academic_Phrasebank_note**：https://github.com/shengmincui/Academic_Phrasebank_note （补充了 hedging 强度表格素材与更多变体）
- **rezaprama/RhetoriLex**（`data/canonical/catalog.v1.jsonl`，48 条证据分级模式，第 11 节大部分直接取自该库）：https://github.com/rezaprama/RhetoriLex
- **Wordvice「Academic Writing Cheat Sheet」PDF**：https://wordvice.com/blog/useful-phrases-for-writing-academic-papers/
- **ML 惯用句式**：依据 ML 顶会论文通行写法归纳，已逐条标注「ML 惯用」
