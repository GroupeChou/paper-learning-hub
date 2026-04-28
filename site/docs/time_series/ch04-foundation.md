# 第四章：基础模型篇 (Foundation Models)

> **学习目标**：掌握时序基础模型的最新进展——用 LLM 的思路做时序预测。

---

## 📋 什么是时序基础模型？

传统时序模型是**任务特定**的：一个模型只能做一种预测。
时序基础模型是**通用**的：一个模型可以处理多种时序任务，类似 GPT 对文本的作用。

---

## 📚 核心论文清单

| 序号 | 论文 | 机构 | 年份 | 核心思想 | 状态 |
|------|------|------|------|---------|------|
| 4.1 | **Time-LLM: Time Series Forecasting by Reprogramming LLMs** | UIUC / UWA | 2023 | 将时序"重编程"为LLM可理解的token | 🔄 待收录 |
| 4.2 | **Chronos: Learning the Language of Time Series** | Amazon | 2024 | 将时序值离散化为token，直接用语言模型 | 🔄 待收录 |
| 4.3 | **Moirai: A Universal Architecture for Time Series** | Salesforce | 2024 | 统一概率预测架构，多粒度适配 | 🔄 待收录 |
| 4.4 | **TimesFM: A Foundation Model for Time Series** | Google | 2024 | 随机解码器预训练，零样本能力强 | 🔄 待收录 |
| 4.5 | **Lag-Llama: Zero-Shot Probable Time-Series Forecasting** | ServiceNow | 2024 | LagLlama架构用于零样本概率预测 | 🔄 待收录 |

---

## 💡 技术路线对比

```
Time-LLM     — 复用已有LLM权重，通过重编程适配时序（轻量级）
Chronos      — 从头训练，离散化时序值为token（中等成本）
Moirai       — 通用分布变换器，统一多种时序任务（重工程）
TimesFM      — 随机解码器预训练，专注时间序列（Google出品）
Lag-Llama    — 结合LagLlama与概率预测（学术探索）
```

---

## 🔗 相关章节

- 上一章：[第三章：Transformer革命](ch03-transformer.md)
- 下一章：[第五章：长序列预测](ch05-long-horizon.md)
- 交叉：[交叉融合领域：时序Agent](../cross_domain/ts-agent.md)
