# 注释规范

一句话：**注释只解释 why，不解释 what、不解释 how。**

## 核心规则

### 1. 自包含 + 只讲 why

所有注释都应**自包含**。

- **不要**解释你是怎么做的
- **不要**解释这段代码块**做了**什么
- **只**解释我们**为什么**要这么做

注释要**精简**。如果它不是在解释 why，**就删掉**。按这个标准，**大部分 AI 写的注释都该删**。

### 2. 署名

给自己的注释加上名字，格式：

```python
# note (gaoyang):
```

真实用例：

```python
# Note (Chenyang): As a general comment and my usual understanding
# of SGLang Omni, SGLang Omni has a poor runtime which leads to a
# underutilized GPU/SMs. To address this, we recommend users to set
# batchs for your compute but never wait for grouping the batchs.
# As SGLang Omni Runtime moves better, we shall probably wait several
# ms for grouping the batchs, but right now, set it to 0.0.
```

### 3. 禁止反引号

**Python 的 inline comment 和 docstring 里都不能用 `` ` ``。**

坏：

```python
# Speaker-timestamp DER (diarization error rate, already a percentage in the
# result JSON). None until the first DER calibration fills in the reference.
MOSS_TD_SPEAKER_TIMESTAMP_DER_PERCENT_REF: float | None = 20.975903756491164
```

—— 这段的问题不只是没解释 why，还在于它花了四行说明"N 是什么"这种看名字就知道的事。

坏（docstring）：

```python
"""Valid frame counts after the encoder's stride-2 ``conv2``."""
```

好：

```python
"""Valid frame counts after the encoder's stride-2 conv2."""
```

坏（inline）：

```python
    Emits OpenAI-style ``transcript.text.delta`` events for each partial text
    chunk, then a terminal ``transcript.text.done`` event carrying the full
    post-processed transcript.
```

好：

```python
    Emits OpenAI-style transcript.text.delta events for each partial text
    chunk, then a terminal transcript.text.done event carrying the full
    post-processed transcript.
```

### 4. 文件与类级别的禁令

- **不要在文件开头写注释。**
- **类定义后不要写超长注释**解释各类元素。用简单的注释说明就行。
- 每个文件最多**一行**简短的模块 docstring。

---

## 好的注释长什么样

```python
# Note (chenyang): AISHELL4-long runs only 20 samples, so a single straggler
#  or a flipped orderline sample moves the aggregate metrics far more than
# the 800-sample movies800 corpus. Widen its slack accordingly.
AISHELL4_LONG_THRESHOLD_SLACK_HIGHER = 0.8
AISHELL4_LONG_THRESHOLD_SLACK_LOWER = 1.2
```

为什么这段好：它解释了**为什么是这个数值**——样本量小导致单个样本波动大，所以放宽阈值。这是从代码本身绝对读不出来的信息。而且它**带署名**、**无反引号**、**没有解释什么是 slack**。

对比坏的：

```python
# Speaker-timestamp DER (diarization error rate, already a percentage in the
# result JSON). None until the first DER calibration fills in the reference.
MOSS_TD_SPEAKER_TIMESTAMP_DER_PERCENT_REF: float | None = 20.975903756491164
MOSS_TD_CER_VALID_SAMPLES_MIN: int | None = 784
MOSS_TD_CP_CER_VALID_SAMPLES_MIN: int | None = 784
```

为什么这段坏：它在解释**是什么**。看名字就知道这是 DER 百分比、这是有效样本数下限。至于 `20.97` 这个魔数**从哪来的**、为什么是 `784`——真正需要解释的东西——一个字没有。

---

## Docstring 规范

- **Google 风格，1–3 行。**
- `Args`/`Returns` **只在非显而易见时**才写。
- 每个文件一个简短的模块 docstring。
- 不用反引号。

```python
def encode(
    self,
    tokenizer: PreTrainedTokenizerFast,
    ignore_loss_tokens: list[str] | None = None,
) -> EncodedMessage:
    """Encode messages into token ids with a loss mask.

    Loss is computed on assistant turns only; tool results are masked out.
    """
```

---

## 禁止的注释标记

以下标记一律禁止出现在源码注释里：

| 类别 | 禁止项 |
|---|---|
| 进程标记 | `★`、`# P1`、`# [FIX]`、无 ticket 的 `# TODO`、`# === SECTION ===` banner |
| 日志前缀 | 手工的 `[Info]`、`[Warn]`、`[step N]`（level 字段已经说明了） |
| 来源泄漏 | 源码里提及其他 repo、upstream、"the closed source" |
| 冗长 rationale | why 属于设计文档 / commit message / PR 描述，不属于源码行间 |
| 复述代码 | 任何"这段在做什么"的注释 |
| 语言 | 中文注释 |

## 例外与边界

- **`# noqa: <code>` 允许，但必须带理由。** 光秃秃的 `# noqa` 不行。
- **长期 workaround 用一行注释说明约束**，不要写十行块。
- **经验常数必须带来源注释**：
  ```python
  DECODE_TOKS_PER_SEC = 6.7  # measured on H20; used to estimate rollout time
  ```
- **forward pass 里为了极致内存优化做的就地操作**，必须写显式注释说明。

## 自查

对每一行注释问一句：

> **一个懂这个领域的读者，还需要这条注释吗？**

不需要 → **删掉**。
