# ML/CV/NLP 论文写作短语库 —— 按论文章节组织

> 用法：`[...]` 为可替换槽位。每条后面的中文标注说明语气与适用场景。
> 来源见文末。ML 特有句式（标注「ML 惯用」）来自对 ML 顶会论文的通行写法归纳，与 Manchester Phrasebank 通用句式区分。

---

## 1. Abstract（摘要）

**开头（领域 + 任务）：**
1. "Recent advances in [...] have demonstrated remarkable progress in [...]." —— 开场引入大领域热度，最通用的 ML 开头
2. "[...] is a fundamental task in [...] and plays a critical role in [...]." —— 强调任务重要性，适合 CV/NLP 任务型论文
3. "The past decade has witnessed the rapid development of [...]." —— 时间跨度开场，比 "Recently" 更有历史纵深感
4. "Deep learning approaches have achieved impressive performance on [...]. However, [...]." —— 两句式：先立后破，直接引出问题（ML 惯用）

**问题/缺口：**
5. "However, existing methods [...] when [...]." —— 指出现有方法在特定条件下失效，摘要标准转折（ML 惯用）
6. "However, these approaches typically suffer from [...], limiting their applicability to [...]." —— 指出局限并说明后果，语气正式
7. "Despite recent progress, it remains challenging to [...] due to [...]." —— 语气克制，强调困难本身而非前人失误

**本文方法：**
8. "In this paper, we propose [...], a novel [...] that [...]." —— 提出方法的标配套路，给方法命名时用（ML 惯用）
9. "We present [...], which [...] by [...]." —— 简洁版方法陈述，适合篇幅受限的摘要
10. "To address this issue, we introduce [...], which [...] without requiring [...]." —— 强调"解决痛点 + 免除某代价"，卖点前置
11. "Unlike prior work, our approach [...] rather than [...]." —— 需要与前人形成鲜明对比时用（ML 惯用）

**结果声明：**
12. "Extensive experiments on [...] benchmarks demonstrate that [...] outperforms state-of-the-art methods by a large margin." —— 摘要结果句标配，注意 "demonstrate" 是强断言，需有数据支撑（ML 惯用）
13. "Experimental results show that our method achieves [...] while reducing [...] by [...]." —— 数字卖点版，性能与代价同时给出
14. "We conduct extensive experiments on [...] datasets, and the results verify the effectiveness of [...]." —— 保守版结果句，效果没有碾压性优势时用

**贡献预告：**
15. "Our code and models are publicly available at [...]." —— 开源声明，现在 ML 会议基本标配（ML 惯用）

---

## 2. Introduction（引言）

### 2.1 背景与重要性

1. "X is a fundamental problem in [...], with applications ranging from [...] to [...]." —— 定义问题重要性的标准写法，应用面广时用
2. "X plays a vital / critical / central role in [...]." —— 强调研究对象在系统中的地位（Manchester）
3. "There is a growing body of literature that recognises the importance of [...]." —— 用文献量侧面烘托热度（Manchester）
4. "Recently, there has been renewed interest in [...] due to [...]." —— 说明该问题近期回潮及原因，适合老问题新解法（Manchester）
5. "The past thirty years have seen increasingly rapid advances in the field of [...]." —— 领域级时间叙事开场（Manchester）
6. "Driven by [...], X has attracted increasing attention from the community." —— ML 版背景句，用技术驱动力解释热度（ML 惯用）

### 2.2 问题界定（作为待解决问题）

7. "X is a major / challenging problem in [...]." —— 直陈问题地位（Manchester）
8. "There is an urgent need to address [...], since [...]." —— 强调紧迫性，需在 since 中给出理由（Manchester）
9. "Despite its practical importance, X remains largely under-explored / notoriously difficult because [...]." —— "重要但难"组合拳，为引出本文铺垫（ML 惯用）

### 2.3 已有工作与共识

10. "Extensive research has shown that [...]." —— 中性引述大量既有结论（Manchester）
11. "Previous research has established that [...]." —— 语气比上一条更强，用于公认结论（Manchester）
12. "A number of studies have attempted to [...] (Smith et al., 2020; Jones et al., 2021)." —— 列举具体工作，适合 Related Work 前置的 Introduction（Manchester）

### 2.4 缺口（gap）—— Introduction 的核心转折

13. "However, previous studies of X have not dealt with [...]." —— 直接指出未覆盖面（Manchester）
14. "However, most existing methods [...] and thus fail to [...]." —— "主流做法 → 由此失效"因果链（ML 惯用）
15. "However, these methods are built on the assumption that [...], which often does not hold in practice." —— 攻击隐含假设，比批评表面缺陷更深刻（ML 惯用）
16. "While some research has been carried out on X, no previous study has investigated [...]." —— "有但不足"标准句式（Manchester）
17. "There is little published data / a paucity of research on [...]." —— 指出研究稀缺（Manchester）
18. "It is still not known whether [...]." —— 知识空白型 gap（Manchester）
19. "The mechanisms / factors that underpin X are not fully understood." —— 理解型空白，适合分析类工作（Manchester）
20. "A much debated question is whether [...]." —— 领域争议型开场（Manchester）
21. "The existing accounts fail to resolve the contradiction between X and Y." —— 指出矛盾未解，适合提出统一解释的工作（Manchester）
22. "However, far too little attention has been paid to [...]." —— 强调关注不足的经典句（Manchester）

### 2.5 目的、贡献与意义

23. "In this paper, we propose / present / introduce [...]." —— 贡献陈述的万能开头（ML 惯用）
24. "To fill this gap / To bridge this gap, we [...]." —— 承接 gap 句的标准衔接（ML 惯用）
25. "The main contributions of this paper are summarized as follows: (1) ... (2) ... (3) ..." —— ML 论文贡献 bullet 的标准引导句（ML 惯用）
26. "We further propose [...] to [...], which [...] for the first time." —— "for the first time" 声明首创性，用前务必核实（ML 惯用）
27. "To the best of our knowledge, this is the first work to [...]." —— 首创声明的保守版，带自我保护（ML 惯用）
28. "This study provides new insights into [...]." —— 强调理解性贡献而非性能贡献（Manchester）
29. "We demonstrate that [...] can be achieved with [...], challenging the prevailing assumption that [...]." —— 反直觉结果 + 挑战共识，适合 high-risk high-reward 的主张（ML 惯用）

### 2.6 结构预告

30. "The remaining part of this paper proceeds as follows / is organized as follows. Section 2 reviews [...]. Section 3 describes [...]." —— 结构段标准写法（Manchester）
31. "This paper begins by [...]. It will then go on to [...]." —— 非编号版结构预告（Manchester）

---

## 3. Related Work（相关工作）

### 3.1 文献总体评述

1. "A large and growing body of literature has investigated [...]." —— 说明领域文献规模（Manchester）
2. "The literature on X has highlighted several [...]." —— 引出文献的若干主题线（Manchester）
3. "Much of the current literature on X pays particular attention to [...]." —— 指出文献关注焦点（Manchester）
4. "There is a relatively small body of literature that is concerned with [...]." —— 某子方向文献少，为本文留空间（Manchester）
5. "Different methods have been proposed to address [...]. These can be roughly divided into two categories: [...] and [...]." —— Related Work 分类骨架句，ML 论文最常用组织方式（ML 惯用）

### 3.2 历史脉络

6. "Research into X has a long history, dating back to [...]." —— 老问题追溯起源（Manchester）
7. "Early approaches relied on [...]. Over the past decade, most research in X has shifted toward [...]." —— 从早期到近年的范式转移叙事（Manchester 改写，ML 惯用）
8. "Only in the past ten years have studies of X directly addressed [...]." —— 强调某问题最近才被正视（Manchester）
9. "It is only since the work of Smith (2015) that the study of X has gained momentum." —— 归功于某篇开创性工作（Manchester）

### 3.3 逐条引用（三种主语位置）

10. "Smith et al. (2020) proposed [...] and demonstrated [...]." —— 研究者做主语，最常用引用格式（Manchester）
11. "Smith et al. (2020) were among the first to [...]." —— 归属首创（Manchester 改写）
12. "In 2017, Smith et al. introduced [...], which has since become a standard baseline." —— 时间做主语 + 地位评价（Manchester）
13. "A seminal study in this area is the work of [...]." —— 标记奠基性文献（Manchester）
14. "To address X, Jones et al. (2019) compared [...]." —— 目的做主语，突出动机而非作者（Manchester）
15. "It has been shown that [...] (Smith et al., 2019; Jones et al., 2020)." —— 研究做主语的弱作者引用，多文献合引（Manchester）

### 3.4 综合：支持与对比

16. "Similarly, Jones (2015) found that [...]." —— 并列同类发现（Manchester）
17. "This view is supported by Jones (2015), who [...]." —— 顺承支持（Manchester）
18. "In contrast to Smith, Jones (2013) argues that [...]." —— 并置对立观点（Manchester）
19. "While Smith (2008) focuses on X, Jones (2009) is more concerned with [...]." —— 一句内完成分工对比，Related Work 收束常用（Manchester）
20. "Other studies, however, have concluded that [...]." —— 引入不一致结论（Manchester）

### 3.5 收束小结（Related Work 末尾）

21. "Taken together, these studies support the notion that [...]." —— 综合归纳（Manchester）
22. "Overall, these studies highlight the need for [...]." —— 从综述滑向"还需要做什么"，自然引出本文（Manchester）
23. "However, such studies remain narrow in focus, dealing only with [...]." —— 指出整体盲区（Manchester）
24. "There remain several aspects of X about which relatively little is known." —— 综述留白句，为下文铺垫（Manchester）
25. "Unlike these works, our method [...] [...]. A detailed comparison is provided in Section [...]." —— ML 版收束：声明差异 + 指引对比表（ML 惯用）

---

## 4. Method（方法）

### 4.1 动机与设计理念

1. "Motivated by this observation, we design [...]." —— 从观察滑向设计，方法节开头标配（ML 惯用）
2. "A natural question arises: [...]. To answer this, we [...]." —— 设问推进式，适合直觉先行的方法（ML 惯用）
3. "Our key insight is that [...]." —— 声明核心洞见，一句话给足设计理由（ML 惯用）
4. "The intuition behind [...] is that [...]." —— 弱化版 insight，语气更谦逊（ML 惯用）
5. "We draw inspiration from [...], and adapt it to [...]." —— 跨领域借力时的诚实声明（ML 惯用）
6. "This design choice is guided by the following consideration: [...]." —— 正式版设计理由（ML 惯用）

### 4.2 方法选用理由（为何这样做）

7. "A major advantage of this approach is that [...]." —— Manchester 标准优势句（Manchester）
8. "This method is particularly useful for [...], since [...]." —— 适用场景 + 理由（Manchester）
9. "X was selected for its [...] and [...]." —— 简洁的选择理由（Manchester）
10. "We adopt [...] rather than [...], because [...]." —— A/B 选择句，评委会想问的问题提前回答（ML 惯用）
11. "One advantage of [...] is that it avoids the problem of [...]." —— 以"回避了什么问题"定义优势（Manchester）
12. "The benefit of this formulation is twofold: [...] and [...]." —— 列举两点好处的收束式（Manchester 改写）

### 4.3 方法流程描述

13. "Our framework consists of two / three main components: [...], [...] and [...]." —— 总分结构开场（ML 惯用）
14. "The overall pipeline is illustrated in Figure 2. Given [...], our model first [...], then [...], and finally [...]." —— 图文配合 + 流程串联（ML 惯用）
15. "Formally, given [...], we define [...] as [...]." —— 公式引入句（ML 惯用）
16. "To this end, we formulate the task as [...]." —— 数学化表述的衔接句（ML 惯用）
17. "Specifically, [...] is computed by [...]." —— 细节展开句（ML 惯用）
18. "The first step in this process is to [...]. Once [...], [...] is performed." —— 步骤顺序描述（Manchester）
19. "In order to [...], we [...] ." —— 目的引导的过程描述（Manchester）
20. "We train [...] end-to-end with [...], using [...]." —— 训练配置一句话（ML 惯用）

### 4.4 与既有方法的关系

21. "Our approach builds upon [...], but differs in that [...]." —— 站在前人肩膀上 + 划清边界（ML 惯用）
22. "Compared with [...], our method replaces [...] with [...], thereby [...]." —— 差异点 + 因果收益（ML 惯用）
23. "Following common practice [...], we [...]." —— 声明沿用惯例的部分，降低审稿人质疑（ML 惯用）

### 4.5 方法局限（诚实声明，可选）

24. "Note that our method assumes [...], which may not hold when [...]." —— 主动声明适用条件（ML 惯用）
25. "A limitation of the proposed approach is its reliance on [...]." —— Manchester 局限句式的 ML 移植（Manchester）

---

## 5. Experiments（实验）

### 5.1 实验设置

1. "We evaluate our method on [...] benchmarks / datasets." —— 数据集声明（ML 惯用）
2. "We compare our approach against [...] strong baselines, including [...]." —— 基线声明 + "strong" 定性（ML 惯用）
3. "Following previous work [...], we adopt [...] as the evaluation metric." —— 沿用惯例的指标声明（ML 惯用）
4. "All experiments are conducted on [...] with [...]." —— 硬件/实现声明（ML 惯用）
5. "Implementation details are provided in the Appendix / supplementary material." —— 细节外移声明（ML 惯用）
6. "For a fair comparison, all methods are trained / evaluated under the same setting." —— 公平性声明，防审稿质疑（ML 惯用）

### 5.2 主结果

7. "Table 1 shows / presents / summarizes the results of [...]." —— 表格引入（Manchester）
8. "As shown in Table 2, our method outperforms all baselines on [...]." —— 主结果声明（Manchester 改写）
9. "Our approach achieves [...] on [...], surpassing the previous best method [...] by [...]." —— 数字对比版（ML 惯用）
10. "Notably, our method achieves this improvement without additional [...]." —— 强调零代价改进，性价比卖点（ML 惯用）
11. "What stands out in the table is [...]." —— 引导读者注意表中亮点（Manchester）
12. "It can be observed that [...]." —— 中性观察句，"we can see that" 的正式版（ML 惯用）

### 5.3 消融实验（Ablation）

13. "To investigate the contribution of each component, we conduct ablation studies on [...]." —— 消融开场标配（ML 惯用）
14. "We ablate [...] by removing / replacing it with [...]." —— 消融方式声明（ML 惯用）
15. "As shown in Table 3, removing [...] leads to a drop of [...] in [...], indicating that [...]." —— "去掉 → 掉点 → 证明必要"三段式（ML 惯用）
16. "The performance gain mainly comes from [...], rather than [...]." —— 归因分析，排除"只是调参好"的质疑（ML 惯用）

### 5.4 分析、解释与深入讨论

17. "Interestingly, [...]." —— 引出意外观察（Manchester）
18. "The most striking result to emerge from the data is that [...]." —— 强调最惊人的发现（Manchester）
19. "A possible explanation for this is that [...]." —— 解释观察，弱断言（Manchester）
20. "We attribute this improvement to [...]." —— 归因句，中等断言强度（ML 惯用）
21. "This result suggests that [...] rather than [...]." —— 用结果做二选一判断（ML 惯用）
22. "Figure 3 visualizes [...] and illustrates how [...]." —— 可视化分析引导句（ML 惯用）
23. "Contrary to expectations, [...]." —— 反直觉结果引入（Manchester）
24. "These results are in line with those of previous studies [...]." —— 与文献互相印证（Manchester）

### 5.5 泛化与稳健性（ML 常见小节）

25. "To assess the generalization ability of [...], we further evaluate [...] on [...]." —— 泛化实验开场（ML 惯用）
26. "Our method remains robust across [...], whereas baselines degrade significantly when [...]." —— 稳健性对比（ML 惯用）
27. "These findings cannot be extrapolated to [...]; further validation is needed for [...]." —— 主动限定结论范围（Manchester）

---

## 6. Conclusion（结论）

### 6.1 重述工作

1. "In this paper, we proposed [...], which [...]." —— 结论首句标配（ML 惯用）
2. "This study set out to examine [...]." —— 以研究目标回扣开头（Manchester）
3. "We presented a novel approach to [...] that [...]." —— "novel" 声明 + 一句话方法（ML 惯用）

### 6.2 总结发现

4. "Our experimental results demonstrate that [...]." —— 中强断言的结果总结（Manchester 改写）
5. "This study has identified [...]." —— 以发现为主语（Manchester）
6. "Taken together, our results suggest that [...]." —— 带适度 hedging 的综合总结（Manchester）

### 6.3 意义与贡献

7. "We believe this work sheds light on [...]." —— 强调启发意义，ML 结论常用（ML 惯用）
8. "The findings reported here provide new insights into [...]." —— 理解性贡献声明（Manchester）
9. "Our approach lays the groundwork for future research into [...]." —— 铺垫性贡献（Manchester）
10. "Beyond [...], the proposed framework can be readily extended to [...]." —— 泛化应用展望（ML 惯用）

### 6.4 局限与未来工作

11. "A limitation of this work is that [...]." —— 直接承认局限（Manchester）
12. "Despite these promising results, [...] remains an open problem." —— 承认未竟之处（ML 惯用）
13. "In future work, we plan to explore [...]." —— 已计划项（ML 惯用）
14. "Further work is needed to determine whether [...]." —— 待验证项（Manchester）
15. "An interesting direction for future research would be to investigate [...]." —— 展望式未来工作（Manchester）
16. "It would be worthwhile to extend our method to [...] settings." —— 推广式建议（Manchester 改写）

---

## 来源

- **Manchester Academic Phrasebank**（各分类页）：https://www.phrasebank.manchester.ac.uk/ —— 章节类（introducing-work / referring-to-sources / describing-methods / reporting-results / discussing-findings / writing-conclusions）与语言功能类共 12 个页面
- **shengmincui/Academic_Phrasebank_note**（Manchester 中英对照笔记）：https://github.com/shengmincui/Academic_Phrasebank_note
- **rezaprama/RhetoriLex**（证据分级写作模式库）：https://github.com/rezaprama/RhetoriLex
- **Wordvice「Useful Phrases for Academic Papers」cheat sheet**：https://wordvice.com/blog/useful-phrases-for-writing-academic-papers/
- **ML 惯用句式**：依据 ML 顶会（NeurIPS/ICML/ICLR/CVPR/ACL）论文通行写法归纳，已逐条标注「ML 惯用」
