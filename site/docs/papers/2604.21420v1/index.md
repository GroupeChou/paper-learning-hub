# FairQE：缓解翻译质量估计中性别偏见的多智能体框架

## FairQE: Multi-Agent Framework for Mitigating Gender Bias in Translation Quality Estimation

Jinhee Jang¹, Juhwan Choi²†, Dongjin Lee¹†, Seunguk Yu¹, Youngbin Kim¹

¹中央大学（韩国）  ²AITRICS

†同等贡献

---

## 摘要

质量估计（QE）旨在无需参考翻译即可评估机器翻译质量，但近期研究表明现有 QE 模型表现出系统性性别偏见。在性别模糊语境中偏向阳性形式，甚至在性别明确指定时也可能对性别错配的翻译分配更高分数。

我们提出 **FairQE**，一个基于多智能体的公平感知 QE 框架：
1. **性别线索检测**：12 类细粒度线索分类（显式 C1-C6 + 模糊 C7-C12）
2. **性别翻转变体生成**：生成阴性/阳性/中性变体
3. **双流质量估计**：传统 QE 分数 + LLM 基于推理的无偏评分
4. **动态偏见感知聚合**：根据检测到的偏见严重程度动态合并双流信号

在四个性别偏见评估场景和多语言设置中，FairQE 持续改善性别公平性，同时在 WMT 2023 基准上保持或提升通用 QE 性能。

---

## 1 引言

QE 模型的性别偏见：
- **性别模糊场景**：源句无性别线索 → QE 模型偏向阳性翻译
- **性别明确场景**：源句指定阴性 → QE 模型仍可能给阳性翻译更高分

**偏见逆转**——即使在性别明确时，偏见版本得分更高。

---

## 2 FairQE 框架

### 2.1 五个智能体

| 智能体 | 功能 | 输入→输出 |
|--------|------|-----------|
| **Agent_cue（线索检测）** | 12类性别线索分类 | (s,t,C) → D |
| **Agent_amb（模糊变体生成）** | 模糊场景：生成所有有效性别变体 | (s,t,c_s,c_t) → V_amb |
| **Agent_exp（显式变体生成）** | 显式场景：验证对齐+生成变体 | (s,t,c_s,c_t) → (A_i, V_i) |
| **Agent_qe（传统QE）** | 传统 QE 模型评分 | (s,t) → q_orig, Q_var |
| **Agent_uqe（无偏QE推理）** | LLM 推理驱动无偏评分 | (s,t,D,V,A_exp) → q_uqe |

### 2.2 四阶段流水线

**阶段 1：性别线索检测**
Agent_cue 输出的 12 类线索（表 13）：
- **显式 C1-C6**：代词(C1)、亲属称呼(C2)、性别名词对(C3)、称号(C4)、说话者标记(C5)、性数一致(C6)
- **模糊 C7-C12**：中性职业(C7)、中性代词(C8)、未知人名(C9)、主语省略(C10)、中性关系名词(C11)、泛指(C12)

**阶段 2：性别翻转变体生成**
- 模糊：生成所有未在原文中出现的有效性别变体
- 显式：验证目标性别是否对齐源句约束，生成对比变体

**阶段 3：双流质量估计**
- Agent_qe（定量流）：COMETKiwi 22 等传统 QE 模型，为原文和所有变体评分
- Agent_uqe（推理流）：LLM 进行显式无偏推理：
  - 模糊场景：检查各性别变体的评分一致性→标记无上下文依据的评分差异
  - 显式场景：验证性别对齐忠实性→惩罚违反源句约束

**阶段 4：动态偏见感知聚合**
**量化偏见分数：**

$$b_{amb} = \max(Q_{var} \cup \{q_{orig}\}) - \min(Q_{var} \cup \{q_{orig}\})$$

$$b_{exp} = \begin{cases} \max(0, \max(Q_{var}) - q_{orig}) & \text{if } A_{exp}=True \\ \max(0, q_{orig} - \max(Q_{var})) & \text{if } A_{exp}=False \end{cases}$$

$$B = \alpha \cdot b_{amb} + \beta \cdot b_{exp}$$

**动态门控融合：**

$$w = \frac{B}{1+B}, \quad (0 \leq w < 1)$$

$$q_{final} = w \cdot q_{uqe} + (1-w) \cdot q_{orig}$$

当偏见可忽略（B≈0）时 w→0，优先 Agent_qe。偏见升高时 w 增大，更多依赖 Agent_uqe 的推理。

---

## 3 实验

### 3.1 设置

**数据集：**
- **GATE**（ES, FR, IT）：模糊场景评价
- **MT-GenEval** 上下文子集（AR, DE, HI）：模糊场景评价
- **mGeNTE**（DE, ES, IT）：中性 vs 有性别场景
- **MT-GenEval** 反事实子集（AR, DE, HI）：显式场景评价

**QE 骨干：** COMETKiwi 22、MetricX 24 L、GPT-4.1-mini（LLM Agent）

### 3.2 结果

**表 1：女性/男性 QE 分数比（模糊场景，值越接近 1 越公平）**

| 方法 | ES | FR | IT | AR | DE | HI |
|------|-----|-----|-----|-----|-----|-----|
| COMETKiwi 22 | 0.9832 | 0.9783 | 0.9791 | 0.9851 | 0.9937 | 0.9909 |
| GEMBA-MQM | 0.9737 | 0.9658 | 0.9695 | 0.9700 | 0.9749 | 0.9740 |
| **FairQE (w/ CK22)** | **0.9947** | **0.9857** | **0.9917** | **0.9938** | **0.9993** | **0.9965** |

FairQE 持续使比率更接近 1，大幅减少偏见。

**表 3：显式场景准确率（%）**

| 方法 | AR | DE | HI |
|------|-----|-----|-----|
| COMETKiwi 22 | 95.0 | 99.2 | 55.3 |
| **FairQE (w/ CK22)** | **97.3** | **99.7** | **74.0** |

FairQE 大幅提升显式场景准确率，HI 上 +18.7 pp。

**表 4：WMT 2023 通用 QE 性能（EN-DE）**

| 方法 | avg-corr | 系统级acc | 段级acc |
|------|---------|---------|---------|
| COMETKiwi 22 | 0.743 | 0.864 | 0.548 |
| **FairQE (w/ CK22)** | **0.812** | **0.985** | **0.574** |

在改善公平性的同时，FairQE 的通用 QE 性能也提升。

### 3.3 消融

**组件消融（表 5）：**
- FairQE-NoVar（无变体生成）：平均 0.9899（< 完整 0.9936）
- FairQE-UQEOnly（仅LLM分）：平均 0.9832（< 完整 0.9936）
- **完整 FairQE**：所有语言最佳

**超参数分析（α/β）：** α 在模糊场景中作用更大，β 在显式场景中更关键。

**与更强 LLM 对比（表 8）：** FairQE（GPT-4.1-mini）平均偏差 0.00638 vs o3 的 0.0263——改善不来自模型能力，而来自结构化设计。

### 3.4 成本分析

| 指标 | 数值 |
|------|------|
| 每 100 样本 API 调用 | 176 次 |
| 输入令牌 | 157,192 |
| 输出令牌 | 19,824 |
| **总成本** | **$0.0946/100样本**（<$0.001/样本） |

---

## 4 结论

FairQE 是多智能体框架，通过检测性别线索→生成翻转变体→动态合并传统QE分数+LLM无偏推理，缓解了性别偏见。实验证明可以在**不牺牲评估精度**的前提下改善公平性，且模型无关、即插即用。

---

## 参考文献

- Rei et al. COMETKiwi. WMT 2022/2023.
- Juraska et al. MetricX-24. WMT 2024.
- Kocmi & Federmann. GEMBA-MQM. WMT 2023.
- Savoldi et al. Gender bias in MT. TACL 2021.
- Zaranis et al. Watching the watchers. ACL 2025.
- Rarrick et al. GATE. arXiv 2023.
- Currey et al. MT-GenEval. EMNLP 2022.
- Savoldi et al. mGeNTE. EMNLP 2025.
- Freitag et al. WMT23 Metrics Shared Task. WMT 2023.
