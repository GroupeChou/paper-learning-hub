# The Last Harness You'll Ever Build

<!-- 论文元数据卡片 -->
<div class="paper-meta">
  <div class="paper-meta-item">
    <span class="paper-meta-label">机构</span>
    <span class="paper-meta-value org-Meta FAIR">Meta FAIR</span>
  </div>
  <div class="paper-meta-item">
    <span class="paper-meta-label">方向</span>
    <span class="paper-meta-value">AI Agent</span>
  </div>
  <div class="paper-meta-item">
    <span class="paper-meta-label">日期</span>
    <span class="paper-meta-value">2026-04-22</span>
  </div>
</div>

!!! info ""
    <span class="paper-tag paper-tag-translated">✅ 已完成精读</span>

- **来源**：arXiv
- **论文链接**：[https://arxiv.org/abs/2604.21003v1](https://arxiv.org/abs/2604.21003v1)
- **状态**：已生成

## 摘要

AI 智能体正越来越多地部署在复杂、领域特定的工作流上——它们需要导航需要数十次点击和表单填写的企业级 Web 应用、编排跨越搜索—提取—综合的多步骤研究管线、自动化对不熟悉代码仓库的代码审查，以及处理需要细致领域知识的客户升级请求。每一个新的任务领域都需要费力且依赖专家经验的 harness 工程：设计让基础模型有效运行的 prompt、工具、编排逻辑和评估标准。我们提出一个**双层框架**来自动化这一过程。

在第一层，**Harness 进化循环（Harness Evolution Loop）** 为单个任务优化 Worker Agent 的 harness H：Worker Agent W_H 执行任务，Evaluator Agent V 以对抗方式诊断失败并评分性能，Evolution Agent E 基于完整的历史尝试记录修改 harness。

在第二层，**元进化循环（Meta-Evolution Loop）** 跨不同的任务优化进化协议 Λ = (W_H, H^(0), V, E) 本身，学习一个最优协议 Λ^best，使得在任何新任务上都能快速收敛 harness——这样将智能体适配到新领域完全不需要人工 harness 工程。我们将该框架形式化为元学习的对应结构，并给出了两个算法。该框架将**人工 harness 工程**转变为**自动化 harness 工程**，并更进一步——**自动化了自动化本身的设计**。

---

## 1 引言

### 中文翻译

近期关于 harness 工程的研究表明，精心设计的脚手架（scaffolding）——执行环境、反馈循环、评估标准和上下文管理——可以极大地增强智能体的能力（Lopopolo, 2026; Rajasekaran, 2026）。

[扩展] 这里的"harness"是一个核心概念，它指的是为了让 LLM/Agent 在特定任务上有效运行而搭建的所有外部基础设施的总和。类似于传统软件工程中的"测试夹具"（test harness），但涵盖的范围更广。

然而，这些 harness 本身就是高度密集、专业化的**人工工程产物**。Lopopolo (2026) 描述了构建自定义 linter、代码仓库本地的可观测性栈（日志、指标、追踪）、Chrome DevTools 集成以及结构化文档层级——所有这些手工打造，目的就是让代码库对 Agent 可理解。Rajasekaran (2026) 报告了多轮 evaluator prompt 校准（附带 few-shot 示例）、设计 4 个针对主观设计质量的评分标准、以及构建一个包含 planner-generator-evaluator 三个 Agent 的架构，其间还有 Agent 之间协商出来的 sprint 合约。

在这两个案例中，harness 都需要深厚的领域知识来构建，以及大量的迭代来调优。Harness 提升了 Agent 的能力，但**改善 harness 本身仍然需要大量的人类专家在每个特定任务领域上投入**。

[扩展] 这里揭示了一个深层的悖论：Agent 试图自动化人类的工作，但让 Agent 自动化本身却需要大量人工。这正是本论文要解决的核心问题。

虽然自动化的 prompt 优化方法（如 LLM-AutoDiff, Yin & Wang, 2025）可以调优单个组件，但它们无法处理完整的 harness——包括工具、编排逻辑、基础设施以及它们之间的交互。

[扩展] 现有的自动化方法都是"局部优化"——只优化 prompt 或只优化工具——但 harness 是一个系统性问题，各组件之间存在复杂的相互作用。

我们提出一个双层框架来自动化这一改进循环。在第一层，**Harness 进化循环**通过三个 Agent 的闭环循环为单个任务优化 Worker Agent 的 harness H：

1. **Worker Agent W_H**（被优化的 Agent，由 harness H 参数化）执行任务并产生执行轨迹
2. **Evaluator Agent V** 以对抗方式验证任务结果、诊断失败模式、评分性能
3. **Evolution Agent E** 基于完整的先前尝试历史修改 harness——包括 prompt、工具、编排逻辑、观察结果和模型配置——以解决诊断出的失败模式

从初始 harness H^(0)（可能是一个通用的、未调优的 Agent 脚手架）开始，循环迭代 K 步：每步 worker 执行任务，evaluator 诊断并评分，evolution agent 基于完整的先前尝试历史生成改进的 harness，最终返回最优的 harness H^best。这些组件共同构成一个**进化协议** Λ = (W_H, H^(0), V, E)，完整指定了 harness 如何被进化。

在第二层，**元进化循环**跨不同的任务优化 Λ 本身，学习一个进化协议 Λ^best，使得在任何新任务上都能快速收敛 harness——这不仅将 harness 工程本身自动化，还将**harness 工程过程的设计**转化为一个自动优化问题。

### 术语解释
- **Harness（夹具/脚手架）**：让 Agent 在特定任务上有效运行所需的外部基础设施，包括 prompt、工具定义、编排逻辑、评估标准等
- **Evolution Loop（进化循环）**：通过"执行→评估→修改"闭环自动优化 harness 的机制
- **Meta-Learning（元学习）**：学习"如何学习"的框架，本文将其类比为"学习如何设计 harness"
- **Adversarial Evaluation（对抗性评估）**：Evaluator Agent 主动寻找 Worker Agent 的失败模式，而非被动打分

### 图表/公式说明
本片段无图表/公式。Figure 1 的架构图位于第 2-3 页，将在下一节详细描述。

### 关键 takeaway
- **核心问题**：当前 Agent 落地到新领域需要大量人工 harness 工程，成本高、不可扩展
- **核心洞察**：现有自动化方法（如 prompt 优化）只做局部优化，忽略了 harness 的系统性
- **核心方案**：双层框架——第一层自动化单任务 harness 调优，第二层元自动化跨任务传优化经验
- **作者主张**：该框架将"人工 Harness 工程"变为"自动化 Harness 工程"，最终实现"自动化自动化本身的设计"

---

## 2 The Harness Evolution Loop

### 中文翻译

#### 2.1 定义 Agent Harness

**裸模型不是 Agent。**

遵循 Trivedy (2026) 的表述，我们采用以下公式：

**Agent = 模型 + Harness**

Harness 是**除了模型本身之外的所有代码、配置和执行逻辑**——它是让模型的智能变得有用的系统。

[扩展] 这是一个非常重要的定义。它表明：单纯的大语言模型本身不是一个可用的 Agent。要让模型真正"行动"，需要围绕它搭建一整套基础设施——就像汽车引擎需要底盘、轮胎、方向盘才能成为一辆车。

Harness 可以有多种形式；常见的 harness 组件类别包括：

- **系统 prompt 和任务 prompt**：定义 Agent 身份和约束的系统级指令，以及指定目标、成功标准和上下文示例的任务级 prompt
- **工具、技能及其描述**：Agent 可以调用的能力（如文件编辑、shell 执行、UI 交互、Web 搜索、MCP 服务器）
- **捆绑的基础设施**：提供给 Agent 的执行环境（文件系统、沙箱、浏览器、可观测性栈）
- **编排逻辑**：结构化 Agent 交互循环的控制流（子 Agent 生成、任务交接、模型路由、反馈循环，以及诸如 Ralph Loop 的续接模式）
- **Hook 和中间件**：围绕模型注入的确定性执行保证（压缩、续接、lint 检查、验证循环）
- **模型配置**：底层模型的选择、推理参数（温度、采样策略、token 限制）以及决定哪个模型处理哪个子任务的模型路由规则

Harness 遍布整个 Agent 生态系统。**AdaL**（SylphAI, 2026）、**Claude Code**（Anthropic, 2025）和**Codex**（OpenAI, 2025）是通用软件工程的 harness——它们将 LLM 与文件系统访问、shell 执行、Web 搜索和多文件编辑封装在一起。**OpAgent**（Guo et al., 2026）是自主 Web 导航的 harness，将 Planner、Grounder、Reflector 和 Summarizer 组合成一个多 Agent 管线，在 WebArena（Zhou et al., 2024）上取得了 state-of-the-art 的结果。

在每个案例中，**决定 Agent 能感知什么、如何行动、如何编排和验证工作的，是 harness，而不是模型本身**。

[扩展] 这一段是论文的核心论点之一：harness 比模型更重要。作者用多个业界知名系统（AdaL、Claude Code、Codex）作为例证，说明同一模型配上不同的 harness 会产生截然不同的能力。

#### 2.2 任务定义

一个任务 t = (I, S) 由以下部分组成：
- **指令 I**：给 Worker Agent 的具体目标
- **成功标准 S = {s₁, s₂, ..., sₘ}**：Evaluator 用来判断完成情况的**可验证条件检查清单**

[扩展] 这个定义非常工程化：任务被显式拆解为"做什么"（指令）和"怎么算做好"（成功标准）。这为后续的自动化评估奠定了基础。

#### 2.3 Worker Agent

Worker Agent W_H 是被优化的 Agent——由它的 harness H 参数化。它暴露一个单一接口 `W_H.execute(t)`：给定任务 t，worker 接收指令 I，通过工具接口与目标环境交互，并生成一个包含环境观察、动作日志和每步时序信息的**执行轨迹 τ**。

第 2.1 节描述的基于 harness 的 Agent——AdaL、Claude Code、Codex 和 OpAgent——都可以被设置为 Worker Agent W_H，每个都尝试使用特定的 harness 配置来解决问题。

#### 2.4 Evaluator Agent

Evaluator Agent V 是一个独立的、**对抗性的审查者**。它暴露接口 `V.evaluate(τ, t) → (report, score)`：给定执行轨迹 τ 和原始任务 t = (I, S)，它生成一个结构化的诊断报告和一个数值评分。Evaluator 执行四个功能：

1. **状态验证**：将 worker 在 τ 中的观察与真实环境状态交叉验证，确认 Agent 实际感知到了它声称的内容，检测幻觉或错误解释的状态
2. **标准检查**：针对每个成功标准 sᵢ ∈ S 评估 worker 的最终状态，生成每个标准的通过/失败判定
3. **性能审计**：将总执行时间分解为 LLM 时间（模型推理延迟）和工具时间（环境交互延迟），识别瓶颈是计算性的还是行为性的
4. **评分**：计算双层指标——首先按通过/失败（任务是否成功完成），然后按执行时间作为平局决胜。这个排名决定了代码变更是净改进还是回退

[扩展] Evaluator Agent 的设计非常精妙：它不仅回答"任务完成了吗"，还回答"为什么完成/没完成"、"哪里出了问题"、"瓶颈在哪里"。这种多维度的诊断信息为 Evolution Agent 提供了可操作的改进方向。

#### 2.5 Evolution Agent

Evolution Agent E 是整个系统的**进化驱动力**。它暴露接口 `E.evolve(history, H^best) → H'`：给定完整的进化历史和最优性能的 harness，它生成一个修改后的 harness H'。它的运作方式类似于一位**资深工程师**：

1. **聚合诊断**：读取完整的进化历史——包括尝试了哪些 harness 变体、它们的 evaluator 报告、评分以及每次变更是改进还是回退。这个历史上下文防止 evolution agent 重复不成功的策略，并使其能够基于先前的洞察进行构建
2. **识别失败模式**：将失败分类为重复出现的类别（如不正确的工具使用、推理循环、错误解释的环境状态、过长的延迟）
3. **修改 Harness**：基于诊断出的失败模式，evolution agent 编辑 worker 的 harness H——构成 Agent 的除模型参数之外的所有代码和配置——包括工具实现、系统 prompt、编排逻辑、观察结构或模型配置，以解决根本原因

### 术语解释
- **Agent = 模型 + Harness**：Trivedy (2026) 提出的核心公式，强调外部基础设施对 Agent 能力的关键作用
- **执行轨迹 τ**：Agent 执行任务时的完整行动记录，包括环境状态、动作日志、时序信息
- **Scaffolding（脚手架）**：与 harness 近义，指支撑 Agent 运行的外部结构
- **Ralph Loop**：一种 Agent 续接模式，允许 Agent 在长时间运行的任务中自动管理上下文窗口

### 图表/公式说明
**Figure 1：系统架构图**（第 2-3 页，1 张图）

该图展示了双层框架的整体架构：
- **内层（蓝色）**：Harness 进化循环——Worker（执行）→ Evaluator（评估）→ Evolution Agent（修改代码）→ 回到 Worker 的迭代循环
- **外层（绿色）**：元进化循环——跨多个训练任务 t₁, t₂, ..., tₙ 运行内层循环，元进化 Agent 聚合所有任务的评分并修改进化协议，将更新后的协议反馈到下一轮
- **输出**：最优进化协议 Λ^best

**Algorithm 1：Harness 进化循环**
```
输入：任务 t, Worker Agent W_H, 初始 harness H^(0), Evaluator V, Evolution E, 迭代数 K
输出：最优 harness H^best, 最优得分, 进化历史

初始化 H^best = H^(0), best_score = -∞, history = []
for k = 1 to K:
    1. 用 H^(k-1) 重建 W_H
    2. Worker 执行任务 → 生成轨迹 trace
    3. Evaluator 评估 → (report, score)
    4. if score > best_score: 标记 IMPROVED, 更新 H^best
       else: 标记 REGRESSED
    5. 记录 (H^(k-1), report, score, verdict) 到 history
    6. Evolution Agent 基于 history 和 H^best 生成新的 H^(k)
return H^best, best_score, history
```

**Algorithm 2：元进化循环**（见第 3 节）
```
输入：训练任务集 T_train, 元进化 Agent E_meta, 初始协议 Λ^(0), 内层预算 K
输出：最优协议 Λ^best, 最优元得分, 元进化历史

for j = 0, 1, 2, ...:
    for each task t_i in T_train:
        运行 Algorithm 1 → (H^best_i, score_i, history_i)
    元得分 = 聚合(所有任务的得分)
    if 元得分提升: 更新 Λ^best
    元历史记录 (Λ^(j), 任务结果, 元得分)
    E_meta 基于元历史生成新的 Λ^(j+1)
return Λ^best
```

### 关键 takeaway
- **Harness 的定义**：Agent = 模型 + Harness，harness 是决定 Agent 能力的核心因素
- **四个组件**：Worker（执行者）、Evaluator（审查者）、Evolution Agent（进化者）、以及它们之间的闭环编排
- **对抗性评估**：Evaluator 不仅验证完成度，还诊断失败模式、分解性能瓶颈
- **进化驱动力**：Evolution Agent 像资深工程师一样，基于完整历史诊断问题并修改 harness 的每一部分

---

## 3 Meta-Evolution: Learning to Evolve Harnesses

### 中文翻译

如前所述，Harness 进化循环为单个固定的任务优化 Worker Harness H。但 harness 进化循环本身——evaluator prompt、evolution agent 的诊断策略、评分函数、观察结构以及编排逻辑——**本身也是一个 harness**，我们将其记作 Λ。形式化地：

`Λ = (W_H, H^(0), V, E)` (公式 1)

其中 W_H 是 Worker Agent，H^(0) 是初始 Worker Harness，V 是 Evaluator Agent，E 是 Evolution Agent。这些组件共同定义了循环如何运作。在当前系统中，Λ 由人类工程师设计，并在整个进化过程中保持不变。

[扩展] 这是本文最核心的 insight：不仅"Agent 的 harness"可以被优化，"优化 harness 的协议"本身也是一个 harness，同样可以被优化。这种"递归的自动化"思路非常 elegant。

我们现在描述一个自然的泛化：**一个元进化 Agent 来优化 Λ 本身**，使得内层的 harness 进化循环能够更快、更可靠地收敛到高性能的 Worker Harness，跨不同的任务都有效。

#### 3.1 Harness 进化循环本身也是一个 Harness

注意到 Λ 与任何其他 harness 具有完全相同的结构：它由 prompt（evaluator 和 evolution agent 的指令）、工具（评分函数、版本控制操作、代码编辑能力）、观察（从 worker、evaluator 和 evolution agent 中暴露哪些遥测数据和轨迹）以及编排逻辑（运行多少次迭代、何时提交或回退、如何选择和排序任务）组成。因此，优化 Λ 是**在更高抽象层次上的 harness 优化**。

[扩展] 这是一个典型的"递归抽象"模式：你在解决的问题和你解决问题的方法，本质上是同一类问题。

元进化 Agent 可以修改的 Λ 的组件包括：
- **Evaluator Agent prompt**——查找哪些失败模式、如何评分、需要什么证据
- **Evolution Agent prompt**——如何诊断失败模式、优先进行哪些代码修改、修改 worker 的激进程度
- **Worker 观察结构**——从 worker 的执行中暴露哪些遥测数据、轨迹和中间状态
- **Evaluator 和 evolution agent 的观察**——每步在 Agent 之间流动哪些信息
- **评分函数设计**——指标结构（如双层 vs. 多维）、阈值和平局决胜规则
- **循环超参数**——迭代次数、并行度、回退阈值和停止标准

#### 3.2 元学习形式化

这个双层优化可以直接映射到元学习框架（Thrun & Pratt, 1998）。设 T_train = {t₁, t₂, ..., tₙ} 是一组元训练任务，每个代表来自潜在不同领域的 Agent 任务。T_test 是用于评估泛化能力的保留元测试任务。

两个循环的运作方式如下：

- **内循环（Harness 进化）**：给定固定的 harness 进化协议 Λ 和单个任务 tᵢ，运行 harness 进化循环 K 次迭代，产生优化的 Worker Harness H^(K)。**衡量收敛轨迹**：worker 在该任务上的改进速度和程度。
- **外循环（元进化）**：跨多个任务 tᵢ ∈ T_train，评估当前 Λ 驱动内循环的效果。修改 Λ 以提高**适应速度**——内循环在单个任务上收敛到高性能的速率。

外循环的目标是找到一个最大化跨训练任务的任务性能的 harness 进化协议 Λ^best：

`Λ^best = arg max_Λ E_{tᵢ~T_train}[best_score(HARNESS_EVOLUTION_LOOP(tᵢ, Λ, K))]` (公式 2)

其中 HARNESS_EVOLUTION_LOOP(tᵢ, Λ, K) 运行 Algorithm 1 共 K 次迭代，返回表现最佳的 harness H^best、其得分和完整的进化历史。进化协议 Λ 仅由在每个任务上达到的**最终最优得分**来判断——而不是中间进展。

这个形式化在 Algorithm 2 中展示，并镜像了元学习，其对应关系如表 1 所示。

**表 1：元学习与元进化的对应关系**

| 元学习 | 元进化 |
|--------|--------|
| 被适应的参数：θ | 被进化的 Harness：H |
| 适应过程：(θ^(0), 优化器, 损失) | 进化协议：Λ = (W_H, H^(0), V, E) |
| 内循环：在任务 tᵢ 上的梯度更新 | 内循环：HARNESS_EVOLUTION_LOOP(tᵢ, Λ, K) |
| 外循环：元梯度更新 | 外循环：E_meta.evolve(meta_history, Λ^best) |
| 元训练任务 | 训练任务 T_train |
| 元测试任务 | 保留任务 T_test |
| 目标：快速适应新任务 | 目标：快速在新任务上收敛 harness |

#### 3.3 评估协议

泛化能力在 T_test 上评估：给定一个新的、未见过的任务，配置了学习到的 Λ^best 的内层 harness 进化循环**需要多快**才能产生一个高性能的 Worker Harness？关键指标包括：

- **收敛速度**：达到目标性能阈值所需的内层迭代次数
- **最终性能**：固定迭代次数后的任务通过率
- **鲁棒性**：跨不同元测试任务的收敛速度的方差

一个良好优化的 Λ^best 应该使 harness 进化循环能够**快速适应任何新任务**——以比人工设计的 harness 进化循环更少的迭代和更少的计算量产生有效的 Worker Harness。

### 术语解释
- **元进化（Meta-Evolution）**：不仅优化单个任务的 harness，还优化"优化 harness 的协议"本身
- **进化协议 Λ**：定义 harness 如何被进化的完整规范，包括所有组件和超参数
- **收敛轨迹（Convergence Trajectory）**：harness 在迭代过程中性能提升的路径和速度
- **元学习（Meta-Learning）**：学习一个学习算法，使其在新任务上快速适应（本论文的核心理论类比）

### 图表/公式说明
**公式 1**：`Λ = (W_H, H^(0), V, E)` — 进化协议的形式化定义。每个元素都是可被优化的组件。
**公式 2**：`Λ^best = arg max_Λ E[best_score(HARNESS_EVOLUTION_LOOP(tᵢ, Λ, K))]` — 元进化的目标函数，最大化跨任务的期望最优得分。
**表 1**：元学习 vs. 元进化的对应表。这是论文的关键理论贡献：将双层 harness 优化与成熟的元学习框架建立起精确的类比，使得元学习领域的大量理论工具可以直接迁移到 harness 优化中。

### 关键 takeaway
- **递归洞察**：优化 harness 的协议本身也是一个 harness，可以被优化——这是论文最具原创性的 insight
- **元学习类比**：通过严格的对应关系（表 1），将 harness 优化锚定到元学习框架中，提供了理论 rigor
- **优化对象**：Λ 的可优化组件包括 evaluator/evolution agent 的 prompt、观察结构、评分函数、超参数
- **评估标准**：泛化能力通过收敛速度、最终性能和鲁棒性三个维度衡量

---

## 4 结论

### 中文翻译

我们提出了 **Harness 进化循环**，一种闭环架构，通过重复的任务执行、对抗性评估和代码修改，自动优化 AI Agent 的 harness H——即围绕基础模型的 prompt、工具、编排逻辑和基础设施。该系统将 Agent 形式化为 W_H，将评估（V）与进化（E）分离，并在跟踪完整收敛历史的同时迭代改进 H。

然后我们引入了 **元进化循环**，该循环跨不同的任务优化进化协议 Λ = (W_H, H^(0), V, E) 本身。通过在每个训练任务 tᵢ ∈ T_train 上运行内层的 harness 进化循环并衡量收敛，元进化 Agent E_meta 学习一个协议 Λ^best，使其能够快速适应未见过的任务。这个双层形式化镜像了元学习：内循环将 harness 适应到单个任务，而外循环则优化适应过程的泛化能力。

在传统上，harness 工程需要针对每个特定任务领域投入深入的**人类专家经验**。Harness 进化循环将此过程完全自动化——将**人工 harness 工程转变为自动化 harness 工程**。而元进化循环更进一步：它**自动化了自动化本身的设计**——学习如何进化 harness，而不是进化任何一个单一的 harness。

[扩展] 结论的升华非常漂亮：第一层自动化解决了"怎么做"的问题，第二层元自动化解决了"怎么自动地做"的问题，本质上是在学习"学习如何设计 Agent"。

我们计划在后续工作中提供跨多个多样化工作流的实证结果——这些工作流即使使用最先进的 Agent 和 harness 也难以轻易自动化——从复杂的定制化客户工作流到领域特定的企业流程。目的是证明该框架可以打开那些之前被认为对自主 Agent 来说过于脆弱或过于专业化的任务类别。最终，我们将发布一个基于学习到的进化协议 Λ^best 的产品：一个系统，任何用户都可以将一个通用 Agent 指向一个新的任务领域，它就会自动**进化成一个专门的、高性能的 Agent**——不需要任何 harness 工程专业知识。

[扩展] 最后一段为该框架描绘了一个宏大的愿景：一个"即插即用"的 Agent 产品。用户不需要理解任何 harness 工程，只需要告诉 Agent"去干这个"，它就能自动调优自己。这就像把"训练一个专家"的过程自动化了。

### 术语解释
- **自动化自动化（Automating the automation）**：元进化的本质——不仅自动化任务执行，还自动化任务自动化的设计过程
- **收敛历史（Convergence History）**：每次迭代的 (harness 版本, 评估报告, 得分, 判定) 的完整记录
- **通用 Agent vs. 专门 Agent**：通用 Agent 能处理广泛但表面的任务；专门 Agent 通过调优 harness 在特定领域达到高精度

### 图表/公式说明
本片段无图表/公式。

### 关键 takeaway
- 本文提出了**两个层次的自动化**：自动化 harness 工程（第一层）和自动化 harness 工程过程的设计（第二层）
- 核心贡献是一个**理论框架**（双层进化 + 元学习形式化）和**两个算法**（Algorithm 1 & 2）
- 实证结果尚未发表（TODO），但计划在多样化复杂工作流上验证
- 最终愿景是一个**零配置的 Agent 产品**——用户只需描述任务，系统自动进化出高性能的专门 Agent
- **对 Hermes/青青 的启示**：这篇论文的方法论可以直接应用于物流预测 Agent 的自动调优——对于每个新场地（如 755W、021WJ），自动进化出最优的预测 prompt 和工具配置，而无需人工为每个场地编写不同的 Skill

## 复核建议

- 当前未发现明显的解析降级信号，仍建议抽样检查图表和公式。
- 特别关注 Algorithm 1 和 Algorithm 2 的伪代码在站点渲染中的可读性。
