# P0–P4 规范全文（canonical）

所有代码都必须遵守的规范。按优先级组织：**正确性 (P0) > 性能 (P1) > 可维护性 (P2) > 风格 (P3) > 流程 (P4)**。

写代码时按需查，交付前逐条过。不要只看 SKILL.md 的摘要表。

---

## P0 — Correctness（最高优先级）

### Fail Fast

- **程序员错误的不变量用 `assert`**。**用户输入的坏值用 `raise ValueError/TypeError`**。
- **在公开 API 入口和系统边界校验输入**（HTTP handler、配置解析）。内部 helper 可以假定输入合法。
- **用早返回和 guard clause**，放在函数顶部，而不是深层嵌套的 if-else。
- **不要过度保护**：如果一个操作 99% 的情况下都是对的，就不要为它的失败加防御处理。**LLM 天生倾向于过度保护，要抵抗这个本能。**
- **不要过度 catch**：`try/except` 必须有清晰、**窄**的保护区域。**绝不要用单个 `try/except` 包住一大块代码。**

判断案例：

```python
# 坏：一个 try 包住了四行互不相关的操作，出错了根本不知道是谁炸的
try:
    cfg = load_config(path)
    model = build_model(cfg)
    ckpt = torch.load(cfg.ckpt)
    model.load_state_dict(ckpt)
except Exception:
    logger.warning("setup failed")
```

```python
# 好：让失败自己冒出来，栈回溯会告诉你哪一行炸了
cfg = load_config(path)
model = build_model(cfg)
model.load_state_dict(torch.load(cfg.ckpt))
```

### Concurrency & Thread Safety

- **显式文档化线程安全保证**——凡是会被多线程访问的类/函数都要写清楚。
- **最小化锁范围**。**持有锁时绝不做 I/O 或 GPU 操作。**
- **优先消息传递（queue）而非共享可变状态。**

### Resource Management

- **只在 profiling 证明必要时**才用 `del` + `torch.cuda.empty_cache()` 释放大的中间张量。**不要防御性地到处撒这两句。**
- **文件句柄、socket、CUDA stream 必须用 context manager（`with`）。**
- **任何缓存或缓冲区必须有界**，或者带淘汰策略。长跑循环里不允许出现只 `append` 的 list。

---

## P1 — Performance

这是一个**每一毫秒都重要**的高性能系统。

- **严格避免在模型推理路径上频繁调用 `.item()`、`.cpu()`、`.tolist()`。** 每一次这样的调用都可能意味着一次 host-device 同步，会把异步执行流水线打断。
- **数据处理尽可能保持 GPU 向量化。热路径上的 CPU fallback 不可接受。**
- **用低开销实现优化热路径。** 紧循环里任何不必要的 Python 层开销都要标出来。

> 审查提示：看到推理路径里的 `.item()`，先问它是不是用在控制流判断上（如 early-exit、动态 shape 分支）。是的话，它强制了一次同步——要么改写成张量运算，要么解释清楚为什么必须同步。

---

## P2 — Maintainability

### Architecture & Decoupling

- **DRY**：重复代码**超过 5 行**必须抽成共享函数。
- **文件超过 2,000 行必须拆**（Mixin 模式或子模块）。
- **函数尽量不超过 50 行**（不含 docstring）。把逻辑子步骤抽成私有 helper。

> 注意：这条与"反对过度碎片化"是**同一个天平的两端**。50 行是上限不是目标；一个 60 行自顶向下、一眼能读完的函数，好过三个各 20 行、各被调用一次的 `_step_one/_two/_three`。

### Naming Clarity

- **公开 API 不用缩写**：写 `request_count` 不写 `req_cnt`。例外：广为人知的术语（`num`、`idx`、`cfg`、`bs`）。
- **布尔变量加前缀**：`is_`、`has_`、`should_`、`can_`。
- **对称性**：成对命名保持一致——`start/stop`、`begin/end`、`open/close`、`send/recv`。**不要混**（例如不能 `start/finish`）。
- **不用泛化名字**：没有限定的 `data`、`result`、`info`、`tmp`、`manager`、`handler` 一律禁止。要用 `token_ids`、`decode_result` 这种。

### Imports

- **顺序**：stdlib → third-party → local，段间空行（`isort` 风格）。
- **绝不用 `from module import *`**。
- **重型可选依赖用 lazy import**，放在真正使用它的函数内部。
- **不允许循环导入**——需要的话把共享接口抽到第三个模块。

> 这条与"尽量避免 lazy import"的边界：lazy import 只保留给**重型可选依赖**和**已文档化的循环依赖破解**。其余一律在文件开篇 import。

### Constants

- **禁止魔数**。抽成具名常量：`MAX_BATCH_SIZE = 256`。
- 例外：显而易见的算术/索引场景下的 `0`、`1`、`-1`。
- **经验常数要带来源注释**：`DECODE_TOKS_PER_SEC = 6.7  # 在 H20 上实测`。

---

## P3 — Style

### Function Purity

- **优先纯函数。避免就地修改入参。**
- 例外：forward pass 里为了极致内存优化做的就地操作，**必须写显式注释**说明。

### Pythonic & Clean

- **构造函数要精简**：`__init__` 参数保持简洁。只传必要参数，**不要传巨大的 config 对象**。
- **避免动态属性**（`getattr`/`setattr`）。代码应当是显式的。
- **三元运算符只用于极简单的情形**。复杂逻辑用标准 `if-else`。
- **把复杂的多行分支逻辑抽成独立的私有函数。**
- **分支完整**：如果一个 `if` 给变量赋值或返回值，**必须带 `else`**。Guard clause（早返回/raise/continue）不需要 `else`。分支超过 3 层就重构成 `if/elif/.../else` 或 dispatch dict。
- **所有公开 API 和函数签名必须带类型标注。**
- **类/文件内部函数用 `_private` 前缀**；否则就是公开的。
- **删除随手写的调试注释和日志。删除中文注释。**

### Typing

- 全量类型标注，用现代语法：`X | Y`、`list[...]`、`dict[str, Any]`、`X | None`。**返回类型也要标。**
- **一个 repo 只用一种类型风格**。不要把 `Optional[X]`/`Union[X, Y]` 和 `X | Y` 混用。
- 要么 `requires-python >= 3.10`，要么 `from __future__ import annotations`。
- **闭合取值集合用 `Literal[...]` 或 `Enum`**，不要用裸字符串做比较。
- **禁止 `Any` 标注，禁止裸 `dict`/`list`/`tuple`**，禁止 `tokenizer: any`。
- **禁止可变默认参数**：`def f(x=[])` / `= {}` 是 bug。用 `None` 哨兵或 `field(default_factory=list)`。

---

## P4 — Process

### Testing

- **PR 描述里提供验证脚本**，让 reviewer 能复制粘贴直接跑。
- **重要功能补 CI 单测。**
- **测契约（输入 → 输出），不测内部状态。**
- **测试里固定随机种子**，保证确定性。
- **一个测试函数，一个概念，一个断言。**

> 反例警示：不要为"防御了根本不可能出现的错误"的 `try/except` 写单测。单测要简洁有力、覆盖合理，抓住函数**主要的**错误可能就够了。

---

## 成熟度分阶段（重要）

规范不是一刀切，按代码成熟度分阶段：

| 阶段 | 允许什么 |
|---|---|
| **原型期** | 围绕你还不信任的调用写 `try/except` 是可以的。 |
| **成熟期** | **把它删掉。** 把 `if x is not None and isinstance(x, ...)` 链换成 `assert` 或直接调用。防御性脚手架（为对齐 AllReduce 的 dummy forward、logger 开关体操、类型强制转换循环、宽泛的 `try/except` 吞错）是**债，不是安全**。信任你的不变量，让失败以栈回溯的形式暴露。 |
| **自查时** | 每个 `try/except` 和防御性 `if` 都必须回答："删掉它会坏什么？"答案是"不会，那是调试用的"——**删**。 |

写正式代码时按**成熟期**标准来。

长期 workaround 用**一行**注释说明约束，不要写十行。

---

## 训练代码的特殊约定

训练代码应分为 **`train` 和 `trainer` 两个脚本**：把训练相关的函数等内容封装到 `trainer` 里，`train` 只负责调用 `trainer` 进行循环。

---

## 日志

- **一个 repo 只用一种日志库**。不要混用 stdlib `logging` 和 `loguru`。只配置一次。
- **一个模块一个 logger**：`logging.getLogger(__name__)` 或 `from loguru import logger`。
- **英文简短，不加手工前缀**（level 字段已经写了 INFO/WARNING）。
- `print` 只用于**终端用户会读的 CLI 输出**（`--help`、可视化、`__main__` demo）。运行时信息——哪怕是 debug——都走 logger。
- **统一用 f-string**：`logger.info(f"Loading model: {path}")`，不要 `logger.info("Loading %s", path)`。
- 分布式：用 logger 配置或 `RankedLogger` 风格的适配器统一守 rank-zero，**不要到处撒 `if is_main:`**。（训练循环里保留它自己的写法，但不要把这个模式扩散出去。）

---

## 配置与魔法值

- **源码里不允许硬编码 URL、绝对路径、主机名、或没有解释的魔数**。放配置文件、环境变量、或模块顶部的具名常量。
- **经验常数要具名 + 带来源注释**：`DECODE_TOKS_PER_SEC = 6.7  # 在 H20 上实测；用于估算 rollout 时长`。
- **一个 repo 只用一种配置机制**（Hydra / argparse+yaml / dataclass / env）。不要混。**不要放一个"只当文档、从不加载"的 yaml。**

---

## 结构

- **文件 > ~400 行就考虑抽模块**。但一个 30 行、只装一个被调用一次的 `_helper` 的文件也是错的——**合并掉**。
- **禁止 `sys.path.insert` hack**。用 package import、PYTHONPATH，或 `pyrootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)`。一个 repo 只在一处。
- **除已文档化的循环依赖破解外，禁止函数内 import**。纯类型层面的循环依赖用 `if TYPE_CHECKING:` + 字符串引号解决。

> 注意与"不要用 `if TYPE_CHECKING:` 糊弄 lint"的区别：`TYPE_CHECKING` 只允许用于**真正的**类型层循环依赖，不允许拿来把本该开篇 import 的东西藏起来骗过 linter。

- **一个 repo 只用一种入口机制**（hydra/argparse/fire/`[project.scripts]`）。`if __name__ == "__main__"` 只出现在入口模块，绝不出现在库模块。
- **模块级副作用**（改环境变量、全局状态、`setup_root`、注册 resolver）**只允许在入口模块**。库模块的 import 必须无副作用。
- **`__init__.py`**：显式 `__all__`，禁止 `from .x import *`，最小化 re-export。**不要用 `__init__.py` 做 import**——从根路径以包的方式 import 每个文件，例如 `from xxx.yy.zzz import kkk`。
- **禁止死代码**：不可达分支、未使用的参数、注释掉的代码块、过期的 TODO、"留着以后用"的 stub。

---

## 工具链

- 优先用配置好的 linter/formatter（ruff/black/isort）+ 类型检查器（pyright/mypy）。
- 如果没配，**至少在宣称"做完了"之前跑一遍** `python -m py_compile` / `ruff check`。
- 配好类型检查器是更高的标准——朝它努力。
- **新逻辑要有测试**。零测试的 repo 本身就是坏味道，别让它更糟。

---

## 语言与注释的硬要求

- **只写英文**：注释、docstring、日志字符串、CLI help 全用英文。（需要走 i18n 的用户可见字符串不在此列。repo 本身是非英文的话，跟随 repo。）
- **注释稀疏、一行、只给真正不显然的地方**。复述代码就是噪音。
- **禁止进程标记**：`★`、`# P1`、`# [FIX]`、无 ticket 的 `# TODO`、`# === 分节 banner ===`、手工日志前缀 `[Info]`/`[step N]`。
- **禁止来源泄漏**：源码里绝不提及其他 repo / upstream / "the closed source"。
- **禁止在注释里写长篇 rationale** —— why 属于设计文档 / commit / PR。
- **docstring**：Google 风格，$1$–$3$ 行。`Args`/`Returns` 只在非显然时写。每个文件一行简短的模块 docstring。
- **不写文件头注释**；类定义后不写超长注释解释各类元素，用简单注释说明即可。
- `# noqa: <code>` 允许，但**必须带理由**；光秃秃的 `# noqa` 不行。

---

## 数据结构的选型

- **内部值对象**（config、messages、state）：`@dataclass`，优先 `kw_only=True`；可变默认值用 `field(default_factory=...)`。
- **跨边界 schema**（API 请求/响应、不可信输入、需要校验）：`pydantic.BaseModel`。不要手搓 pydantic 免费提供的校验器。
- **同一个概念不要混用两者**。按角色选，不要按心情选。

---

## 不要重造已有轮子

不要重造 stdlib 或已经 import 的依赖提供的东西：`itertools`、`functools`、`collections`、`pathlib`、`dataclasses`、`pydantic`、`torch.nn.functional`。**一个包住 `lru_cache` 的三行包装就是噪音。**

- **不要在第二个具体实现出现之前就加 interface / base class / registry / plugin system。** 先有两个 case，再抽象。
- **不要为了"更清晰的主流程"预先抽 `_helper`/`_impl`**，除非它被复用、或者长到一屏读不完。
- **不要堆 config dataclass + yaml loader + validator + CLI override**，如果 argparse + dict 就够。跟随 repo 已有的机制；没有的话选最轻的那个。

---

## 命名约定

- 类 `PascalCase`；函数/变量 `snake_case`；常量 `UPPER_SNAKE`；内部成员加前导下划线。`__double` 只在需要名字改编时用（罕见）。
- **名字说 what 不说 how**：`load_checkpoint` 而不是 `do_thing`；`num_codebooks` 而不是 `n`。
- **不要写 `_function` 这种带下划线前缀的函数名**，直接用 `function`，更易维护。

---

## 一个 repo 一种机制

- **一种入口机制**（hydra / argparse / fire / `[project.scripts]`）。`if __name__ == "__main__"` 只出现在入口模块，绝不出现在库模块。
- **模块级副作用**（改环境变量、全局状态、`setup_root`、注册 resolver）只允许在入口模块。**库模块的 import 必须无副作用。**
- **一种配置机制**（Hydra / argparse+yaml / dataclass / env）。不要混。不要放一个"只当文档、从不加载"的 yaml。
- **一种日志库**，一种 f-string 风格。

---

## 自查清单（写完自己的代码时）

逐条过：

- 只有一个调用点的 `_helper`/`_impl`？→ **inline 掉**。
- 文件 <30 行、只装一个 helper？→ **合并掉**。
- 只有一个实现的 interface/base class/registry？→ **删掉**，等第二个实现出现再说。
- `try/except` 或 `if isinstance / if x is not None` 链，防的是不存在的失败模式？→ **删掉**。
- 非英文文本、`★` / `# P1` / `# [FIX]` 标记、banner 注释、手工日志前缀？→ **标出来**。
- 文件 > ~400 行且可以拆？→ **标出来**。
- 硬编码路径/URL、`sys.path` hack、函数内 import、裸 except、无类型签名、`Optional` 与 `X|Y` 混用、可变默认参数、复述代码的注释？→ **全部标出来**。
- 每一条注释：领域读者还需要它吗？不需要 → **删**。
- 每一个私有函数：被调用超过一次吗？不是 → **inline**。
