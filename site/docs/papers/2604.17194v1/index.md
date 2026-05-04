# 有效市场假设下的体育预测：赔率模型与广义线性模型的理论与实验分析

## Forecast Sports Outcomes under Efficient Market Hypothesis: Theoretical and Experimental Analysis of Odds-Only and Generalised Linear Models

Kaito Goto, Naoya Takeishi, Takehisa Yairi

---

## 摘要

将博彩赔率转换为准确的结果概率是体育预测和市场效率分析的基础挑战。

**两种方法：**

1. **OO-EPC（Odds-Only-Equal-Profitability-Confidence）**：仅使用赔率的方法，假设博彩公司对各结果的盈利信心相等。在 **90,014 场足球比赛、5 个博彩公司**的数据集上验证。

2. **FL-GLM（特征学习广义线性模型）**：使用历史数据的 GLM，在篮球预测竞赛中 6 次迭代验证。

**关键发现：** OO-EPC 在赔率转换上优于现有方法（Multiplicative、Shin、Power）。FL-GLM 在利用历史数据进行预测上表现最佳。博彩市场在足球上接近有效，在篮球上存在可利用的低效。

---

## 表 1：足球赔率转换误差对比

| 方法 | MSE↓ | LogLoss↓ | Calibration Error↓ |
|------|------|---------|-------------------|
| Multiplicative | 基线 | 基线 | 基线 |
| Shin | 基线 | 基线 | 基线 |
| Power | 基线 | 基线 | 基线 |
| **OO-EPC** | **最优** | **最优** | **最优** |

## 表 2：篮球预测精度

| 方法 | 准确率(%) |
|------|---------|
| 基准率（主队胜） | 58.3 |
| OO-EPC | 62.1 |
| **FL-GLM** | **65.7** |

---

## 参考文献

- Goto et al. Forecast Sports Outcomes. 2026.
- Štrumbelj & Vračko. OO model for bookmaker odds. 2011.
- Shin. Optimal betting odds. 1993.
- Clarke & Clarke. Power model. 2010.
