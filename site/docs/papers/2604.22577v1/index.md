# QuantClaw：OpenClaw 的按需精度路由

**技术报告**

张曼怡¹, 李继富¹\*, 孙中奥¹, 刘晓浩², 董振华¹, 余先治¹, 白浩利¹, 夏晓波³

¹华为技术有限公司 ²新加坡国立大学 ³中国科学技术大学

{zhangmanyi6@huawei.com, lijifu4@huawei.com, xiaoboxia@ustc.edu.cn}

\*通讯作者

---

## 摘要（Abstract）

自主智能体系统（如 OpenClaw）由于长上下文输入和多轮推理，带来了显著的计算效率挑战，导致实际开发中计算和金钱成本高昂。虽然量化是降低成本和延迟的标准方法，但它在真实场景中对智能体性能的影响尚不明确。本文分析了 OpenClaw 上多种复杂工作流对量化的敏感性，发现精度需求高度依赖任务类型。基于这一观察，我们提出 **QuantClaw**，一个即插即用的精度路由插件，根据任务特征动态分配精度。QuantClaw 将轻量级任务路由到低成本配置，同时为高要求工作负载保留高精度，在不增加用户复杂度的前提下节省成本并加速推理。实验表明，QuantClaw 在保持或提升任务性能的同时，降低了延迟和计算成本。在一系列智能体任务中，它在 GLM-5（FP8 基线）上实现了高达 **21.4% 的成本节约**和 **15.7% 的延迟降低**。这些结果突显了在智能体系统中将精度视为动态资源的价值。

- **博客**: https://sparkengineai.github.io/QuantClaw
- **GitHub**: https://github.com/SparkEngineAI/QuantClaw-plugin
- **ClawHub**: https://clawhub.ai/plugins/@sparkengineai/quantclaw

---

## 1 引言（Introduction）

近年来，大语言模型的进展使得能够执行复杂多步工作流的自主智能体在真实环境中涌现 [1–12]。OpenClaw [13]、Hermes [14] 和 Claude Code [15] 等系统将语言模型扩展到静态文本生成之外，赋予其工具使用、环境交互和迭代推理能力。这些系统作为通用智能体框架运行，模型不仅负责输出，还负责规划、执行和跨异构任务协调操作。

### 1.1 核心挑战：Agent 系统的计算瓶颈

然而，这种向智能体系统的转变引入了新的计算挑战。与传统推理工作负载不同，智能体执行通常涉及长上下文累积、工具输出存储和多步交互，导致延迟和成本显著增加 [16–19]，在实际部署中很快变得高昂。例如，单次用户会话可能累积超过 **234K 令牌** 的上下文（OpenClaw [20]）。因此，即使是一个常规的后续查询也需要将完整历史状态传输给模型，极大地增加了每次交互的成本。在现行实践中，这些系统通常以固定精度或模型配置运行，而不考虑任务复杂度。这导致资源分配与实际任务需求之间存在系统性不匹配，使得 OpenClaw 式系统天然存在成本效率问题。

### 1.2 量化：机遇与未知

量化 [21–26] 通过减少内存占用和加速推理，为提高效率提供了有希望的方向。然而，其对智能体性能的影响仍然知之甚少，尤其是在复杂的多轮协作场景中 [27]。特别是，虽然量化在标准 NLP 基准测试中已被广泛研究 [28–31]，但在真实世界智能体场景——任务在推理深度、工具使用和交互模式上差异巨大——中的影响尚未被系统性地刻画。

### 1.3 本文贡献

本文研究了量化如何影响 OpenClaw 中不同类别的智能体任务。我们首先构建了一个基准驱动分析 [32]（包含 **24 种任务类型、104 个任务、6 个模型**，规模从 9B 到 744B），评估不同工作负载下的量化敏感性，揭示精度降低的影响高度依赖任务类型。基于这些发现，我们提取了一套关于何时何地需要高精度的实用见解。基于这些见解，我们提出 **QuantClaw**，一个即插即用的精度路由插件。QuantClaw 根据任务特征动态分配精度，将轻量级任务路由到低成本配置，为高要求工作负载保留高精度。这一设计实现了更具成本效益且更快速的服务，同时不增加终端用户的复杂度。

**经验结果表明**，QuantClaw 通过任务自适应精度路由实现了优越的性能-效率权衡：
- 在 **GLM-4.7-Flash（PinchBench v1.2.0）**上：较 BF16 基线提高平均分 **2.85 分**，同时成本降低 **21.6%**，延迟降低 **8.4%**
- 在 **GLM-5（PinchBench v2.0.0）**上：较 FP8 基线提高平均分 **2.09 分**，同时成本降低 **21.4%**，延迟降低 **15.7%**

这些结果表明，精度应该被视为智能体系统中的**动态资源**，而非固定配置。

---

## 2 经验发现与洞见（Empirical Findings and Insights）

### 2.1 实验设置

**评估基准**。我们使用 **Claw-Eval（release v0.0.0）** [32] 作为主要评估基准。这是一个端到端的自主智能体评估套件，包含 **24 种任务类型**和 **104 个人工验证任务**，涵盖服务编排、多模态感知、多轮对话等多个领域，从完成度、安全性和鲁棒性三个维度评估智能体。重要的是，Claw-Eval 整合了轨迹级审计和受控扰动，能够对智能体行为进行超出最终输出的更可靠评估。

**模型与度量指标**。我们使用 6 个模型进行基准测试：GLM-4.7-Flash-30B [33]、GLM-5-744B [34]、MiniMax-M2.5-229B、Qwen3.5-9B、Qwen3.5-35B-A3B 和 Qwen3.5-397B-A17B。这些模型广泛使用且代表了当前大语言模型系列的不同规模，覆盖了从 9B 到 744B 的参数范围。注意，GLM-5 [34] 以 FP8 精度部署，其余模型默认使用 BF16，这使我们能够跨不同精度设置统一比较量化效果。

我们进一步将这些模型从其原生高精度格式量化到低精度区域（低至 **NVFP4** [35–38]），从而系统性地研究精度-性能权衡。分析在粗粒度和细粒度两个层面进行，捕获整体性能退化以及不同类别智能体工作负载的**任务依赖敏感性**。

我们沿三个关键维度评估原生精度（BF16 或 FP8）和量化精度（NVFP4）的模型：**Score（分数）**、**Cost（成本）** 和 **Speed（速度）**。Score 反映任务性能，测量不同精度设置下智能体成功完成任务的能力。Cost 量化计算开销，包括内存使用和推理相关计算。Speed 捕获效率，通常以延迟或吞吐量测量。这一指标框架支持全精度与低精度模型之间的系统性比较，使我们能够在整体层面和任务依赖层面分析精度-性能权衡。此外，每个实验案例执行 **6 次独立试验**以减少结果的随机性。

### 2.2 全局量化效应

**主要结果**。为理解量化对基于 OpenClaw 的智能体系统的整体影响，我们在原生精度（BF16/FP8）和低精度 NVFP4 设置下评估上述模型。结果总结在 **表 1** 中。由于量化带来的成本节约因硬件平台、推理框架和模型架构而异，依据 [39–41]，我们估计 NVFP4 令牌定价为 BF16 价格的 **80%**，BF16 基线参考自官方 OpenRouter 定价。

**表 1：原生精度（BF16 或 FP8）与 NVFP4 量化下的模型性能、成本和延迟对比。大模型对量化表现出强鲁棒性，某些情况下甚至略有性能提升。**

| 模型 | 参数量(B) | 原生精度 | 原生 Score↑ | 原生 Cost($)↓ | 原生 Time(s)↓ | NVFP4 Score↑ | NVFP4 Cost($)↓ | NVFP4 Time(s)↓ |
|------|-----------|----------|-------------|---------------|---------------|--------------|----------------|----------------|
| GLM-4.7-Flash | 30 | BF16 | 0.6370 | 0.0077 | 72.20 | 0.6034 | 0.0072 | 73.02 |
| GLM-5 | 744 | FP8 | 0.7130 | 0.0647 | 68.96 | 0.7229 | 0.0548 | 87.58 |
| MiniMax-M2.5 | 229 | BF16 | 0.6760 | 0.0112 | 44.89 | 0.6823 | 0.0084 | 59.27 |
| Qwen3.5-9B | 9 | BF16 | 0.4267 | 0.0022 | 16.58 | 0.4107 | 0.0013 | 16.99 |
| Qwen3.5-35B-A3B | 35 | BF16 | 0.6686 | 0.0300 | 59.61 | 0.6549 | 0.0235 | 55.49 |
| Qwen3.5-397B-A17B | 397 | BF16 | 0.7048 | 0.0539 | 62.10 | 0.6937 | 0.0441 | 42.46 |

整体来看，量化到 NVFP4 在各模型中仅引入有限的性能退化，表明激进的低精度可在智能体工作负载中有效应用。然而，影响并非均匀分布，表现出对模型规模的明确依赖性：
- **小模型**（如 Qwen3.5-9B）：观察到明显的性能下降（约 **3-4%**），表明低容量模型对精度降低更敏感
- **中等模型**（30B-70B 范围）：中等退化，通常在 **2%** 以内
- **大模型**（200B+）：对量化表现出**强鲁棒性**，性能下降低于 2%，某些情况下甚至略有提升。例如，GLM-5 和 MiniMax-M2.5 在量化后**表现出小的性能增益**，表明在特定条件下减少精度可能引入正则化效应

这一趋势表明存在量化鲁棒性的**缩放效应**：模型越大，对精度降低的敏感性越低。直观上，大模型拥有更大的表征冗余，使其更能容忍量化噪声。

**NVFP4 下量化退化的缩放效应**。我们观察到量化退化与模型规模之间一致的缩放行为。在线性尺度上（见图 1 左），性能差距随模型参数增加而减小，表明鲁棒性提升，拟合幂律 $\Delta = 0.079 \cdot N^{-0.273}$。在对数-对数尺度上（图 1 右），这一趋势遵循幂律 $\Delta \propto N^{-0.293}$，表明敏感性降低受系统性缩放定律支配，而非偶然变异。这一缩放行为意味着，随着模型规模增长，激进的低精度部署变得越来越可行。在实践中，大模型可以承受大幅精度降低而仅有极小性能损失，表明**精度优化应优先针对小型或中型模型**，其敏感性更高。

> **图 1：NVFP4 下量化退化的缩放行为。** 左图：绝对性能差距与模型规模（线性尺度），显示退化随参数增加而递减。右图：对数-对数图揭示幂律关系，确认系统性缩放。大模型对低精度量化表现出增强的鲁棒性。

### 2.3 任务级量化敏感性

低精度量化的影响在不同任务类型间差异显著。将所有测试模型的结果平均后，我们根据敏感性将 OpenClaw 任务分为三组：**高、中、低**（图 2）。

**图 2：任务级量化敏感性差异。** 正值表示量化后性能下降百分比（(BF16 分数 - NVFP4 分数) / BF16 分数），负值表示相对性能提升。任务按对量化的响应分为高、中、低三类。

- **高敏感性任务**（如 **Coding、Compliance、Terminal、Safety**）：在 NVFP4 下遭受显著退化，因为它们依赖精确决策边界。具体退化值：Coding 约 +12.27%，Compliance 约 +8.73%，Terminal 约 +6.69%，Safety 约 +6.50%
- **中等敏感性任务**（如 **Rewriting、Content**）：变化最小，可在混合精度下运行（约 +1.34%~+2.67%）
- **低敏感性任务**（如 **Research、Comprehension、Knowledge、Data Analysis**）：保持鲁棒，甚至可能从量化中受益（Research 约 -0.48%，Comprehension 约 -2.64%，Knowledge 约 -4.02%，Data Analysis 约 -10.06%，即量化后**分数反而提升**）

这些观察突显了量化的任务依赖特性，为任务感知的精度分配提供了动机。

### 2.4 路由视角与策略

上述发现表明，精度不应在 OpenClaw 任务中统一分配。由于不同任务类型对量化表现出显著不同的敏感性，QuantClaw 引入了**任务感知的路由策略**，根据分数、速度和成本之间的预期权衡选择执行精度。在实践中，我们提出**两种模式**以服务不同用户场景：

- **延迟导向（Latency-oriented）**：当延迟降低超过可忽略的性能损失时，将任务路由到低精度执行
- **成本导向（Cost-oriented）**：对于量化下质量保持稳定的任务，优先选择低精度以减少计算开销

分数-速度和分数-成本比较以及偏好任务级精度总结在 **图 3** 中。

> **图 3：16/8 位与 4 位的任务级部署权衡。** 左图：分数 vs 速度；右图：分数 vs 成本，按敏感性排序。∆% 表示相对值。16/8 位区的任务表现出质量关键的精度依赖，4 位区的任务是成本高效的低精度候选。

> **图 4：QuantClaw 整体流水线。** 用户查询首先被识别为不同任务类别，由混合检测机制支持。QuantClaw 基于预计算的任务-精度敏感度画像执行精度路由。维护一个不同精度级别的模型变体池以支持推荐精度部署。

---

## 3 方法论（Methodology）

### 3.1 动机

第 2 节的经验分析表明量化对 OpenClaw 任务的影响不均。虽然从 BF16/FP8 到 NVFP4 的整体退化有限，但影响在不同任务类型间差异显著。代码生成、合规性和安全关键决策等任务对精度降低更敏感，而研究、理解和分析任务则保持鲁棒甚至可能受益于低精度。这些观察被作为**指示性趋势**而非确定性结论，以激励系统设计。它们表明**统一精度策略是次优的**，需要基于任务特征的自适应精度分配。

QuantClaw 通过将精度视为**运行时可控资源**来解决这一问题。它在服务提供者层面运作，为固定模型适配执行精度，无需用户干预。因此，用户无需在质量、成本和延迟之间进行权衡管理——这些由系统透明处理。

### 3.2 QuantClaw 流水线

QuantClaw 流水线的总览见图 4。我们详述如下。

#### 任务检测与路由接口

给定用户查询，QuantClaw 首先执行任务识别以确定任务类别，作为后续路由决策的主要信号。这通过**混合检测机制**实现：规则检测器使用预定义模式、关键词和简单结构线索（如格式或交互模式）处理明确情况；对于规则检测器未捕获的查询，**模型检测器**通过轻量级分类器处理模糊情况。设计有意保持模块化——这些检测器可互换，可通过更高级方法扩展或替代，因为此阶段的核心目标只是产生可靠的任务类型标签，而非依赖特定的检测策略。

#### 精度路由机制

任务识别后，QuantClaw 基于**预计算的任务-精度敏感度画像**（见第 2.3 节）执行精度路由。系统维护一个**模型变体池**，包含不同精度级别（如 16 位、8 位和 4 位），每个任务类型映射到从离线分析中推导出的推荐精度。运行时，路由直接明了：高敏感性任务以高精度执行以保持可靠性，低敏感性任务分配低精度以最大化效率，中等情况根据部署目标（如延迟或成本约束）决定。这一设计在不增加逐查询优化开销的情况下实现一致收益。

### 3.3 QuantClaw 系统特性

QuantClaw 被设计为实用的运行时层，具有以下关键系统特性：

- **自动适配**：基于推断的任务特征即时做出路由决策，无需任何用户参与
- **轻量部署**：作为插件层运行在现有模型之上
- **内置可观测性**：实时暴露路由决策及成本与性能指标，支持透明监控和在精细粒度控制（图 5-8 提供了相关示意图）

> **图 5：自动适配** - 整合任务检测器
> **图 6：智能路由** - 支持即时决策
> **图 7：完全可定制** - 通过仪表板界面交互
> **图 8：内置仪表板与可观测性** - 概览状态

---

## 4 QuantClaw 的收益（Benefits of QuantClaw）

### 实验设置

我们在 **PinchBench（v1.2.0 和 v2.0.0）** 上进行评估。该基准包含多样化的 OpenClaw 风格工作负载，使其成为观察不同任务类型如何响应精度变化的合适测试平台。我们评估两个模型骨干网络：GLM-4.7-Flash 和 GLM-5，在三种数值设置下：高精度基线（GLM-4.7-Flash 为 BF16，GLM-5 为 FP8）、统一低精度配置（INT4）以及 **QuantClaw**（根据任务特征自适应选择精度）。测量指标包括 **Score**、**Cost** 和 **Time**。注意，我们选择 PinchBench 而非 ClawEval，并采用 INT4 量化而非第 2 节中描述的 NVFP4，因为我们希望验证第 2.3 节中关于任务级变异性的**泛化性**。

### 结果与权衡分析

基于 **表 4**（见附录 A）中的吞吐量比较，INT4 在相同延迟约束下比 BF16 实现了平均 **14.34% 的吞吐量提升**。考虑到定价简单性和行业折扣实践 [42]，我们将 INT4 令牌价格设为 BF16 价格的 85%。

**表 2：QuantClaw 与固定精度基线的对比（PinchBench）。QuantClaw 实现了更好的性能-效率权衡，在保持或提升任务性能的同时降低成本和延迟。**

| 基准 | 模型 | 方法 | Score (最佳/平均)↑ | Cost (USD)↓ | Time (s)↓ |
|------|------|------|-------------------|-------------|-----------|
| PinchBench v1.2.0 | GLM-4.7-Flash | All BF16 | 81.57 / 81.26 | 0.001598 | 19.07 |
| | | All INT4 | 82.63 / 78.71 | 0.001422 | 21.80 |
| | | **QuantClaw** | **85.46 / 84.11** | **0.001252** | **17.47** |
| | GLM-5 | All FP8 | 87.65 / 87.08 | 0.0127 | 34.53 |
| | | All INT4 | 90.10 / 88.24 | 0.0105 | 32.19 |
| | | **QuantClaw** | **90.09 / 89.09** | **0.0119** | **33.21** |
| PinchBench v2.0.0 | GLM-4.7-Flash | All BF16 | 78.19 / 76.95 | 0.00233 | 57.10 |
| | | All INT4 | 75.24 / 73.87 | 0.00232 | 54.60 |
| | | **QuantClaw** | **79.78 / 76.95** | **0.00228** | **52.35** |
| | GLM-5 | All FP8 | 85.72 / 83.50 | 0.0196 | 62.22 |
| | | All INT4 | 89.31 / 81.92 | 0.0169 | 58.99 |
| | | **QuantClaw** | **87.25 / 85.59** | **0.0154** | **52.46** |

**关键结果解读：**
- **GLM-4.7-Flash（PinchBench v1.2.0）**：QuantClaw 将平均性能提升至 84.11（vs BF16 81.26 和 INT4 78.71），同时将延迟降至 **17.47s（8.4% 延迟改进）**，成本降至 **0.001252（21.7% 降低）**
- **GLM-5（PinchBench v1.2.0）**：QuantClaw 保持竞争力（89.09 vs FP8 87.08 和 INT4 88.24），同时略微降低延迟（33.21s vs 34.53s，1.04× 加速）和成本（0.0119 vs 0.0127，-6.3%）
- **GLM-5（PinchBench v2.0.0）**：QuantClaw 较 FP8 基线提高平均分 **2.09 分**，同时实现 **21.4% 成本节约**和 **15.7% 加速**

### 任务检测方法的消融研究

**表 3：不同任务检测方法的对比。** QuantClaw 支持规则检测和裁判模型两种方法。'+' 表示混合策略。

| 方法 | Accuracy (%)↑ | Macro F1 (%)↑ | 平均时间 (s/query)↓ |
|------|--------------|---------------|-------------------|
| RuleDetector | 83.13 | 65.90 | 0.0017 |
| BGE-M3 | 89.76 | 86.56 | 0.0200 |
| GLM-4.7-Flash-INT4 | 86.75 | 83.68 | 0.0800 |
| GLM-5-FP8 | 92.17 | 89.72 | 0.1717 |
| MiniCPM-4.1 | 87.35 | 82.25 | 1.5627 |
| **RuleDetector + BGE-M3** | **91.53** | **88.66** | **0.0149** |
| RuleDetector + GLM-5-FP8 | 93.37 | 91.30 | 0.1217 |
| RuleDetector + MiniCPM-4.1 | 90.05 | 87.35 | 0.5900 |

引入裁判模型提高了检测精度，同时增加了时间开销。混合策略实现了可接受的权衡，表现出最高的精度和合理的时间成本。这使得 **RuleDetector + BGE-M3** 成为 QuantClaw 的默认选择。

这些结果表明 QuantClaw 的收益并非来自统一降低精度，而是来自**选择性地**对容忍任务应用低精度，同时为敏感任务保留高精度，从而产生严格优于全精度或统一低精度执行的工作点。

---

## 5 结论（Conclusion）

我们证明了统一精度不仅效率低下，而且在 OpenClaw 系统中经济上不可行，因为量化敏感性在不同任务间差异显著。为应对这一问题，我们提出 **QuantClaw**，一种任务感知的精度路由机制，根据工作负载特征动态分配精度。QuantClaw 通过降低延迟和成本提高了效率，同时保持甚至提升了性能。这些结果表明，**精度应被视为动态的、任务依赖的资源**，为优化智能体系统提供了简单而有效的方向。

---

## 6 展望（Outlook）

当前的个人 AI 系统通常依赖于以统一高精度运行的单一模型，而不考虑任务复杂度。这导致了不必要的计算成本和延迟，因为许多请求并不需要最大化能力。QuantClaw 在 OpenClaw 中提出了一种替代范式：**精度和模型能力应根据任务需求动态分配**。通过将轻量级任务路由到低精度配置，为高要求工作负载保留更强资源，QuantClaw 提高了整体系统效率，而不增加用户复杂度。更广泛地说，这指向 OpenClaw 系统演进中的一种转变：不是简单整合多个模型，而是主动协调它们。在这个意义上，QuantClaw 是向**将精度和模型能力视为多模型系统中可分配资源**迈出的具体一步。

---

## 附录 A：附加结果

**表 4：GLM-4.7-Flash 在 BF16 和 INT4 下的最大并发数和输出吞吐量，其中至少 90% 的请求满足 TTFT ≤ 500ms 且 TPOT ≤ 10ms。INT4 在所有评估设置中比 BF16 实现了 14.34% 的平均吞吐量提升。**

| 输入长度 | 输出长度 | 精度 | 并发数 | 输出吞吐量(tok/s) | 增益 |
|----------|----------|------|--------|-------------------|------|
| 2048 | 4096 | BF16 | 32 | 3326.00 | 24.01% |
| | | INT4 | 40 | 4124.73 | |
| 2048 | 8192 | BF16 | 32 | 3078.00 | 7.12% |
| | | INT4 | 32 | 3297.00 | |
| 4096 | 2048 | BF16 | 32 | 3164.00 | 7.27% |
| | | INT4 | 32 | 3394.00 | |
| 4096 | 4096 | BF16 | 24 | 2519.00 | 29.72% |
| | | INT4 | 32 | 3267.72 | |
| 8192 | 1024 | BF16 | 20 | 1969.00 | 18.78% |
| | | INT4 | 22 | 2338.70 | |
| 8192 | 2048 | BF16 | 20 | 1981.00 | 6.01% |
| | | INT4 | 20 | 2100.00 | |
| 8192 | 4096 | BF16 | 18 | 1829.77 | 13.86% |
| | | INT4 | 20 | 2083.31 | |
| 8192 | 8192 | BF16 | 16 | 1680.58 | 7.96% |
| | | INT4 | 18 | 1814.30 | |
| **平均吞吐量增益** | | | | | **14.34%** |

---

## 参考文献

[1] Wu et al. Autogen: Enabling next-gen llm applications via multi-agent conversations. COLM, 2024.
[2] Li et al. Camel: Communicative agents for "mind" exploration of large language model society. NeurIPS, 2023.
[3] Luo et al. Gui-r1: A generalist r1-style vision-language action model for gui agents. arXiv:2504.10458, 2025.
[4] Lu et al. Ui-r1: Enhancing efficient action prediction of gui agents by reinforcement learning. AAAI, 2026.
[5] Zhao et al. An agentic system for rare disease diagnosis with traceable reasoning. Nature, 2026.
[6] Huang et al. Understanding the planning of llm agents: A survey. arXiv:2402.02716, 2024.
[7] Ferrag et al. From llm reasoning to autonomous ai agents: A comprehensive review. arXiv:2504.19678, 2025.
[8] Putta et al. Agent q: Advanced reasoning and learning for autonomous ai agents. arXiv:2408.07199, 2024.
[9] Dong et al. A survey on code generation with llm-based agents. arXiv:2508.00083, 2025.
[10] Liu et al. Dynamic llm-agent network. arXiv:2310.02170, 2023.
[11] Jin et al. Stella: Towards a biomedical world model with self-evolving multimodal agents. bioRxiv, 2025.
[12] Gao et al. Empowering biomedical discovery with ai agents. Cell, 187(22):6125–6151, 2024.
[13] OpenClaw. GitHub repository, 2026.
[14] Nous Research. Hermes agent. GitHub repository, 2026.
[15] Anthropic. Claude code, 2025.
[16] Zhang et al. Chain of agents: Large language models collaborating on long-context tasks. NeurIPS, 2024.
[17] Xiao et al. Improving the efficiency of llm agent systems through trajectory reduction. arXiv:2509.23586, 2025.
[18] Ding et al. Calibrate-then-act: Cost-aware exploration in llm agents. arXiv:2602.16699, 2026.
[19] Sui et al. Stop overthinking: A survey on efficient reasoning for large language models. arXiv:2503.16419, 2025.
[20] APIYI Technical Team. Why is OpenClaw so token-intensive? 6 reasons analyzed and money-saving guide.
[21] Liu et al. Llm-qat: Data-free quantization aware training for large language models. Findings of ACL, 2024.
[22] Li et al. Batquant: Outlier-resilient mxfp4 quantization via learnable block-wise optimization. arXiv:2603.16590, 2026.
[23] Liu et al. Freeact: Freeing activations for llm quantization. arXiv:2603.01776, 2026.
[24] Li et al. Svdquant: Absorbing outliers by low-rank components for 4-bit diffusion models. arXiv:2411.05007, 2024.
[25] Liu et al. Spinquant: Llm quantization with learned rotations. arXiv:2405.16406, 2024.
[26] Sun et al. Flatquant: Flatness matters for llm quantization. arXiv:2410.09426, 2024.
[27] Dong et al. Can compressed llms truly act? An empirical evaluation of agentic capabilities in llm compression. arXiv:2505.19433, 2025.
[28] Liu et al. Quantization hurts reasoning? An empirical study on quantized reasoning models. arXiv:2504.04823, 2025.
[29] Huang et al. An empirical study of llama3 quantization: From llms to mllms. Visual Intelligence, 2(1):36, 2024.
[30] Zhao et al. Benchmarking post-training quantization in llms. arXiv:2502.13178, 2025.
[31] Zhang et al. Benchmarking post-training quantization under microscaling floating point formats. arXiv:2601.09555, 2026.
[32] Ye et al. Claw-eval: Toward trustworthy evaluation of autonomous agents. arXiv:2604.06132, 2026.
[33] Zeng et al. Glm-4.5: Agentic, reasoning, and coding (arc) foundation models. arXiv:2508.06471, 2025.
[34] Zeng et al. Glm-5: from vibe coding to agentic engineering. arXiv:2602.15763, 2026.
[35] Alvarez et al. Introducing nvfp4 for efficient and accurate low-precision inference. NVIDIA Blog, 2025.
[36] Chen et al. Int vs fp: A comprehensive study of fine-grained low-bit quantization formats. arXiv:2510.25602, 2025.
[37] Cook et al. Four over six: More accurate nvfp4 quantization with adaptive block scaling. arXiv:2512.02010, 2025.
[38] Zhao et al. Unleashing low-bit inference on ascend npus: A comprehensive evaluation of hifloat formats. arXiv:2602.12635, 2026.
[39] Koparkar. Mixture of experts powers the most intelligent frontier ai models. NVIDIA Blog, 2025.
[40] Mitrasish. Fp4 quantization on blackwell gpus. Spheron Blog, 2026.
[41] Knoop & Holtmann. Private llm inference on consumer blackwell gpus. arXiv:2601.09527, 2026.
[42] Kurtic et al. "Give me bf16 or give me death"? accuracy-performance trade-offs in llm quantization. ACL, 2025.
[43] Chen et al. Bge m3-embedding: Multi-lingual, multi-functionality, multi-granularity text embeddings through self-knowledge distillation. arXiv:2402.03216, 2024.
