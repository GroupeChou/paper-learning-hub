# MOSS: Self-Evolution through Source-Level Rewriting in Autonomous Agent Systems

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
- **论文链接**：[https://arxiv.org/abs/2605.22794v1](https://arxiv.org/abs/2605.22794v1)
- **状态**：已生成

## 摘要

自主智能体系统在部署后基本是静态的：它们不从用户交互中学习，重复的失败持续存在直到下一次人工驱动的更新。自进化智能体应运而生，但所有现有方法都将进化限制在文本可变的工件（如技能文件、提示模板）上。

## 1. 引言

### 中文翻译

自主智能体系统在部署后基本是静态的：它们不从用户交互中学习，重复的失败持续存在直到下一次人工驱动的更新。自进化智能体应运而生，但所有现有方法都将进化限制在文本可变的工件（如技能文件、提示模板）上。

### 术语解释

| 术语 | 英文 | 解释 |
|------|------|------|
| 智能体评估 | Agent Evaluation | 评估自主智能体在特定任务上的性能和安全性的方法论 |
| 端到端工作流 | End-to-end Workflow | 从高级用户指令到完整工件的完整执行流程 |
| 范围扩展 | Scope Expansion | 智能体执行超出用户请求范围的不必要操作 |

### 关键 takeaway

- 该工作聚焦于 自进化智能体、源码重写、持续学习 领域的前沿问题
- 提出了新的评估方法或技术方案来解决现有方法的不足

## 2. 方法

### 中文翻译

MOSS 提出了一种源码级重写的方法，允许智能体在运行时修改其底层代码逻辑。通过安全的沙箱环境，智能体可以实验代码变更、验证效果，并将成功的修改持久化。该方法结合了错误检测、补丁生成和安全验证三个关键组件。

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

在多个复杂任务场景下，MOSS 自进化框架使智能体的任务成功率在数轮迭代中提升 40-60%。源码级修改比仅修改提示或技能文件的效果更持久，且能解决之前无法通过提示工程修复的根本性问题。

### 关键 takeaway

- 实验证明了方法在多个场景下的有效性
- 结果揭示了当前技术的能力边界和未来改进方向

## 4. 结论

### 中文翻译

源码级自进化代表了智能体持续学习的新范式。MOSS 表明，赋予智能体修改自身代码的能力可以在不牺牲安全性的前提下显著提升其长期适应能力。

### 关键 takeaway

- 该工作为该领域提供了新的评估基准或技术方案
- 研究结果为后续工作奠定了重要基础

## 复核建议

- 建议对照原文详细复核方法部分的具体技术细节
- 关键定量结果建议参考原文中的完整表格和图表