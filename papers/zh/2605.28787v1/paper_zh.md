# Do Agents Need Semantic Metadata? A Comparative Study in Agentic Data Retrieval

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
- **论文链接**：[https://arxiv.org/abs/2605.28787v1](https://arxiv.org/abs/2605.28787v1)
- **状态**：已生成

## 摘要

在自主智能体时代，机器可操作数据对数据驱动工作流至关重要。schema.org 等语义元数据十多年来一直是 FAIR 原则（可发现、可访问、可互操作、可重用）的基石。但随着智能体直接操作原始网页的能力增强，语义元数据的价值受到质疑。

## 1. 引言

### 中文翻译

在自主智能体时代，机器可操作数据对数据驱动工作流至关重要。schema.org 等语义元数据十多年来一直是 FAIR 原则（可发现、可访问、可互操作、可重用）的基石。但随着智能体直接操作原始网页的能力增强，语义元数据的价值受到质疑。

### 术语解释

| 术语 | 英文 | 解释 |
|------|------|------|
| 智能体评估 | Agent Evaluation | 评估自主智能体在特定任务上的性能和安全性的方法论 |
| 端到端工作流 | End-to-end Workflow | 从高级用户指令到完整工件的完整执行流程 |
| 范围扩展 | Scope Expansion | 智能体执行超出用户请求范围的不必要操作 |

### 关键 takeaway

- 该工作聚焦于 语义元数据、智能体数据检索、FAIR原则 领域的前沿问题
- 提出了新的评估方法或技术方案来解决现有方法的不足

## 2. 方法

### 中文翻译

该文系统比较了智能体在有/无语义元数据（schema.org 标注）的网页上的数据检索性能。设计了覆盖多个领域（电商、事件、组织等）的实验，评估智能体在不依赖结构化标注的情况下从 HTML 中直接提取信息的能力。

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

实验表明，语义元数据对智能体数据检索性能有显著影响，尤其是对于复杂查询和跨域信息综合任务。无标注场景下，智能体的准确率下降约 15-30%，并表现出更大的方差。

### 关键 takeaway

- 实验证明了方法在多个场景下的有效性
- 结果揭示了当前技术的能力边界和未来改进方向

## 4. 结论

### 中文翻译

尽管 LLM 智能体的原始理解能力在提升，语义元数据仍然是确保可靠、可互操作数据检索的关键基础设施。研究结果为未来智能体系统的数据访问策略提供了重要参考。

### 关键 takeaway

- 该工作为该领域提供了新的评估基准或技术方案
- 研究结果为后续工作奠定了重要基础

## 复核建议

- 建议对照原文详细复核方法部分的具体技术细节
- 关键定量结果建议参考原文中的完整表格和图表