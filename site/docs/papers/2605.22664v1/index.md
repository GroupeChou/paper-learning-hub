# WorkstreamBench: Evaluating LLM Agents on End-to-End Spreadsheet Tasks in Finance
> WorkstreamBench：Evaluating 大语言模型Agents on End-to-End Spreadsheet Tasks in Finance


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
- **论文链接**：[https://arxiv.org/abs/2605.22664v1](https://arxiv.org/abs/2605.22664v1)
- **状态**：已生成

## 摘要

LLM 智能体越来越被期望执行端到端工作流，从高级用户指令生成完整的工件。为满足企业需求，前沿 AI 实验室开发了能够从零开始构建完整电子表格的智能体。这在金融领域尤其重要，其中复杂的数据分析、建模和报告是日常工作。

## 1. 引言

### 中文翻译

LLM 智能体越来越被期望执行端到端工作流，从高级用户指令生成完整的工件。为满足企业需求，前沿 AI 实验室开发了能够从零开始构建完整电子表格的智能体。这在金融领域尤其重要，其中复杂的数据分析、建模和报告是日常工作。

### 术语解释

| 术语 | 英文 | 解释 |
|------|------|------|
| 智能体评估 | Agent Evaluation | 评估自主智能体在特定任务上的性能和安全性的方法论 |
| 端到端工作流 | End-to-end Workflow | 从高级用户指令到完整工件的完整执行流程 |
| 范围扩展 | Scope Expansion | 智能体执行超出用户请求范围的不必要操作 |

### 关键 takeaway

- 该工作聚焦于 LLM智能体、电子表格、金融工作流 领域的前沿问题
- 提出了新的评估方法或技术方案来解决现有方法的不足

## 2. 方法

### 中文翻译

WorkstreamBench 是一个评估 LLM 智能体在金融领域端到端电子表格任务上的基准。包含从真实金融工作流中提取的多种任务类型：数据清洗与整合、财务建模、报表生成、敏感性分析和场景模拟。每个任务有明确的评估标准和参考答案。

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

评估了多个主流 LLM 智能体，结果显示智能体在简单的数据操作任务上表现良好，但在需要领域知识的多步推理任务上显著下降。即使是最好模型在复杂财务建模中的端到端成功率也不到 40%。

### 关键 takeaway

- 实验证明了方法在多个场景下的有效性
- 结果揭示了当前技术的能力边界和未来改进方向

## 4. 结论

### 中文翻译

WorkstreamBench 揭示了当前 LLM 智能体在真实金融工作流中的能力边界，为领域特定的智能体能力提升提供了明确的改进方向。

### 关键 takeaway

- 该工作为该领域提供了新的评估基准或技术方案
- 研究结果为后续工作奠定了重要基础

## 复核建议

- 建议对照原文详细复核方法部分的具体技术细节
- 关键定量结果建议参考原文中的完整表格和图表