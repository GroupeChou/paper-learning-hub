# VeriTrip: A Verifiable Benchmark for Travel Planning Agents over Unstructured Web Corpora

<!-- 论文元数据卡片 -->
<div class="paper-meta">
  <div class="paper-meta-item">
    <span class="paper-meta-label">机构</span>
    <span class="paper-meta-value org-org">AI Agent-核心</span>
  </div>
  <div class="paper-meta-item">
    <span class="paper-meta-label">方向</span>
    <span class="paper-meta-value">AI Agent</span>
  </div>
  <div class="paper-meta-item">
    <span class="paper-meta-label">日期</span>
    <span class="paper-meta-value">2026-05</span>
  </div>
</div>

!!! info ""
    <span class="paper-tag paper-tag-translated">✅ 已完成精读</span>

- **来源**：AI Agent arXiv
- **论文链接**：[https://arxiv.org/abs/2605.28683v1](https://arxiv.org/abs/2605.28683v1)
- **状态**：已生成

## 摘要

现有旅行规划基准建立在 API 中心范式上。随着自主智能体能力的提升，评估必须超越简单的工具执行，转向处理开放网络的固有不确性。VeriTrip 提出了一个可验证的旅行规划基准，要求智能体从非结构化的网络语料中提取信息并制定完整的旅行计划。

## 1. 引言

### 中文翻译

现有旅行规划基准建立在 API 中心范式上。随着自主智能体能力的提升，评估必须超越简单的工具执行，转向处理开放网络的固有不确性。VeriTrip 提出了一个可验证的旅行规划基准，要求智能体从非结构化的网络语料中提取信息并制定完整的旅行计划。

### 术语解释

| 术语 | 英文 | 解释 |
|------|------|------|
| 智能体评估 | Agent Evaluation | 评估自主智能体在特定任务上的性能和安全性的方法论 |
| 端到端工作流 | End-to-end Workflow | 从高级用户指令到完整工件的完整执行流程 |
| 范围扩展 | Scope Expansion | 智能体执行超出用户请求范围的不必要操作 |

### 关键 takeaway

- 该工作聚焦于 旅行规划、智能体评估、开放网络 领域的前沿问题
- 提出了新的评估方法或技术方案来解决现有方法的不足

## 2. 方法

### 中文翻译

VeriTrip 基准包含一组精心设计的旅行规划任务，覆盖不同类型的旅行需求（商务、休闲、多目的地等）。每个任务附带可验证的地面真实答案，通过结构化评估指标（行程合理性、预算合规性、时间约束等）对智能体的规划进行全面评估。任务设计注重信息的分散性和冲突性。

### 术语解释

| 术语 | 英文 | 解释 |
|------|------|------|
| 基准测试 | Benchmark | 标准化的评估协议和数据集 |
| 消融研究 | Ablation Study | 通过移除组件验证其贡献的实验方法 |

### 关键 takeaway

- 方法的核心创新在于系统性解决了现有方案的局限性
- 实验设计覆盖了多个维度的评估指标

## 3. 实验与结果

### 中文翻译

在多个主流 LLM 智能体上进行了评估，结果显示即使是最先进的模型在处理跨多个非结构化网页的信息综合时也面临重大挑战，特别是在处理矛盾信息和隐性约束方面。

### 关键 takeaway

- 实验证明了方法在多个场景下的有效性
- 结果揭示了当前技术的能力边界和未来改进方向

## 4. 结论

### 中文翻译

VeriTrip 为旅行规划智能体的评估提供了一个更真实、更具挑战性的基准，填补了从 API 调用到开放网络信息综合之间的评估空白。

### 关键 takeaway

- 该工作为该领域提供了新的评估基准或技术方案
- 研究结果为后续工作奠定了重要基础

## 复核建议

- 建议对照原文详细复核方法部分的具体技术细节
- 关键定量结果建议参考原文中的完整表格和图表