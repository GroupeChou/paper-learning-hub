# paper

<!-- 论文元数据卡片 -->
<div class="paper-meta">
  <div class="paper-meta-item">
    <span class="paper-meta-label">机构</span>
    <span class="paper-meta-value org-"></span>
  </div>
  <div class="paper-meta-item">
    <span class="paper-meta-label">方向</span>
    <span class="paper-meta-value"></span>
  </div>
  <div class="paper-meta-item">
    <span class="paper-meta-label">日期</span>
    <span class="paper-meta-value"></span>
  </div>
</div>

!!! info ""
    <span class="paper-tag paper-tag-translated">✅ 已完成精读</span>

- **来源**：[]()
- **论文链接**：[]()
- **状态**：已生成

## 摘要





---

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
