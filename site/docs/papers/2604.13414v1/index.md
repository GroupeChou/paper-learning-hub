# 马尔可夫依赖下多数投票集成的最小最大最优性与谱路由

## Minimax Optimality and Spectral Routing for Majority-Vote Ensembles under Markov Dependence

Ibne Farabi Shihab\*†¹, Sanjeda Akter\*¹, Anuj Sharma²

¹爱荷华州立大学计算机科学系  ²爱荷华州立大学土木建筑与环境工程系

---

## 摘要

多数投票集成通过对多样化的、近似独立的基学习器取平均来实现方差缩减。当训练数据表现出**马尔可夫依赖**时（如时序预测、RL 重放缓冲、空间网格），这一经典保证以现有理论未能完全量化的方式退化。

我们针对固定维马尔可夫设置下的离散分类提供了这一现象的**最小最大特征**，以及一个在图正则子类上匹配速率的**自适应算法**。

**三项贡献：**

1. **信息论下界**：对平稳可逆几何遍历链，任何可测估计量的超额分类风险不低于 $\Omega(\sqrt{T_{mix}/n})$，其中 $T_{mix}$ 是混合时间

2. **依赖不可知 Bagging 的次优性**：在 AR(1) 见证子类上，统一 bagging 的超额风险下界为 $\Omega(T_{mix}/\sqrt{n})$，暴露 $\sqrt{T_{mix}}$ 算法差距

3. **自适应谱路由**：通过依赖图的经验 Fiedler 特征向量划分训练数据，在图正则子类上实现最小最大速率 $O(\sqrt{T_{mix}/n})$，且无需知道 $T_{mix}$

**实验验证：** 合成马尔可夫链、2D 空间网格、UCR 128数据集存档、Atari DQN 集成。

---

## 1 贡献详述

### 信息论下界

对于输入链 X₁,...,X_n ~ 平稳马尔可夫链，混合时间 $T_{mix}$：

$$\inf_{\hat{f}} \sup_{P \in \mathcal{P}} \mathbb{E}[R(\hat{f}) - R^*] \geq c \cdot \sqrt{\frac{T_{mix}}{n}}$$

任何估计器都要支付此代价，无论其有多复杂。

### 依赖不可知 Bagging 的次优性

依赖不可知的统一 bagging：

$$\inf_{f_{bag}} \sup_{P \in \mathcal{P}_{AR(1)}} \mathbb{E}[R(f_{bag}) - R^*] \geq c' \cdot \frac{T_{mix}}{\sqrt{n}}$$

差距：bagging 的 $T_{mix}/\sqrt{n}$ vs 最优的 $\sqrt{T_{mix}/n}$ — 当混合时间大时差距显著。

### 自适应谱路由

1. 基于时间/空间邻近性构建依赖图 G
2. 计算 G 的经验 Fiedler 特征向量（图拉普拉斯的第二小特征值对应的特征向量）
3. 根据特征向量符号将数据分为两组
4. 每组训练独立的基学习器
5. 多数投票组合结果

**理论保证：** 在图正则子类上，无需知道 $T_{mix}$，自适应谱路由的速率匹配最小最大 $O(\sqrt{T_{mix}/n})$。

---

## 2 实验

**合成马尔可夫链：**

| 方法 | $T_{mix}=10$ | $T_{mix}=50$ | $T_{mix}=100$ |
|------|------------|------------|-------------|
| 独立 Bagging | 0.031 | 0.142 | 0.285 |
| 依赖不可知 Bagging | 0.042 | 0.189 | 0.376 |
| **谱路由（本文）** | **0.028** | **0.058** | **0.087** |

**2D 空间网格：**

| 方法 | 分类误差 |
|------|---------|
| 标准 Bagging | 0.128 |
| **谱路由** | **0.076** |

**Atari DQN 集成：**

| 方法 | 集成 Q 方差 |
|------|-----------|
| 标准集成 | 基线 |
| **谱路由** | **-35%** |

---

## 3 结论

在马尔可夫依赖下，多数投票集成需要显式建模依赖关系才能达到最优。自适应谱路由提供了理论保证下的可行方案，其深层 RL 和目标方差的含义在附录中展开。

---

## 参考文献

- Shihab et al. Minimax Majority-Vote. 2026.
- Bickel & Bühlmann. Bagging for dependent data. 1999.
- Breiman. Bagging predictors. Machine Learning, 1996.
- Levin & Peres. Markov Chains and Mixing Times. 2017.
- Fiedler. Algebraic connectivity of graphs. 1973.
