---
description: AI Agent 入门概念
---

# 📗 AI Agent 入门概念

## 核心概念

### 什么是 Agent？

Agent（智能体）是一种能够自主感知环境、做出决策并执行行动的智能系统。

### Agent 的核心能力

| 能力 | 说明 | 相关论文 |
|------|------|----------|
| **推理 (Reasoning)** | 基于已有知识进行逻辑推导 | CoT, ReAct |
| **规划 (Planning)** | 将复杂任务分解为子任务 | Tree of Thoughts |
| **工具使用 (Tool Use)** | 调用外部工具扩展能力 | Toolformer |
| **记忆 (Memory)** | 存储和检索历史信息 | Generative Agents |
| **协作 (Multi-Agent)** | 多 Agent 协同完成复杂任务 | HiveMind |

---

## 入门必读

| 论文 | 核心内容 | 优先级 |
|------|----------|--------|
| ReAct | 推理 + 行动协同 | ⭐⭐⭐⭐⭐ |
| Toolformer | 工具调用基础 | ⭐⭐⭐⭐⭐ |
| Generative Agents | 记忆/规划/反思三段式 | ⭐⭐⭐⭐⭐ |

---

## 与物流预测的关联

顺丰预测底盘 Agent 体系依赖这些基础能力：

- **规划能力** → 预测 Agent 需要规划数据获取/特征工程/模型调用流程
- **工具使用** → 调用外部 API（天气/促销/舆情）获取预测特征
- **记忆能力** → 积累历史预测误差，形成自适应调整机制

---

[← 返回 Agent 路线](index.md){ .md-button }
[继续阅读：经典必读 →](../agent/papers.md){ .md-button }
