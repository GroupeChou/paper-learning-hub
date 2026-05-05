# SWE-Edit: Rethinking Code Editing for Efficient SWE-Agent

<!-- 论文元数据卡片 -->
<div class="paper-meta">
  <div class="paper-meta-item">
    <span class="paper-meta-label">机构</span>
    <span class="paper-meta-value org-Microsoft">Microsoft</span>
  </div>
  <div class="paper-meta-item">
    <span class="paper-meta-label">方向</span>
    <span class="paper-meta-value">AI Agent</span>
  </div>
  <div class="paper-meta-item">
    <span class="paper-meta-label">日期</span>
    <span class="paper-meta-value">2026-04-28</span>
  </div>
</div>

!!! info ""
    <span class="paper-tag paper-tag-translated">✅ 已完成精读</span>

- **来源**：[Microsoft arXiv query](https://arxiv.org/abs/2604.26102v1)
- **论文链接**：[https://arxiv.org/pdf/2604.26102v1](https://arxiv.org/pdf/2604.26102v1)
- **状态**：已生成

## 摘要

大型语言模型智能体在软件工程任务上取得了显著进展，然而当前方法存在一个根本性的上下文耦合问题（context coupling problem）：标准的代码编辑界面将代码检查、修改规划和编辑执行混在同一个上下文窗口中，迫使智能体将探索性查看与严格格式化的编辑生成交错进行。

这导致无关信息不断累积，损害了智能体的性能。

为了解决这一问题，我们提出了 SWE-Edit，它将代码编辑分解为两个专门的子智能体：一个 Viewer（查看器），按需提取与任务相关的代码；一个 Editor（编辑器），根据高层规划执行修改——从而让主智能体专注于推理，同时将上下文密集型操作委托给干净的上下文窗口。

我们进一步研究了什么构成一个有效的编辑模型：观察到当前主流的查找-替换格式容易出错，我们使用 GRPO 训练 Qwen3-8B，使其自适应地选择编辑模式，相比单一格式基线提升了编辑效率。

在 SWE-bench Verified 上，SWE-Edit 将解决率提升了 2.1%，同时将推理成本降低了 17.9%。

我们还额外提出了一个代码编辑基准，能够可靠地预测下游智能体性能，为编辑模型选择提供实用指导。

我们的代码已公开在 https://github.com/microsoft/SWE-Edit。

*Yikai Zhang 1 2 *，Jiaxin Pei 3，Kenan Li 1，Maoquan Wang 1，Jin Pan 2，Yu Kang 1，Shengyu Fu 1，Elsie Nallipogu 1，Junjie Hu 2，Yufan Huang 1，Zijian Jin 1*

*工作完成于微软实习期间。*
1 微软，美国华盛顿州雷德蒙德
2 威斯康星大学麦迪逊分校计算机科学系，美国威斯康星州麦迪逊
3 斯坦福大学以人为本人工智能研究所（HAI），美国加利福尼亚州斯坦福

## 1 引言

大型语言模型（LLM）智能体在软件工程任务上取得了显著进展，从代码生成、bug 修复到仓库级别的软件工程。

然而，当前方法存在一个根本性的设计问题：标准的代码编辑界面将代码检查、修改规划和编辑执行耦合在同一个上下文窗口中。

这迫使智能体将探索性查看（如搜索相关代码）与严格格式化的编辑生成（如查找-替换块）交错进行。

随着智能体在代码库中导航，查看操作产生的无关信息在上下文中累积，稀释了智能体对真正修改目标的注意力。

我们称这个问题为上下文耦合（context coupling）。

为了解决上下文耦合，我们提出 SWE-Edit，一个将代码编辑界面分解为专业化子智能体的框架。

一个 Viewer（查看器）子智能体接收完整文件，按需仅提取与任务相关的代码，从而消除主智能体上下文中的探索性污染。

一个 Editor（编辑器）子智能体根据高层自然语言规划执行修改，将推理与对格式敏感的代码生成解耦。

这种分解使得主智能体能够纯粹专注于问题求解，同时将上下文密集型操作委托给干净、专门的上下文。

在脚手架设计之外，我们研究了什么构成一个有效的编辑模型。

我们观察到，最优编辑策略因任务而异——查找-替换适用于小范围修改，而全文件重写则适合处理复杂重构——因此我们使用 GRPO 训练 Qwen3-8B，使其能够根据修改复杂度自适应选择编辑模式。

得到的模型在单一格式基线上取得了提升。

为了支撑这种训练，我们需要一个能够可靠预测下游智能体性能的高效编辑基准。

为此我们提出了 PR-Edit 基准，该基准基于真实 GitHub PR，提供可扩展的、自动化的编辑评估。

借助 PR-Edit，基于 RL 的编辑器训练变得可行，我们证明使用归一化匹配奖励的 GRPO 在小型开源骨干模型（Qwen3-8B）上带来了 12.5 个百分点的编辑成功率提升，远超单纯模型缩放的效果。

这三者——脚手架、基准和训练——共同提供了一套可部署且成本高效的代码编辑子智能体方案。

在 SWE-bench Verified 上，SWE-Edit 将解决率从 69.9% 提升至 72.0%（+2.1%），同时将推理成本降低了 17.9%。

![Figure 1: SWE-Edit 框架架构总览](assets/page-009-img-01.png)

*图 1. 提出的 SWE-Edit 框架架构总览。该图展示了双重优化机制，说明了优化如何在脚手架层面（协调组件和上下文）和模型层面（精炼底层模型）同时发生。*

## 2 相关工作

**代码编辑与 SWE 智能体。** LLM 的应用已从代码生成扩展到代码编辑以及仓库级别的软件工程。

早期的 SWE 任务方法，如 bug 修复，采用固定流水线，将问题分解为定位、修复和验证阶段。

最近的智能体系统则赋予 LLM 工具用于迭代式代码库交互。

我们的工作通过重新设计代码编辑界面——即 SWE 智能体检查和修改代码的核心机制——推进了这一范式。

**多智能体系统。** 多智能体系统将复杂问题分解给专门的智能体。

在软件工程中，MetaGPT 和 ChatDev 等工作将不同的开发角色分配给通信的智能体，而近期工作则将研究查询分配到独立的、可并行化的子任务中。

这些方法在任务或角色层面进行分解——每个智能体追求一个可分离的目标。

相比之下，SWE-Edit 在认知层面进行分解：决定修改什么和生成正确格式的编辑不是独立的子任务，而是在共享上下文时相互干扰的相互交织的能力。

我们的子智能体设计在代码编辑界面内解耦了这些冲突的认知需求，并且可以集成到更广泛的多智能体 SWE 框架中。

最接近的现有设计是 Aider 的 Architect 模式，它将高容量推理模型与较小的编辑模型分离。

Aider Architect 针对的是不同的瓶颈：它在单文件层面将推理与编辑格式化解耦，但并未解决探索性文件检查导致的上下文污染，且其高容量推理阶段增加了成本。

相比之下，SWE-Edit 引入了一个 Viewer 子智能体来防止上下文污染，并使用可训练的 Editor 来降低推理成本。

## 3 SWE-Edit 框架

### 3.1 脚手架设计

SWE-Edit 的核心是将代码编辑分解为两个专门的子智能体。

**Viewer 子智能体。** 当主智能体需要检查一个文件时，Viewer 接收完整的文件内容和一个自然语言查询，返回仅与查询相关的代码行及其行号。

Viewer 直接执行查看操作，无需主智能体产生格式敏感的查找-替换命令。

这使得高层推理——决定查看什么——与低层生成——产生正确格式化的视图输出——得以解耦。

**Editor 子智能体。** 当主智能体决定进行修改时，它向 Editor 发出一个高层自然语言指令，描述所需修改。

Editor 直接执行编辑，无需主智能体产生对格式敏感的查找-替换命令。

这使得高层推理——决定修改什么——与低层生成——产生正确格式化的编辑语法——得以解耦。

两个子智能体都使用更小、成本高效的模型实现，而主智能体则纯粹专注于问题求解和编排。

完整实现细节和提示语见附录 A。

### 3.2 模型优化

给定脚手架分解后，一个自然的问题随之而来：什么构成一个有效的编辑器？

如图 2 所示，最优编辑策略因任务而异。

查找-替换（find-replace）对于局部修改是 token 高效的，但需要精确字符串匹配——一个空白字符的不匹配就会导致失败。

全文件重写（whole-file rewrite）避免了匹配错误，但成本更高，且对于长文件存在意外修改的风险。

在异构编辑任务中，静态选择任何一种模式都是次优的。

**算法 1 轻量级代码规范化**

输入：原始代码字符串 C
输出：规范化后的代码字符串 ˜C

1: 步骤 1：移除注释
2:   移除 C 中的所有多行注释
3:   移除 C 中的所有单行注释
4: 步骤 2：规范化空白符
5:   将 C 中的空白符合并为单个空格
6:   ˜C ← 修剪(C)
7: 返回 ˜C

我们通过训练编辑器自适应选择编辑模式来解决这个问题。

我们将模式选择建模为单步决策问题：给定文件内容 c 和编辑指令 q，编辑器选择模式 m ∈ {find-replace, whole-file-rewrite} 并生成相应的输出。

我们使用 GRPO 优化这一策略，配合归一化匹配奖励，该奖励在规范化空白符和移除注释后将模型输出与真实值进行比较（算法 1）。

这一奖励为编辑正确性提供了可靠的、无需执行的代理指标。

## 4 实验

### 4.1 实验设置

我们在 SWE-bench Verified 上评估 SWE-Edit，该基准包含 500 个来自真实 Python 仓库的 GitHub issue。

我们采用来自 Anthropic 的参考智能体脚手架作为基线，该基线配备了两个工具：`execute_bash` 用于 shell 命令执行，`str_replace_editor` 用于文件操作。

![Figure 2: 自适应编辑模式选择](assets/page-009-img-01.png)

*图 2. 自适应编辑模式选择。编辑器分析任务特征，在查找-替换（token 高效但匹配敏感）和全文件重写（鲁棒但成本高）之间进行选择，实现基于编辑范围和复杂度的最优策略选择。*

### 4.2 脚手架层面结果

**表 1. SWE-bench Verified 上的主要结果（500 个实例，3 次运行平均）。SWE-Edit 提升了解决率（+2.1%）和编辑可靠性（+3.5%），同时成本降低 17.9%。**

| 配置 | 解决率 (%) | 成本 ($) | Viewer 调用 | Editor 调用 | 编辑成功率 (%) |
|---|---|---|---|---|---|
| Baseline | 69.9 | 243.7 | 5.78 | 2.86 | 93.4 |
| + Viewer | 70.3 (+0.4) | 225.0 (-7.7%) | 4.26 (-1.52) | 2.75 (-0.11) | 94.3 (+0.9) |
| + Editor | 71.3 (+1.4) | 268.4 (+10.1%) | 7.78 (+2.00) | 2.33 (-0.53) | 96.1 (+2.7) |
| SWE-Edit | 72.0 (+2.1) | 200.1 (-17.9%) | 7.49 (+1.71) | 2.37 (-0.49) | 96.9 (+3.5) |

**Viewer：减少上下文污染。** Viewer 的加入将解决率提升至 70.3%（+0.4%），成本降低 7.7%。

定性分析表明，Viewer 改变了主智能体的代码检查行为：智能体不再逐个文件完整查看，而是发出针对性的查询，消除了来回文件检查的需要。

定量上，Viewer 平均仅返回请求文件内容的 39.7%——减少 60.3% 的代码表面积——这使主智能体消耗的非缓存输入 token 下降了 34.5%（276.7K → 181.3K）。

**Viewer vs. 检索基线。** 基于 LLM 的 Viewer 的一个自然替代方案是经典代码检索。

**表 2. Viewer vs. 检索基线在 50 个保留 PR-Edit 实例上的结果。真实相关行取自 PR diff。LLM Viewer 在显著减少上下文的同时实现了最高的召回率和 F1。"Ctx. Red." 是返回片段中被省略的输入文件百分比。**

| 方法 | 召回率 | 精确率 | F1 | 上下文缩减 |
|---|---|---|---|---|
| LLM Viewer (GPT-5-mini) | 0.938 | 0.179 | 0.272 | 60.3% |
| Dense (text-embedding-3-small) | 0.868 | 0.092 | 0.140 | 28.6% |
| BM25 (Okapi) | 0.537 | 0.056 | 0.083 | 64.4% |

**Editor：提升编辑精度与可靠性。** Editor 的加入将 SWE-bench Verified 解决率从 69.9% 提升至 71.3%（+1.4%），编辑成功率从 93.4% 提升至 96.1%（+2.7%）。

这些结果证实，将高层推理与语法执行解耦不仅解决了格式化错误，还促进了逻辑正确的补丁的生成。

每次实例的平均编辑器调用次数也从 2.86 降至 2.33——更高的编辑可靠性意味着当编辑因补丁错误失败时所需的重试次数更少。

然而，这一可靠性提升带来了成本增加（+10.1%）。

分析智能体轨迹发现，主智能体在委托编辑时变得更加探索性：Viewer 调用从 5.78 增加到 7.78。

**协同效应：打破精度-成本权衡。** 完整的 SWE-Edit 框架结合了两个子智能体，结果揭示了协同效应：SWE-Edit 以最低成本（$200.1）实现了最高解决率（72.0%），相比基线提升了 2.1% 的解决率并降低了 17.9% 的成本。

### 4.3 模型层面结果：训练自适应编辑器

在确认 SWE-Edit 跨模型家族带来稳健收益后，我们现在转向编辑器本身的优化。

在所提出的分解下，一个自然的问题随之而来：我们如何有效地训练和选择模型以在编辑器的专门角色中表现出色？

为回答这个问题，我们利用框架的模块化特性，在基于 Qwen3-8B 的骨干模型上执行了针对性的强化学习，将其转化为一个自适应、高精度的编辑子智能体。

**4.3.1. PR-Edit 基准。** 为支持高效的编辑器开发和评估，我们引入 PR-Edit，一个基于真实 GitHub PR 的代码编辑基准。

PR-Edit 的核心是归一化匹配奖励——一个无需执行、轻量级的编辑正确性度量，对空白符和注释差异具有鲁棒性。

我们进一步引入 GPT Grader，一个使用 GPT-4.1 判断两段代码是否功能等价的语义等价性判断器。

GPT Grader 仅用于 PR-Edit 中间基准；我们的主要 SWE-bench Verified 评估完全基于执行（补丁被应用并运行完整仓库测试套件）。

GPT Grader 作为代理指标的有效性得到其与下游基于测试的指标强相关性的支持。

**4.3.2. 自适应编辑器训练评估。** 我们在编辑器层面和下游智能体性能两个层面评估自适应编辑器训练的有效性。

**表 4. PR-Edit 基准结果。GRPO 训练显著提升了 Qwen3-8B，达到与 GPT-5-nano 相当的性能。**

| 模型 | 格式成功率 (%) | GPT Grader (%) | 归一化匹配 (%) |
|---|---|---|---|
| Qwen3-8B | 76.8 | 56.0 | 32.0 |
| Qwen3-8B + GRPO | 90.4 | 68.4 | 38.8 |
| GPT-5-nano | 89.8 | 66.4 | 38.8 |
| GPT-5-mini | 96.1 | 77.5 | 41.7 |
| GPT-5 | 98.1 | 77.2 | 44.1 |

GRPO 训练显著提升了 Qwen3-8B 作为编辑器模型的能力：格式成功率从 76.8% 提升至 90.4%（+13.6%），GPT Grader 准确率从 56.0% 提升至 68.4%（+12.4%）。

在所有报告指标上，训练后的模型超过了 GPT-5-nano。

**表 5. 使用不同编辑器模型在 SWE-bench Verified 上的下游性能。更高的 PR-Edit 分数预测更好的解决率、更高的编辑成功率和更低的主智能体成本。**

| 编辑器模型 | PR-Edit (%) | 解决率 (%) | 智能体成本 ($) | 编辑成功率 (%) |
|---|---|---|---|---|
| Qwen3-8B | 56.0 | 68.5 | 231.7 | 68.6 |
| Qwen3-8B + GRPO | 68.4 | 69.9 | 215.9 | 81.1 |
| GPT-5-nano | 66.4 | 70.0 | 207.1 | 82.0 |
| GPT-5-mini | 77.5 | 72.0 | 179.6 | 95.9 |

PR-Edit 基准上的改进一致地对应更强的下游性能，包括更高的解决率、更高的编辑成功率和更低的主智能体推理成本。

特别是，GRPO 训练的 Qwen3-8B 将 SWE-bench Verified 解决率从 69.9% 提升至 71.3%（+1.4%），同时将主智能体推理成本降低了 6.8%。

这些收益由编辑成功率从 68.6% 大幅提升至 81.1%（+12.5%）推动。

### 4.4 缩放分析

**表 7. 编辑器模型规模的影响。更强的模型显示出递减的回报：GPT-5 以 5.8 倍的成本仅带来微小的精度提升。**

| 编辑器模型 | 解决率 (%) | 编辑成功率 (%) | 编辑器成本 ($) |
|---|---|---|---|
| GPT-5-mini | 72.0 | 95.9 | 5.4 |
| GPT-5 | 72.4 (+0.4) | 97.5 (+1.6) | 31.2 (5.8×) |

GPT-5 仅将解决率提升了 0.4%（72.0% → 72.4%），同时将编辑器成本提升了 5.8 倍（$5.4 → $31.2）。

模型规模如此大幅跃升带来的边际收益表明，单纯缩放并不是提升编辑器角色最具成本效益的手段。

更具决定性的对比是在缩放和训练之间：基于 GRPO 的自适应编辑器训练在 Qwen3-8B 上带来了 12.5 个百分点的编辑成功率提升（68.6% → 81.1%），比从 GPT-5-mini 到 GPT-5 获得的 +1.6% 大一个数量级。

这表明格式层面的决策主要是一种可学习的技能，而非仅在规模化时涌现的能力。

![Figure 5: 固定 vs. 自适应格式选择的训练动态](assets/page-009-img-01.png)

*图 5. 固定 vs. 自适应格式选择的训练动态。y 轴是验证奖励（归一化匹配），x 轴是 rollout 步数。虽然固定查找-替换起点更高（格式更简单，更容易学习），但自适应训练通过学习何时调用全文件重写超越了它。*

### 4.5 发现总结

综合来看，我们的实验结果验证了 SWE-Edit 的两个核心主张：界面分解在性能和成本效率上带来稳定一致的收益，以及基于强化学习的自适应编辑器优化能够在此分解下学习鲁棒且高效的编辑行为。

在脚手架层面，实验确认 Viewer 通过减少上下文污染提升效率，Editor 通过消除格式化错误提升可靠性，两者结合产生协同效应，打破了精度-成本的权衡。

在模型层面，PR-Edit 基准结合归一化匹配奖励和 GPT Grader 提供了一个高效且预测性的评估框架。

GRPO 训练使小模型在编辑角色中超越了其规模预期，而缩放分析显示，将额外容量投入主智能体比投入编辑器更具成本效益。

## 5 结论

我们提出了 SWE-Edit，一个通过专业化子智能体解决代码编辑中上下文耦合问题的框架。

Viewer 子智能体按需提取相关代码，消除上下文污染；Editor 子智能体根据高层规划执行修改，解耦推理与格式敏感的生成。

我们还引入了 PR-Edit 基准，实现了高效的编辑模型开发。

借助 PR-Edit，基于 RL 的编辑器训练变得可行，我们证明使用归一化匹配奖励的 GRPO 在小型开源骨干模型（Qwen3-8B）上带来了 12.5 个百分点的编辑成功率提升，远超单纯模型缩放的效果。

这三者——脚手架、基准和训练——共同提供了一套可部署且成本高效的代码编辑子智能体方案。

我们当前方法的一个局限是我们在隔离环境中使用来自真实编辑的静态奖励信号训练编辑器模型。

一个自然的扩展是在端到端的智能体强化学习循环中训练编辑器，使其接收来自主智能体下游成功或失败的反馈。

这将使编辑器不仅能学习格式化正确性，还能学习促进有效智能体-编辑器协作的属性——例如生成在出错时更容易被主智能体验证或调试的编辑。

一个互补的方向是用智能体作为评判员的评估器替代 GPT Grader，该评估器使用更广泛的仓库上下文来评估编辑，而非在隔离环境中比较两个 diff。

更广泛地说，我们的子智能体分解为研究专门组件如何在多智能体软件工程系统中共同进化提供了模块化基础。

## 影响声明

本文的工作旨在推进机器学习领域的发展。我们的工作可能存在多种潜在的社会影响，但此处我们认为无需特别强调任何一项。

## 参考文献

Austin, J., Odena, A., Nye, M., Bosma, M., Michalewski, H., Dohan, D., Jiang, E., Cai, C., Terry, M., Le, Q., et al. Program synthesis with large language models. *arXiv preprint arXiv:2108.07732*, 2021.

Chen, M. Evaluating large language models trained on code. *arXiv preprint arXiv:2107.03374*, 2021.

Gauthier, P. Aider architect: Separating code reasoning from editing. https://aider.chat/2024/09/26/architect.html, 2024a.

Gauthier, P. Aider polyglot code editing benchmark. https://aider.chat/docs/benchmarks.html, 2024b.

Hadfield, E. C., Li, K., Zhang, Y., Nallipogu, E., Fan, J., Jin, Z., Huang, Y., and Lab, M. A. Agent laboratory: A flexible environment for multi-agent research. *arXiv preprint arXiv:2505.04380*, 2025.

Hong, S., Zheng, X., Chen, J., Cheng, Y., Zhang, C., Wang, Z., Yau, S. K. S., Lin, Z., Zhou, L., Ran, C., et al. Metagpt: Meta programming for multi-agent collaborative framework. *arXiv preprint arXiv:2308.00352*, 2023.

Jain, N., Vaidyanath, S., Iyer, A., Natarajan, N., Parthasarathy, S., Rajamani, S., and Sharma, R. Jigsaw: Large language models meet program synthesis. In *Proceedings of the 46th IEEE/ACM International Conference on Software Engineering*, pp. 1–12, 2024.

Jimenez, C. E., Yang, J., Wettig, A., Yao, S., Pei, K., Press, O., and Narasimhan, K. Swe-bench: Can language models resolve real-world github issues? *arXiv preprint arXiv:2310.06770*, 2023.

MiniMax AI. Minimax-m2.1: Technical report. https://platform.minimaxi.com, 2025.

Moonshot AI. Kimi-k2-thinking: Technical report. https://kimi.moonshot.cn, 2025.

Örwall, A. A. Automated bug fixing using large language models: A case study. *arXiv preprint arXiv:2403.16879*, 2024.

Qian, C., Cong, X., Yang, C., Chen, W., Su, Y., Xu, J., Liu, Z., and Sun, M. Communicative agents for software development. *arXiv preprint arXiv:2307.07924*, 2024.

Schluntz, J. Announcing Claude 3.5 Sonnet and Claude Code. https://www.anthropic.com/news/claude-3-5-sonnet, 2025.

Shao, Z., Wang, P., Zhu, Q., Xu, R., Song, J., Bi, X., Zhang, H., Zhang, M., Li, Y. K., Wu, Y., et al. Deepseekmath: Pushing the limits of mathematical reasoning with open-source language models. *arXiv preprint arXiv:2402.03300*, 2024.

Sun, W., Lu, M., Ling, Z., Liu, K., Yao, X., Yang, Y., and Chen, J. Scaling long-horizon llm agent via context-folding. *arXiv preprint arXiv:2510.11967*, 2025.

Wang, H., Hou, Z., Wei, Y., Tang, J., and Dong, Y. Swe-dev: Building software engineering agents with training and inference scaling. *arXiv preprint arXiv:2506.07636*, 2025.

Wang, X., Li, B., Song, Y., Xu, F. F., Tang, X., Zhuge, M., Pan, J., Song, Y., Li, B., Singh, J., et al. Openhands: An open platform for ai software developers as generalist agents. *arXiv preprint arXiv:2407.16741*, 2024.

Xia, C. S., Deng, Y., Dunn, S., and Zhang, L. Agentless: Demystifying llm-based software engineering agents. *arXiv preprint arXiv:2407.01489*, 2024.

Xia, C. S., Wang, Z., Yang, Y., Wei, Y., and Zhang, L. Live-swe-agent: Can software engineering agents self-evolve on the fly? *arXiv preprint arXiv:2511.13646*, 2025.

Xie, C., Li, B., Gao, C., Du, H., Lam, W., Zou, D., and Chen, K. Swe-fixer: Training open-source llms for effective and efficient github issue resolution. *arXiv preprint arXiv:2501.05040*, 2025.

Yang, A., Li, A., Yang, B., Zhang, B., Hui, B., Zheng, B., Yu, B., Gao, C., Huang, C., Lv, C., et al. Qwen3 technical report. *arXiv preprint arXiv:2505.09388*, 2025.

Yang, J., Jimenez, C. E., Wettig, A., Lieret, K., Yao, S., Narasimhan, K., and Press, O. Swe-agent: Agent-computer interfaces enable automated software engineering. *Advances in Neural Information Processing Systems*, 37:50528–50652, 2024.

ZhipuAI. GLM-4.7: Advancing the coding capability. https://z.ai/blog/glm-4.7, December 2025.

Zhu, Z., Xie, C., Lv, X., and slime Contributors. slime: An llm post-training framework for rl scaling. https://github.com/THUDM/slime, 2025.

Zhuo, T. Y., Vu, M. C., Chim, J., Hu, H., Yu, W., Widyasari, R., Yusuf, I. N. B., Zhan, H., He, J., Paul, I., et al. Bigcodebench: Benchmarking code generation with diverse function calls and complex instructions. *arXiv preprint arXiv:2406.15877*, 2024.

---

## 附录

### A. 实现细节

本附录提供了实验中使用的智能体脚手架、工具定义和提示语的完整细节。

#### A.1. 基线智能体脚手架

我们采用来自 Anthropic 的参考智能体脚手架，该脚手架为智能体配备了两个工具：`execute_bash` 用于 shell 命令执行，`str_replace_editor` 用于文件操作。

编辑器工具提供了用于查看、创建和通过精确字符串替换编辑文件的子命令。

这反映了当前智能体软件工程的最佳实践。

**工具定义。** 基线智能体使用以下工具：

**Listing 1. Bash 工具架构。**
```json
{
  "type": "function",
  "name": "execute_bash",
  "description": "在 bash shell 中运行命令\n"
}
```

**Listing 2. 编辑器工具架构。**
```json
{
  "type": "function",
  "name": "str_replace_editor",
  "description": "用于查看、创建和编辑文件的自定义编辑器工具",
  "parameters": {
    "type": "object",
    "properties": {
      "command": {
        "type": "string",
        "enum": ["view", "create", "edit"],
        "description": "要运行的命令。可选值：'view', 'create', 'edit'。"
      },
      "path": {
        "type": "string",
        "description": "文件或目录的绝对路径"
      },
      "query": {
        "type": ["string", "null"],
        "description": "'view' 命令在 path 指向文件时必需。描述要查找内容的自然语言查询。"
      },
      "instruction": {
        "type": ["string", "null"],
        "description": "'edit' 命令必需。描述如何修改文件的详细指令。"
      }
    }
  }
}
```

Viewer 子智能体提示语：当调用 `view` 命令时，Viewer 子智能体接收文件内容和查询，返回相关行范围。

Editor 子智能体提示语：当调用 `edit` 命令时，Editor 子智能体接收文件内容和编辑指令，以搜索-替换格式或全文件重写输出修改。

### B. 完整实验结果

**表 8. SWE-bench Verified 上的详细性能指标。每个配置的结果为三次独立运行的平均值。"Succ." 表示编辑器工具调用的成功率。**

| 配置 | 解决率 (%) | 轮次 | 智能体成本 ($) | 编辑器成本 ($) | Viewer成本 ($) | 总成本 ($) | 输出 Tokens | 总输入 | 缓存输入 | 非缓存输入 | Viewer 调用 | Editor 调用 | 成功率 (%) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Baseline | 69.9 | 24.2 | 243.7 | — | — | 243.7 | 9632 | 369.8K | 276.7K | 5.78 | 2.86 | 93.4 |
| + Viewer | 70.3 | 23.0 | — | — | — | 225.0 | — | — | — | — | — | 94.3 |
| + Editor | 71.3 | — | — | — | — | 268.3 | — | — | — | — | — | 96.1 |
| SWE-Edit | 72.0 | — | — | — | — | 200.1 | — | — | — | — | — | 96.9 |

**表 9. SWE-bench Verified 上每次运行的均值±标准差（500 个实例，3 次运行）。**

| 配置 | 解决率 (%) | 成本 ($) | 编辑成功率 (%) |
|---|---|---|---|
| Baseline | 69.9 ± 0.6 | 243.7 ± 6.5 | 93.4 ± 0.8 |
| + Viewer | 70.3 ± 1.6 | 225.0 ± 5.6 | 94.3 ± 0.3 |
| + Editor | 71.3 ± 0.2 | 268.3 ± 19.3 | 96.1 ± 0.2 |
| SWE-Edit | 72.0 ± 0.0 | 200.1 ± 16.8 | 96.9 ± 0.1 |

### C. PR-Edit 基准

本节提供了 PR-Edit 基准的实现细节，包括用于计算归一化匹配奖励的归一化函数、用于 GPT-4.1 等价性评分的提示语以及数据集中的一个示例。

#### C.1. 代码归一化

归一化匹配奖励在规范化空白符和移除注释后将模型输出与真实值进行比较。

这为训练期间编辑正确性提供了一个可靠的、无需执行的代理指标。

**Listing 3. 用于计算归一化匹配奖励的代码归一化函数。**
```python
def normalize_code(code: str) -> str:
    \"\"\"
    通过移除注释和规范化空白符来归一化代码。
    允许容忍注释和空白符差异的比较。
    注意：这使用基于正则的启发式方法，可能错误处理字符串字面量中的类似注释的模式。
    对于大多数代码比较任务，这是一个可接受的权衡。
    \"\"\"
    # 首先移除多行注释
    code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)
    # Python 文档字符串 / 用作注释的多行字符串
    code = re.sub(r'""".*?"""', "", code, flags=re.DOTALL)
    code = re.sub(r"'''.*?'''", "", code, flags=re.DOTALL)
    # HTML/XML 注释
    code = re.sub(r"<!--.*?-->", "", code, flags=re.DOTALL)
    # 移除单行注释
    code = re.sub(r"//.*$", "", code, flags=re.MULTILINE)
    code = re.sub(r"#.*$", "", code, flags=re.MULTILINE)
    # 规范化空白符
    code = re.sub(r"\s+", " ", code)
    return code.strip()
```

### D. 开源模型评估细节

#### D.1. 模型选择

我们的主要实验使用 GPT-5，一个专有模型。

为验证 SWE-Edit 跨模型家族的泛化能力，我们在三个近期的开源推理模型上进行了评估：Kimi-K2-Thinking、MiniMax-M2.1 和 GLM-4.7。

选择这些模型有两个原因：（1）它们代表了最新一代具有强推理能力的开源模型；（2）它们经过了大量的智能体训练，使其成为挑战性软件工程任务的合适候选。

#### D.2. 推理配置

所有三个模型都配置了交错思考（Interleaved Thinking）和保留思考（Preserved Thinking）。

交错思考允许模型在每次响应和工具调用之前进行推理，改善指令遵循和生成质量。

保留思考自动在多轮对话中保留推理块，重用现有推理而非从头推导——减少信息损失并提高长程智能体任务的一致性。
