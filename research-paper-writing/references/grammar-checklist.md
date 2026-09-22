# 学术英语语病检查清单（ML/CV/NLP 论文 · AI agent 执行版）

> 用法：改论文时按文末「检查顺序」逐条对照。每条含规则（中文）→ 正例 → 反例 → 修改动作（一句话指令式）。
> 缩写说明：【搜】= grep/搜索指令提示；【读】= 需读上下文判断；【写】= 生成文字时直接遵守。

---

## 1. 冠词（Articles）—— 中国作者最高频错误

### 1.1 复数泛指不加冠词

- 规则：表示一类事物的复数名词（泛指、非特指）前面不加 the/a。
- 正例：`Convolutional neural networks have achieved remarkable results.` / `Data augmentations improve robustness.`
- 反例：`The convolutional neural networks have achieved remarkable results.`（除非特指某一组特定网络）
- 动作：【读】对每个带 the 的复数名词，问：读者能否确定是哪一组？不能则删 the。

### 1.2 特指才加 the

- 规则：the 的判定标准是「读者能否唯一定位该名词」。第二次提及、有后置限定语（of X、in this paper）、文中唯一时加 the。
- 正例：`We propose a memory module. The module stores historical features.`（首次 a，再次 the）
- 反例：`We propose the memory module.`（首次提及，读者无从定位）
- 动作：【读】每个 the，向前文中搜索该名词的首次出现；找不到首次出现且无限定语时，考虑删 the 或改为 a。

### 1.3 首次提及句型 "We propose X, a novel..."

- 规则：同位语（apposition）介绍新名词时用 a，不用 the；即使内容是 "novel/first/new"。
- 正例：`We propose DiffNet, a novel diffusion-based network for image restoration.`
- 反例：`We propose DiffNet, the novel diffusion-based network...` / `We propose a method, which is a novel...`（冗余拆句）
- 动作：【搜】正则 `propose [A-Za-z]+, (the|an?)`，检查同位语冠词；再搜 `novel|first` 前是否误用 the。

### 1.4 唯一性名词加 the

- 规则：文中唯一存在的事物（proposed framework 里的某层、某损失、the ground truth、the dataset 划分）加 the。
- 正例：`The encoder consists of three blocks.`（本文模型里的那个 encoder）
- 反例：`Encoder consists of three blocks.`（漏 the，中式英语高频）
- 动作：【搜】句首或逗号后的裸名词作主语且指本文模型部件（encoder/decoder/loss/module），无 the 则补。

### 1.5 不可数名词不加冠词、不用复数

- 规则：research, evidence, information, knowledge, code, hardware, software, literature, training, inference, feedback 前不加 a，不加 s。
- 正例：`This provides strong evidence for...` / `We conduct extensive experiments.`
- 反例：`a strong evidence` / `researches` / `informations` / `knowledges`
- 动作：【搜】`a (evidence|information|knowledge|research|software|hardware|code|feedback|literature)` 和 `(researches|informations|knowledges|evidences|feedbacks|softwares)`，全部改写。

### 1.6 抽象动作名词前通常不加冠词

- 规则：泛指过程时 ablation, evaluation, comparison, optimization, supervision 前不加 the/a。
- 正例：`Ablation studies verify the effectiveness of each component.` / `We perform ablation on...`
- 反例：`The ablation studies verify...`（若泛指一般做法）；但特指本文的消融实验时 `The ablation study in Table 3` 加 the 正确。
- 动作：【读】区分泛指（无冠词）与特指本文实验（the）。

### 1.7 方法名/模型名前不加 the

- 规则：专有模型名（ResNet, BERT, GPT-4, U-Net, Faster R-CNN）不加 the。
- 正例：`We compare our method with ResNet and Swin Transformer.`
- 反例：`We compare our method with the ResNet.`
- 动作：【搜】`the (ResNet|BERT|VGG|Transformer|CNN|GAN|ViT|U-Net)`，删 the（"the Transformer architecture" 这类泛指架构除外）。

### 1.8 our/the proposed 的选择

- 规则：指自己的方法用 `our method` 或 `the proposed method`，二者都带限定词；不能裸用 `proposed method`，也不必叠用 `the proposed our method`。
- 正例：`Our method outperforms the baseline.` / `The proposed framework consists of...`
- 反例：`Proposed method outperforms baseline.` / `Our proposed the method...`
- 动作：【搜】句中裸出现的 `proposed (method|framework|model|approach|network)`，前面无 our/the 时补 the。

### 1.9 数据集名：有 dataset 后缀才加 the

- 规则：`the COCO dataset`、`the ImageNet dataset` 加 the；裸名 `on COCO`、`on ImageNet` 不加。
- 正例：`Experiments on COCO and ImageNet demonstrate...` / `We evaluate on the COCO dataset.`
- 反例：`Experiments on the COCO demonstrate...` / `on COCO dataset`（缺 the）
- 动作：【搜】`on (the )?[A-Z][a-zA-Z]+ dataset`，核对冠词；`the (COCO|ImageNet|CIFAR|VOC|KITTI|ADE20K|LSUN|FFHQ)\b`（后无 dataset）删 the。

### 1.10 章节图表引用

- 规则：`Section 3`、`Figure 1`、`Table 2`、`Eq. (5)` 前不加 the；`the third section`、`the first figure` 用序数词时才加。
- 正例：`As shown in Figure 3, ...` / `We detail this in Section 4.`
- 反例：`As shown in the Figure 3, ...` / `in the Section 4`
- 动作：【搜】`the (Section|Figure|Table|Eq\.|Algorithm) \d`，删 the。

### 1.11 "in this paper / in this work" 前加 in、不加冠词错位

- 规则：固定短语 `in this paper/work/section`；不用 `on this paper`。
- 正例：`In this paper, we address...`
- 反例：`On this paper, we address...` / `At this paper...`
- 动作：【搜】`(on|at) this (paper|work|study|section)`，改 in。

### 1.12 泛指学科/领域不加 the

- 规则：computer vision, machine learning, natural language processing 前不加 the。
- 正例：`This has broad applications in computer vision.`
- 反例：`in the computer vision`
- 动作：【搜】`the (computer vision|machine learning|deep learning|natural language processing)\b`，删 the。

### 1.13 序数词与最高级前加 the

- 规则：the first/second/best/most important 后接名词时加 the。
- 正例：`the first method that...` / `the best performance`
- 反例：`first method that...`（缺 the，但 "a first attempt" 在特定语境可接受）
- 动作：【搜】句中裸的 `(first|second|last|best|worst|only) `，检查前有无 the。

### 1.14 play a role / take an approach 等固定搭配中的冠词

- 规则：`play a (key|important|vital) role`、`as an alternative`、`in a real-time manner` 固定带 a/an；an 用于元音音素开头。
- 正例：`Attention plays a key role in...` / `As an alternative, ...`
- 反例：`plays key role` / `a important contribution`（an 误为 a）
- 动作：【搜】`plays? (key|important|crucial|vital) role` 补 a；【搜】`a (important|interesting|effective|influence)` 换 an（按发音，如 a university / an hour）。

---

## 2. 时态（Tenses）

### 2.1 各节标准时态分配

- 规则：
  - Abstract：本文做了什么（现在时）+ 主要结果（现在时）。
  - Introduction：背景与已有工作（现在时/现在完成时），本文贡献（现在时）。
  - Related Work：他人工作（过去时为主）。
  - Method：本文方法描述（现在时）。
  - Experiments：实验设置与做了什么（过去时），结果陈述（现在时/过去时均可但需一致）。
  - Conclusion：总结贡献（现在时/现在完成时），展望（将来时）。
- 正例：Abstract `We propose X. Experiments show that our method achieves...`；Method `The encoder extracts features from...`
- 反例：Method 一节写成 `The encoder extracted features...`（方法描述用过去时）
- 动作：【读】逐节检查时态是否符合上表；Method 节搜过去式动词（-ed 结尾的规则动词）逐一核对。

### 2.2 描述已有工作：过去时 vs 现在完成时 vs 现在时

- 规则：
  - 具体某人某年的动作 → 过去时：`Lee et al. proposed X in 2019.`
  - 强调延续至今的状态/影响 → 现在完成时：`X has been widely used in...` / `have attracted considerable attention`
  - 描述该工作的内容/结论仍有效 → 现在时：`Their model uses a Transformer backbone.`
- 正例：`Vaswani et al. introduced the Transformer, which has since become the backbone of most NLP models.`
- 反例：`Vaswani et al. have introduced the Transformer in 2017.`（与具体年份连用不可用完成时）
- 动作：【搜】`have (proposed|introduced|presented|developed|shown|demonstrated|designed) `，检查是否与具体年份/单次动作连用；是则改过去时。

### 2.3 描述自己的方法用现在时

- 规则：Method 节的每个动作（extracts, computes, generates, aggregates）用一般现在时。
- 正例：`The attention module aggregates information from all positions.`
- 反例：`The attention module aggregated information...`
- 动作：【读】Method 节第三人称单数动词统一现在时。

### 2.4 实验中做的事用过去时

- 规则：训练、微调、运行等已完成的实验动作 → 过去时；普适结论 → 现在时。
- 正例：`We trained each model for 300 epochs.` / `We fine-tuned on downstream tasks.`
- 反例：`We train each model for 300 epochs.`（叙述已完成实验时）
- 动作：【读】Experiments 节区分「叙述本次实验」（过去时）与「规律性结论」（现在时）。

### 2.5 图表引用用现在时

- 规则：Figure/Table/Eq 作主语时用 shows, presents, illustrates, depicts, reports, summarizes, compares。
- 正例：`Figure 2 shows the qualitative comparison.` / `Table 3 reports the ablation results.`
- 反例：`Figure 2 showed...` / `In Figure 2 we can see...`（口语化，可改 `Figure 2 shows`）
- 动作：【搜】`(Figure|Table|Fig\.) \d+ (showed|presented|illustrated)`，改现在时；【搜】`we can (see|observe) (in|from) Figure`，改 `Figure X shows`。

### 2.6 结果陈述的时态一致

- 规则：同一句/同一段中描述同一组结果，时态不混用。常见模式：`Our method outperforms X by 3.2 mAP.`（现在时）或 `Our method outperformed X by 3.2 mAP.`（全文过去时也可，但须统一）。
- 正例：`Our model achieves 45.2 mAP, which surpasses the baseline by 3.2 points.`
- 反例：`Our model achieves 45.2 mAP, which surpassed the baseline by 3.2 points.`
- 动作：【读】每个结果段落内核对主从句时态一致。

### 2.7 "It has been shown that" 类被动完成式

- 规则：引已有共识 → `It has been shown that...`；引具体论文 → `X showed that...`。
- 正例：`It has been shown that pretraining improves generalization.`
- 反例：`It was shown that pretraining improves generalization.`（弱，且指代不明；具体引用时应写 `Smith et al. showed that`）
- 动作：【搜】`It (was|is) shown that`，改 has been shown 或落到具体作者。

### 2.8 将来时仅用于展望

- 规则：正文中 will 只出现在 conclusion/future work；描述本文方法不用 will（中式英语高频错误）。
- 正例：`We will release the code.` / `In future work, we will explore...`
- 反例：`In the next section, we will introduce the method.`（可接受但建议 `we introduce`；Method 节内 `The model will output...` 则错误）
- 动作：【搜】`will `，逐一核对是否属于展望/计划；Method/Experiments 描述内的 will 删改。

---

## 3. 主谓一致与单复数

### 3.1 data 的数

- 规则：现代 ML 论文惯例 data 作复数（are, were, these data）与单数（is）均常见；全文统一即可。但 `datas` 永远错误。
- 正例：`The data are split into...`（或 `The data is split...`，二选一并统一）
- 反例：`datas` / `a data`
- 动作：【搜】`datas\b`，改 data/data points；全文统计 data is/are 的次数，统一为主。

### 3.2 number of / a total of

- 规则：`the number of X is`（单数）；`a number of X are`（= many，复数）；`a total of 100 images are`（复数）。
- 正例：`The number of parameters is 25M.` / `A total of 100 images are used.`
- 反例：`The number of parameters are 25M.` / `A number of images is used.`
- 动作：【搜】`number of`，按上表核对动词。

### 3.3 each / every / either / neither 作主语

- 规则：each/every/either/neither + 单数名词 + 单数动词，即使后有 of 短语。
- 正例：`Each of the models is evaluated separately.`
- 反例：`Each of the models are evaluated separately.`
- 动作：【搜】`(Each|Every|Either|Neither) of`，核对动词单数。

### 3.4 常见不可数名词清单（禁复数、禁 a）

- 规则：以下名词不可数：research, evidence, information, knowledge, advice, code, hardware, software, literature, equipment, progress, work（指工作内容时）, training, inference, supervision, storage, memory（内存义）, computation, feedback, staff, luggage。
- 正例：`much research` / `little evidence` / `a piece of code` / `several pieces of evidence`
- 反例：`many researches` / `several evidences` / `an equipment` / `a progress`
- 动作：【搜】`(many|several|few|a) (researches?|evidences?|informations?|knowledges?|equipments?|softwares?|hardwares?|progresses?|advices?|literatures?)`，改写为 much/little/a piece of 结构。

### 3.5 拉丁/希腊复数形易错词

- 规则：phenomenon→phenomena, criterion→criteria, medium→media, analysis→analyses, datum→data, formula→formulae/formulas, index→indices/indexes, matrix→matrices, basis→bases, hypothesis→hypotheses。
- 正例：`These phenomena suggest...` / `The evaluation criteria include...`
- 反例：`These phenomenons...` / `criterias` / `analysises`
- 动作：【搜】`(phenomenons|criterias|matrixes|formulas?es|indexs|basises|hypothesises)`，改正确复数；【搜】单数位置的 `a phenomena|a criteria|a media|an analyses`（复数误作单数），改单数形。

### 3.6 集合名词

- 规则：team/committee/community 在美式用法中多作单数；the community is。全称 `the authors of [X]` 用复数。
- 正例：`The community has shown great interest.`
- 反例：`The community have shown...`（英式可接受，但需全文一致）
- 动作：【读】集合名词动词单复数全文统一。

### 3.7 就近误配（复杂主语）

- 规则：动词与核心名词一致，与最近的名词无关。`The set of images is...`（set 单数）；`The results of the experiments show...`（results 复数）。
- 正例：`The collection of samples provides...`
- 反例：`The collection of samples provide...`
- 动作：【读】找 `of` 结构作主语核心的句子，动词与 of 前的核心名词核对一致。

### 3.8 there be 句型一致

- 规则：there is/are 与后面真正的主语一致。
- 正例：`There are several reasons for this.` / `There exists a trade-off.`
- 反例：`There is several reasons for this.`
- 动作：【搜】`There (is|are)`，与后接名词核对。

### 3.9 百分比/分数主语

- 规则：`80% of the data are/is`（视 data 的用法）；`Half of the images are`（复数）。总原则与 of 后名词一致。
- 正例：`Approximately 80% of the samples are misclassified.`
- 反例：`Approximately 80% of the samples is misclassified.`
- 动作：【搜】`\d+% of`，核对动词。

### 3.10 "the following" 与倒装主语

- 规则：`The following are...`（following 复数时）；倒装句 `Among them is/are` 动词与后置真主语一致。
- 正例：`The following are the key contributions.` / `Among these methods is the one proposed by...`
- 反例：`Among these methods are the one proposed by...`
- 动作：【搜】`Among .*(is|are)`，与后置名词核对单复数。

---

## 4. 句法结构错误

### 4.1 逗号粘连（comma splice）

- 规则：两个独立分句不能仅用逗号连接；用句号、分号或连词。
- 正例：`The model converges quickly; however, it overfits on small datasets.`
- 反例：`The model converges quickly, however, it overfits on small datasets.`（however 不是连词）
- 动作：【搜】`, however,|, therefore,|, moreover,|, thus,`，检查前半句是否为完整分句；是则把逗号改分号或句号。

### 4.2 连接副词 vs 连词混用

- 规则：however, therefore, moreover, thus, hence, consequently 是副词，不能像 but/and/so 一样连接两个分句。
- 正例：`The loss decreases. Therefore, the gradient vanishes.`
- 反例：`The loss decreases, therefore the gradient vanishes.`
- 动作：与 4.1 同一动作；改写时优先分号+副词。

### 4.3 残缺句（fragment）

- 规则：每个句子须有主谓结构。以 Because/Although/While/Which/That 开头的小句不能独立成句。
- 正例：`Because the dataset is small, we adopt heavy augmentation.`
- 反例：`Because the dataset is small. We adopt heavy augmentation.`
- 动作：【搜】`(Because|Although|While|Since|Given that) [^.]*\.` 检查其后是否接完整主句；【搜】句首 `Which|That is why` 独立成句的，并入前句。

### 4.4 悬垂修饰语（dangling modifier）—— 学术文高频

- 规则：句首分词短语（Using/Given/Compared with/After/By/When）的逻辑主语必须等于主句主语。
- 正例：`Using the proposed loss, we train the model to convergence.`（we 是 using 的执行者）
- 反例：`Using the proposed loss, the model is trained to convergence.`（model 不是 using 的执行者）
- 动作：【搜】句首 `(Using|Given|Compared|Based|Following|After|Before|By) `，检查主句主语是否是分词短语的执行者；不是则改写（把主句主语改为执行者，或把分词短语改为从句 `Since/When/While...`）。

### 4.5 "Compared with X, Y..." 的主语核对

- 规则：Compared with 短语的隐含主语须是被比较对象本身。
- 正例：`Compared with the baseline, our method reduces latency by 40%.`
- 反例：`Compared with the baseline, the latency is reduced by 40%.`（latency 不能与 baseline 比较）
- 动作：【搜】`Compared (with|to) `，检查主句主语能否与比较对象同类。

### 4.6 平行结构

- 规则：both...and / either...or / not only...but also / neither...nor 连接的成分必须语法同类（名词对名词、动名词对动名词、不定式对不定式）。
- 正例：`not only improves accuracy but also reduces latency`
- 反例：`not only improves accuracy but also the reduction of latency`
- 动作：【搜】`(both|either|neither|not only)`，找到配对连词，核对两侧词性结构一致。

### 4.7 列表一致性（A, B, and C）

- 规则：三项以上并列，各项语法形式一致（全名词短语、全动名词或全句子）。
- 正例：`We evaluate the model on classification, detection, and segmentation.`
- 反例：`We evaluate the model on classification, detecting objects, and for segmentation.`
- 动作：【读】每个三项以上列表，逐项核对开头词的词性。

### 4.8 which 从句指代不明

- 规则：which 就近指代前面的名词；若可能误解，改用 that + 名词复指（`a property that...`）或重组。
- 正例：`We introduce a regularization term, which penalizes large weights.`（term 是 which 的先行词，明确）
- 反例：`We train the model on the new dataset, which improves performance.`（which 指 dataset 还是 train？）
- 动作：【搜】`, which `，核对先行词是否无歧义；歧义则改写为 `This improves...` 或补名词复指。

### 4.9 that vs which 限定性

- 规则：限定性从句（不可缺少）用 that（无逗号）；非限定性从句（补充说明）用 which（有逗号）。美式惯例。
- 正例：`The model that we trained achieves...` / `Our model, which was trained on COCO, achieves...`
- 反例：`The model which we trained achieves...`（可接受但美式惯例偏 that）；`The model, that we trained,...`（错误）
- 动作：【搜】`, that `，改 `which` 或去逗号。

### 4.10 it 形式主语滥用

- 规则：`It is worth noting that` / `It should be noted that` / `It is obvious that` / `It can be seen that` 多数可删或更直接。
- 正例：`Notably, ...` / `Note that ...` / `Interestingly, ...`
- 反例：`It is worth mentioning that our method is simple.` → `Notably, our method is simple.`
- 动作：【搜】`It is (worth|should be noted|important to note|obvious|clear|evident)`，改写为直接陈述或 Note that。

### 4.11 长主语与头重句

- 规则：避免主语超过一行再接动词；用形式主语或拆句。
- 正例：`Training large models requires...`
- 反例：`The process of iteratively refining the generated samples through the reverse diffusion steps over many iterations requires...`
- 动作：【读】主语超过 15 词的句子，考虑 it 形式主语或拆成两句。

### 4.12 句子过长（>45 词）

- 规则：学术英语单句超过 45 词通常应拆分；超过 60 词几乎一定该拆。
- 正例：两句中每句 20-30 词。
- 反例：一句 70 词、含三层从句嵌套。
- 动作：【读】对超长句找插入语/从句边界，拆为 2-3 句。

### 4.13 there be 句头堆叠

- 规则：避免连续多个 There is/are 开头的句子；优先直接主谓。
- 正例：`Two issues remain.` / `A trade-off exists between speed and quality.`
- 反例：`There are two issues. There is a trade-off. There is also a problem.`
- 动作：【搜】连续段落中出现多个 `There (is|are)`，改写一半为直接陈述。

### 4.14 主语省略错误（中国作者特有）

- 规则：英语从句/主句不能省主语（与中文不同）。`When training the model, we found...` 可以（we 是主语）；`When train the model...` 不行。
- 正例：`When evaluating on the test set, we observe...`
- 反例：`When training, the accuracy improves.`（training 无宾语且主句主语错位——这也是 4.4 悬垂）
- 动作：【搜】`When (training|evaluating|testing|comparing), `，核对主句主语。

---

## 5. 介词与搭配

### 5.1 高频介词搭配清单（固定搭配，不可替换）

- 规则：以下为标准搭配：
  - depend **on** / rely **on** / based **on** / focus **on** / concentrate **on** / insist **on**
  - different **from**（≠ different than 英式可、different with 错）
  - consist **of** / be composed **of** / be made up **of**
  - compare **with**（同类细致比较）/ compare **to**（异类比喻）
  - in contrast **to** / compared **to** / with respect **to** / with regard **to**
  - result **in**（导致）/ result **from**（源于）
  - attribute **to**（归因）/ be attributed **to**
  - lead **to** / contribute **to** / be related **to** / be associated **with**
  - substitute **for** / replace **with**（replace A with B，不用 replace by）
  - be aware **of** / be capable **of** / be suitable **for** / be responsible **for**
  - in accordance **with** / in terms **of** / on behalf **of**
  - be superior **to** / be inferior **to** / prior **to** / subsequent **to**
- 正例：`This results in better generalization.` / `The improvement results from pretraining.`
- 反例：`This results to better generalization.` / `depends of` / `different with`
- 动作：【搜】`results? to|depends? of|different (with|than)|replace(d)? by|substitute with|capable to|aware about`，按上表修正。

### 5.2 compare with vs compare to

- 规则：compare A with B = 比较 A 与 B（同类）；compare A to B = 把 A 比作 B（比喻）。实验比较一律 with。
- 正例：`We compare our method with several baselines.`
- 反例：`We compare our method to several baselines.`（虽然美式常混用，正式论文偏 with）
- 动作：【搜】`compare (our|the) .* to `，实验比较语境改 with。

### 5.3 research on / study on

- 规则：research **on** X 正确；study **of/on** X 均可；investigation **into** X。
- 正例：`Recent research on diffusion models has grown rapidly.`
- 反例：`Recent researches about diffusion models...`
- 动作：【搜】`research (about|for) `，改 on；【搜】`researches`，改 research。

### 5.4 experiment on / with / for

- 规则：experiment **on** a task/dataset（在…上做实验）；experiment **with** a method/idea（尝试用…做实验）。
- 正例：`We experiment with different learning rates.` / `Experiments on ImageNet show...`
- 反例：`Experiments about ImageNet show...`
- 动作：【读】核对 experiment 后介词与宾语类型匹配。

### 5.5 中文式 "discuss about / emphasize on / research about"

- 规则：discuss, emphasize, mention, consider, investigate, enter, approach 均为及物动词，直接接宾语，不加介词。
- 正例：`We discuss the limitations.` / `This paper emphasizes efficiency.`
- 反例：`We discuss about the limitations.` / `emphasizes on efficiency` / `mention about`
- 动作：【搜】`(discuss|emphasize|mention|consider|investigate|stress) (about|on|upon)`，删介词。

### 5.6 in/on/at 空间与场景

- 规则：
  - **in** the paper/figure/table/section/experiment（书面语境）
  - **on** the dataset/benchmark/task（数据集/任务上）
  - **at** the beginning/end, at 300 epochs（时间点）
- 正例：`in Figure 3` / `on the COCO dataset` / `at the end of training`
- 反例：`on Figure 3` / `in the COCO dataset`（可接受但 on 更惯用）/ `in 300 epochs`
- 动作：【搜】`on (Figure|Table|Eq)`，改 in；【搜】`in (epoch|step|iteration) \d`，改 at。

### 5.7 by vs with 表示手段

- 规则：by + 动名词/手段（by adding noise）；with + 工具/成分（with a residual connection）。
- 正例：`We improve the model by adding skip connections.` / `We enhance it with a residual connection.`
- 反例：`We improve the model with adding...`
- 动作：【读】with + 动名词组合改 by + 动名词。

### 5.8 increase/decrease 介词

- 规则：increase **by** X（幅度）/ increase **to** X（终值）/ increase **from** A **to** B。
- 正例：`Accuracy increases by 3.2%` / `increases to 95.6%` / `from 92.4% to 95.6%`
- 反例：`increases 3.2%`（缺 by）/ `increases with 3.2%`
- 动作：【搜】`(increase|decrease|improve|drop|reduce|gain)s? \d`，补 by/to。

### 5.9 "the performance of X on Y" 链式 of/on

- 规则：性能属于方法、在数据集上测：`the performance of our method on COCO`。
- 正例：`the performance of the proposed method on the test set`
- 反例：`the performance on the test set of the proposed method`（头重且歧义）
- 动作：【读】`performance on ... of ...` 语序颠倒的，重排为 of X on Y。

### 5.10 中文高频 "has the ability to / in order to" 冗余

- 规则：has the ability to → can；in order to → to（in order to 仅在需要避免歧义时用）。
- 正例：`Our model can handle...` / `To speed up training, ...`
- 反例：`Our model has the ability to handle...` / `In order to speed up, ...`
- 动作：【搜】`has the (ability|capability) to `，改 can；【搜】`In order to`，多数改 To。

---

## 6. 用词与风格

### 6.1 which vs that

- 规则：见 4.9。补充：that 前不能有逗号；which 引导非限定从句须有逗号。
- 动作：同 4.9。

### 6.2 less vs fewer

- 规则：可数名词用 fewer（fewer parameters, fewer samples）；不可数用 less（less memory, less noise）。
- 正例：`Our method uses fewer parameters and less memory.`
- 反例：`less parameters` / `fewer computation`
- 动作：【搜】`less (parameters|samples|images|epochs|layers|steps|tokens)`，改 fewer；【搜】`fewer (memory|computation|noise|data|information|time)`，改 less。

### 6.3 affect vs effect

- 规则：affect 是动词（影响），effect 是名词（效果/影响）。effectively 副词。
- 正例：`This affects performance.` / `The effect of pretraining is significant.`
- 反例：`This effects performance.` / `The affect of pretraining...`
- 动作：【搜】`effects? (the )?(performance|accuracy|results)`（动词位），核对词性。

### 6.4 principal vs principle

- 规则：principal = 主要的（principal component, the principal contribution）；principle = 原则（the principle of causality）。
- 正例：`the principal contribution` / `the principle behind our design`
- 反例：`the principle contribution` / `principal components analysis`（正确是 principal component analysis）
- 动作：【搜】`(principles?|principals?)`，逐个核对语义。

### 6.5 comprise vs compose vs consist

- 规则：A comprises B（A 包含 B，不加 of）；B is composed of A；A consists of B（最常用、最安全）。
- 正例：`The framework consists of three modules.`
- 反例：`The framework is comprised of three modules.`（有争议，避免）/ `The framework composes three modules.`
- 动作：【搜】`comprise(s|d)? of|composes? |is comprised`，改 consist(s) of 或 is composed of。

### 6.6 大小写惯例

- 规则：
  - `Figure 1` / `Fig. 1`（期刊要求不同，全文统一）；句子中间用 `Figure 1`，全称大写 F。
  - `Section 3` / `Section 3.2`；`Table 2`；`Algorithm 1`；`Eq. (5)` 或 `Equation (5)`。
  - 模型名保留官方大小写：BERT, GPT-3, ResNet-50, Swin Transformer, DeiT, CLIP, U-Net, RoBERTa。
  - 数据集：COCO, ImageNet, CIFAR-10, ADE20K, Kinetics-400。
  - `our method` 小写；`the Proposed Method`（标题式的全大写/词首大写滥用）避免。
- 正例：`As shown in Figure 3, our ResNet-50 variant...`
- 反例：`As shown in figure 3` / `we propose A Novel Method...` / `BERT` 写成 `bert`
- 动作：【搜】`\bfigure \d|table \d|section \d|algorithm \d|equation \d`（小写开头），句中位置改大写；核对模型名大小写与官方一致。

### 6.7 数字与单位排版

- 规则：
  - 10 以下用词（five images），10 及以上用数字（15 images）；统计/技术量一律数字（3 layers, 5 images in a technical sense）。
  - 句首不放数字：`Fifteen images...`。
  - 数字与单位间空格：`3.2 GB`, `10 ms`, `5 kHz`；% 前是否空格全文统一（`45%` 惯例无空格，`45 %` 在部分欧刊可见）。
  - 范围用 en-dash：`100--200 epochs`（LaTeX）/ `100-200`。
  - 小数点前有 0：`0.85`（不写 .85）。
- 正例：`We train for 200 epochs with a batch size of 32.`
- 反例：`We train for two hundred epochs` / `batchsize of 32` / `.85 accuracy` / `95.6%.` 前后不一致
- 动作：【搜】`batchsize|batch-size`（核对官方用 batch size）；【搜】`\s\.\d`，补前导 0；核对 % 前空格全文统一。

### 6.8 缩写首次定义

- 规则：每个缩写首次出现时给出全称：`convolutional neural network (CNN)`；之后只用缩写。Abstract 与正文首次出现分别定义。标题中的缩写一般避免（除非领域通行，如 NLP、GAN）。
- 正例：`a vision transformer (ViT)` → 之后 `the ViT`
- 反例：`We use a CNN...`（首次出现即用缩写）；`the Vision Transformer (ViT)` 用了两次定义
- 动作：【读】对每个缩写搜首次出现位置，核对是否定义过；对全称+缩写并存的短语搜索重复定义。

### 6.9 连字符复合词

- 规则：
  - 作定语加连字符：`state-of-the-art method`, `end-to-end training`, `real-time inference`, `large-scale dataset`。
  - 作表语/宾语通常不加：`our method is state of the art`（可接受，但全文统一即可）；`trained end to end`。
  - 副词+形容词不加：`highly effective`（无连字符）；`well-known method`（well 系列加）。
- 正例：`an end-to-end framework` / `trained in an end-to-end manner` / `the method is well-known`
- 反例：`a end to end framework` / `real time inference`（作定语缺连字符）
- 动作：【搜】`(end to end|real time|state of the art|large scale|high resolution|multi [a-z]|cross [a-z]) `，核对作定语时的连字符；【搜】`a state-of-the-art`（a vs an）。

### 6.10 弱动词与名词化冗余

- 规则：`perform an analysis of` → `analyze`；`make a comparison` → `compare`；`conduct an investigation` → `investigate`；`is able to` → `can`。
- 正例：`We analyze the failure cases.`
- 反例：`We perform an analysis of the failure cases.`
- 动作：【搜】`perform(s|ed)? an? (analysis|comparison|evaluation|investigation|examination) of`，改直接动词；【搜】`is able to|are able to`，改 can。

### 6.11 冗余短语（中文论文直译常见）

- 规则：删除无信息量的填充语：`It is well known that`、`As we all know`、`obviously`、`in fact`（多数可删）、`very`（用精确形容词替代）、`really`。
- 正例：`Pretraining improves generalization.`（删掉 It is well known that）
- 反例：`As we all know, pretraining improves generalization.`
- 动作：【搜】`As we all know|It is well known|obviously|in fact, |very (good|large|small|important|effective)`，删或换精确词。

### 6.12 literally / actually / basically 口语词

- 规则：正式论文避免 basically, actually, literally, totally, huge, a lot of。
- 正例：`substantial improvement` / `many`
- 反例：`basically, the model...` / `a lot of experiments`
- 动作：【搜】`\b(basically|actually|literally|totally|huge)\b|a lot of`，替换。

---

## 7. 学术文特有规范

### 7.1 we vs passive voice

- 规则：现代 ML 论文惯例多用 we（主动、直接）；描述通用流程/客观事实时用被动。同一节内不过度切换。避免把 we 用于非作者行为（`we can see that` 口语化）。
- 正例：`We train the model for 300 epochs.`（作者行为，主动）/ `The data are augmented with random cropping.`（通用流程）
- 反例：`It can be seen that the method works.`（口语化被动）→ `The results show that the method works.`
- 动作：【搜】`we can see|we can observe|it can be seen`，改 `Figure X shows` 或直接陈述结果。

### 7.2 not/never/only 的位置

- 规则：only 紧贴它限定的成分；not 的否定范围默认覆盖全句，放错位置改变语义。
- 正例：`Our method only uses 25% of the parameters.`（仅参数量少）/ `Only our method uses...`（只有本方法）/ `Our method uses only 25%...`
- 反例：`We only evaluate on COCO.`（想表达 only evaluate 还是 only COCO？）
- 动作：【搜】`\bonly\b`，核对位置是否紧贴被限定成分。

### 7.3 respectively 的正确用法

- 规则：respectively 要求两个平行列表一一对应：`A and B are X and Y, respectively.`。单列表不能用；对应关系不明时不能滥用。
- 正例：`The encoder and decoder have 12 and 6 layers, respectively.`
- 反例：`The accuracy and F1 score are high, respectively.`（无对应列表，错）；`Respectively, we first...`
- 动作：【搜】`respectively`，核对两侧是否为等长平行列表；不是则删除或重写。

### 7.4 et al. 与缩写点

- 规则：
  - `et al.` = et alii，al. 后有点；et al. 后不加第二个句号；`Lee et al. (2019) proposed`（et al. 作主语，动词用复数更规范：`Lee et al. (2019) proposed` 亦通行，全文统一）。
  - `i.e.`（= that is）、`e.g.`（= for example）、`cf.`、`viz.`、`w.r.t.`、`a.k.a.`；句尾 et al. 写作 `... by Lee et al.`（不再加点，句号兼缩写点）。
  - i.e. / e.g. 后美式加逗号：`..., e.g., images and videos`。
  - et al. 用于人名三个以上作者；两作者用 `A and B`。
- 正例：`Methods such as ResNet (He et al., 2016) and ViT (Dosovitskiy et al., 2021) ...`
- 反例：`He et al (2016)`（al 缺点）/ `e.g. images`（缺逗号，视期刊）/ `Lee et. al`
- 动作：【搜】`et\. al|et al[^.]`，核对缩写点；【搜】`\b(e\.g\.|i\.e\.) `，核对后逗号全文统一。

### 7.5 引用句式规范

- 规则：`X et al. [12] proposed...` 或 `... (He et al., 2016)`；避免 `In [12], the authors propose...`（可接受但啰嗦）；引用编号前空格规范（LaTeX `~\cite{}` 防断行）。
- 正例：`Diffusion models (Ho et al., 2020) have achieved...`
- 反例：`In paper [12], they proposed...`（they 指代不明）
- 动作：【读】引用作主语时核对指代清楚；LaTeX 中 `\cite` 前加 `~`。

### 7.6 首字母缩略词的 a/an

- 规则：按发音选 a/an：an SVM（/ɛs/）、a U-Net（/juː/）、an LSTM、a CNN。
- 正例：`an SVM classifier` / `a U-Net backbone`
- 反例：`a SVM` / `an U-Net`
- 动作：【搜】`a (SVM|LSTM|SQL|SOTA|FCN|RNN|MLP)`，改 an；【搜】`an (U-Net|UNet|UNI|VIP)`，改 a。

### 7.7 避免绝对化声称

- 规则：不用 proves（数学证明之外用 demonstrates/shows/indicates）；不用 solves/completely solves；不加 the first unless 可验证；避免 significant（无统计检验时用 substantial/considerable）。
- 正例：`Our results demonstrate that...` / `a substantial improvement`
- 反例：`Our method proves that...` / `significant improvement`（无 t-test 时）
- 动作：【搜】`prove(s|d)? (that|the effectiveness)`，改 demonstrates；【搜】`significant` 无统计检验语境的，改 substantial。

### 7.8 hedge 与限定域

- 规则：声称加范围限定（on the benchmarks we tested / in our experiments）；避免全称量词 all, every, always, never。
- 正例：`Our method outperforms baselines on all four benchmarks tested.`
- 反例：`Our method always outperforms all existing methods.`
- 动作：【搜】`\b(always|never|all existing|every)\b`，加限定或改 usually/most。

### 7.9 图表内与正文的一致性

- 规则：Figure/Table 编号连续且被引用；每个 figure/table 至少在正文中被引用一次；图注用完整句（现在时）。
- 正例：`Figure 3: Qualitative results on COCO. Our method recovers finer details.`
- 反例：`Figure 3: Results.`（过简）
- 动作：【读】交叉核对正文 `\ref{fig:...}` 与图表编号；图注是否完整句。

### 7.10 标点：逗号后的连接词、牛津逗号

- 规则：牛津逗号（A, B, and C）在多数 CV/NLP 会议模板中默认使用，全文统一；however/moreover 等句中副词两侧逗号。
- 正例：`accuracy, robustness, and efficiency` / `The model, however, fails to...`
- 反例：`accuracy, robustness and efficiency`（与全文其他列表不一致）
- 动作：【读】抽 3-5 个三项列表核对牛津逗号统一；however 两侧逗号核对。

### 7.11 避免口语化缩写

- 规则：不用 don't, can't, won't, it's, doesn't；写 do not, cannot（一个词）, will not, it is, does not。
- 正例：`The model cannot handle long sequences.`
- 反例：`The model can't handle...` / `can not`（两词错误）
- 动作：【搜】`n't\b|it's\b|can not\b`，改正式写法；`cannot` 一词。

### 7.12 大小写敏感的缩写展开

- 规则：句首缩写展开或重组避免 awkward 大写：`w.r.t.` 尽量换成 `with respect to`（部分会议禁止缩写）。
- 动作：【搜】`w\.r\.t\.|resp\.`，按目标会议规范改全称。

---

## 检查顺序（agent 逐条执行序列）

按「错误频率 x 修改收益」从高到低排序。执行时逐条跑搜索指令，命中后按该条的动作修改。

1. **冠词扫描**（第 1 节全部）：搜 `the ` 逐个核对（1.1-1.7）；搜 `propose .*, (the|an?)`（1.3）；搜 `on (COCO|ImageNet|...)|the (COCO|...)`（1.9）；搜 `the (Figure|Table|Section|Eq\.|Algorithm) \d`（1.10）。
2. **悬垂修饰语**（4.4, 4.5, 4.14）：搜句首 `Using|Given|Compared|Based|Following|When ...ing`，逐一核对主句主语。
3. **不可数名词**（1.5, 3.4）：搜 `researches|informations|evidences|knowledges|a evidence|a research|a software` 等全部命中改写。
4. **连接副词粘连**（4.1, 4.2）：搜 `, however,|, therefore,|, moreover,|, thus,`，检查逗号前是否完整分句。
5. **时态**（第 2 节）：Method 节搜过去式核对（2.3）；Experiments 节核对实验动作用过去时（2.4）；搜 `Figure \d+ (showed|presented)`（2.5）；搜 `have (proposed|introduced|presented) .* \d{4}`（2.2）。
6. **主谓一致**（3.2, 3.3, 3.7, 3.8）：搜 `number of|Each of|There (is|are)`，逐一核对。
7. **介词搭配**（5.1, 5.5, 5.8）：搜 `results? to|depends? of|different with|discuss about|emphasize on|increases? \d`，逐个修正。
8. **respectively**（7.3）：搜 `respectively`，核对平行列表。
9. **拉丁复数**（3.5）：搜 `phenomenons|criterias|matrixes`，改正确复数形。
10. **平行结构**（4.6, 4.7）：搜 `both|not only|either` 及三项列表，核对一致性。
11. **which 指代**（4.8, 4.9）：搜 `, which`，核对先行词无歧义；搜 `, that`，改写。
12. **it 形式主语与冗余**（4.10, 6.10, 6.11）：搜 `It is (worth|obvious|important)|perform an analysis|As we all know|in order to`，改写。
13. **缩写定义**（6.8, 7.6, 7.12）：全文抽每个缩写核对首现定义；搜 `a (SVM|LSTM)` 核对 a/an。
14. **大小写与排版**（6.6, 6.7）：搜 `\bfigure \d|table \d|section \d`，改大写；核对 % 空格、小数前导 0、单位空格统一。
15. **连字符**（6.9）：搜 `end to end|real time|state of the art`，核对定语连字符。
16. **用词替换**（6.2, 6.3, 6.4, 6.5, 6.12）：搜 `less (parameters|samples)|more parameters`、`affect/effect` 词性、`comprise of|is comprised`、口语词。
17. **绝对化声称与 hedge**（7.7, 7.8）：搜 `prove|significant|always|never|all existing`，加限定或降级动词。
18. **we vs passive 与口语化**（7.1, 7.11）：搜 `we can see|it can be seen|can't|don't|can not`，改写。
19. **标点统一**（7.10）：抽核对牛津逗号、however 双逗号。
20. **图表引用完整性**（7.9, 2.5）：核对每个 Figure/Table 至少被引用一次、编号连续、图注完整句。

每完成一条，记录命中数与修改数；无法机械判定的（标【读】的条目）读上下文后人工判断，不要猜。
