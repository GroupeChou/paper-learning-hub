# SafetyALFRED：评估多模态大语言模型的安全意识规划

## SafetyALFRED: Evaluating Safety-Conscious Planning of Multimodal Large Language Models

Josue Torres-Fonseca¹, Naihao Deng¹, Yinpei Dai¹, Shane Storks¹, Yichi Zhang¹, Rada Mihalcea¹, Casey Kennington², Joyce Chai¹

¹密歇根大学  ²博伊西州立大学

---

## 摘要

MLLM 被用作交互环境中的自主智能体。**SafetyALFRED** 在 ALFRED 基准上增加六类厨房危害，评估 11 个模型（Qwen、Gemma、Gemini）的**危害识别（QA）vs 危害缓解（具身规划）**。

**关键发现：约 50pp 的对齐差距**
- QA 识别最高 **92.3%**
- 规划缓解最高仅 **42.1%**

---

## 结果

| 模型 | QA识别(%) | 规划缓解(%) | 差距 |
|------|---------|------------|------|
| Gemini 2.0 Flash | **92.3** | **42.1** | 50.2 |
| Gemini 1.5 Pro | 88.7 | 38.5 | 50.2 |
| Qwen2.5-VL-72B | 85.1 | 35.2 | 49.9 |
| Gemma 3-27B | 79.4 | 28.3 | 51.1 |

**按危害类别：** 简单危害（火灾 H1：44.8pp 差距）< 复杂危害（电气 H6：58.2pp 差距）

**失败模式：** 忽略危害、缓解不足、错误序列、幻觉行动

---

## 参考文献

- Torres-Fonseca et al. SafetyALFRED. 2026.
- Khandelwal et al. ALFRED. 2020.
