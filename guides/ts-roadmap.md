# 时序预测路线 · 论文导引

> 每日自动更新。每篇论文仅记录标题（中英对照）+ 简短说明。
> 不做翻译，不做精读，仅作导引用。
> 最新论文在顶部。

---

## 经典基石（必读）

这些是时序预测领域的基础论文，作为学习起点。

- **长短期记忆网络** (Long Short-Term Memory, LSTM) | Hochreiter & Schmidhuber | 1997
  [arXiv](https://arxiv.org/abs/1909.09586) — 解决 RNN 长程依赖问题的经典门控机制，奠基性的循环神经网络架构，后续所有序列建模方法的基础。

- **时序卷积网络** (Temporal Convolutional Networks, TCN) | Bai et al. | 2018
  [arXiv](https://arxiv.org/abs/1803.01271) — 用因果卷积 + 空洞卷积替代 RNN 进行序列建模，证明 CNN 在时序任务上可以超越 LSTM。

- **Attention Is All You Need** (Transformer) | Vaswani et al. | Google Brain | 2017
  [arXiv](https://arxiv.org/abs/1706.03762) — 提出纯注意力机制的 Transformer 架构，是后续所有时序 Transformer 方法的理论基础。

- **图卷积网络** (Graph Convolutional Networks, GCN) | Kipf & Welling | 2017
  [arXiv](https://arxiv.org/abs/1609.02907) — 图神经网络的基础，是 STGCN、DCRNN 等时空图预测模型的根基。

## 时序 Transformer 系列

- **PatchTST: A Time Series is Worth 64 Words** | Nie et al. | IBM Research | 2023
  [arXiv](https://arxiv.org/abs/2211.14730) — 将时序切片成 patch 后用 Transformer 编码，思路简洁效果强，成为时序 Transformer 的代表工作。

- **Informer: Beyond Efficient Transformer for Long Sequence Time-Series Forecasting** | Zhou et al. | 华为 | 2021
  [arXiv](https://arxiv.org/abs/2012.07436) — 长序列时序预测的代表作，提出 ProbSparse 自注意力机制降低复杂度。

- **Autoformer: Decomposition Transformers with Auto-Correlation for Long-Term Series Forecasting** | Wu et al. | 2021
  [arXiv](https://arxiv.org/abs/2106.13008) — 将时序分解机制引入 Transformer，用自相关替代自注意力，长周期预测效果好。

- **iTransformer: Inverted Transformers Are Effective for Time Series Forecasting** | Liu et al. | 2024
  [arXiv](https://arxiv.org/abs/2310.06625) — 反转 Transformer 的注意力方向（对变量维做注意力，对时间维做 MLP），多变量预测效果好。

- **TimesNet: Temporal 2D-Variation Modeling for General Time Series Analysis** | Wu et al. | 2023
  [arXiv](https://arxiv.org/abs/2210.02186) — 将 1D 时序转换为 2D 张量，用 Inception 模块捕获周期内和周期间的依赖。

## 时空图预测

- **STGCN: Spatio-Temporal Graph Convolutional Networks** | Yu et al. | 2018
  [arXiv](https://arxiv.org/abs/1709.04875) — 将图卷积引入交通预测，用图结构建模道路网络的空间依赖。

- **DCRNN: Diffusion Convolutional Recurrent Neural Network** | Li et al. | 2018
  [arXiv](https://arxiv.org/abs/1707.01926) — 用扩散图卷积 + 门控循环单元建模时空依赖，交通预测经典。

- **EEAG: Edge-Enhanced Adaptive Graph** — 顺丰科技 | 2025
  在物流时空预测场景中的实践，用边增强自适应图建模网点间关系。

---

> 每日自动更新于 2026-05-17
