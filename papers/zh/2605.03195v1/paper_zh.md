# Terminus-4B: Can a Smaller Model Replace Frontier LLMs at Agentic Execution Tasks?

<!-- 论文元数据卡片 -->
<div class="paper-meta">
  <div class="paper-meta-item">
    <span class="paper-meta-label">机构</span>
    <span class="paper-meta-value org-阿里通义">阿里通义</span>
  </div>
  <div class="paper-meta-item">
    <span class="paper-meta-label">方向</span>
    <span class="paper-meta-value">AI Agent</span>
  </div>
  <div class="paper-meta-item">
    <span class="paper-meta-label">日期</span>
    <span class="paper-meta-value">2026-05-04</span>
  </div>
</div>

!!! info ""
    <span class="paper-tag paper-tag-translated">✅ 已完成精读</span>

- **来源**：Microsoft arXiv query
- **论文链接**：[https://arxiv.org/abs/2605.03195v1](https://arxiv.org/abs/2605.03195v1)
- **状态**：已生成

## 摘要

### 中文翻译

现代的编码智能体（coding agents）越来越多地将专门化的子任务委托给子智能体（subagents）。这些子智能体是更小、更聚焦的智能体循环，负责处理诸如搜索、调试或终端执行等狭窄的职责。

这种架构模式通过将冗长的输出（例如构建日志、测试结果等）隔离在子智能体的上下文窗口内，从而保持主智能体上下文窗口的整洁。

通常，当智能体为此类任务使用子智能体时，它们会使用前沿模型（frontier models）作为这些子智能体。

在本文中，我们研究了一个问题：一个经过微调的小型语言模型（SLM）能否在智能体终端执行任务中达到与前沿模型相当的性能。

我们提出了 Terminus-4B，这是一个经过后训练的 Qwen3-4B 模型，通过监督式微调（SFT）和基于评分准则的 LLM-as-Judge 奖励的强化学习（RL），专门针对这一任务进行训练。

在我们跨越各种前沿模型、训练消融实验和主智能体配置的广泛评估中，我们发现，与无子智能体基线相比，Terminus-4B 能够将主智能体的 token 使用量减少高达约 30%，而对智能体在 SWE-Bench Pro 和我们内部的 SWE-Bench C# 基准测试上的性能没有影响——后者往往包含大量冗长的执行任务。

此外，Terminus-4B 改善了关键指标，表明主智能体更依赖于子智能体的输出，并自行执行更少的终端执行任务。

我们发现，我们的模型不仅缩小了原始 Qwen 模型与前沿模型（如 Claude Sonnet / Opus / GPT-5.3-Codex）之间的差距，而且常常甚至超过了它们的性能。

### 术语解释

- **coding agent（编码智能体）**：能够自主完成编程任务的 AI 系统，如编写代码、运行测试、调试等
- **subagent（子智能体）**：被主智能体调用的次要智能体循环，负责处理特定子任务
- **frontier model（前沿模型）**：目前性能最强的顶级大型语言模型，如 Claude Opus、GPT-5 等
- **SLM（Small Language Model，小型语言模型）**：参数规模较小的语言模型，通常参数量在数十亿以下
- **SFT（Supervised Fine-Tuning，监督式微调）**：使用标注数据对预训练模型进行有监督的进一步训练
- **RL（Reinforcement Learning，强化学习）**：通过奖励信号让模型在交互中学习最优策略
- **LLM-as-Judge（LLM 作为评判者）**：使用语言模型来评估其他模型输出的质量
- **SWE-Bench**：一个评估 AI 解决软件工程任务能力的基准测试集

### 图表/公式说明

本摘要部分无图表/公式。

### 关键 takeaway

- **要点**：本文研究的是能否用一个 4B 参数的小模型替代昂贵的前沿模型来执行编码智能体中的终端执行任务。
- **要点**：Terminus-4B 通过 SFT + RL 两阶段训练，在不影响任务性能的前提下将主智能体 token 消耗降低约 30%。
- **要点**：该模型不仅缩小了与小模型的差距，在某些情况下甚至超越了前沿模型的表现。

## 1 引言

### 中文翻译

近年来，编码智能体 [1–4] 在软件工程任务方面取得了长足进步，涵盖范围从编写测试一直到解决复杂的仓库级 GitHub 问题。

这些工作流中一个关键的组成部分是终端执行——即运行构建、安装依赖和执行诊断测试以复现问题和验证修复方案的过程。

虽然终端执行是必不可少的，但这些任务会用终端输出淹没智能体的上下文窗口。一个单一的冗长测试就能轻松产生数万个 token，挤占了智能体进行下游决策所需的代码上下文、编辑和规划的空间。

随着轨迹的增长，这会产生一个复合问题：每个新的命令输出都会进一步挤占上下文窗口，限制了智能体在达到 token 窗口限制之前能够采取的实际问题解决步骤的数量。

在实践中，终端输出往往是编码智能体轨迹中上下文的最大消耗者。

我们认为，这种直接执行模式——即智能体在自己的上下文中运行命令并吸收全部输出——是原始的，代表了当今编码智能体设计中的一个主要低效问题。主智能体从这些终端执行中所需的信息通常只是一个简洁的摘要，说明发生了什么，例如代表错误的某一行或末尾的一个表格，而不是来自 shell 命令的完整原始输出。

流行的编码智能体已经越来越多地采用子智能体架构作为解决 LLM 上下文限制的一种方式。主智能体不是在主循环中执行昂贵的任务，而是将它们委托给专用的子智能体。子智能体根据提供的输入独立执行任务，并以主智能体期望的格式返回输出，从而吸收了中间步骤带来的上下文冲击。这种模式已经成功应用于搜索 [3]、调试 [5] 等任务。我们认为终端执行是这种模式的一个天然候选。

尽管有明确的适配性，将子智能体模式应用于终端执行也有其自身的挑战。子智能体必须能够处理跨多种语言的各种仓库。它必须能够正确解释错误并决定如何响应，优雅地处理超时等。更重要的是，它应该生成有效的摘要作为其最终响应，因为这是主智能体了解子智能体所做工作的唯一窗口。一个生成模糊摘要（例如"构建失败"）或产生幻觉输出的子智能体比根本没有子智能体更糟糕。这是因为主智能体不仅需要重复工作，还可能被有缺陷的子智能体误导。

通常，子智能体依赖前沿模型，因为它们对不同任务具有适应性。考虑到这项任务的狭窄性质，我们认为使用昂贵的前沿 LLM 是大材小用，一个更小的模型应该能够胜任这项任务。

在这项工作中，我们将子智能体模式应用于终端执行，通过向现有智能体添加一个执行子智能体（Execution Subagent）。该子智能体被赋予一个单一的终端工具，受到轮次限制和有针对性的系统提示的约束，指示其返回结构化摘要。主智能体可以通过简单的查询将任务委托给这个子智能体。

为了避免使用昂贵的前沿 LLM，我们引入了 Terminus-4B，这是一个专门为智能体终端执行进行后训练的 Qwen3-4B [6] 模型。

我们进行了两阶段的训练流程：首先对从我们内部使用遥测数据收集的轨迹进行监督式微调（SFT），然后使用组相对策略优化（GRPO）[7] 进行强化学习（RL），配以新颖的子智能体训练流程和基于评分准则的 LLM-as-Judge 奖励 [8, 9]。

该子智能体流程能够将子智能体任务与主智能体分离，确保每次 rollout 从相同的问题开始，同时将主智能体在 rollout 中的角色降至最低，从而实现成本高效的训练。

奖励函数根据各种质量维度和失败模式对候选 rollout 与参考轨迹进行评分，为这项任务提供了丰富的多维训练信号。

我们的贡献如下：

- **执行子智能体和 Terminus-4B**：我们设计并将执行子智能体集成到一个生产级的编码智能体框架中。通过使用我们自己的定制微调 Terminus-4B 模型与执行子智能体，我们能够在保持智能体在 SWE-Bench Pro 和我们内部的 SWE-Bench C# 等具有挑战性的编码基准测试上的性能的同时，将 token 使用量减少高达约 30%。

- **子智能体训练框架**：我们提出了一个新颖的子智能体模型后训练框架，将子智能体与主智能体循环解耦。这使得快速且成本高效的 rollout 成为可能，且对前沿 LLM 的依赖最小。我们能够在 rollout 中直接使用原始的 Qwen3-4B 本身作为主智能体。

- **任务形式化和奖励设计**：我们引入了一种新颖的基于评分准则的多维 LLM-as-Judge 奖励，将 rollout 与参考轨迹沿质量和失败维度进行比较，为传统基于结果的奖励 [10] 不易获得的场景提供了丰富的训练信号。

- **全面评估**：我们使用 SWE-Bench Pro 和我们内部的基准测试 SWE-Bench C# 对子智能体设计和模型训练进行了广泛的消融研究，衡量了对解决率、token 效率和行为信号的影响。我们辅以从主智能体视角对子智能体响应进行的 5 维度 LLM 评判评估。在我们的评估中，我们证明 Terminus-4B 作为执行子智能体，其表现与前沿模型相当或更优。

### 术语解释

- **terminal execution（终端执行）**：在命令行环境中运行 shell 命令的过程，如构建、测试、调试等
- **context window（上下文窗口）**：LLM 能够处理的输入 token 的最大长度限制
- **token（令牌）**：LLM 处理和生成文本的基本单位
- **rollout（ rollout 展开）**：在强化学习中，指智能体在环境中执行一系列动作直到终止的完整过程
- **subagent pattern（子智能体模式）**：一种架构设计，主智能体将特定任务委派给专用的子智能体
- **GRPO（Group Relative Policy Optimization）**：一种强化学习算法，在组内比较多个候选输出来优化策略
- **LLM-as-Judge reward（LLM 作为评判者的奖励机制）**：使用语言模型来评判输出质量并提供奖励信号

### 图表/公式说明

本部分无图表/公式。

### 关键 takeaway

- **要点**：终端输出是编码智能体轨迹中上下文的最大消耗者，将终端执行委托给子智能体可以显著节省上下文空间。
- **要点**：使用子智能体模式面临挑战：子智能体必须能生成有效的摘要，否则会产生误导。
- **要点**：本文的核心是验证"小模型能否在终端执行任务上替代前沿模型"这一命题。

## 2 背景与相关工作

### 中文翻译

我们的工作与编码智能体领域的几个研究线索相交并扩展，例如多智能体/子智能体架构、面向智能体工作负载的小型语言模型、面向多轮 LLM 智能体的 RL，以及 LLM-Judge/基于评分准则的奖励设计。下面我们逐一讨论。

#### 2.1 多智能体和子智能体架构

将复杂任务分解到多个智能体上已经得到了广泛研究。AutoGen [11] 提供了一个用于智能体间对话的灵活框架。MetaGPT [12]、ChatDev [13] 等作品探索了多智能体之间基于角色的协作。He 等人 [14] 系统性地回顾了基于 LLM 的软件工程多智能体系统的现状，强调了这些方法的当前能力和局限性。Anthropic 的多智能体研究 [15] 系统采用了编排者-工作者模式，其中领导智能体将任务委托给在隔离上下文中运行的专门化子智能体。Claude Code [3] 进一步将这种模式形式化为子智能体，内置了通用型和规划型子智能体，并支持编写自定义子智能体。我们的执行子智能体遵循相同的编排者-工作者模式，但专门针对编码智能体中的终端执行任务领域——这是一个特别容易出现冗长工具输出的任务。

#### 2.2 面向智能体任务的小型语言模型

越来越多的研究认为，小型语言模型对于智能体 AI 的未来至关重要 [16]。他们认为，智能体调用中的大部分涉及重复性任务，对于这些任务，SLM 不仅足够胜任，而且比前沿 LLM 便宜 10-30 倍。Qwen3 系列 [6] 代表了一个强大的开源 SLM 系列，具有原生工具调用能力，并且越来越多的研究表明，适当的后训练 [17, 18] 可以使它们在聚焦的任务上取得有竞争力的结果。Terminus-4B 将这些学习和原理应用于终端执行这一目标明确且影响深远的任务。

#### 2.3 终端任务和执行智能体

与我们领域最接近的可能是 TerminalBench [?]，它提供了一个在沙箱 Docker 环境中执行的实际命令行任务基准测试，发现前沿 LLM 仍然只能解决不到 65% 的任务，而较小的模型仅能达到约 15%。最近的编码智能体训练工作 [19, 20] 明确地将 Terminal-Bench 作为域外任务进行评估，以检验 LLM 是否能泛化到此类任务。与我们工作更相关的是，Gandhi 等人 [21] 通过程序生成终端任务，并使用 vanilla PPO 来训练用于终端使用的小模型。我们的工作与之不同，因为我们通过一种新颖的基于评分准则的奖励设计，在从 GitHub 问题中挖掘的任务上进行训练，并将终端执行视为一个可委托的子智能体，我们的目标是减少主智能体的 token 使用量。据我们所知，先前的工作将终端执行视为主智能体的能力，而不是可以委托给运行微调小模型的专门子智能体的任务。我们的工作填补了这一空白。

#### 2.4 长跨度任务的上下文管理

随着 LLM 和智能体能力的增长，它们的轨迹长度也在增长，上下文管理成为智能体设计中的一个重要关注点。长上下文会推高成本，并通过将注意力从轨迹中与任务相关的 token 上分散开来，从而降低推理能力。Focus [22] 引入了一个智能体，能够自主决定何时将关键学习内容整合到持久化块中，并主动修剪智能体交互历史。Sun 等人引入了 Context folding [23]，这是一个框架，允许智能体分支子轨迹以处理子任务，然后将它们折叠回主轨迹。Memex(RL) [24] 引入了带有简洁结构化摘要和稳定索引的紧凑上下文表示。SWE-ContextBench [25] 明确评估了摘要化和原始上下文如何影响编码智能体的能力。我们的子智能体方法与这些先前的方法是互补的。执行子智能体不是压缩上下文，而是拥有独立的智能体循环来运行冗长的终端命令，并阻止它们的输出进入主智能体的上下文，将其吸收在子智能体上下文中，只返回结构化摘要。

### 术语解释

- **multi-agent system（多智能体系统）**：由多个智能体协作完成任务的系统架构
- **orchestrator-worker pattern（编排者-工作者模式）**：一个中央智能体（编排者）分配任务给多个工作智能体
- **open-weight（开放权重）**：模型的权重参数公开可获取
- **tool calling（工具调用）**：LLM 调用外部工具/API 的能力
- **context folding（上下文折叠）**：将子轨迹折叠回主轨迹的上下文管理技术
- **post-training（后训练）**：在预训练之后对模型进行针对性优化的过程

### 图表/公式说明

本部分无图表/公式。

### 关键 takeaway

- **要点**：本文与现有子智能体/多智能体工作的区别在于专门聚焦于终端执行这一特定任务领域。
- **要点**：与 Gandhi 等人用 PPO 训练终端使用模型不同，本文使用基于评分准则的奖励+GRPO，并从 GitHub 问题中挖掘训练数据。
- **要点**：执行子智能体的方法（吸收输出在子智能体上下文中）与上下文压缩方法形成互补。

## 3 动机示例

### 中文翻译

在本节中，我们通过一个真实世界的例子来说明我们方法的优势。

图 1 展示了两个智能体轨迹，解决来自 Serilog C# 仓库（serilog/serilog #2053）的同一个任务。该问题要求智能体添加一个新的批处理 API 接口。由于这是一个全新的功能，智能体必须构建解决方案、运行单元测试、识别失败并应用必要的修复以使构建/测试错误消失。

当我们比较有子智能体和没有子智能体的智能体输出的轨迹时，我们看到了非常不同的结果。

在基线智能体中，每个终端命令将其完整的原始输出返回到智能体自己的上下文窗口中。在轨迹过程中，主智能体进行了 18 次直接的终端调用，其中许多是带有细微变化的重复调用，因为智能体尝试了 grep 和 tail 过滤器的不同组合来从冗长的构建和测试日志中提取相关信息。例如：

```
$ dotnet test ... 2>&1 | tail -40
$ dotnet test ... 2>&1 | grep -E "passed|failed|error"
$ dotnet test ... 2>&1 | grep -A 10 "Error Message"
$ dotnet test ... 2>&1 | grep -E "passed|failed|Error Message|Assert"
$ dotnet test ... 2>&1 | tail -20
...
```

每次调用都会向上下文中添加新的原始输出，这些输出会作为输入上下文发送给后续每一轮的 LLM。到轨迹结束时，智能体在 40 轮中消耗了 2.46M 主智能体 token，其中终端输出占用了大部分上下文。

在子智能体配置中，主智能体通过一次查询将同样的任务委托给执行子智能体（使用我们的 RL 训练模型 Terminus-4B）："运行构建，然后运行单元测试和验收测试，并报告通过/失败计数及错误详情"。

子智能体在子智能体上下文中内部执行了总计 9 个命令，并返回如下所示的最终答案：

```
<final_answer>
Command: dotnet build /testbed/Serilog.sln
Summary: Build succeeded. 9 warnings, 0 errors.
Command: dotnet test .../Serilog.Tests.csproj
Summary: All 769 tests passed, 0 failed, 0 skipped.
Command: dotnet test .../Serilog.ApprovalTests.csproj
Summary: Test Run Failed - 1 failed.
Error: Serilog.received.txt does not match Serilog.approved.txt.
The diff shows new API surface in LoggerAuditSinkConfiguration.
To fix: update the approved snapshot file.
</final_answer>
```

主智能体每次收到的不是完整的原始终端输出，而是一个约 200 token 的摘要，这立即识别出了导致测试失败的底层问题。总体而言，该轨迹在 32 轮中仅消耗了 740k 主智能体 token，远低于基线智能体。此外，由于子智能体使用的是 Terminus-4B，消耗的 token 成本仅为主智能体 token 成本的一小部分。这种对比突显了此类子智能体的必要性。

### 术语解释

- **trajectory（轨迹）**：智能体在解决一个任务过程中的完整交互序列
- **baseline（基线）**：作为比较基准的配置或方法
- **token usage（token 使用量）**：智能体在运行过程中消耗的 token 总数

### 图表/公式说明

- **Figure 1**：对比有/无执行子智能体时，Serilog 仓库中一个真实问题的智能体轨迹。无子智能体时（上方），主智能体必须直接调用终端命令，处理冗长的构建和测试输出，并花费额外轮次解释结果，消耗显著更多的 token 和轮次。使用子智能体时（下方），终端执行任务被委托给子智能体，子智能体吸收原始输出并仅以预定义格式的简洁最终答案返回关键发现。主智能体无需处理冗长的终端输出，从而保留了其上下文窗口。

  ![Figure 1: 有无执行子智能体的智能体轨迹对比](assets/assets/page-004-img-01.png)

### 关键 takeaway

- **要点**：一个真实案例显示，无子智能体时智能体消耗 2.46M token/40 轮，有子智能体时仅消耗 740k token/32 轮，节省约 70% token。
- **要点**：子智能体返回约 200 token 的结构化摘要，主智能体无需处理原始终端输出。
- **要点**：子智能体模式显著降低了上下文污染，使主智能体能专注于更高级的决策。

## 4 方法论

### 中文翻译

在本节中，我们描述执行子智能体的设计以及它如何集成到现有的编码智能体中，随后介绍用于生产 Terminus-4B 的后训练流程。图 2 展示了我们方法的高层概览。我们首先定义什么是子智能体：

**子智能体**：一个次级的基于 LLM 的智能体循环，由父智能体（或"主"智能体）调用以处理专门的子任务。与解决广泛任务的主智能体不同，子智能体处理更狭窄、通常更简单的任务集。与主智能体类似，子智能体有自己的系统提示、上下文窗口和工具集，用于实现主智能体委托给它的目标。

#### 4.1 执行子智能体

执行子智能体就是这样一种子智能体，专门用于顺序生成和执行终端命令，并向主智能体返回结构化结果摘要。

它作为简单的工具暴露给主智能体，只接受以下两个参数：

- **查询（必需）**：执行任务的自然语言描述，即要运行什么命令以及要报告什么信息。例如："运行测试套件并报告哪些测试失败以及它们的错误信息。"
- **描述（必需）**：在子智能体执行期间向用户 UI 显示的简短摘要。

子智能体返回一个结构化响应，其中包含每个已运行命令的摘要、其结果以及任何相关输出（错误信息、测试计数、构建状态），以 XML 风格的 `<final_answer>` 标签分隔。这种简单的查询-回答接口使主智能体免受原始终端输出的冗长信息的干扰。主智能体可以灵活地描述它希望运行什么以及返回什么，而子智能体负责实现具体过程。

##### 4.1.1 工具与轮次限制

执行子智能体只能访问一个工具：Terminal（终端）。该工具接受一个 shell 命令、一个执行模式（同步或异步）和一个以毫秒为单位的超时时间，并返回截断至 60KB 的 shell 命令输出。这正是给主智能体用于运行终端命令的同一个工具。

此外，我们还限制子智能体每轮只能调用一次该工具——即不支持并行工具调用，使用同步模式，并受可配置的轮次限制（默认为 10）。如果在子智能体自行退出前达到轮次限制，我们会注入一条用户消息（"好的，你分配的轮次已经用完。请显示 `<final_answer>`。"），引导子智能体给出最终答案。

这些约束旨在简化设计，使子智能体保持专注和可预测。子智能体没有获得读取文件、编辑代码或其他工具，只能运行终端命令。这种狭窄的范围正是使这项任务适合小型微调模型的原因。

##### 4.1.2 系统提示

图 3 显示了执行子智能体使用的系统提示。该提示指示模型：1）运行终端命令以完成委托的任务，根据需要进行命令调整；2）遵循终端工具使用的特定规则——即使用同步模式、设置显式超时、不并行调用；3）返回包含每个命令摘要的 `<final_answer>`，包括运行的命令和结果的简洁描述。提示还包括一个展示 2 步交互的示例。

（注：图 3 中提示的具体内容见原文第 7 页）

### 术语解释

- **system prompt（系统提示）**：指导 LLM 行为和工作方式的初始指令
- **turn limit（轮次限制）**：智能体在单次任务中允许的最大交互轮数
- **final_answer tag（最终答案标签）**：子智能体用于包裹最终结构化输出的 XML 标签
- **query-answer interface（查询-回答接口）**：一种简单的交互模式，主智能体发送查询，子智能体返回结构化的回答

### 图表/公式说明

- **Figure 2**：Terminus-4B 训练流程。❶ 首先将执行子智能体作为工具集成到主智能体框架中。❷ 然后在来自遥测数据的专家轨迹上对基础 Qwen3-4B 模型进行 SFT。❸ 接着在 GitHub 示例上使用 GRPO 进行 RL 训练，其中 rollout 由基于评分准则的 LLM-as-Judge 奖励根据前沿 LLM 生成的参考轨迹进行评分。

  ![Figure 2: Terminus-4B 训练流程](assets/assets/page-005-img-01.png)

### 关键 takeaway

- **要点**：执行子智能体只有一个工具（Terminal），且每轮只能调用一次，这种极简设计使小模型也能胜任。
- **要点**：子智能体通过简单的查询-回答接口与主智能体交互，主智能体无需处理原始终端输出。
- **要点**：轮次限制默认为 10，超限后自动引导子智能体给出最终答案。

#### 4.2 后训练流程

##### 4.2.1 监督式微调（SFT）

在本工作中，我们使用内部遥测数据构建了专家轨迹数据集。这些轨迹来自真实开发者在使用编码智能体时的会话，其中智能体被配置为使用执行子智能体，而子智能体运行的是前沿 LLM（Claude Opus/Sonnet）。

**数据收集**。我们从生产环境中收集遥测数据。每当主智能体调用执行子智能体时，我们记录以下内容：子智能体的系统提示、委托给它的查询、子智能体生成的完整轨迹（包括每轮的工具调用和 LLM 输出），以及最终的 `<final_answer>` 响应。

**轨迹过滤**。我们应用以下过滤标准来确保数据质量：1）子智能体必须正常退出（即未达到轮次限制），2）`<final_answer>` 必须格式正确且包含结构化摘要，3）子智能体轨迹必须包含至少一次 Terminal 工具调用。过滤后，我们得到 2,766 条轨迹。

**数据多样性**。收集的轨迹覆盖了多种类型的任务。表 2 显示了执行任务类型的分布。

表 2：收集的执行任务集中包含的任务类型。

| 任务类型（非排他性） | 数量 |
|---|---|
| 测试执行 | 2,692 (97.3%) |
| 构建/编译 | 969 (35.0%) |
| 错误诊断 | 2,166 (78.3%) |
| 依赖管理 | 106 (3.8%) |

我们发现，得到的轨迹包含了跨越 730 个仓库的 3,009 次唯一的执行子智能体调用。我们将这些轨迹作为我们的黄金标准参考轨迹。这些轨迹稍后将用于在 RL 过程中对我们的 rollout 进行评分。

**SFT 训练**。我们使用标准的语言建模目标（下一个 token 预测）对 Qwen3-4B-Instruct-2507 基座模型进行微调。我们将 2,766 条轨迹划分为训练集（2,500 条）和测试集（266 条），并训练了 3 个 epoch，学习率为 1e-5。训练使用 8×H100 GPU，DeepSpeed ZeRO-3，完成约需 2 小时。

**提示格式**。我们训练中使用的提示格式与推理时使用的系统提示相同（如图 3 所示）。每条训练样本包含完整的子智能体轨迹——从系统提示开始，到子智能体的工具调用和 LLM 响应，最后以 `<final_answer>` 结束。我们保留完整轨迹以保持对话结构的连续性。

##### 4.2.2 强化学习（RL）

在对模型进行 SFT 训练后，我们使用基于评分准则的 LLM-as-Judge 奖励进行 RL 训练。

**子智能体训练流程**。直接在主智能体环境中训练子智能体成本过高：每次 rollout 都需要运行完整的主智能体轨迹（可能消耗数百万 token）。为解决这个问题，我们设计了一个解耦的训练流程，将子智能体从主智能体循环中分离出来。具体来说：

1. 我们克隆找到子智能体调用的遥测轨迹。
2. 我们在主智能体调用子智能体的确切点截断轨迹——保留之前的上下文作为子智能体的"输入状态"。
3. 然后我们从这个状态开始运行子智能体 rollout，使用当前的策略模型。
4. rollout 完成后，我们将生成的子智能体响应注入到原始主智能体轨迹中的对应位置。
5. 然后我们使用 LLM-Judge 对这个合成的主智能体轨迹进行评分。

这种设计使我们能够在保持与真实主智能体轨迹一致的同时，以每个 rollout 仅数千 token 的成本运行子智能体训练。

**奖励设计**。我们基于评分准则的 LLM-as-Judge 奖励函数评估子智能体响应的质量。评判 LLM 接收以下输入：1）主智能体调用子智能体之前的上下文，2）子智能体接收到的查询，3）子智能体生成的响应，4）主智能体在子智能体调用后的后续轨迹。评判 LLM 在以下维度上对响应进行评分（0-1）：

- 任务完成度：子智能体是否完全完成了要求的工作？
- 事实准确性：响应是否基于事实？是否产生了幻觉？
- 信息丰富度：响应是否包含足够的主智能体继续工作的细节？
- 相关性：响应是否集中在任务上？
- 可操作性：主智能体是否可以根据响应确定明确的下一步？

总分为所有维度的平均值。

**训练细节**。我们使用 GRPO 算法进行 RL 训练。每组生成 8 个候选响应，KL 惩罚系数为 0.04。我们训练了 60 步，使用 8×H100 GPU。每步的 rollout 成本约为 15K token。整个 RL 训练约需 4 小时。

### 术语解释

- **telemetry（遥测数据）**：从生产系统中收集的使用数据和日志
- **gold-standard reference trajectory（黄金标准参考轨迹）**：由专家或高质量模型生成的标准答案轨迹
- **DeepSpeed ZeRO-3**：一种分布式深度学习训练优化技术
- **rollout**：在强化学习中，指策略在环境中执行以收集经验数据的过程
- **KL divergence（KL 散度）**：衡量两个概率分布之间差异的指标，在 RL 中用于约束策略更新幅度

### 图表/公式说明

- **Table 2**：执行任务类型分布。测试执行 2,692 次（97.3%），构建/编译 969 次（35.0%），错误诊断 2,166 次（78.3%），依赖管理 106 次（3.8%）。注意比例之和超过 100% 是因为一个轨迹可能包含多种任务类型。

### 关键 takeaway

- **要点**：SFT 数据来自真实生产环境中使用前沿 LLM 的子智能体轨迹，覆盖 730 个仓库、3,009 次调用。
- **要点**：RL 训练流程通过解耦子智能体与主智能体，实现了低成本（每 rollout 约 15K token）的高效训练。
- **要点**：奖励函数使用多维度的 LLM-as-Judge 评分，涵盖任务完成度、事实准确性、信息丰富度、相关性和可操作性五个维度。

## 5 评估设置

### 中文翻译

#### 5.1 基准测试

我们在两个基准测试上评估我们的方法：

**SWE-Bench Pro**[29]：一个多语言基准测试，涵盖 Python、JavaScript、TypeScript、Java、Go 等语言。我们使用 SWE-Bench Pro 的完整测试集，其中包含来自 GitHub 问题的 500 个真实软件工程任务。

**SWE-Bench C#**（内部）：由于 SWE-Bench 主要基于 Python 仓库，我们构建了一个内部的 C# 基准测试。该基准测试包含 150 个来自 C# 开源仓库（如 Serilog、Newtonsoft.Json、Dapper 等）的 GitHub 问题，专门针对终端执行任务较重的场景。所有评估在 Docker 容器中进行，使用沙箱环境确保可重复性。

#### 5.2 实验细节

##### 5.2.1 训练

SFT 和 RL 训练的详细超参数如下：

**SFT 超参数**：模型为 Qwen3-4B-Instruct-2507，训练 3 个 epoch，学习率 1e-5，批次大小 128，最大序列长度 8192。使用 AdamW 优化器，权重衰减 0.01，学习率预热 10% 的步数，线性衰减。训练在 8×H100 GPU 上进行，使用 DeepSpeed ZeRO-3，约需 2 小时。

**RL 超参数**：算法为 GRPO，组大小 8，KL 惩罚系数 0.04，学习率 1e-6，训练 60 步。每步 rollout 成本约 15K token。使用 8×H100 GPU，训练约需 4 小时。

##### 5.2.2 评估配置

我们在所有评估中使用以下配置：

- 主智能体模型：Claude Opus 4.6（默认），以及在消融中使用的 Claude Sonnet 4.5 和 GPT-5.3-Codex
- 子智能体模型：Terminus-4B（我们的模型）、SFT-4B（仅 SFT，无 RL）、Vanilla-4B（未训练的 Qwen3-4B）以及前沿模型子智能体（Claude Opus、Claude Sonnet）作为对比
- 子智能体轮次限制：10
- 主智能体终端工具：默认启用，消融中移除

##### 5.2.3 基线

我们评估以下三种配置：

- **无子智能体**：主智能体直接使用 Terminal 工具。这是标准的编码智能体设置。
- **子智能体 + Terminal 工具**：执行子智能体启用，同时 Terminal 工具可用。主智能体可以选择将终端工作委托给子智能体或直接使用 Terminal。
- **仅子智能体（无 Terminal）**：执行子智能体是主智能体可用的唯一终端执行工具。

##### 5.2.4 指标

对于所有配置，我们使用评估框架的输出来计算以下指标：

- **解决率（%）**：通过基准测试评估的实例比例。
- **Token 使用量**：主智能体/子智能体消耗的平均输入和输出 token 数。
- **主智能体 Terminal 调用次数**：主智能体直接调用 Terminal 工具的平均次数。
- **子智能体→Terminal 调用次数**：在执行子智能体之后立即调用 Terminal 工具的平均次数。我们预计这些情况中的大多数是主智能体因为子智能体的输出不够有用而不得不重做工作。
- **最终答案率（%）**：返回格式良好的 `<final_answer>` 标签的子智能体调用比例。
- **LLM-Judge 分数**：为了从主智能体的角度衡量最终答案的实用性，我们计算一个 LLM 分数。LLM 会获得子智能体调用之前的轨迹、最终响应以及子智能体调用后的 N=5 步，以评估结果是否实际被使用。LLM 被提示沿多个维度对最终响应进行评分。使用的提示如图 7 所示。

### 术语解释

- **ablation（消融实验）**：通过移除或修改某个组件来研究其对整体系统贡献的实验方法
- **SWE-Bench**：一个用于评估 AI 解决软件工程任务能力的主流基准测试集
- **sandbox environment（沙箱环境）**：隔离的、可重复的实验环境，通常使用 Docker 容器
- **resolve rate（解决率）**：智能体成功解决问题的比例

### 图表/公式说明

本部分无图表/公式。

### 关键 takeaway

- **要点**：评估使用两个基准测试——多语言的 SWE-Bench Pro（500 个任务）和内部的 SWE-Bench C#（150 个任务）。
- **要点**：评估三种配置：无子智能体（基线）、子智能体+Terminal（主智能体可自由选择）、仅子智能体（纯子智能体模式）。
- **要点**：核心指标包括解决率、token 使用量、主智能体 Terminal 调用次数、子智能体→Terminal "不信任"信号以及 LLM-Judge 评分。

## 6 结果

### 中文翻译

#### 6.1 RL 训练

图 6 显示了两种配置在训练过程中奖励和 KL 散度的变化趋势：将 GRPO 直接应用于基础 Qwen3-4B-Instruct-2507 模型（即无 SFT），以及从 SFT 检查点开始进行 GRPO。

比较奖励图，我们可以看到"无 SFT"运行的奖励在大约 20 处趋于平稳，与运行初期看到的基线分数相比未能改善。然而，KL 散度迅速上升到超过 0.2，表明策略在没有显著学习的情况下大幅偏离了参考模型。我们认为这是因为基础模型缺乏对这项任务的基本理解（如输出格式等），并且在训练过程中未能偶然发现这些行为以提供 GRPO 所需的梯度信号来强制执行这些行为。

与此形成鲜明对比的是，从 SFT 检查点开始的 RL 运行在更高的奖励（约 37）下开始，并稳步攀升至 50+，同时 KL 保持在接近 SFT 检查点的水平（0.05 以内）。直觉上，这是因为 SFT 能够为模型提供任务机制的良好起始知识——即期望的输出格式是什么、Terminal 工具的使用方式等。这些结果证实 SFT 不仅是有帮助的，而且是必不可少的。我们将 RL 训练得到的最终模型称为 Terminus-4B 模型。我们通过消融实验展示了 RL 训练本身的效用。

#### 6.2 基准测试消融实验

在本小节中，我们讨论在评估设置中的基准测试上进行的各种消融实验。

##### 6.2.1 跨语言泛化（通过 SWE-Bench Pro）

为了测试执行子智能体架构和 Terminus-4B 是否能泛化到不同语言，我们在 SWE-Bench Pro [29] 上进行了评估，这是一个涵盖 Python、JavaScript、TypeScript、Java、Go 等的多语言基准测试。我们在所有子智能体配置中使用 Claude Opus 4.6 作为主智能体模型。表 3 显示了结果。

表 3：使用 Claude Opus 4.6 作为主智能体模型时，不同模型作为执行子智能体在 SWE-Bench Pro 上的结果。

| 子智能体配置 | 解决率 % | 主智能体 Token | 子智能体 Token | 前沿 LLM Token | 主智能体 Terminal | 子→Terminal | 最终答案 % |
|---|---|---|---|---|---|---|---|
| 无子智能体 | 30.0 | 836k | - | 836k | 3.8 | - | - |
| Opus | 32.0 | 729k (-12.8%) | 19k | 748k (-10.5%) | 0.5 (-86.8%) | 0.04 | 100.0 |
| Sonnet | 32.6 | 756k (-9.6%) | 19k | 774k (-7.4%) | 0.6 (-84.2%) | 0.06 | 100.0 |
| Vanilla-4B | 30.4 | 840k (+0.5%) | 6k | 840k (+0.5%) | 1.9 (-50.0%) | 0.27 | 99.0 |
| SFT-4B | 32.4 | 727k (-13.0%) | 17k | 727k (-13.0%) | 1.1 (-71.1%) | 0.17 | 98.5 |
| Terminus-4B | 31.5 | 730k (-12.7%) | 18k | 730k (-12.7%) | 1.0 (-73.7%) | 0.14 | 97.9 |

我们看到，在 token 使用量方面，所有子智能体配置都比无子智能体配置有所改善。我们还看到智能体在基准测试上的性能没有受到影响，因为所有解决率百分比都接近 30% 的基线解决率。这证实了将终端执行委托给子智能体在复杂编码任务中是有益的。

关于前沿 token 使用量，我们看到 SFT-4B 和 Terminus-4B 都节省了约 13%（或每实例约 110k token），高于 Sonnet 或 Opus 作为子智能体时的前沿 LLM token 使用量。相比而言，原始 Qwen3-4B 模型的 token 使用量实际上比基线增加了约 0.5%，因为主智能体可能不得不通过自行运行 Terminal 命令来补偿子智能体无用的响应——从高的子智能体→Terminal 值（0.27）可以看出，这意味着超过四分之一的执行子智能体调用之后紧接着是主智能体的 Terminal 调用。这清楚地表明我们的训练相比原始模型有所改进。

更仔细地看行为指标，主智能体的 Terminal 使用量从每实例平均 3.8 次调用下降到我们 RL 训练模型的 1 次，减少了约 74%。相比原始模型（1.9）和 SFT 模型（1.1），这是一个改进。我们还看到 Terminus-4B 的子智能体→Terminal 值也有类似降低，只有 14% 的子智能体调用之后跟随主智能体的终端使用。虽然这与 Opus 和 Sonnet 在此指标上的表现（分别为 4% 和 6%）仍有差距，但相比原始模型和 SFT 模型已是很大进步。这些结果表明，在后训练中学到的执行行为——即 Terminal 工具使用模式、通过有效摘要生成最终答案——能够有效跨编程语言迁移。

##### 6.2.2 跨主智能体模型泛化（通过 SWE-Bench C#）

为了测试子智能体和 Terminus-4B 是否能够与不同的前沿 LLM 主智能体协同工作，我们在 SWE-Bench C# 上使用三个主智能体模型进行了评估：Claude Opus 4.6、Claude Sonnet 4.5 和 GPT-5.3-Codex。

表 4：不同子智能体和主智能体模型组合在 SWE-Bench C# 上的解决率（%）和子智能体调用率。

| 子智能体 | Claude Opus 4.6 | | Claude Sonnet 4.5 | | GPT-5.3-Codex | |
|---|---|---|---|---|---|---|
| | 解决率 % | 调用率 % | 解决率 % | 调用率 % | 解决率 % | 调用率 % |
| 无子智能体 | 46.7 | - | 47.3 | - | 38.0 | - |
| Opus | 46.0 | 94.6 | 46.7 | 75.3 | 40.3 | 89.3 |
| Sonnet | 46.0 | 93.3 | 44.7 | 72.0 | 40.7 | 90.7 |
| Vanilla-4B | 44.0 | 91.0 | 44.0 | 74.3 | 36.9 | 87.1 |
| SFT-4B | 47.0 | 95.3 | 44.0 | 73.2 | 42.0 | 89.9 |
| Terminus-4B | 46.7 | 89.3 | 46.7 | 74.7 | 38.0 | 85.3 |

从表 4 中，我们可以看到所有子智能体配置的解决率保持相当稳定，Terminus-4B 在所有主智能体模型下都与无子智能体基线持平或接近。这证实了子智能体不会降低智能体的端到端性能，无论主智能体模型如何。调用率显示不同模型选择调用子智能体的频率。我们看到 Opus 更可能调用执行子智能体（超过 90% 的实例），而 Sonnet 略低（约 72-75%）。

在 token 效率指标方面，Terminus-4B 在 Claude Opus 4.6 和 GPT-5.3-Codex 上实现了最大的主智能体和前沿 LLM token 缩减——这些场景中 subagent 使用率保持较高。我们可以清楚地看到，这些 token 使用量的减少高于前沿 LLM 作为子智能体时的水平。对于 Sonnet 作为主智能体，定制训练模型的表现与 Opus 和 Sonnet 作为子智能体相当。原始 Qwen3-4B 模型在所有场景中展示了最弱的节省效果，显示了针对此任务进行后训练的重要性。

最后，行为指标在所有三个主智能体中也展现出一致的模式。Terminus-4B 将主智能体的 Terminal 调用次数相比无子智能体基线减少了 62-79%。我们还看到后训练降低了子智能体→Terminal 的不信任信号。Terminus-4B 在所有主智能体模型上，在不信任信号方面相比原始模型和 SFT 都有显著改进。这表明 RL 带来的质量改进具有鲁棒性，并且能够跨不同主智能体模型迁移。

表 5：不同模型作为执行子智能体、不同主智能体模型在 SWE-Bench C# 上的结果。

| 子智能体 | Claude Opus 4.6 | | | | Claude Sonnet 4.5 | | | | GPT-5.3 Codex | | | |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| | Main | Sub | Frontier | SLM | Main | Sub | Frontier | SLM | Main | Sub | Frontier | SLM |
| 无子智能体 | 1,010k | - | 1,010k | - | 1,496k | - | 1,496k | - | 1,036k | - | 1,036k | - |
| Opus | 710k (-29.7%) | 25k | 734k | - | 1,125k (-24.8%) | 26k | 1,151k | - | 764k (-26.3%) | 25k | 789k | - |
| Sonnet | 757k (-25.0%) | 27k | 784k | - | 1,074k (-28.2%) | 28k | 1,102k | - | 758k (-26.8%) | 30k | 789k | - |
| Vanilla-4B | 802k (-20.6%) | 11k | 802k | 11k | 1,460k (-2.4%) | 9k | 1,460k | 9k | 902k (-12.9%) | 12k | 902k | 12k |
| SFT-4B | 833k (-17.5%) | 23k | 833k | 23k | 1,109k (-25.9%) | 24k | 1,109k | 24k | 726k (-29.9%) | 36k | 726k | 36k |
| Terminus-4B | 693k (-31.4%) | 25k | 693k | 25k | 1,177k (-21.3%) | 27k | 1,177k | 27k | 704k (-32.0%) | 42k | 704k | 42k |

| | 主智能体 Terminal & 子智能体→Terminal | | | | | | | | | | |
|---|---|---|---|---|---|---|---|---|---|---|---|
| | Main Terminal | Sub→Terminal | | Main Terminal | Sub→Terminal | | Main Terminal | Sub→Terminal |
| 无子智能体 | 6.2 | - | | 6.3 | - | | 4.2 | - |
| Opus | 0.7 (-88.7%) | 0.09 | | 1.0 (-84.1%) | 0.06 | | 0.0 (-100%) | 0.00 |
| Sonnet | 0.9 (-85.5%) | 0.13 | | 1.1 (-82.5%) | 0.11 | | 0.1 (-97.6%) | 0.02 |
| Vanilla-4B | 2.5 (-59.7%) | 0.39 | | 3.6 (-42.9%) | 0.36 | | 1.4 (-66.7%) | 0.43 |
| SFT-4B | 2.1 (-66.1%) | 0.31 | | 2.1 (-66.7%) | 0.23 | | 0.8 (-81.0%) | 0.25 |
| Terminus-4B | 1.7 (-72.6%) | 0.23 | | 2.4 (-61.9%) | 0.17 | | 0.9 (-78.6%) | 0.19 |

##### 6.2.3 移除 Terminal 工具

为了隔离子智能体的质量与主智能体通过自行运行 Terminal 工具来补偿不良响应的能力，我们运行了一个消融实验，其中从主智能体中完全移除 Terminal 工具。在这种配置下，所有终端执行都必须通过执行子智能体进行。这提供了对不同子智能体模型质量的清晰比较和压力测试。我们使用 Claude Opus 4.6 作为主智能体。此外，我们不显示先前评估中的子智能体→Terminal 指标，而是显示子智能体→子智能体作为衡量主智能体需要重复子智能体调用频率的指标。

表 6：从主智能体中移除 Terminal 工具后在 SWE-Bench C# 上的结果（Claude Opus 4.6 作为主智能体）。

| 子智能体 | 解决率 % | 主智能体 Token | 子智能体 Token | 前沿 LLM Token | SLM Token | 子调用次数 | 子→子 | 最终答案 % |
|---|---|---|---|---|---|---|---|---|
| Opus | 45.3 | 704k | 35k | 740k | - | 2.4 | 0.89 | 100.0 |
| Sonnet | 48.0 | 632k | 33k | 664k (-10.3%) | - | 2.3 | 0.76 (-14.6%) | 99.4 |
| Vanilla-4B | 44.7 | 810k | 18k | 810k (+9.5%) | 18k | 3.1 | 1.51 (+69.7%) | 99.4 |
| SFT-4B | 45.3 | 590k | 32k | 590k (-20.3%) | 32k | 2.5 | 1.07 (+20.2%) | 98.7 |
| Terminus-4B | 45.9 | 605k | 34k | 605k (-18.2%) | 34k | 2.4 | 0.89 (0.0%) | 98.9 |

再次，所有配置的解决率仍然相当（44-48% 范围），确认即使没有 Terminal 工具访问权，执行子智能体也足以让主智能体有意义地完成任务。我们还看到 Terminus-4B 能够以极低的成本像前沿模型一样有效地执行这一角色。

没有主智能体调用 Terminal 工具的能力后，子智能体质量的影响变得尤为明显。原始 Vanilla-4B 模型实际上使 token 使用量超过了 Opus 基线（+9.5%），并表现出 1.51 的子→子率，意味着主智能体平均每实例重新调用子智能体超过 1.5 次，比 Opus 增加了约 70%。我们还看到子智能体轨迹太短（仅 18k token），表明它们可能缺乏主智能体继续工作所需的细节。相比之下，我们看到 SFT 和 Terminus-4B 模型在前沿 LLM token 消耗方面相比原始模型和 Opus 基线都有显著改善（约 20%）。我们还看到 SFT 和 Terminus 模型的子智能体轨迹 token 消耗也更高，从 SLM token 使用量可以看出。

比较 SFT 和 RL 模型，我们看到不信任指标子→子率从 SFT 到 Terminus-4B 有所改善，从超过 1.0 降低到每实例 0.89，与 Opus 持平。这表明 RL 阶段在教会模型生成一次就能满足主智能体的响应方面至关重要。

##### 6.2.4 通过 LLM-Judge 评估响应质量

为了从主智能体的角度衡量子智能体响应的实用性，我们还采用了 LLM-as-a-Judge 评估。我们使用 Claude Opus-4.6 作为评判模型，并提示它根据子智能体调用前的主智能体轨迹以及之后 N 步的轨迹来对子智能体响应进行评分。我们将 N 设为 5，因为我们相信这应该足以观察主智能体使用该响应的能力。

图 8：LLM-Judge 对子智能体响应质量的评分分布（无 Terminal 消融实验中，从主智能体视角评估）。

评判维度包括：
- **任务完成度**：子智能体是否完全完成了被要求的任务？
- **事实准确性**：子智能体的断言是否基于事实？是否产生幻觉？
- **信息丰富度**：响应是否包含足够的细节以让主智能体无需重新运行命令就可继续？
- **相关性**：响应是否集中在任务上？是否做了不必要的工作？
- **可操作性**：主智能体是否可以根据响应确定明确的下一步？

总分为五个维度的平均值。我们在无 Terminal 工具消融实验的运行上运行此评估。评判提示包含以下信息：1）主智能体的系统提示和原始问题描述，2）子智能体调用之前的轨迹（先前的工具调用和结果），3）子智能体查询和响应，以及 4）主智能体收到子智能体响应后的后续 5 轮轨迹。后续轨迹在这里很关键，因为它为评判者提供了理解主智能体如何回应子智能体响应以及是否能直接使用它（还是需要以不同的查询重新调用子智能体）的能力。

观察结果，我们可以看到 Terminus-4B 的得分与前沿 LLM 相当。有趣的是，我们发现 Sonnet 实际上在这项评估中表现最好。Terminus-4B 的结果似乎接近 Sonnet 的水平，且略好于 Opus。这与该配置中 Opus 和 Terminus-4B 的子→子不信任指标相等的结果一致（见表 6）。

具体比较小模型之间的分数，我们可以清楚地看到 Terminus-4B 的中位分数高于 SFT-4B。SFT 和 Terminus-4B 都比原始模型更好，显示了后训练两个阶段的重要性。

### 术语解释

- **KL divergence（KL 散度）**：衡量策略模型与参考模型之间差异的指标
- **GRPO（Group Relative Policy Optimization）**：一种强化学习优化算法
- **checkpoint（检查点）**：训练过程中保存的模型参数快照
- **ablation study（消融研究）**：通过逐一移除组件来研究其贡献的实验

### 图表/公式说明

本部分包含以下图表：
- **Figure 6**：GRPO 训练曲线。左图显示奖励随训练步数的变化：无 SFT 的 GRPO 奖励趋于平缓（约 20），而 SFT 后的 GRPO 从约 37 稳步攀升至 50+。右图显示 KL 散度：无 SFT 的 KL 快速上升至超过 0.2，SFT 后的 KL 保持在 0.05 以内。

- **Table 3**：SWE-Bench Pro 结果表。Terminus-4B 实现 31.5% 解决率（基线 30.0%），前沿 LLM token 节省 12.7%（约 110k token/实例），主智能体 Terminal 调用从 3.8 降至 1.0（-73.7%）。
- **Table 4**：SWE-Bench C# 结果表（子智能体调用率）。Terminus-4B 在所有三个主智能体模型上解决率与基线相当。
- **Table 5**：SWE-Bench C# 详细 token 和行为指标表。Terminus-4B 实现主智能体 token 最高节省 32.0%（GPT-5.3-Codex 作为主智能体）。
- **Table 6**：无 Terminal 消融结果表。Terminus-4B 的子→子率为 0.89，与 Opus 持平，远优于原始模型的 1.51。
- **Figure 8**：LLM-Judge 评分分布图。Terminus-4B 的评分与前沿 LLM 相当。

### 关键 takeaway

- **要点**：SFT 是 RL 训练的必要前提——无 SFT 时 GRPO 无法学习到有效策略，KL 快速发散。
- **要点**：Terminus-4B 在 SWE-Bench Pro 上实现约 13% 前沿 token 节省，同时保持解决率（31.5% vs 基线 30.0%）。
- **要点**：在无 Terminal 消融中（最严格的测试），Terminus-4B 的子→子率与 Opus 持平（0.89），证明 RL 阶段显著提升了响应质量。
- **要点**：Terminus-4B 的行为改进（主智能体 Terminal 调用减少 62-79%）跨不同主智能体模型（Claude、GPT）迁移良好。

## 7 局限性

### 中文翻译

虽然我们的结果证明，经过微调的小型语言模型能够在编码智能体的终端执行任务上有效替代前沿 LLM，但仍存在若干局限性：

**平台/Shell 覆盖范围**。我们的训练和评估都偏向于基于 Unix/Bash 的终端任务。我们没有包含来自其他 shell 的任务，如 Windows 的 Powershell 或 Command Prompt，或 Mac 的 Zsh，尽管这些在实际开发中很常见。将 Terminus-4B 扩展到处理这些其他 shell 是这项工作未来的自然方向。

**评估范围**。我们的评估几乎完全在 SWE-Bench 风格的基准测试上进行，这些基准测试源自 GitHub 问题，通过在已包含项目所需依赖的 Docker 容器中运行智能体来解决。虽然这与先前文献中的编码智能体评估一致，但这可能无法反映智能体的真实使用场景，后者可能更加复杂和混乱，可能包含从调试应用到部署或基础设施级别任务的无数任务。

**基座模型选择**。我们仅基于 Qwen3-4B 模型进行训练，这代表了此类任务的一个合理大小和模型系列。我们的结果证明，一个 4B 参数的模型经过充分训练可以胜任此任务，但我们的研究排除了更大的模型（8B、30B 等）以及其他模型系列。相同的后训练配方是否能有效迁移到其他系列/模型大小仍有待验证。

### 术语解释

- **shell**：命令行解释器，如 Bash、PowerShell、Zsh
- **SWE-Bench style benchmark**：以 SWE-Bench 为模板的基准测试，从 GitHub 问题中提取任务
- **post-training recipe（后训练配方）**：后训练的超参数和配置组合

### 图表/公式说明

本部分无图表/公式。

### 关键 takeaway

- **要点**：论文仅测试了 Unix/Bash 环境，未覆盖 Windows/Mac 的 shell。
- **要点**：评估仅限于 SWE-Bench 风格的 GitHub 问题解决任务，可能无法完全代表真实编码场景。
- **要点**：仅基于 Qwen3-4B 训练，未探索更大模型或其他模型系列。

## 8 结论

### 中文翻译

在这项工作中，我们提出了执行子智能体和 Terminus-4B——一个 4B 参数的语言模型，经过微调以作为编码智能体内的执行子智能体。

通过两阶段后训练流程，我们证明即使是一个小型语言模型，也能在终端执行这一狭窄任务上与前沿 LLM 表现相当或更优，同时将前沿 LLM 的 token 使用量减少高达约 30%。

我们在 SWE-Bench Pro 和 SWE-Bench C# 等基准测试上的广泛评估证明，Terminus-4B 能跨编程语言和主智能体模型选择（涵盖 Claude 和 GPT 两个流行模型系列）进行泛化。

我们评估中的行为指标证实，后训练显著改善了原始 Qwen3-4B 模型，且主智能体学会了以与前沿 LLM 相同的水平依赖 Terminus-4B 的响应，很少需要重做工作。

更广泛地说，我们的工作还展示了一种实用的范式：将较小的 LM 训练为子智能体，并通过将 token 使用分流到子智能体来降低运行编码智能体的成本。子智能体架构提供了一种自然的方式，将复杂任务分解为较小的子任务，这些子任务可以在不同能力的模型之间共享。

我们相信，我们的结果直接适用于其他类型的子智能体，并提供了一条可扩展的路径，通向更有能力、更具成本效益且对所有人都更可及的编码智能体。

### 术语解释

- **paradigm（范式）**：一种通用的方法论或模式
- **cost-effective（成本效益高的）**：以较低成本获得较好效果
- **accessible（可及的）**：易于获得和使用

### 图表/公式说明

本部分无图表/公式。

### 关键 takeaway

- **要点**：Terminus-4B 证明了小模型（4B）在特定窄任务上可以替代前沿模型，节省约 30% token 成本。
- **要点**：子智能体架构为降低编码智能体运行成本提供了可扩展的范式。
- **要点**：本文的方法可以直接推广到其他类型的子智能体。

## 参考文献

[1] Microsoft, "VSCode Agent Mode," https://code.visualstudio.com/blogs/2025/04/07/agentMode, 2025, accessed: 2025-09-28.

[2] X. Wang, B. Li, Y. Song, F. F. Xu, X. Tang, M. Zhuge, J. Pan, Y. Song, B. Li, J. Singh, H. H. Tran, F. Li, R. Ma, M. Zheng, B. Qian, Y. Shao, N. Muennighoff, Y. Zhang, B. Hui, J. Lin, R. Brennan, H. Peng, H. Ji, and G. Neubig, "Opendevin: An open platform for ai software developers as generalist agents," 2024. [Online]. Available: https://arxiv.org/abs/2407.16741

[3] Anthropic, "Claude for Coding," https://www.anthropic.com/claude-code, 2024, accessed: 2025-07-14.

[4] J. Yang, C. E. Jimenez, A. Wettig, K. Lieret, S. Yao, K. Narasimhan, and O. Press, "Swe-agent: Agent-computer interfaces enable automated software engineering," 2024. [Online]. Available: https://arxiv.org/abs/2405.15793

[5] S. Garg and Y. Huang, "Debug2fix: Can interactive debugging help coding agents fix more bugs?" 2026. [Online]. Available: https://arxiv.org/abs/2602.18571

[6] A. Yang, A. Li, B. Yang, B. Zhang, B. Hui, B. Zheng, B. Yu, C. Gao, C. Huang, C. Lv, C. Zheng, D. Liu, F. Zhou, F. Huang, F. Hu, H. Ge, H. Wei, H. Lin, J. Tang, J. Yang, J. Tu, J. Zhang, J. Yang, J. Yang, J. Zhou, J. Zhou, J. Lin, K. Dang, K. Bao, K. Yang, L. Yu, L. Deng, M. Li, M. Xue, et al., "Qwen3 technical report," 2025. [Online]. Available: https://arxiv.org/abs/2505.09388

[7] Z. Shao, P. Wang, Q. Zhu, R. Xu, J. Song, X. Bi, H. Zhang, M. Zhang, Y. K. Li, Y. Wu, and D. Guo, "Deepseekmath: Pushing the limits of mathematical reasoning in open language models," 2024. [Online]. Available: https://arxiv.org/abs/2402.03300

[8] L. Zheng, W.-L. Chiang, Y. Sheng, S. Zhuang, Z. Wu, Y. Zhuang, Z. Lin, Z. Li, D. Li, E. P. Xing, H. Zhang, J. E. Gonzalez, and I. Stoica, "Judging llm-as-a-judge with mt-bench and chatbot arena," 2023. [Online]. Available: https://arxiv.org/abs/2306.05685

[9] H. Hashemi, J. Eisner, C. Rosset, B. Van Durme, and C. Kedzie, "Llm-rubric: A multidimensional, calibrated approach to automated evaluation of natural language texts," in Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers). Association for Computational Linguistics, 2024, p. 13806–13834. [Online]. Available: http://dx.doi.org/10.18653/v1/2024.acl-long.745

[10] L. Ouyang, J. Wu, X. Jiang, D. Almeida, C. L. Wainwright, P. Mishkin, C. Zhang, S. Agarwal, K. Slama, A. Ray, J. Schulman, J. Hilton, F. Kelton, L. Miller, M. Simens, A. Askell, P. Welinder, P. Christiano, J. Leike, and R. Lowe, "Training language models to follow instructions with human feedback," 2022. [Online]. Available: https://arxiv.org/abs/2203.02155

[11] Q. Wu, G. Bansal, J. Zhang, Y. Wu, B. Li, E. Zhu, L. Jiang, X. Zhang, S. Zhang, J. Liu, A. H. Awadallah, R. W. White, D. Burger, and C. Wang, "Autogen: Enabling next-gen llm applications via multi-agent conversation," 2023. [Online]. Available: https://arxiv.org/abs/2308.08155

[12] S. Hong, M. Zhuge, J. Chen, X. Zheng, Y. Cheng, C. Zhang, J. Wang, Z. Wang, S. K. S. Yau, Z. Lin, L. Zhou, C. Ran, L. Xiao, C. Wu, and J. Schmidhuber, "Metagpt: Meta programming for a multi-agent collaborative framework," 2024. [Online]. Available: https://arxiv.org/abs/2308.00352

[13] C. Qian, W. Liu, H. Liu, N. Chen, Y. Dang, J. Li, C. Yang, W. Chen, Y. Su, X. Cong, J. Xu, D. Li, Z. Liu, and M. Sun, "Chatdev: Communicative agents for software development," 2024. [Online]. Available: https://arxiv.org/abs/2307.07924

[14] J. He, C. Treude, and D. Lo, "Llm-based multi-agent systems for software engineering: Literature review, vision and the road ahead," 2025. [Online]. Available: https://arxiv.org/abs/2404.04834

[15] Anthropic. (2025) How we built our multi-agent research system. Published June 13, 2025. [Online]. Available: https://www.anthropic.com/engineering/built-multi-agent-research-system

[16] P. Belcak, G. Heinrich, S. Diao, Y. Fu, X. Dong, S. Muralidharan, Y. C. Lin, and P. Molchanov, "Small language models are the future of agentic ai," 2025. [Online]. Available: https://arxiv.org/abs/2506.02153

[17] D. Guo, D. Yang, H. Zhang, J. Song, P. Wang, Q. Zhu, R. Xu, R. Zhang, S. Ma, X. Bi, X. Zhang, X. Yu, Y. Wu, Z. F. Wu, Z. Gou, Z. Shao, Z. Li, Z. Gao, A. Liu, B. Xue, B. Wang, B. Wu, B. Feng, C. Lu, C. Zhao, C. Deng, C. Ruan, D. Dai, D. Chen, D. Ji, E. Li, F. Lin, F. Dai, F. Luo, G. Hao, G. Chen, G. Li, H. Zhang, H. Xu, H. Ding, H. Gao, H. Qu, H. Li, J. Guo, J. Li, J. Chen, J. Yuan, J. Tu, J. Qiu, J. Li, J. L. Cai, J. Ni, J. Liang, J. Chen, K. Dong, K. Hu, K. You, K. Gao, K. Guan, K. Huang, K. Yu, L. Wang, L. Zhang, L. Zhao, L. Wang, L. Zhang, L. Xu, L. Xia, M. Zhang, M. Zhang, M. Tang, M. Zhou, M. Li, M. Wang, M. Li, N. Tian, P. Huang, P. Zhang, Q. Wang, Q. Chen, Q. Du, R. Ge, R. Zhang, R. Pan, R. Wang, R. J. Chen, R. L. Jin, R. Chen, S. Lu, S. Zhou, S. Chen, S. Ye, S. Wang, S. Yu, S. Zhou, S. Pan, S. S. Li, S. Zhou, S. Wu, T. Yun, T. Pei, T. Sun, T. Wang, W. Zeng, W. Liu, W. Liang, W. Gao, W. Yu, W. Zhang, W. L. Xiao, W. An, X. Liu, X. Wang, X. Chen, X. Nie, X. Cheng, X. Liu, X. Xie, X. Liu, X. Yang, X. Li, X. Su, X. Lin, X. Q. Li, X. Jin, X. Shen, X. Chen, X. Sun, X. Wang, X. Song, X. Zhou, X. Wang, X. Shan, Y. K. Li, Y. Q. Wang, Y. X. Wei, Y. Zhang, Y. Xu, Y. Li, Y. Zhao, Y. Sun, Y. Wang, Y. Yu, Y. Zhang, Y. Shi, Y. Xiong, Y. He, Y. Piao, Y. Wang, Y. Tan, Y. Ma, Y. Liu, Y. Guo, Y. Ou, Y. Wang, Y. Gong, Y. Zou, Y. He, Y. Xiong, Y. Luo, Y. You, Y. Liu, Y. Zhou, Y. X. Zhu, Y. Huang, Y. Li, Y. Zheng, Y. Zhu, Y. Ma, Y. Tang, Y. Zha, Y. Yan, Z. Z. Ren, Z. Ren, Z. Sha, Z. Fu, Z. Xu, Z. Xie, Z. Zhang, Z. Hao, Z. Ma, Z. Yan, Z. Wu, Z. Gu, Z. Zhu, Z. Liu, Z. Li, Z. Xie, Z. Song, Z. Pan, Z. Huang, Z. Xu, Z. Zhang, and Z. Zhang, "Deepseek-r1 incentivizes reasoning in llms through reinforcement learning," Nature, vol. 645, no. 8081, p. 633–638, 2025. [Online]. Available: http://dx.doi.org/10.1038/s41586-025-09422-z

[18] Q.-A. Dang and C. Ngo, "Reinforcement learning for reasoning in small llms: What works and what doesn't," 2026. [Online]. Available: https://arxiv.org/abs/2503.16219

[19] R. Cao, M. Chen, J. Chen, Z. Cui, Y. Feng, B. Hui, Y. Jing, K. Li, M. Li, J. Lin, Z. Ma, K. Shum, X. Wang, J. Wei, J. Yang, J. Zhang, L. Zhang, Z. Zhang, W. Zhao, and F. Zhou, "Qwen3-coder-next technical report," 2026. [Online]. Available: https://arxiv.org/abs/2603.00729

[20] S. Cao, D. Li, F. Zhao, S. Yuan, S. R. Hegde, C. Chen, C. Ruan, T. Griggs, S. Liu, E. Tang, R. Liaw, P. Moritz, M. Zaharia, J. E. Gonzalez, and I. Stoica, "Skyrl-agent: Efficient rl training for multi-turn llm agent," 2025. [Online]. Available: https://arxiv.org/abs/2511.16108

[21] K. Gandhi, S. Garg, N. D. Goodman, and D. Papailiopoulos, "Endless terminals: Scaling rl environments for terminal agents," 2026. [Online]. Available: https://arxiv.org/abs/2601.16443

[22] N. Verma, "Active context compression: Autonomous memory management in llm agents," 2026. [Online]. Available: https://arxiv.org/abs/2601.07190

[23] W. Sun, M. Lu, Z. Ling, K. Liu, X. Yao, Y. Yang, and J. Chen, "Scaling long-horizon llm agent via context-folding," 2025. [Online]. Available: https://arxiv.org/abs/2510.11967

[24] Z. Wang, H. Chen, J. Wang, and W. Wei, "Memex(rl): Scaling long-horizon llm agents via indexed experience memory," 2026. [Online]. Available: https://arxiv.org/abs/2603.04257

[25] J. Zhu, M. Hu, and J. Wu, "Swe context bench: A benchmark for context learning in coding," 2026. [Online]. Available: https://arxiv.org/abs/2602.08316

[26] Fireworks AI, "Fireworks AI: Fast inference platform," https://fireworks.ai, 2025.

[27] THUDM, "Slime: Distributed training framework," https://github.com/THUDM/slime, 2025.

[28] Q. Yu, Z. Zhang, R. Zhu, Y. Yuan, X. Zuo, Y. Yue, W. Dai, T. Fan, G. Liu, L. Liu, X. Liu, H. Lin, Z. Lin, B. Ma, G. Sheng, Y. Tong, C. Zhang, M. Zhang, W. Zhang, H. Zhu, J. Zhu, J. Chen, J. Chen, C. Wang, H. Yu, Y. Song, X. Wei, H. Zhou, J. Liu, W.-Y. Ma, Y.-Q. Zhang, L. Yan, M. Qiao, Y. Wu, and M. Wang, "Dapo: An open-source llm reinforcement learning system at scale," 2025. [Online]. Available: https://arxiv.org/abs/2503.14476

[29] X. Deng, J. Da, E. Pan, Y. Y. He, C. Ide, K. Garg, N. Lauffer, A. Park, N. Pasari, C. Rane, K. Sampath, M. Krishnan, S. Kundurthy, S. Hendryx, Z. Wang, V. Bharadwaj, J. Holm, R. Aluri, C. B. C. Zhang, N. Jacobson, B. Liu, and B. Kenstler, "Swe-bench pro: Can ai agents solve long-horizon software engineering tasks?" 2025. [Online]. Available: https://arxiv.org/abs/2509.16941

[30] OpenAI, "Introducing swe-bench verified," https://openai.com/index/introducing-swe-bench-verified/, 2024, published August 13, 2024; updated February 24, 2025. [Online]. Available: https://openai.com/index/introducing-swe-bench-verified/

## 复核建议

- 对关键公式、表格和实验结论做抽样核对。
- 如已接入真实模型，可重新运行该论文以覆盖 mock 内容。
