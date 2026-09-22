# 《The Science of Scientific Writing》（Gopen & Swan, American Scientist 1990）核心要点

> 来源：George Gopen & Judith Swan, "The Science of Scientific Writing," *American Scientist* 78:550–558 (Nov-Dec 1990)。本文件基于 American Scientist 官网重刊全文（americanscientist.org/blog/the-long-view/the-science-of-scientific-writing）逐段提取整理，所有法则陈述和例句均可直接追溯到原文。用途：给 AI agent 当修改论文句子/段落流畅度的可操作手册。

**方法论根基**：读者不是"读"，而是"解释"（Readers do not simply read; they interpret）。读者对散文结构中各位置应出现什么信息有相对固定的期望（reader expectations）；作者若把信息放在读者期望的位置，就能控制读者对它的识别度和强调度。结构被持续违反时，读者被迫把本应用于理解内容的精力转去解开结构。

**全文最后总结的七条原则**（原文编号）：
1. 语法主语之后尽快跟动词。
2. 想让读者强调的"新信息"放进 stress position（句尾强调位）。
3. 一句话讲"谁的故事"，就把那个人/物/概念放在句首 topic position。
4. 把合适的"旧信息"（前文已出现的内容）放进 topic position，用于向后衔接、向前铺垫。
5. 每个从句/句子的动作要用动词明确说出来。
6. 总体上：先给读者 context，再要求读者接受任何新东西。
7. 总体上：让内容的相对重要性落在结构所引导的相对强调期望上。

---

## 一、Subject–Verb Separation：主语后尽快跟动词

**法则**：读者期望语法主语后立刻出现它的动词。主谓之间插入的任何长成分都被读作"打断"，从而被判定为次要信息——无论它实际多重要。

**认知机制**：读者有一种"句法分辨率"（syntactic resolution）的迫切需求，只有动词到来才被满足。没有动词，读者不知道主语在做什么、句子在讲什么，于是把注意力押在动词到达上，并拒绝把打断性材料当作重点。打断越长，其中恰含重要信息的概率越大，但结构位置会一直给它打上"次要"的烙印——等读者发现它的价值时句子已经结束了。作者由此失去对内容的控制权。

**反例**（原文 URF 句，主语 "the smallest" 与动词 "has been identified" 被隔开 23 个词，占全句一半以上）：

> The smallest of the URF's (URFA6L), a 207-nucleotide (nt) reading frame overlapping out of phase the NH2-terminal portion of the adenosinetriphosphatase (ATPase) subunit 6 gene has been identified as the animal equivalent of the recently discovered yeast H+-ATPase subunit 8 gene.

**正例 A**（插入内容确实重要 → 用分号给它自己的完整小句，制造第二个 stress position）：

> The smallest of the URF's is URFA6L, a 207-nucleotide (nt) reading frame overlapping out of phase the NH2-terminal portion of the adenosinetriphosphatase (ATPase) subunit 6 gene; it has been identified as the animal equivalent of the recently discovered yeast H+-ATPase subunit 8 gene.

**正例 B**（插入内容只是枝节 → 删掉，让句子直冲重点）：

> The smallest of the URF's (URFA6L) has been identified as the animal equivalent of the recently discovered yeast H+-ATPase subunit 8 gene.

**判断标准**：只有作者知道插入内容是否重要——但正因如此，作者必须替读者做这个决定，而不是让 23 个词悬在主谓之间。

**ML 论文风格的补充例**：
- 反例：`The proposed adapter, which consists of a lightweight cross-attention module conditioned on the speaker embedding, a duration predictor trained with monotonic alignment, and a vocoder finetuned on in-domain data, achieves 4.2 MOS.`
- 正例：`The proposed adapter consists of a lightweight cross-attention module, a duration predictor, and a finetuned vocoder; it achieves 4.2 MOS.` 或 `The proposed adapter achieves 4.2 MOS.`（若三组件细节已在别处交代）

---

## 二、The Stress Position：句尾强调位

**法则**：读者天然强调句子末尾到达的材料——这个位置叫 stress position。想让读者强调什么，就把它放在这里。每个话语单元（不管多大）只应做一个点（serve a single function, make a single point）。

**认知机制**：读者每读一个新句子会先"吸一口气"（mental breath），积聚跟随句法展开的张力；当察觉句子接近尾声，开始"呼气"，这口呼气产生强调感。同时人享受"劳作之后得到奖赏"——以兴奋开头、以平淡收尾会令人失望并摧毁动量（"We do not start with the strawberry shortcake and work our way up to the broccoli"——我们不会先吃草莓蛋糕再啃西兰花）。

**stress position 放错时的两种坏事**（原文）：
1. stress position 上站着明显不配强调的材料 → 读者只能自己猜哪个才是重点，而长难句没有任何次级结构线索可依，误读概率飙升。
2. 更糟：stress position 上站着一件"看起来像能承接强调"的冒牌货（imposter material）→ 读者极可能把它当重点，作者白白丢掉一次引导解释的机会。

**stress position 的边界**：它与"句法闭合点"（moment of syntactic closure）重合——当读者知道后面除了正在读的材料外什么都不剩，stress position 就开始了。所以它可长可短：可以是一个词，也可以是数行，甚至可以是整个被明确预告的编号列表（列表每一项还有自己的内部 stress position）。分号和冒号（前提是前半能独立成句）可以制造次级 stress position，让句子延长到几十词仍有处安放新信息。

**反例→正例**（原文分号用法）：
- 反例（三个重信息挤一个 stress position，见下文氢键例）：`dG and dC were derivatized at the 5' and 3' hydroxyls with triisopropylsilyl groups to obtain solubility of the nucleosides in non-aqueous solvents and to prevent the ribose hydroxyls from forming hydrogen bonds.`
- 正例（为第二个重信息造出分号 stress position）：`dG and dC were derivatized at the 5' and 3' hydroxyls with triisopropylsilyl groups; these groups serve both to solubilize the nucleosides in non-aqueous solvents and to prevent the ribose hydroxyls from forming hydrogen bonds.`

**"句子多长算太长"的正确定义**（原文，重要）：不是 29 词之类的人为阈值（readability formulas 的最爱），而是——**当一个句子里"够格承接强调的候选信息"数量超过了可用的 stress position 数量，它就太长了**。原文见过几乎无法解读的 10 词句，也见过 100 词顺流而下的句子。解决手段不是砍长度，而是加分号/冒号制造更多 stress position，或删掉与主线无连接的材料。

**ML 论文风格的补充例**：
- 反例（结果被淹没在中间）：`We evaluate the model on LibriSpeech, achieving a WER of 1.8 on test-clean, which outperforms all prior work.`
- 正例（重点落句尾）：`On LibriSpeech test-clean, the model achieves a WER of 1.8, outperforming all prior work.`

---

## 三、The Topic Position：句首话题位（视角 + 衔接）

**法则**：句首信息为读者确立观察全句的视角——"读者期望这个话语单元是关于先出现者的故事"。stress position 总结为 "Save the best for last"，topic position 则是它的对偶 "First things first"：句尾需要的是闭合与满足，句首需要的是视角与语境（perspective and context）。

**认知机制**：
1. **视角**："Bees disperse pollen" 与 "Pollen is dispersed by bees" 是同样体面的两句，但一句讲蜜蜂、一句讲花粉。被动句本身不差——若该段落讲的是花粉的持续故事，"Pollen is dispersed by bees" 反而更好。
2. **向后衔接 + 向前铺垫**：读者期望 topic position 里的材料提供 linkage（backward）和 context（forward），而且这材料应来自本篇前文已出现过的内容——即"旧信息"（old information）。首次出现的是"新信息"；够格强调的新信息应去 stress position。

**为什么段首要放旧信息**：旧信息稳定出现在 topic position 能帮读者构建论证的逻辑流——聚焦一条主线，既回望又前倾。反之，句首总是新信息会让读者：(a) 不知道这轮讲谁的故事；(b) 被迫扛着新信息走进句子深处才能挂回讨论；(c) 分不清作者到底想强调什么。原文金句："Writing that continually begins sentences with new information and ends with old information forbids both the sense of comfort and orientation at the start and the sense of fulfilling arrival at the end."（句子总以新信息开头、以旧信息收尾的写法，既剥夺开头的舒适与定向感，也剥夺结尾的完成感。）

**反例**（原文地震段，注意每句的 topic position）：

> Large earthquakes along a given fault segment do not occur at random intervals because it takes time to accumulate the strain energy for the rupture. The rates at which tectonic plates move and accumulate strain at their boundaries are approximately uniform. Therefore, in first approximation, one may expect that large ruptures of the same fault segment will occur at approximately constant time intervals. If subsequent main shocks have different amounts of slip across the fault, then the recurrence time may vary, and the basic idea of periodic mainshocks must be modified. For great plate boundary ruptures the length and slip often vary by a factor of 2. Along the southern segment of the San Andreas fault the recurrence interval is 145 years with variations of several decades. The smaller the standard deviation of the average recurrence interval, the more specific could be the long term prediction of a future mainshock.

七句的 topic position 分别是：`Large earthquakes / The rates / Therefore...one / subsequent mainshocks / great plate boundary ruptures / the southern segment of the San Andreas fault / the smaller the standard deviation...`——大部分是首现的新信息，正好落在读者找旧信息的位置上，于是故事焦点每句一换；仅凭 topic position 序列，没有两个读者能拼出同一个故事。而真正贯穿全段的旧信息主线"recurrence intervals / recurrence time / recurrence interval"（第一句引入非随机间隔、第二句说板块均匀、第三句说可预测、第四句说会变、第五句给一个变异、第六句给加州实例、第七句给统计描述）却几乎从不出现在句首。

**正例**（原文改法：先列出每句的旧信息主线与新信息，再让旧信息进 topic position、新信息进 stress position）：

> Large earthquakes along a given fault segment do not occur at random intervals because it takes time to accumulate the strain energy for the rupture. The rates at which tectonic plates move and accumulate strain at their boundaries are roughly uniform. Therefore, nearly constant time intervals (at first approximation) would be expected between large ruptures of the same fault segment. [However?], the recurrence time may vary; the basic idea of periodic mainshocks may need to be modified if subsequent mainshocks have different amounts of slip across the fault. [Indeed?], the length and slip of great plate boundary ruptures often vary by a factor of 2. [For example?], the recurrence intervals along the southern segment of the San Andreas fault is 145 years with variations of several decades. The smaller the standard deviation of the average recurrence interval, the more specific could be the long term prediction of a future mainshock.

注意：改写后暴露出原文从未明说的句间连接——however/indeed/for example 是否恰当连接词？圣安德烈亚斯例到底怎样连接"变化 2 倍"论断？这些逻辑缺口原本被坏结构掩盖，改写让它们显形（见第五节）。

**重要澄清（原文明确警告）**：不要把它简化成规则"旧信息放句首、新信息放句尾"——**没有这样的规则**。因为既然所有信息非旧即新，topic position 和 stress position 之间的中段也必须被旧新信息填满。正确的表述是**原则（principle）而非规则（rule）**："Put in the topic position the old information that links backward; put in the stress position the new information you want the reader to emphasize."（把向后衔接的旧信息放进 topic position；把你想让读者强调的新信息放进 stress position。）

**为什么作者总犯错**（原文归因，No. 1 problem）：绝大多数作者线性写作，开头最怕新想法溜走，于是先把新信息草草记下，再 leisurely 补上回指前文的语境材料。这是在满足作者"卸货"的需求，而非读者"收货"的需求。原文断言："the misplacement of old and new information turns out to be the No. 1 problem in American professional writing today."

**ML 论文风格的补充例**（同段句首焦点漂移的反例 vs 旧信息领衔的正例）：
- 反例：`Latent diffusion models generate high-quality audio. Neural codecs discretize waveforms into tokens. Autoregressive transformers model sequences well. Combining these approaches, we propose...`（每句换主角，读者不知道这段讲谁）
- 正例：`Latent diffusion models generate high-quality audio, but they are slow at inference. This slowness stems from their iterative denoising schedule. Such schedules can be shortened by...`（每句句首回指上一句句尾，一条主线贯穿）

---

## 四、旧-新契约的实操三步（原文给的检查清单）

原文在地震段改写前给出了逐句检查三件事（可直接抄作操作流程）：

1. 向后衔接的旧信息出现在 topic position；
2. 这句话"讲谁的故事"（人/物/概念）出现在 topic position；
3. 新的、够格强调的信息出现在 stress position。

同时先列两张清单再动手：每句的**旧信息主线**（哪个概念在贯穿）与每句的**新信息/应强调点**。原文改写地震段前就是这样先列出的。

---

## 五、Perceiving Logical Gaps：结构改写会暴露逻辑缺口

**法则**：当一个句子里完全没有旧信息（topic position 或其他位置都没有），读者只能自己脑补逻辑连接。结构诊断的最大副产品是：**它会暴露作者自己都没意识到没写清楚的推理缺口**。

**认知机制**：连接在作者脑中太清晰，作者便觉得不必写出，同时低估阅读过程的困难与歧义。结构含混时，句与句的接缝处读者得不到任何线索，只能靠领域知识沉默补全——其他读者被留在黑暗里。

**原文例**（氢键段）：

> The enthalpy of hydrogen bond formation between the nucleoside bases 2'deoxyguanosine (dG) and 2'deoxycytidine (dC) has been determined by direct measurement. dG and dC were derivatized at the 5' and 3' hydroxyls with triisopropylsilyl groups to obtain solubility of the nucleosides in non-aqueous solvents and to prevent the ribose hydroxyls from forming hydrogen bonds. From isoperibolic titration measurements, the enthalpy of dC:dG base pair formation is -6.65±0.32 kcal/mol.

结构问题：不知道这段讲谁的故事；第一句主谓分离；第二句只有一个 stress position 却装了两三个重信息（"solubility...solvents"、"prevent...forming hydrogen bonds"、或许还有 "triisopropylsilyl groups"）。原文的改写决策序列：
1. 倒装第一句，使主-谓-补连贯，且 dG、dC 作为新信息落进 stress position（并因此必须写出动作施事 "We"）；
2. 第二句中 dG/dC 已成旧信息，留在 topic position；
3. "triisopropylsilyl groups" 是新重信息，用分号为它造 stress position；
4. 它随即变成下一从句的旧信息，放进该从句 topic position；
5. 用旗标词 "both" 预告两个效应将共用一个 stress position。

改到一半停住了：第二句把两个效应放进 stress position，读者自然期待第三句接续它们——结果第三句只报了个数。**作者漏写了"衍生化"与"测量"之间的关系，而这恰是他最想讲的点**。补上两句（"Consequently, when the derivatized nucleosides are dissolved in non-aqueous solvents, hydrogen bonds form almost exclusively between the bases. Since the interbase hydrogen bonds are the only bonds to form upon mixing, their enthalpy of formation can be determined directly by measuring the enthalpy of mixing."）逻辑链才闭合，末句的 "measurements" 也变成旧信息，回扣开头的 "we have directly measured"。

**给 AI agent 的启示**：修改论文时，如果按结构原则重排后发现"补不下去"，缺的不是文笔而是实验叙述缺环——要么补连接句，要么删掉挂不上的材料。原文明确说：第四~六例改到某处都无法再推进，除非"supplying connections between ideas or eliminating some existing material altogether"，即"begun by analyzing the structure of the prose, we were led eventually to reinvestigate the substance of the science"。

**ML 论文风格的补充例**：
- 反例（缺口型）：`We finetune the decoder with the proposed consistency loss. The final model achieves 1.8 WER on test-clean.`（finetune 与最终指标之间缺"为什么这个 loss 带来提升"的连接；读者要自己补因果。）
- 正例：`We finetune the decoder with the proposed consistency loss. This loss prevents the alignment from drifting on unseen speakers, the dominant failure mode in our preliminary runs. With stabilized alignment, the final model achieves 1.8 WER on test-clean.`

---

## 六、Locating the Action：动作要写在动词里（nominalization 的反面）

**法则**：读者期望句子的**动作**由**动词**表达。若动词只是 is/are/has/presumed 之类的弱系动词，动作就藏进了名词或形容词里，读者失去全部次级结构线索去定位动作，只能各猜各的——作者不再控制读者的解释行为。

**认知机制**：动词是读者定位"发生了什么"的唯一结构性锚点。动词无力时，即使读者认得全部名词，也不知道这些角色之间 presumed 要发生什么动作——"We know who the players are, but we are ignorant of the actions they are presumed to perform."

**原文反例**（5S RNA 段）及其中全部动词的穷举：

> Transcription of the 5S RNA genes in the egg extract is TFIIIA-dependent. This is surprising, because the concentration of TFIIIA is the same as in the oocyte nuclear extract. The other transcription factors and RNA polymerase III are presumed to be in excess over available TFIIIA, because tRNA genes are transcribed in the egg extract. The addition of egg extract to the oocyte nuclear extract has two effects on transcription efficiency. First, there is a general inhibition of transcription that can be alleviated in part by supplementation with high concentrations of RNA polymerase III. Second, egg extract destabilizes transcription complexes formed with oocyte but not somatic 5S RNA genes.

动词清单：`is / is...is / are presumed to be / are transcribed / has / is...can be alleviated / destabilizes`——几乎全是系动词或空动词，真正的动作（limit、inhibit）根本没以动词形式出现。同时 topic position 每句一换（egg extract, TFIIIA, oocyte extract, polymerase III, 5S RNA, transcription 轮流坐庄），全段同时讲好几个故事。

**原文正例**（把 limit/inhibit 提为动词，并让最高频旧信息 egg extract 与 TFIIIA 尽量占据 topic position）：

> In the egg extract, the availability of TFIIIA limits transcription of the 5S RNA genes. This is surprising because the same concentration of TFIIIA does not limit transcription in the oocyte nuclear extract. In the egg extract, transcription is not limited by RNA polymerase or other factors because transcription of tRNA genes indicates that these factors are in excess over available TFIIIA. When added to the nuclear extract, the egg extract affected the efficiency of transcription in two ways. First, it inhibited transcription generally; this inhibition could be alleviated in part by supplementing the mixture with high concentrations of RNA polymerase III. Second, the egg extract destabilized transcription complexes formed by oocyte but not by somatic 5S genes.

**改写后的额外收益**：即使改后仍不完美，作者没讲清 "limit" 与 "inhibit" 之间的连接这一点显形了——而那正是作者的两个假设所在（转录受限源于 egg extract 中的 TFIIIA 抑制物；该抑制物的作用可通过把 egg extract 加入 oocyte extract 来检测）。原文点题："As critical scientific readers, we would like to concentrate our energy on whether the experiments prove the hypotheses. We cannot begin to do so if we are left in doubt as to what those hypotheses might be."

原文脚注还强调：选哪两个旧信息（egg extract、TFIIIA）作全段的控制性语境，"既非任意也非逻辑必然，纯粹是一次解释行为"——结构线索越少，读者间的解释变异越大。

**ML 论文风格的补充例**：
- 反例（动作全在名词里）：`The utilization of the proposed regularization leads to an improvement in alignment stability and a reduction in WER.`
- 正例：`The proposed regularization stabilizes alignment and reduces WER.`

---

## 七、语境先行：先 context 后 new（原则 6）

**法则**：总体上，先给读者语境，再要求读者考虑任何新东西。这是"先熟悉新环境再在其中工作"的阅读心理（"we appreciate the opportunity to become familiar with a new environment before having to function in it"）。

**操作形式**：句首用旧信息搭好语境 → 句尾释放新信息 → 下一句以这个新信息（此时已成旧信息）开头。这是 old-new contract 的跨句循环：上一句的 stress position 喂养下一句的 topic position。原文氢键改写中，末句 "measurements" 回接前句 "measured directly"、兑现段首 "we have directly measured" 的承诺，就是这个循环的实例。

**ML 论文风格的补充例**：
- 反例：`A novel frequency-domain rotary augmentation improves robustness. Latent space quantization is known to lose phase information.`（顺序颠倒：先结论后背景）
- 正例：`Latent space quantization is known to lose phase information. This phase loss makes generated speech brittle to pitch shifts. We address this brittleness with a frequency-domain rotary augmentation.`

---

## 八、原则 7 与两条元警告

**原则 7**：让内容的相对重要性与结构所引导的强调期望一致。这是前六条的总结：结构本身就是论证结构（"the structure of the prose becomes the structure of the scientific argument. Improving either one will improve the other"）。

**元警告 1——不是规则**：以上没有一条是"规则"（rules）。死守它们和死守"禁拆分不定式""一律用主动语态"一样糟。任何一条读者期望都可以被有效地违反——最好的文体家正是最熟练的违反者，前提是他们绝大多数时间满足期望，使违反被感知为例外时刻。同理，"被动语态 = 坏"是误读：原文明确说 "Pollen is dispersed by bees" 在讲花粉的段落里是更好的句子。

**元警告 2——结构改写会改科学内容**：改善写作实际改善思考（"Improving the quality of writing actually improves the quality of thought"）。四个实例中只有第一例（URF 段）改完近乎成品；其余三例改写都暴露了概念缺口，必须补连接句或删材料。含义：对别人的论文做结构改写时，你产出的版本反映的是你的解释，不必然是作者本意（"it reflects only our interpretation of the author's intentions"）——但原文若真表达了本意，读者根本不需要这么费力。

---

## 应用到论文修改时的检查动作

逐句/逐段可打勾的检查项（reviewer 可直接执行）：

1. **主谓距离**：找出每个句子的语法主语和它的动词；若中间插入超过约 7~10 个词，判定为打断。逐个决定：插入内容重要（→ 用分号/冒号给它自己的小句和 stress position）还是枝节（→ 删除）。重点排查 `-ing` 分词长定语、`which/that` 长从句、`as well as` 括注插在主谓之间的情况。

2. **stress position 清点**：对每个句子列出"够格承接强调的候选信息"（数字结果、与 prior work 的对比、核心结论、新机制名）。若候选数 > 可用 stress position 数（句尾 + 每个分号/冒号产生的次级闭合点），句子太长——不要按词数砍，而是加 `;` 造次级 stress position，或删无连接材料。检查句尾是否站着 imposter material（如例证引用、致谢式从句、 routine 修饰语）。

3. **topic position 串读测试**：只把每段的每句句首（第一个分句的主语部分）抽出来排成竖列读一遍。若每次都换主角 → 段落没有统一的故事线。找出该段真正贯穿的旧信息（哪个概念反复出现却总不在句首），把它提为多数句子的 topic position。

4. **旧信息前置换位**：对每句检查：句首词是否已在前文出现过？若句首是首现信息，尝试把前句 stress position 里的概念提到本句句首（跨句 old→new 循环）。注意勿机械化：句首与句尾之间的中段允许新旧混杂，规则只有"向后衔接的旧信息放句首、要强调的新信息放句尾"这一条原则。

5. **动词力量审计**：抽出每段全部动词列表。若列表里 `is/are/has/remains/appears` 占多数、真正动作藏在名词化（`utilization/improvement/evaluation/implementation`）里，把动作改写为动词（"the utilization of X leads to an improvement in Y" → "X improves Y"），并确认每个句子的"发生了什么"能只靠读动词序列还原。

6. **逻辑缺口显影**：按上述重排后，如果出现"接不下去"的句缝（上一句 stress position 承诺的话题下一句没接），标记为逻辑缺环：要么补一句连接（交代因果/机制），要么删除挂不上的句子。把这类缺口报告给作者——这通常说明论证本身有洞，不是文笔问题。

7. **语境先于新知**：任何新概念/新名词首次出现前，确认读者已在同句或前句见过足够的语境铺垫；避免段落以新信息开头、以旧信息收尾的组合。

8. **预期违背需有意图**：发现违反上述任一条的地方，不要机械改正；确认它是不是有意的修辞（强调、对比、悬念）。无意图的违反才修；有意图的违反保留，但确保违反处前后期望满足度高，使违反可被感知为例外。

**溯源说明**：本文件全部内容（七条原则、URF/地震/氢键/5S RNA 四组原始改例、认知机制阐述、"No.1 problem" 断言、元警告）均直接提取自 American Scientist 官网重刊的原文全文，非二手转述。仅"ML 论文风格的补充例"各条为按原文模式自造的补充，与原文无对应。
