# FairQE：缓解翻译质量估计中性别偏见的多智能体框架

## FairQE: Multi-Agent Framework for Mitigating Gender Bias in Translation Quality Estimation

Jinhee Jang¹, Juhwan Choi²†, Dongjin Lee¹†, Seunguk Yu¹, Youngbin Kim¹

¹中央大学（韩国）  ²AITRICS

---

## 摘要

质量估计（QE）模型表现出系统性性别偏见：模糊语境偏向阳性，明确语境时仍可能给性别错配翻译更高分。**FairQE** 是一个基于多智能体的公平感知QE框架。

**框架：**
- **Agent_cue（线索检测）**：12类性别线索（显式C1-C6 + 模糊C7-C12）
- **Agent_amb（模糊变体生成）**：生成所有性别变体
- **Agent_exp（显式变体生成）**：验证对齐并生成对比
- **Agent_qe（传统QE评分）**：COMETKiwi 22 评分
- **Agent_uqe（LLM无偏推理）**：GPT-4.1-mini 推理驱动无偏评分

**动态聚合：** $q_{final} = w·q_{uqe} + (1-w)·q_{orig}$，$w = B/(1+B)$

---

## 结果

**表 1：模糊场景女性/男性 评分比（越近1越公平）**

| 方法 | ES | FR | IT | AR | DE |
|------|-----|-----|-----|-----|-----|
| COMETKiwi22 | 0.983 | 0.978 | 0.979 | 0.985 | 0.994 |
| **FairQE** | **0.995** | **0.986** | **0.992** | **0.994** | **0.999** |

**表 2：明确场景准确率（%）**

| 方法 | AR | DE | HI |
|------|-----|-----|-----|
| COMETKiwi22 | 95.0 | 99.2 | 55.3 |
| **FairQE** | **97.3** | **99.7** | **74.0** |

**通用QE性能：** WMT 2023 avg-corr: 0.743 → **0.812**

**成本：** $0.095/100样本（<$0.001/样本）

---

## 参考文献

- Jang et al. FairQE. 2026.
- Rei et al. COMETKiwi. WMT 2022.
- Savoldi et al. Gender bias in MT. TACL 2021.
