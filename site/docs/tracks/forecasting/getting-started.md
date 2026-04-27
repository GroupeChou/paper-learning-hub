---
description: 时序预测入门 — Transformer 基础与 Informer 长序列预测导读
---

# 🚀 时序预测入门：Transformer 基础与 Informer

## 前置知识

### 时序预测核心概念

**问题定义**：给定历史 $X = \{x_1, x_2, ..., x_T\}$，预测未来 $Y = \{x_{T+1}, ..., x_{T+\tau}\}$

其中 $\tau$ 是预测长度（horizon），$T$ 是回看窗口长度（lookback window）。

**顺丰场景示例**：
- 输入 $X$：过去 168 小时（7 天）的网点件量
- 预测 $Y$：未来 24 小时每小时的网点件量
- KPI：业务区 ±8%，网点 ±20%

### 关键术语

| 术语 | 说明 | 顺丰场景对应 |
|------|------|-------------|
| **Lookback Window** | 输入序列长度 | 过去多少小时预测未来 |
| **Prediction Horizon** | 预测长度 | 未来 1h/24h/72h |
| **Univariate / Multivariate** | 单变量 / 多变量预测 | 单网点件量 / 多网点+天气+促销 |
| **Global Model** | 全局模型（多场地共享） | 所有网点用同一个模型 |
| **One-to-One** | 一对一模型 | 每个网点单独建模 |

---

## 入门二篇必读

### 1. Attention Is All You Need — Transformer 基础

> **Attention Is All You Need**
> Google Brain, NeurIPS 2017

**一句话总结**：用纯注意力机制替代 RNN，提出 Transformer 架构——并行计算、长距离依赖、端到端可训练。

**为什么是必读**：Informer、Autoformer、PatchTST、iTransformer 都是 Transformer 的时序变体，不懂原始 Transformer 就不懂这些论文。

**核心架构**：

```
输入嵌入 → 多头自注意力 → 前馈网络 → 输出
           (Multi-Head Self-Attention)
```

**关键机制**：

| 机制 | 作用 | 时序预测中的意义 |
|------|------|----------------|
| **Scaled Dot-Product Attention** | $\text{Attention}(Q,K,V) = \text{softmax}(QK^T/\sqrt{d})V$ | 计算不同时间步之间的相关性 |
| **Multi-Head Attention** | 多个注意力头并行，学习不同子空间 | 捕捉季节性/趋势/异常等多模式 |
| **Positional Encoding** | 注入序列位置信息 | 区分"第1小时"和"第100小时" |
| **Encoder-Decoder** | 编码输入序列，解码生成输出 | 预测任务的标准结构 |

**在时序预测中的演进**：
- 原始 Transformer → 位置编码改为 **可学习的** 或 **时间特征编码**
- Encoder-Decoder → 多变体（Informer 的 Distill、Autoformer 的分解）

---

### 2. Informer — 长序列预测的高效 Transformer

> **Informer: Beyond Efficient Transformer for Long Sequence Time-Series Forecasting**
> Huawei Cloud, AAAI 2021 Best Paper

**一句话总结**：解决了 Transformer 在长序列预测中的三大问题：$O(L^2)$ 注意力复杂度、长序列输入编码效率低、预测速度慢。

**为什么是必读**：AAAI 2021 Best Paper，是时序预测领域影响力最大的深度学习论文，顺丰 72h+ 预测直接面临论文解决的三类问题。

**核心贡献（三合一）**：

| 贡献 | 问题 | 解决方案 | 结果 |
|------|------|---------|------|
| **ProbSparse Self-Attention** | $O(L^2)$ 注意力 | 稀疏注意力，只关注 Top-k 关键 query | $O(L \log L)$ |
| **Distillation** | 长输入编码 | 层级蒸馏，逐步缩短序列 | 压缩输入长度 |
| **Generative Decoder** | 逐点解码太慢 | 一次性生成整个序列 | 从 $O(N)$ 降至 $O(1)$ |

**核心公式**：

**ProbSparse Self-Attention**：
$$A(Q,K,V) = \text{softmax}\left(\frac{\overline{Q}K^T}{\sqrt{d}}\right)V$$

其中 $\overline{Q}$ 是通过 KL 散度筛选出的稀疏 Query，只保留 $Top\_u$ 个关键 query，$u = c \cdot L \cdot \log L$。

**顺丰场景对应**：
- 168h 预测 72h：$L=168, \tau=72$，原始注意力 $O(168^2)=28K$，ProbSparse $O(168 \log 168)=850$，**减少 97% 计算量**

**关键实验结果**（ETTh1 数据集）：

| 方法 | MSE | MAE |
|------|-----|-----|
| LSTM | 0.683 | 0.626 |
| Transformer | 0.574 | 0.537 |
| **Informer** | **0.369** | **0.419** |

---

## 二篇论文的逻辑关系

```
Attention Is All You Need（Transformer 基础）
         ↓
    Informer（第一个时序专用 Transformer）
         ↓
  Autoformer / PatchTST / iTransformer（后续改进）
```

---

## 顺丰场景对照

| 论文 | 顺丰落地场景 | 具体问题 |
|------|------------|---------|
| **Attention Is All You Need** | 所有 Transformer 变体的基础 | — |
| **Informer** | 中转场 72h 预测 | 长序列 $O(L^2)$ 效率问题 |

---

## 下一步

掌握 Transformer 基础后，继续深入：

[→ 阅读 Autoformer：分解式时序 Transformer](../getting-started.md){ .md-button }（路线建设中）

参考 [经典必读页面](../../guides/classics.md) 补充 Attention Is All You Need 精读笔记。
