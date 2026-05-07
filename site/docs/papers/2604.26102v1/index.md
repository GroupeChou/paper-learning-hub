---
title: "SWE-Edit: Rethinking Code Editing for Efficient SWE-Agent"
source: "https://arxiv.org/abs/2604.26102v1"
---

# SWE-Edit: Rethinking Code Editing for Efficient SWE-Agent

**原文链接**：[arXiv PDF](https://arxiv.org/pdf/2604.26102v1) | 点击阅读原论文完整内容

- **作者**：Yikai Zhang, Jiaxin Pei, Kenan Li, Maoquan Wang, Jin Pan, Yu Kang, Shengyu Fu, Elsie Nallipogu, Junjie Hu, Yufan Huang, Zijian Jin
- **机构**：Microsoft
- **发布日期**：2026-04-28
- **标签**：`AI Agent` `Code Editing` `SWE` `Multi-Agent` `Reinforcement Learning`

---

## 核心问题

当前 LLM 代码编辑界面存在**上下文耦合**问题：代码检查、修改规划和编辑执行混在同一个上下文窗口中，无关信息不断累积导致智能体性能下降。

## 方法概述

- **解耦架构**：将代码编辑拆分为两个专门子智能体——Viewer（按需提取任务相关代码）和 Editor（根据高层级自然语言计划执行修改）
- **自适应编辑模式**：使用 GRPO 训练 Qwen3-8B，让编辑器根据修改复杂度自动选择 `find-replace`（适合小改动）或 `whole-file rewrite`（适合复杂重构）
- **轻量级代码规范化**（Algorithm 1）：在奖励计算前去除注释、规范化空白，提供无需执行的编辑正确性代理指标
- **PR-Edit 基准**：提出可预测下游智能体性能的代码编辑基准，无需端到端测试即可评估编辑器模型

## 核心结果

| 指标 | 基线 | SWE-Edit | 提升 |
|------|------|---------|------|
| SWE-bench Verified 解决率 | 69.9% | **72.0%** | **+2.1%** |
| 推理成本 | $243.7 | **$200.1** | **-17.9%** |
| 编辑成功率 | 93.4% | **96.9%** | **+3.5%** |
| Viewer + GRPO 编辑器 (Qwen3-8B) 解决率 | — | 69.9% | +1.4% (vs 未训练) |

## 为什么值得关注

通过合理的接口解耦（而不是模型堆叠），用更小的模型完成了比更大模型更好的编辑效果，打破了"精度-成本"之间的权衡。

## 学习路线

- **前置知识**：SWE-bench 基准、LLM Agent 工具调用、GRPO 强化学习
- **相关论文**：SWE-Agent (Yang et al., 2024)、Aider Architect (Gauthier, 2024a)、Context-Folding (Sun et al., 2025)
- **深入方向**：端到端 Agentic RL 训练编辑器（不依赖静态真值奖励）、Agent-as-Judge 评估器替代 GPT Grader
