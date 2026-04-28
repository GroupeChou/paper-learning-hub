# 第七章：前沿探索篇

> **学习目标**：追踪时序预测最新研究方向，关注 Mamba/MoE/GNN 等新兴范式。

---

## 🔬 当前前沿热点

### 方向一：状态空间模型 (SSM)

| 论文 | 核心思想 | 与时序的关系 |
|------|---------|------------|
| **Mamba: Selective State Space Models** | 选择性状态空间模型，线性复杂度 | 替代Transformer做长序列建模 |

### 方向二：混合专家 (MoE)

| 论文 | 核心思想 | 与时序的关系 |
|------|---------|------------|
| **TimeMoE** | 时序专用MoE架构 | 不同时间段用不同专家 |
| **TimesFM** (Google) | 频率域混合专家 | 基础模型中的稀疏激活 |

### 方向三：时空大模型

| 论文 | 核心思想 |
|------|---------|
| **EEAG** | 时空图增强生成模型（本项目关注方向） |
| **SCINet** | 样本间卷积网络 |

---

## 📥 本库已收录时序前沿论文

| 论文 | 机构 | 日期 | 主题分类 | 链接 |
|------|------|------|---------|------|
| **Forecast Sports Outcomes under Efficient Market Hypothesis** | 智谱 | 2026-04-19 | 概率预测 / 广义线性模型 | [原文](https://arxiv.org/pdf/2604.17194v1) |
| **Minimax Optimality and Spectral Routing for Majority-Vote Ensembles** | MiniMax | 2026-04-15 | 集成学习 / Markov依赖 | [原文](https://arxiv.org/pdf/2604.13414v1) |
| **Revisiting Change VQA in Remote Sensing with Structured and Native Multimodal Qwen Models** | 阿里通义 | 2026-04-20 | 多模态 / 遥感变化检测 | [原文](https://arxiv.org/pdf/2604.18429v1) |
| **Inferring High-Level Events from Timestamped Data** | Meta FAIR | 2026-04-23 | 时序事件推断 | [原文](https://arxiv.org/pdf/2604.21793v1) |

---

## 🔗 返回

- [返回时序预测主线](index.md)
- [返回学习总纲](../roadmap.md)
