# 📈 时序预测技术主线

> **7 个章节**，从经典统计方法到时空基础模型，完整覆盖深度学习时序预测技术栈。

---

## 📚 章节导航

| 章节 | 主题 | 核心内容 | 已收录论文 | 状态 |
|------|------|---------|-----------|------|
| 第一章 | [基础理论](ch01-basics.md) | ARIMA/LSTM/RNN/统计基础 | - | 📝 规划中 |
| 第二章 | [经典方法](ch02-classics.md) | DeepAR/N-BEATS/TFT | - | 📝 规划中 |
| 第三章 | [Transformer革命](ch03-transformer.md) | Informer/Autoformer/Fedformer/PatchTST/iTransformer | - | 📝 规划中 |
| 第四章 | [基础模型](ch04-foundation.md) | Time-LLM/Chronos/Moirai/TimesFM/Lag-Llama | - | 📝 规划中 |
| 第五章 | [长序列预测](ch05-long-horizon.md) | LogTrans/Reformer/DLinear/SCINet | - | 📝 规划中 |
| 第六章 | [多变量时空](ch06-st-gnn.md) | MTGNN/GTS/STGNN/时空图网络 | - | 📝 规划中 |
| 第七章 | [前沿探索](ch07-frontier.md) | Mamba/MoE/GNN最新进展 + 本库已有时序论文 | 4 | ✅ 已收录 |

---

## 🎯 学习目标

本路线围绕**顺丰业务量预测**场景设计，服务于大网/业务区/网点/中转/航空枢纽各级预测模型的技术选型需求。

### 核心问题映射

| 顺丰业务挑战 | 对应章节 | 关键技术方向 |
|-------------|---------|------------|
| 网点级别预测误差 ±20% | 第二章/第五章 | 轻量化模型 / 迁移学习 |
| 长周期预测（7-14天）精度衰减 | 第三章/第五章 | Transformer系列 / 分块策略 |
| 多源数据融合（天气/促销/舆情） | 第四章 | 多模态时序 / 基础模型 |
| 城市间流向预测 ±25% | 第六章 | 时空图神经网络(ST-GNN) |

---

## 📊 当前进度

- ✅ 已精读：0 篇
- 📖 入门推荐：5 篇（Transformer/Informer/Autoformer/PatchTST/iTransformer）
- 🔄 待处理：4 篇已收录，持续扩充中

!!! note "时序方向正在起步"
    当前知识库以 AI Agent 方向为主，时序预测方向的论文正在逐步补充。欢迎关注后续更新。

---

## 🔗 相关入口

- [学习总纲 → 阶段一](../roadmap.md)
- [交叉融合领域：时序×Agent](../cross_domain/index.md)
