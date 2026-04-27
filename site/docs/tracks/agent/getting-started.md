---
description: AI Agent 入门 — ReAct、Toolformer、Generative Agents 三篇奠基性论文导读
---

# 🚀 Agent 入门：基础概念与经典论文

## 前置知识

在开始路线学习之前，需要了解以下核心概念：

### Agent 是什么？

**Agent = LLM + 工具 + 记忆 + 规划**

一个 AI Agent 核心由四部分构成：

```
LLM（大语言模型）  ← 推理中枢
    ↓
工具（Tools）     ← 外部世界交互
    ↓
记忆（Memory）    ← 历史上下文保持
    ↓
规划（Planning）  ← 目标分解与执行策略
```

### 关键概念速查

| 概念 | 全称 | 说明 |
|------|------|------|
| **CoT** | Chain-of-Thought | 思维链，让 LLM 显式展示推理步骤 |
| **ReAct** | Reasoning + Acting | 推理与行动交替进行，CoT 的实践版 |
| **Tool Use** | 工具调用 | Agent 调用外部工具（API/代码/搜索） |
| **RAG** | Retrieval-Augmented Generation | 检索增强生成，知识库 + LLM |
| **MCP** | Model Context Protocol | Anthropic 提出的 Agent 上下文协议 |
| **Multi-Agent** | 多智能体 | 多个 Agent 协作完成复杂任务 |

---

## 入门三篇必读

### 1. ReAct — 推理 + 行动的协同

> **ReAct: Synergizing Reasoning and Acting in Language Models**
> Google Research / Princeton, 2023

**一句话总结**：让 LLM 交替进行"推理步骤"和"行动执行"，解决传统 CoT 缺乏外部交互能力的问题。

**为什么是必读**：ReAct 是当前顺丰 Agent 体系的底层执行逻辑原型——每次预测请求，Agent 需要推理（理解需求）→ 行动（查询数据/调用 Skill）→ 观察结果 → 再推理。

**核心框架**：

```
Thought → Action → Observation → Thought → ...
```

**关键实验结果**：
- HotpotQA（多跳问答）：ReAct 显著优于 CoT
- AlfWorld（物理推理）：ReAct + CoT 混合模式效果最佳

**延伸思考**：在物流预测场景中，ReAct 模式对应：理解需求（Thought）→ 查询数据库或调用 Skill（Action）→ 获得预测结果（Observation）→ 评估置信度（Thought）。

---

### 2. Toolformer — 语言模型自我学习使用工具

> **Toolformer: Language Models Can Teach Themselves to Use Tools**
> Meta AI, 2023

**一句话总结**：用自监督方式，让 LLM 自己学会调用外部工具（搜索/计算器/日历），不需要人工标注。

**为什么是必读**：顺丰 Agent 的 Skills 体系本质上是"工具集"，Toolformer 展示了如何让 Agent 自动学习新工具，而不是手动写调用代码。

**核心方法**：
1. 少量手工标注工具调用样本
2. 用这些样本微调 LLM，让它学会"什么时候该调用工具"
3. 工具调用通过特殊 token 插入到生成序列中

**延伸思考**：顺丰的 7 类 Skills 对应 7 类工具，Toolformer 的思路可以帮助 Agent **自动发现**需要调用哪个 Skill，而不是硬编码判断逻辑。

---

### 3. Generative Agents — 记忆/规划/反思架构

> **Generative Agents: Interactive Simulacra of Human Behavior**
> Stanford / Google, 2023

**一句话总结**：构建了一个虚拟小镇，里面住着 25 个 AI Agent，它们有记忆、会规划、能反思，行为高度拟人化。

**为什么是必读**：顺丰 Agent 需要处理**多日/多轮交互**（不是单次问答），Generative Agents 的三段式架构（记忆流 → 规划 → 反思）是目前最完整的多轮 Agent 架构参考。

**核心架构**：

```
记忆流（Memory Stream）
    ↓ 重要性筛选
反思（Reflection）→ 高级推断
    ↓ 分解
规划（Plan）→ 具体行动计划
    ↓ 执行
Agent 行为
```

**关键机制**：
- **记忆流**：所有 Experience 以时间顺序存储
- **重要性评分**：哪些记忆值得保留（与当前目标相关）
- **反思**：将低级经验凝练为高级判断（"我上周总是迟到，可能因为路线规划有问题"）
- **规划**：基于反思结果，生成未来几小时的行动序列

**延伸思考**：物流 Agent 的长时记忆设计可以借鉴——每次预测结果 + 实际值的偏差都是一次 Experience，积累后可以自动改进 Skill 权重。

---

## 三篇论文的逻辑关系

```
Toolformer（工具能力）
    ↓ 基础能力
ReAct（执行框架）→ Agent 的"思考-行动"循环
    ↓ 扩展到多轮
Generative Agents（长时记忆）→ Agent 的"记忆-规划-反思"
```

---

## 实践建议

1. **先读 ReAct**（最简单，核心思想一页纸）
2. **再看 Toolformer**（方法细节多，快速浏览方法部分即可）
3. **最后 Generative Agents**（架构最完整，细读第三节记忆模块）

每篇论文读完后，在 [经典必读页面](../../guides/classics.md) 追加：
- 核心公式或关键机制
- 与顺丰业务的连接点
- 可复用的代码模式

---

## 下一步

掌握基础后，进入核心论文精读：

[→ 🐝 HiveMind：OS 启发的 Agent 并发调度](papers/2604.17111v1/index.md){ .md-button }
