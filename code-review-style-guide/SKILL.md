---
name: code-review-style-guide
description: 严格的编码规范，写代码和改代码时必须遵守。适用于任何新建函数/类/模块、重构、清理 AI 生成代码或他人代码、写单测、补类型标注、整理注释与日志的场景，也适用于需要一份可直接粘贴进项目 CLAUDE.md 的编码规范时。核心是简洁：不写只被调用一次的 helper、不做过度防御、不用 Any 或 getattr 糊弄类型、注释只讲 why、常量定义在使用处。含 P0–P4 规范、八类高频错误的改前改后对照、注释规则，以及能扫出机械反模式的脚本。命中以下任一信号就必须加载：要写或改 .py 文件、问"这段代码怎么写"、要求重构或清理代码、写新的函数或类、被指出代码风格问题。
agent_created: true
---

# code-review-style-guide

一套**严格的**编码规范。默认立场不是"代码能跑就行"，而是"代码必须是成熟、结构良好的生产级代码"。

北极星只有一条：**简洁** —— 写更少，而不是更多。

## 怎么用这份规范

**写新代码前**：读下面的「写代码时的默认动作」。它覆盖了 $90\%$ 的日常决策。

**写一个具体模块时**：对照 `references/anti-patterns.md` 的八条。这八条是实战中出现频率最高的，比 P0–P4 里的任何单条都更容易踩。

**收尾前**：跑一遍自查命令（见下），再过一遍「交付前自查」清单。

**被人 review 或 review 别人时**：`references/style-guide.md` 是逐条对照用的 canonical 全文。

## 写代码时的默认动作

这一节是整个 skill 的核心。写代码的过程中反复回到这里。

### 先想清楚要不要写这个函数

每写一个函数、helper、包装层或抽象，先问：**它当下就至少有两处调用吗？它真的让调用点更清楚吗？**

答案是否的话就不要写。投机的通用化全是噪音。

这条是最容易违反的一条，因为 AI 天生爱抽 helper。一个 $60$ 行自顶向下、一眼读完的函数，永远好过三个各 $20$ 行、各被调用一次的 `_step_one/_two/_three`。

```python
# 坏：三个函数各只有一个调用点，串成一条链
def _load_json(path): ...
def _parse_config(raw): ...
def _validate(c): ...

def main():
    c = _validate(_parse_config(_load_json(cfg_path)))
```

```python
# 好：四行，自上而下，一眼读完
def main():
    with open(cfg_path, encoding="utf-8") as f:
        c = Config(**json.load(f))
    assert c.lr > 0
```

### 不要写过度防御

**这是 AI 生成代码最典型的病灶，也是这套规范最想根除的一条。**

不要用 `try/except` 去防几乎不会发生的事。不要为这种防御写单测。**只守主路径上真会发生的错。**

每个 `try/except` 和防御性 `if`，写的时候都问一句：**删掉它会坏什么？**

答案是"不会，那是调试用的"——那就别写。

```python
# 坏：三层防御，防的都是不存在的情况
def encode(tokens, model):
    try:
        out = model(tokens)
    except Exception as e:
        logger.warning(f"model failed: {e}")
        out = torch.zeros_like(tokens, dtype=torch.float32)
    if out is None:            # model 从不返回 None
        out = torch.zeros_like(tokens, dtype=torch.float32)
    if not isinstance(out, torch.Tensor):   # model 返回的就是 Tensor
        out = torch.tensor(out)
    return out
```

```python
# 好
def encode(tokens: torch.Tensor, model: nn.Module) -> torch.Tensor:
    return model(tokens)
```

要删的防御性脚手架：为对齐 AllReduce 加的 dummy forward、logger 的 enable/disable 体操、类型强制转换循环、宽泛的 `try/except` 吞错。**这些是债，不是安全。**

### 不要用类型系统糊弄自己

- **不写 `Any`。** 写了就等于放弃类型检查。
- **不用 `getattr`/`hasattr`。** 类型已确定的字段直接读，缺了就该炸。
- **不用 `if TYPE_CHECKING:` 把本该开篇 import 的东西藏起来骗过 linter。** 唯一豁免是真正的类型层循环依赖。
- **不要把参数删掉装作用了**：传进来 `request_id`，第一行 `del request_id`，非常无理。要么用，要么从签名里移除。

```python
# 坏
def solve_flow_euler(decoder, x, t_span, mu, mask, spks, cond, ...): ...
def _flow_lookahead(flow: Any) -> int:
    layer = getattr(flow, "pre_lookahead_layer", None)
    ...

# 好
def solve_flow_euler(
    decoder: ConditionalCFM,
    noisy_mel: torch.Tensor,
    time_span: torch.Tensor,
    token_condition: torch.Tensor,
    mel_mask: torch.Tensor,
    speaker_embedding: torch.Tensor,
    prompt_mel: torch.Tensor,
) -> torch.Tensor: ...

if finalize:
    lookahead = 0
else:
    lookahead = flow.pre_lookahead_len
```

### 名字要说出它是什么

名字表达真实的科学/物理含义，不是随便一个短标识符。

| 别写 | 写成 | 因为 |
|---|---|---|
| `x` / `z` | `noisy_mel` | 它是 ODE 上的带噪 mel |
| `mu` | `token_condition` | token hidden 对齐到 mel |
| `spks` | `speaker_embedding` | 说话人 |
| `cond` | `prompt_mel` | prompt 条件 mel |
| `frames` | `mel_frame` | 和第 2 维 T 一致 |
| `compute_dtype` | `autocast_dtype` | 是 `torch.autocast` 的 dtype |

单字母只允许用在循环下标（`i`、`j`）或数学符号（`x`、`y`、`t`）。

另外：不用没有限定的 `data`、`result`、`info`、`tmp`、`manager`、`handler`。布尔量加 `is_`/`has_`/`should_`/`can_`。成对命名保持一致（`start/stop`，不要 `start/finish`）。

### 控制流：检查提前做，分支要完整

**有 `if` 给变量赋值或返回值，就必须带 `else`。** 但不要堆 `if/else` —— 把和主逻辑无关的检查提前做完，用一层 `if/elif/else` 收口。

Guard clause（早返回、早 raise、early continue）不需要 `else`。

```python
# 坏：一层层 if return None，后面还挂 else
captured = self.graphs.get((batch_size, bucket_frames))
if captured is None:
    return None
if any(...):
    return None
if not self._matches(...):
    return None
# replay
```

```python
# 好：先把秩和最后一维查完，再一层收口
frame_inputs = (noisy_mel, token_condition, mel_mask, prompt_mel)
if noisy_mel.ndim != 3:
    return None
elif any(value.ndim == 0 or value.shape[-1] != int(noisy_mel.shape[2]) for value in frame_inputs):
    return None
else:
    captured = self.graphs.get((batch_size, bucket_mel_frame))
    ...
```

### 注释只讲 why

写注释前先问：**一个懂这个领域的读者，还需要这条注释吗？**

不需要就不要写。解释"这段代码做了什么"、"我是怎么实现的"的注释，一律删掉——那是 AI 注释最典型的特征。

```python
# 坏：四行，全在说 N 是什么，看名字就知道
# Speaker-timestamp DER (diarization error rate, already a percentage in the
# result JSON). None until the first DER calibration fills in the reference.
MOSS_TD_SPEAKER_TIMESTAMP_DER_PERCENT_REF: float | None = 20.975903756491164

# 好：解释了为什么是这个数——这是代码里读不出来的
# Note (chenyang): AISHELL4-long runs only 20 samples, so a single straggler
#  or a flipped orderline sample moves the aggregate metrics far more than
# the 800-sample movies800 corpus. Widen its slack accordingly.
AISHELL4_LONG_THRESHOLD_SLACK_HIGHER = 0.8
```

配套的硬规则（完整版见 `references/comment-rules.md`）：

- **给自己写的注释署名**：`# Note (yourname):`
- **注释和 docstring 里不用反引号 `` ` ``**
- **不写文件头注释**；类定义后不写超长注释
- docstring 走 Google 风格，$1$–$3$ 行
- 禁止：`★`、`# P1`、`# [FIX]`、无 ticket 的 `# TODO`、`# === 分节 banner ===`、手工日志前缀 `[Info]`

### 日志

- **统一用 f-string**：`logger.info(f"Loading model: {path}")`，不要 `%s` 占位。
- **不加手工前缀**：`[Info]`、`[Warn]` —— level 字段已经说了。
- 一个模块一个 logger，一个 repo 一种日志库。
- `print` 只用于终端用户会读的 CLI 输出。

### 别把常量搬来搬去

**只在一个地方用的常量，就定义在用的地方。** 不要为了"集中管理"把它放到 `config.py`，再从使用处 import 一次。

**参数自顶向下传递。** 不要在底层用模块级常量把高层已经传下来的默认值再写一遍——那个副本在高层的默认 config 面前就是小丑。

```python
# 坏：stages.py 把 config 里的默认值又抄了一遍
CODE2WAV_MAX_BATCH_SIZE = 8
CODE2WAV_MAX_BATCH_WAIT_MS = 0.0

# 好：真值在高层 config 里，往下传
def code2wav_stage(*, gpu: int, process: str) -> StageConfig:
    return StageConfig(factory=FactoryArgs(max_batch_size=8, max_batch_wait_ms=0.0))
```

### `_` 前缀只给函数内部的嵌套函数

模块级、类级名字正常写。不要给所有东西都加 `_`。

```python
# 坏
class _FlowCudaGraphRunner:
    def _capture_inputs(...): ...

def _generate_flow(...): ...

# 好
class FlowCudaGraphRunner:
    def capture_inputs(...): ...

def generate_flow(...): ...
```

### import 放在文件开篇

**尽量避免 lazy import。** 函数内 import 只留给重型可选依赖和已文档化的循环依赖破解。

顺序 stdlib → third-party → local，段间空行。绝不用 `from module import *`。

## 八类高频错误速查

命中率高于 P0–P4 里的任何一条。完整改前/改后对照见 `references/anti-patterns.md`。

| # | 病症 | 判据 |
|---|---|---|
| 1 | 函数过度碎片化 | 只被调用一两次的短函数，inline 回调用点 |
| 2 | 到处 `_` | 只有函数内部的嵌套函数用 `_` |
| 3 | 过度防御 | 只守主路径上真会发生的错 |
| 4 | 常量跨文件只 import 一次 | 只在一处用的常量定义在用它的地方 |
| 5 | 用 `Any` 绕开类型检查 | 写真实类型 |
| 6 | 名字没有物理含义 | `x`/`mu`/`cond` → `noisy_mel`/`token_condition`/`prompt_mel` |
| 7 | 有 `if` 必须有 `else` | 同时把检查提前做，少嵌套 |
| 8 | `getattr`/`hasattr` | 类型已确定的字段直接读 |

## P0–P4 速查

优先级：**正确性 (P0) > 性能 (P1) > 可维护性 (P2) > 风格 (P3) > 流程 (P4)**。

| 级别 | 主题 | 一句话 |
|---|---|---|
| **P0** | 正确性 | Fail fast；不过度防御；不过度 catch；锁范围最小；锁内不做 I/O 和 GPU 操作；资源用 context manager；缓存有界 |
| **P1** | 性能 | 推理路径禁 `.item()`/`.cpu()`/`.tolist()`；GPU 数据保持向量化；热路径消灭 Python 层开销 |
| **P2** | 可维护性 | 重复 >$5$ 行抽函数；文件 >$2000$ 行拆分；函数尽量 ≤$50$ 行；命名无缩写、布尔带前缀、成对命名对称；导入分三段；无魔数 |
| **P3** | 风格 | 优先纯函数；避免就地改入参；构造函数精简；禁 `getattr/setattr`；分支完整；公开 API 全类型标注；删调试注释、删中文注释 |
| **P4** | 流程 | 给可复制粘贴的验证脚本；重要功能加单测；测契约不测内部状态；固定随机种子；一个测试函数一个概念一个断言 |

完整版见 `references/style-guide.md`。写代码时按需查，收尾时逐条过。

## 交付前自查

写完之后跑这几步，**不要跳过**。

**第一步，跑脚本。** 它扫的是能机械识别的反模式：只被调用一次的私有函数、函数内 import、裸 except / 宽 except、可变默认参数、被自己 `del` 掉的参数、注释里的反引号、`getattr`、`Any` 标注、注释里的中文。

```bash
python3 scripts/lint_review.py path/to/your_file.py     # 单个文件
python3 scripts/lint_review.py src/                     # 整个目录
git diff | python3 scripts/lint_review.py --diff -      # 只看本次改动
```

退出码非 $0$ 就是有发现。**脚本干净不等于代码好**——它抓不到意图、抓不到抽象是否值得存在、抓不到你的实现有没有达成目标。它只是把你的注意力省下来给这些真正需要判断的事。

**第二步，过清单。** 逐条问自己：

- 有没有只被调用一次的 helper？→ inline 掉
- 有没有 `try/except` 或 `if isinstance / if x is not None` 链，防的是不存在的失败模式？→ 删掉
- 有没有 `Any`、`getattr`、裸 `dict`/`list` 标注？→ 换成真实类型
- 每一个私有函数，被调用超过一次吗？→ 不是就 inline
- 每一条注释，领域读者还需要它吗？→ 不需要就删
- 有没有硬编码路径/URL、`sys.path` hack、魔数、可变默认参数？→ 修掉
- `Optional[X]` 和 `X | Y` 混用了吗？→ 统一
- 有没有死代码：不可达分支、未使用参数、注释掉的代码块、过期 TODO？→ 删掉
- 新逻辑有测试吗？→ 补上

**第三步，跑工具链。** 有 ruff / pyright 就跑到干净。至少 `python -m py_compile` 一遍。

## 成熟度：规范不是一刀切

| 阶段 | 允许什么 |
|---|---|
| 原型期 | 围绕你还不信任的调用写 `try/except` 是可以的 |
| 成熟期 | **把它删掉。** 信任你的不变量，让失败以栈回溯的形式暴露 |

写正式代码时按**成熟期**标准来。长期 workaround 用一行注释说明约束，不要写十行。

## 训练代码的特殊约定

训练代码分为 **`train` 和 `trainer` 两个脚本**：把训练相关的函数封装到 `trainer` 里，`train` 只负责调用 `trainer` 进行循环。

## 语言

规范正文是中文，但**代码里的注释、docstring、日志、CLI help 一律英文**。这是规范本身的要求，两者不矛盾。

## 文件索引

| 文件 | 内容 |
|---|---|
| `references/style-guide.md` | P0–P4 规范全文（canonical） |
| `references/anti-patterns.md` | 八类高频错误的改前/改后完整对照，含 CUDA Graph、Flow Matching 真实案例 |
| `references/comment-rules.md` | 注释规范：why-not-what、署名、禁用标记、docstring、文件头禁令 |
| `scripts/lint_review.py` | 反模式静态扫描器，退出码可作 CI 门禁 |
| `scripts/test_lint_review.py` | 回归测试：坏样本要检出，好样本必须零误报 |
| `scripts/fixtures/good.py` | 符合规范的可运行样板，写代码时可参考它的结构 |
