# 八类高频错误对照

写代码时最容易踩的八条，每条给出**判据**、**改前**、**改后**。案例取自真实的 Flow Matching / CUDA Graph 代码，但判据本身是 repo 无关的。

**写的时候就对着改后那栏写。** 不要先写完再回头清理——中途生成的坏模式会残留。

---

## 1. 函数过度碎片化

**判据**：只被调用一两次的短函数不要独立出去，inline 回调用点。嵌套函数可以留（见 #2）。

每写一个 `_helper`/`_impl`，先问：**它当下就至少有两处调用吗？它真的让调用点更清楚吗？** 两个都答"是"才写。投机的通用化是噪音。

判据的完整表述：**除非当下就被复用、或者长到一屏读不完，否则不要预先抽 helper。**

### 改前

```python
def _flow_t_span(decoder, *, device, dtype):
    t_span = torch.linspace(0, 1, 11, device=device, dtype=dtype)
    if decoder.t_scheduler == "cosine":
        t_span = 1 - torch.cos(t_span * 0.5 * torch.pi)
    return t_span


def _align_flow_cuda_graph_frames(frames: int) -> int:
    return (frames + 15) // 16 * 16


# 调用点
t_span = _flow_t_span(decoder, device=mu.device, dtype=mu.dtype)
bucket_frames = _align_flow_cuda_graph_frames(actual_frames)
```

### 改后

直接写在 `generate_flow` / `run()` 里：

```python
unit_span = torch.linspace(0, 1, 11, device=token_condition.device, dtype=token_condition.dtype)
if decoder.t_scheduler == "cosine":
    time_span = 1 - torch.cos(unit_span * 0.5 * torch.pi)
else:
    time_span = unit_span

bucket_mel_frame = (
    (actual_mel_frame + FLOW_CUDA_GRAPH_FRAME_BUCKET - 1)
    // FLOW_CUDA_GRAPH_FRAME_BUCKET
    * FLOW_CUDA_GRAPH_FRAME_BUCKET
)
```

**同类名单**：`_flow_device_and_dtype`、`_flow_lookahead`、`_apply_pre_lookahead`、`_forward_flow_estimator` —— 全部 inline。

**注意**：嵌套函数可以保留。factory 里的 `_chunk_mask` 只给这一次 capture 用，用 `_` 开头即可（见 #2）。

### 更极端的例子

```python
# 坏：三个只有一个调用点的函数，串成一条链
def _load_json(path: Path) -> dict:  # called once
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _parse_config(raw: dict) -> Config:  # called once
    return Config(**raw)


def _validate(c: Config) -> None:  # called once
    assert c.lr > 0


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

---

## 2. 不要到处 `_`

**判据**：模块级、类级名字正常写。**只有函数内部的嵌套函数**用 `_` 开头。

### 改前

```python
class _FlowCudaGraphRunner:
    def __init__(...):
        self._flow = flow
        self._graphs = {}

    def _capture_inputs(...): ...
    def _right_pad_time(...): ...


def _generate_flow(...): ...
def _pack_flow_inputs(...): ...
```

### 改后

```python
class FlowCudaGraphRunner:
    def __init__(...):
        self.flow = flow
        self.graphs = {}

    def capture_inputs(...): ...
    def right_pad_mel_frames(...): ...


def generate_flow(...): ...
def pack_flow_inputs(...): ...
```

`streaming_vocoder` 里对应变成 `self._vocoder.hift_delta(...)`，不再是 `_hift_delta`。

> 与 P3"类/文件内部函数用 `_private` 前缀"的调和：`_` 表达"不对外"，但**不要把所有东西都标成不对外**。真正对外的 API 就是对外。默认公开，只在确实需要标记内部性时加 `_`。

---

## 3. 过度防御（Over defensive）

**判据**：不要用大 `try/except` 去防几乎不会发生的事，**更不要为这种防御写单测**。只守主路径上真会发生的错。

**这是 AI 生成代码最典型的病灶。** 写每个 `try/except` 和防御性 `if` 时都问一句："删掉它会坏什么？"

### 改前

replay 包一层 `Exception`，失败还清掉整张表；capture 失败 warning 后偷偷退到 eager：

```python
try:
    captured.graph.replay()
    return captured.static_output[..., :actual_frames].clone()
except Exception:
    self._graphs.clear()
    logger.exception("... disabled all Flow CUDA graphs")
    raise

# factory
try:
    runner.capture(capture_shapes)
except Exception as exc:
    logger.warning("startup failed ... using the normal solver")
else:
    flow.attach_cuda_graph_runner(runner)
```

还配套了 `test_replay_failure_clears_resident_graphs`、`test_flow_solve_observability.py`。

### 改后

replay 失败原样抛；shape miss 返回 `None` 再走 Euler。**这才是主路径**：

```python
captured.graph.replay()
return captured.static_output[..., :actual_mel_frame].clone()
```

`next(flow.parameters())` 外包 `AttributeError` 也属于这类——CosyVoice Flow 一定有参数，直接 `next(...)`。

### 成熟代码还在背调试脚手架的例子

```python
# 坏：三层防御，防的都是不存在的情况
def encode(tokens, model):
    try:
        out = model(tokens)
    except Exception as e:
        logger.warning(f"model failed: {e}")  # 失败时静默返回全零
        out = torch.zeros_like(tokens, dtype=torch.float32)
    if out is None:  # model 从不返回 None
        out = torch.zeros_like(tokens, dtype=torch.float32)
    if not isinstance(out, torch.Tensor):  # model 返回的就是 Tensor
        out = torch.tensor(out)
    return out
```

```python
# 好
def encode(tokens: torch.Tensor, model: nn.Module) -> torch.Tensor:
    return model(tokens)
```

**要删的防御性脚手架清单**（规范原文列举）：

- 为对齐 AllReduce 的 dummy forward
- logger 的 enable/disable 体操
- 类型强制转换循环
- 宽泛的 `try/except` 吞错

这些是**债，不是安全**。

---

## 4. 常量不要跨文件只 import 一次

**判据**：只在一个地方用的常量，就定义在用的地方。减少莫名其妙的跨模块 import。

### 改前

`config.py` 定义表，`stages.py` 再 import 一次当 `None` 的默认值：

```python
# config.py
FUN_COSYVOICE3_DEFAULT_FLOW_CUDA_GRAPH_CAPTURE_SHAPES = ((1, 304), ...)


# stages.py
from sglang_omni.models.fun_cosyvoice3.config import (
    FUN_COSYVOICE3_DEFAULT_FLOW_CUDA_GRAPH_CAPTURE_SHAPES,
)


def _resolve_flow_cuda_graph_capture_shapes(capture_shapes, *, max_batch_size):
    if capture_shapes is None:
        capture_shapes = FUN_COSYVOICE3_DEFAULT_FLOW_CUDA_GRAPH_CAPTURE_SHAPES
```

### 改后

表只活在 `config.py`，**config 传进来**。`stages.py` 只 verify 传入的 tuple，不再 import 那张表。

`FLOW_CUDA_GRAPH_FRAME_BUCKET = 16` 只在 `stages.py` 用，就定义在 `stages.py`。

### 相关：参数要自顶向下传递

不要在底层用常量把高层传下来的默认参数再写一遍。

```python
# sglang_omni/models/minicpm_o/stages.py —— 坏：底层又定义了一遍
CODE2WAV_MAX_BATCH_SIZE = 8
CODE2WAV_MAX_BATCH_WAIT_MS = 0.0
CODE2WAV_BATCH_WAIT_WHEN_IDLE = False
```

```python
# sglang_omni/models/minicpm_o/config.py —— 好：真值在高层 config 里
def code2wav_stage(*, gpu: int, process: str) -> StageConfig:
    return StageConfig(
        name="code2wav",
        process=process,
        factory_path=f"{PKG}.stages.create_code2wav_executor",
        factory=FactoryArgs(
            max_batch_size=8,
            max_batch_wait_ms=0.0,
            batch_wait_when_idle=False,
        ),
        # Note (Chenyang): As a general comment and my usual understanding
        # of SGLang Omni, SGLang Omni has a poor runtime which leads to a
        # underutilized GPU/SMs. To address this, we recommend users to set
        # batchs for your compute but never wait for grouping the batchs.
        # As SGLang Omni Runtime moves better, we shall probably wait several
        # ms for grouping the batchs, but right now, set it to 0.0.
        gpu=gpu,
        terminal=True,
    )
```

**前面的常量在高层的默认 config 面前就是小丑。**

---

## 5. 不要用 `Any` 混过类型检查

**判据**：`Any` 是糊弄 pre-commit，不是类型。写真实类型。**写代码时就不要起这个头**——事后补类型比一开始就写对贵得多。

### 改前

```python
def _generate_flow(flow: Any, packed: _PackedFlowBatch, ...): ...


class _FlowCudaGraphRunner:
    def __init__(self, flow: Any, *, compute_dtype: torch.dtype | None): ...
```

### 改后

写成真实对象：

```python
def generate_flow(flow: FunCosyVoice3Flow, packed: PackedFlowBatch, ...): ...


class FlowCudaGraphRunner:
    def __init__(
        self,
        flow: FunCosyVoice3Flow,
        *,
        autocast_dtype: torch.dtype | None,
    ) -> None: ...


self.pool: tuple[int, int] | None = None  # graph_pool_handle() 返回的就是 (device, pool id)
```

Euler 的 decoder 是 `ConditionalCFM`，内层 CosyVoice 模块是 `CausalMaskedDiffWithDiT`。

**不要糊弄类型检查的另一种形态**：

```python
# 坏：传入了 request_id，函数第一行就 del 掉，非常无理
def decode_delta(
    self,
    request_id: str,
    state: CosyVoice3StreamState,
    *,
    is_final: bool,
) -> torch.Tensor | None:
    del request_id
```

---

## 6. 名字要有物理含义

**判据**：名字要表达其真实的科学/物理含义，不要随便用不表达含义的名字。

### 改前

`x` / `z` / `mu` / `spks` / `cond` / `frames` / `compute_dtype`：

```python
def solve_flow_euler(decoder, x, t_span, mu, mask, spks, cond, ...):
    ...
z = decoder.rand_noise[:, :, :max_mel]...
generated = cuda_graph_runner.run(z, t_span, mu, mask, embedding, cond)
```

### 改后

| 旧 | 新 | 含义 |
|---|---|---|
| `x` / `z` | `noisy_mel` | ODE 上的带噪 mel |
| `mu` | `token_condition` | token hidden 对齐到 mel |
| `spks` | `speaker_embedding` | 说话人 |
| `cond` | `prompt_mel` | prompt 条件 mel |
| `frames` | `mel_frame` | 和第 2 维 T 一致 |
| `compute_dtype` | `autocast_dtype` | `torch.autocast` 的 dtype |

**单字母只允许**用在循环下标（`i`、`j`）或数学符号（`x`、`y`、`t`）。

---

## 7. 有 `if` 必须有 `else`；检查提前做，少嵌套

**判据**：如果一个 `if` 给变量赋值或返回值，必须带 `else`。但**不要堆 `if/else`**——把类型和数据检查提前做完，用一层 `if/elif/else` 收口。Guard clause（早返回/raise/continue）不需要 `else`。

### 改前

`run()` 先查表，再一层层 `if return None`，后面还挂 `else`：

```python
captured = self._graphs.get((batch_size, bucket_frames))
if captured is None:
    return None
if any(...):
    return None
if not self._matches(...):
    return None
# replay
```

### 改后

和 graph 无关的秩 / 最后一维先做完，再用一层 `if/elif/else`：

```python
frame_inputs = (noisy_mel, token_condition, mel_mask, prompt_mel)
if noisy_mel.ndim != 3:
    return None
elif any(value.ndim == 0 or value.shape[-1] != int(noisy_mel.shape[2]) for value in frame_inputs):
    return None
else:
    captured = self.graphs.get((batch_size, bucket_mel_frame))
    ...
```

`generate_flow` 里 cosine / 线性时间网格也是完整分支——不要写完 `linspace` 再单独跟一个没有 `else` 的 `if cosine`。

---

## 8. 不要 `getattr` / `hasattr`

**判据**：类型已经确定的字段，直接读。**缺了就该炸。**

### 改前

```python
def _flow_lookahead(flow: Any) -> int:
    layer = getattr(flow, "pre_lookahead_layer", None)
    layer_len = getattr(layer, "pre_lookahead_len", None)
    if layer_len is not None:
        return max(int(layer_len), 0)
    return max(int(getattr(flow, "pre_lookahead_len", PRE_LOOKAHEAD_LEN)), 0)


if hasattr(torch._dynamo.config, "cache_size_limit"):
    torch._dynamo.config.cache_size_limit = 1024
```

### 改后

```python
if finalize:
    lookahead = 0
else:
    lookahead = flow.pre_lookahead_len

torch._dynamo.config.cache_size_limit = 1024
torch._dynamo.config.accumulated_cache_size_limit = 1024
```

---

## 9. 统一用 f-string 写日志

### 改前

```python
logger.info(
    "Loading %s config=%s split=%s revision=%s from HuggingFace ...",
    repo_id,
    config_name or "default",
    split,
    revision or "default",
)
```

### 改后

```python
logger.info(f"Loading {repo_id} config={config_name or 'default'} split={split} revision={revision or 'default'} from HuggingFace ...")
```

**日志不要手工加前缀**：

```python
# 坏
logger.info(f"[Info] loading model: {path} (~43s)")
logger.warning("[Warn] judge unavailable! reward will be all 0, no training signal.")
```

```python
# 好：level 字段已经说明了级别
logger.info(f"Loading model: {path} (~43s)")
logger.warning("Judge unavailable; reward will be 0, no training signal.")
```

---

## 10. 注释里不能有反引号 `` ` ``

### 改前（docstring）

```python
"""Valid frame counts after the encoder's stride-2 ``conv2``."""
```

### 改前（inline comment）

```python
    Emits OpenAI-style ``transcript.text.delta`` events for each partial text
    chunk, then a terminal ``transcript.text.done`` event carrying the full
    post-processed transcript.
```

### 改后

```python
"""Valid frame counts after the encoder's stride-2 conv2."""
```

```python
    Emits OpenAI-style transcript.text.delta events for each partial text
    chunk, then a terminal transcript.text.done event carrying the full
    post-processed transcript.
```

---

## 11. 不要用 `if TYPE_CHECKING:` 糊弄 lint

### 改前

```python
if TYPE_CHECKING:
    from sglang_omni.models.minicpm_o.components.token2wav.vocoder import SpeakerPrompt
```

### 改后

在文件开篇 import。

> **唯一豁免**：真正的类型层循环依赖。此时用 `if TYPE_CHECKING:` + 使用点的字符串引号（`"ModelConfig"`）。判据是"不这样写就会循环导入"，不是"这样写 linter 就不报错"。

---

## 12. 参数要自顶向下传递

见 #4 的"相关"一节。总结：**不要在底层用常量重复一遍高层传下来的默认参数。**

---

## 13. 尽量避免 lazy import

**判据**：在文件开篇 import。函数内 import 只保留给重型可选依赖和已文档化的循环依赖破解。

### 改前

```python
def create_sglang_talker_executor_from_config(
    model_path: str,
    *,
    gpu_id: int = 0,
    tp_rank: int = 0,
    tp_size: int = 1,
    nccl_port: int | None = None,
    max_seq_len: int = 4096,
    server_args_overrides: dict[str, Any] | None = None,
    total_gpu_memory_fraction: float | None = None,
) -> OmniScheduler:
    """Returns OmniScheduler for the native sglang MiniCPM-o talker."""
    from sglang.srt.arg_groups.model_override_base import resolved_view

    from sglang_omni.models.minicpm_o.bootstrap import create_talker_scheduler
    from sglang_omni.models.minicpm_o.hf_config import register_minicpm_o_hf_config
    from sglang_omni.scheduling.generation_batch_policy import (
        build_generation_batch_overrides,
        validate_generation_batch_policy,
    )
    from sglang_omni.scheduling.sglang_backend.server_args_builder import (
        build_sglang_server_args,
    )
    from sglang_omni.utils.misc import avail_gpu_mem
```

### 改后

这些全部提到文件开篇。

---

## 附：注释类反模式

**先记住总则：注释只讲 why。写之前问一句——一个懂这个领域的读者，还需要这条注释吗？**

```python
# 坏：★ 标记、`# P1` 标记、section banner、冗长的 rationale
# ★ Disable loralib auto-merge, switch to rsLoRA scaling = alpha/sqrt(r)
# merge_weights=False -> train()/eval() won't auto-merge; scaling=0 reliably emulates base model
# ==================== Reference Policy LoRA Snapshot (trust region, mirrors upstream) ====================
# ref = policy snapshot from N steps ago (not disable_lora=base): KL(policy||recent) trust region,
# does not cap improvements that need to move far from base...
```

```python
# 好：精简，只留 why
# Disable loralib auto-merge; use rsLoRA scaling = alpha/sqrt(r).
# --- reference policy LoRA snapshot (trust region) ---
# ref = policy snapshot from N steps ago; KL(policy||recent) does not cap base-divergent gains.
```

**禁止的注释形态**（清单）：

- 进程标记：`★`、`# P1`、`# [FIX]`、没有 ticket 的 `# TODO`、`# === SECTION ===` banner、手工日志前缀如 `[Info]`/`[step N]`
- 来源泄漏：源码里绝不提及其他 repo / upstream / "the closed source"
- 冗长的 rationale：why 属于设计文档 / commit / PR，不属于源码注释
- 复述代码的注释
- 中文注释
