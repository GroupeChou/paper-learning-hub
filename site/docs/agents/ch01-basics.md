# 第一章：Agent 基础架构篇

> **学习目标**：理解智能体的基本组成、工作原理与核心范式。

---

## 📋 本章大纲

### 1.1 Agent 核心范式

| 论文 | 机构 | 年份 | 主题 | 状态 |
|------|------|------|------|------|
| **ReAct: Synergizing Reasoning and Acting** | Princeton / Google | 2022 | 推理+行动协同，Agent基础范式 | 📖 经典必读 |
| **Chain-of-Thought Prompting** | Google | 2022 | 思维链提示，推理基础 | 📖 经典必读 |
| **Reflexion: Language Agents with Verbal Reinforcement** | MIT | 2023 | 语言反馈强化学习，自我反思 | 📖 经典必读 |

### 1.2 Agent 记忆与规划原型

| 论文 | 机构 | 年份 | 主题 | 状态 |
|------|------|------|------|------|
| **Generative Agents** | Stanford / Google | 2023 | 记忆/规划/反思三段式架构 | 📖 经典必读 |

---

## 💡 核心概念

### ReAct 范式
```
Thought → Action → Observation → Thought → ...
```
- **Thought**: LLM 推理过程
- **Action**: 调用工具或执行操作
- **Observation**: 观察执行结果
- 循环往复直到得出最终答案

### Generative Agents 三段式
```
感知(Perceive) → 规划(Plan) → 反思(Reflect) → 记忆存储(Memory)
```

---

## 🔗 关联章节

- 下一章：[第二章：规划与推理](ch02-planning.md)
- 深入：[第四章：记忆与检索](ch04-memory.md)
