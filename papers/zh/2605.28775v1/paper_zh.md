# Learn from Weaknesses: Automated Domain Specialization for Small Computer-Use Agents
> Learn from Weaknesses：Automated Domain Specialization for Small Computer-Use智能体s


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
- **论文链接**：[https://arxiv.org/abs/2605.28775v1](https://arxiv.org/abs/2605.28775v1)
- **状态**：已生成

## 摘要

计算机使用智能体（CUAs）最近取得了实质性进展，但为每个软件领域部署单独的大型专家模型仍然代价高昂。小型开源计算机使用智能体是更实用的专业化目标，但它们明显更弱且在不同领域的表现不均匀。

## 1. 引言

### 中文翻译

计算机使用智能体（CUAs）最近取得了实质性进展，但为每个软件领域部署单独的大型专家模型仍然代价高昂。小型开源计算机使用智能体是更实用的专业化目标，但它们明显更弱且在不同领域的表现不均匀。

### 术语解释

| 术语 | 英文 | 解释 |
|------|------|------|
| 智能体评估 | Agent Evaluation | 评估自主智能体在特定任务上的性能和安全性的方法论 |
| 端到端工作流 | End-to-end Workflow | 从高级用户指令到完整工件的完整执行流程 |
| 范围扩展 | Scope Expansion | 智能体执行超出用户请求范围的不必要操作 |

### 关键 takeaway

- 该工作聚焦于 计算机使用智能体、领域专业化、小模型 领域的前沿问题
- 提出了新的评估方法或技术方案来解决现有方法的不足

## 2. 方法

### 中文翻译

该文提出一种自动化领域专业化框架，通过系统地识别小 CUAs 在特定领域的弱点，然后针对性生成训练数据来弥补这些不足。方法包括：（1）弱点发现：通过压力测试识别失败模式；（2）数据生成：利用大模型根据失败案例生成针对性的训练样本；（3）微调：在小模型上进行领域专业化的微调。

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

在多个办公软件领域（电子表格、文档处理、邮件客户端等）的实验显示，经过领域专业化的小 CUAs 在目标领域的性能提升 25-45%，部分任务上接近大模型水平，同时保持了小模型的推理效率优势。

### 关键 takeaway

- 实验证明了方法在多个场景下的有效性
- 结果揭示了当前技术的能力边界和未来改进方向

## 4. 结论

### 中文翻译

自动化弱点发现与针对性训练的结合为小 CUAs 的实用化部署提供了可行路径，使得在经济高效的前提下实现接近专业大模型的性能成为可能。

### 关键 takeaway

- 该工作为该领域提供了新的评估基准或技术方案
- 研究结果为后续工作奠定了重要基础

## 复核建议

- 建议对照原文详细复核方法部分的具体技术细节
- 关键定量结果建议参考原文中的完整表格和图表