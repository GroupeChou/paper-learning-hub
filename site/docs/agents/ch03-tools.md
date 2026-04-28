# 第三章：工具使用与API篇

> **学习目标**：学习 Agent 如何调用外部工具和 API 完成复杂任务。

---

## 📋 本章大纲

### 3.1 工具学习能力

| 论文 | 机构 | 年份 | 主题 | 状态 |
|------|------|------|------|------|
| **Toolformer: Language Models Can Teach Themselves to Use Tools** | Meta AI | 2023 | 自主学会工具调用 | 🔄 待收录 |
| **Function Calling in LLMs** | OpenAI | 2023 | 结构化函数调用 | 🔄 待收录 |
| **Gorilla: LLM with API Store** | UC Berkeley | 2023 | 大规模 API 集成 | 🔄 待收录 |

### 3.2 本库已收录相关论文

| 论文 | 机构 | 日期 | 与本章关系 | 入口 |
|------|------|------|-----------|------|
| **QuantClaw: Precision Where It Matters for OpenClaw** | 智谱 | 2026-04-24 | 长上下文 + 多轮推理中的工具精度优化 | [原文](https://arxiv.org/pdf/2604.22577v1) ❌ 待处理 |

---

## 💡 核心概念

工具使用是 Agent 区别于普通 LLM 的关键能力：
- **Toolformer** 通过自监督学习让模型自主学会何时调用什么工具
- **Function Calling** 将工具调用结构化为 JSON Schema
- **Gorilla** 展示了 LLM 可以在数千个 API 中准确选择正确的调用方式
