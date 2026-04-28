# 第六章：多变量时空篇

> **学习目标**：掌握多变量时序与时空图网络(GNN)的建模方法。

---

## 📋 本章内容

### 6.1 图神经网络 + 时序

| 论文 | 机构 | 年份 | 核心贡献 | 状态 |
|------|------|------|---------|------|
| **MTGNN: Multivariate Time Series Graph Neural Networks** | KDD | 2020 | 图学习+混合跳跃传播层 | 🔄 待收录 |
| **GTS: Graph Learning for Traffic Speed Forecasting** | NeurIPS | 2020 | 图卷积+门控机制 | 🔄 待收录 |
| **STGNN Survey** | ACM Computing Surveys | 2022 | 时空GNN全面综述 | 🔄 待收录 |

### 6.2 本库已收录相关论文

| 论文 | 机构 | 日期 | 内容摘要 | 入口 |
|------|------|------|---------|------|
| **Inferring High-Level Events from Timestamped Data** | Meta FAIR | 2026-04-23 | 时间戳数据推断高层事件（复杂性+医学应用） | [原文](https://arxiv.org/pdf/2604.21793v1) |

---

## 💡 与顺丰业务的关联

顺丰物流预测中，**城市间流向预测 ±25%** 是核心痛点：
- 流向 = 起点 × 终点，天然构成**图结构**
- ST-GNN 可以同时建模空间依赖和时间演化
- 这是时序预测主线中最贴近实际业务的方向之一
