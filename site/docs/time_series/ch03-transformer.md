# 第三章：Transformer 革命篇

> **学习目标**：理解 Transformer 在时序预测中的创新应用与演进脉络。

!!! important "这是时序预测最核心的一章"
    Transformer 彻底改变了时序预测领域。从 Informer 到 iTransformer，每一篇都值得精读。

---

## 📋 演进路线图

```
Attention Is All You Need (2017)
        ↓
Informer: ProbSparse Attention, O(n·logn)          ← AAAI 2021 Best
        ↓
Autoformer: Auto-Correlation Decomposition         ← NeurIPS 2021
        ↓
Fedformer: Frequency-Enhanced Decomposition         ← ICML 2022
        ↓
PatchTST: Patching + Channel Independence          ← ICLR 2023
        ↓
DLinear: "Will Transformers be the Future?"       ← AAAI 2022
        ↓
iTransformer: Inverted Transformer                  ← NeurIPS 2024
```

---

## 📚 核心论文清单

| 序号 | 论文 | 会议/期刊 | 年份 | 核心创新 | 状态 |
|------|------|----------|------|---------|------|
| 3.1 | **Transformer: Attention Is All You Need** | NeurIPS | 2017 | 原始Attention机制 | 🔄 待收录 |
| 3.2 | **Informer: Beyond Efficient Transformer for Long Sequence Time-Series Forecasting** | AAAI Best Paper | 2021 | ProbSparse注意力，O(n·logn)复杂度 | 🔄 待收录 |
| 3.3 | **Autoformer: Decomposition Transformers with Auto-Correlation for Long-Term Series Forecasting** | NeurIPS | 2021 | 自相关机制替代点积Attention | 🔄 待收录 |
| 3.4 | **FEDformer: Frequency Enhanced Decomposed Transformer for Long-term Series Forecasting** | ICML | 2022 | 频域增强分解（FFT） | 🔄 待收录 |
| 3.5 | **PatchTST: Can Self-Supervised Learning Be Pretrained for Time Series?** | ICLR | 2022 | 分块策略(Patching) + 通道独立 | 🔄 待收录 |
| 3.6 | **Are Transformers Effective for Time Series Forecasting? (DLinear)** | AAAI | 2022 | 线性模型的反击——简单但有效 | 🔄 待收录 |
| 3.7 | **iTIMES: Inverted Time Series Made Simple** | NeurIPS | 2024 | 反向Transformer：时间维度做Attention | 🔄 待收录 |

---

## 💡 关键技术对比

| 模型 | Attention机制 | 复杂度 | 关键优势 |
|------|--------------|--------|---------|
| Informer | ProbSparse | O(n·logn) | 长序列高效 |
| Autoformer | Auto-Correlation | O(n·logn) | 序列分解原生支持 |
| Fedformer | FFT频域 | O(n) | 频率信息利用 |
| PatchTST | Full + Patching | O(n²)→有效降低 | 预训练友好 |
| DLinear | 无(线性层) | O(n) | 极简高效 |
| iTransformer | Inverted | O(n×d²) | 变量间关系建模 |

---

## 🔗 下一章

[第四章：基础模型(Foundation Models)](ch04-foundation.md)
