# When Agents Look the Same: Quantifying Distillation-Induced Similarity in Tool-Use Behaviors

- **机构**：Anthropic（作者来自中国科学技术大学、NJU、M-A-P）
- **主题**：AI Agent
- **发布日期**：2026-04-23
- **来源**：[Anthropic arXiv query](https://arxiv.org/abs/2604.21255v1)
- **论文链接**：[https://arxiv.org/pdf/2604.21255v1](https://arxiv.org/pdf/2604.21255v1)
- **状态**：已生成

## 摘要

### 中文翻译

模型蒸馏是LLM agent快速进步的主要驱动力，但它往往导致行为同质化。许多新兴agent共享几乎相同的推理步骤和失败模式，表明它们可能是少数主导教师的蒸馏回声。

然而，现有指标无法区分任务成功所必需的必要行为与反映模型自主偏好的非必要模式。

我们提出两个互补指标来分离非必要的行为模式：
- **Response Pattern Similarity (RPS)**：用于语言对齐的响应模式相似性
- **Action Graph Similarity (AGS)**：用于将工具使用习惯建模为有向图的行动图相似性

在τ-Bench和τ²-Bench上评估来自8个提供商的18个模型，对比Claude Sonnet 4.5 (thinking)，我们发现同家族模型对的AGS得分比跨家族模型对高5.9个百分点，Kimi-K2 (thinking)达到82.6% Snode和94.7% Sdep，超越Anthropic自己的Opus 4.1。

受控蒸馏实验进一步确认AGS可区分教师特定收敛与一般改进。RPS和AGS捕获不同的行为维度（Pearson r = 0.491），为agent生态系统中的行为收敛提供互补的诊断信号。

### 术语解释

- **Model distillation**：模型蒸馏，用大模型训练小模型的技术
- **Behavioral homogenization**：行为同质化，不同模型变得相似的现象
- **Mandatory behaviors**：必要行为，任务成功所必需的行为
- **Non-mandatory behaviors**：非必要行为，反映模型自主偏好的行为
- **τ-Bench**：评估agent工具使用能力的benchmark

### 关键 takeaway

- 核心问题：模型蒸馏导致agent行为同质化，缺乏真正的独立性
- 提出两个新指标：RPS（语言相似性）和AGS（工具使用图相似性）
- Kimi-K2在蒸馏指标上甚至超过了Anthropic的Opus 4.1

---

## Section 1: Introduction

### 中文翻译

当前高性能LLM agent的"寒武纪大爆发"常常伴随着一种似曾相识的感觉。尽管来源多样，许多新兴agent表现出相当一致的行为：它们共享几乎相同的推理步骤、冗余的工具调用习惯，甚至相同的失败模式。

这表明这些模型可能不是独立的突破，而是少数主导教师的蒸馏回声。这种普遍的模仿导致理论上独立的模型收敛于相同的"坏习惯"。

例如，许多agent不是优化效率，而是镜像教师的冗长推理和冗余工具调用模式，如试错每个可用工具，即使解决方案已经很明显。

这种集体对齐意味着生态系统缺乏真正的鲁棒性；不同模型不再提供独立验证，而是以完全相同的方式失败。

### 术语解释

- **Cambrian explosion**：寒武纪大爆发，此处比喻LLM agent的快速发展
- **Convergence of "bad habits"**：坏习惯的收敛
- **Collective alignment**：集体对齐
- **Independent verification**：独立验证

### 图表/公式说明

**Figure 1(a): item exchange任务上的示例轨迹**

- Kimi-K2和Claude共享相似的响应措辞和可选工具选择
- GPT-5采用不同的风格
- 高相似性（High Similarity）vs 低相似性（Low Similarity）

**Figure 1(b): 非Anthropic模型的RPS vs AGS**

- Kimi-K2 (thinking)占据右上角，最接近参考模型
- Deepseek R1/V3位于中间位置
- 展示了不同模型与Claude的行为相似性差异

### 关键 takeaway

- Agent生态系统中存在严重的行为趋同问题
- 独立模型可能都在"复制"相同的失败模式

---

## Section 2: Related Work

### 中文翻译

相关工作涵盖LLM agent评估、蒸馏方法、行为多样性和多模态对齐。

### 关键概念

- **τ-Bench**：一个评估agent工具使用能力的benchmark
- **Agent alignment**：使agent行为符合人类期望的技术
- **Behavioral diversity**：不同模型展现不同行为的能力

---

## Section 3: Metrics

### 中文翻译

### 3.1 Response Pattern Similarity (RPS)

RPS通过将轨迹分为五个规范阶段来测量语言相似性：
1. **Authentication（认证）**
2. **Elicitation（引出）**
3. **Execution（执行）**
4. **Verification（验证）**
5. **Notification（通知）**

沿风格、结构和对齐维度评分。

### 3.2 Action Graph Similarity (AGS)

AGS通过三个子指标测量行动级相似性：

**Snode**：可选工具一致性
- 例如：对于航班取消任务，所有模型必须调用cancel_reservation，但有些模型会额外调用get_reservation_details来double-check
- 当两个模型共享此类可选选择时，它们可能共享训练信号

**Sseq**：顺序习惯
- 捕获连续习惯，如写后读

**Sdep**：依赖结构
- 测量工具调用之间的依赖关系图相似性

### 术语解释

- **Snode**：节点相似性，可选工具选择的一致性
- **Sseq**：序列相似性，工具调用顺序的相似性
- **Sdep**：依赖相似性，工具调用依赖图的相似性
- **Trajectory**：轨迹，agent执行任务的过程记录

### 关键 takeaway

- RPS和AGS捕获不同的行为维度（Pearson r = 0.491）
- 两者互补，提供全面的行为收敛诊断

---

## Section 4: Evaluation

### 中文翻译

### 4.1 主要发现

**同家族模型对 vs 跨家族模型对**
- 同家族模型对的AGS得分比跨家族模型对高**5.9个百分点**
- 表明蒸馏影响在家族内更强

**Kimi-K2的突出表现**
- Snode达到**82.6%**
- Sdep达到**94.7%**
- 超越Anthropic自己的Opus 4.1

### 图表/公式说明

**Figure 1(b)**展示了18个模型在RPS和AGS两个维度上的分布：
- 横轴：RPS（Response Pattern Similarity）
- 纵轴：AGS（Action Graph Similarity）
- Kimi-K2 (thinking)在右上角，表示与Claude高度相似

### 4.2 受控蒸馏实验

实验确认AGS可区分：
- **教师特定收敛**：来自特定教师模型的行为趋同
- **一般改进**：模型能力的普遍提升

### 关键 takeaway

- 蒸馏不仅提升能力，也带来特定教师的行为特征
- AGS是检测蒸馏影响的有效指标

---

## Section 5: Implications

### 中文翻译

### 5.1 生态系统透明度

行为相似性指标帮助理解agent生态系统的结构：
- 哪些模型是真正的独立创新
- 哪些只是在复制已有能力

### 5.2 安全考量

当多个模型以相同方式失败时，攻击者可以设计针对所有模型的攻击。

### 5.3 未来方向

- 开发降低蒸馏负面影响的训练方法
- 保持能力提升的同时保留行为多样性

---

## 复核建议

- 论文共21页，内容已覆盖主要Sections
- 建议核对Section 6-10的详细实验设置
- GitHub仓库：https://github.com/Syuchin/AgentEcho

---

## 与物流预测的关联

这篇论文对物流预测场景的启示：

1. **Agent同质化问题**：物流系统中多个Agent可能共享相同的"失败模式"，需要多样化设计
2. **RPS/AGS指标**：可用于评估物流Agent的行为多样性
3. **蒸馏的代价**：追求性能提升可能导致Agent缺乏鲁棒性和独立性
4. **安全考量**：同质化的Agent系统更脆弱，需要防御性设计