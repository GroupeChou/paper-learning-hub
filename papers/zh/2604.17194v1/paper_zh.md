# 有效市场假设下的体育预测：赔率模型与广义线性模型的理论与实验分析

## Forecast Sports Outcomes under Efficient Market Hypothesis

Kaito Goto, Naoya Takeishi, Takehisa Yairi

---

## 摘要

将博彩赔率转换为准确的结果概率是体育预测和市场效率分析的基础挑战。我们提出两种方法：

1. **OO-EPC（Odds-Only-Equal-Profitability-Confidence）**：一种仅使用赔率的方法，无需历史数据拟合，与博彩公司的"各结果盈利信心相等"定价目标对齐。在 **90,014 场足球比赛、5 个博彩公司**的数据集上，OO-EPC 优于现有方法。

2. **FL-GLM（Feature-Learning GLM）**：一个使用历史数据拟合的广义线性模型，在篮球预测竞赛中使用 6 次迭代验证。

**关键发现：** 博彩市场在足球上接近有效，在篮球上存在可利用的低效。

---

## 1 方法

### 1.1 OO-EPC 模型

现有赔率转换方法（Multiplicative、Shin、Power）不调整我们在数据中发现的偏差。OO-EPC 假设博彩公司对各结果的盈利信心相等。

### 1.2 FL-GLM

使用广义线性模型结合历史特征进行预测。

---

## 2 结果

| 方法 | 足球赔率转换误差↓ | 篮球预测精度↑ |
|------|-----------------|-------------|
| Multiplicative | 基线 | — |
| Shin | 基线 | — |
| Power | 基线 | — |
| **OO-EPC（本文）** | **最优**✅ | — |
| FL-GLM | — | **最优**✅ |

---

## 3 结论

OO-EPC 在赔率转换上优于现有方法，FL-GLM 在利用历史数据进行体育预测上表现最佳。

---

## 参考文献

- Goto et al. Forecast Sports Outcomes. 2026.
