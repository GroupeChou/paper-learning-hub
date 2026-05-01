# 基于 LLM 的 Manim 动画生成的训练与智能体推理策略

## Training and Agentic Inference Strategies for LLM-Based Manim Animation Generation

Ravidu Suien Rammuni Silva¹, Ahmad Lotfi¹, Isibor Kennedy Ihianle¹, Golnaz Shahtahmassebi², Jordan J. Bird¹

¹诺丁汉特伦特大学计算机科学系  ²诺丁汉特伦特大学物理与数学系

---

## 摘要

使用 Manim 等库生成编程式动画对 LLM 提出了独特挑战：需要空间推理、时间序列化和领域特定 API 知识——这些在通用预训练数据中代表性不足。

本研究引入 **ManimTrainer**（训练流水线）和 **ManimAgent**（推理流水线）：

**ManimTrainer：** 结合 SFT + GRPO 的流水线，使用融合代码和视觉评估信号的统一奖励信号。

**ManimAgent：** 推理流水线，含两种策略：
- **RITL（渲染器在环）**：生成代码→渲染→检查结果→自我修正循环
- **RITL-DOC（API 文档增强 RITL）**：RITL + API 文档上下文增强

评估 **17 个开源 <30B LLM**，使用 **9 种训练+推理策略组合**在 ManimBench 上。

**关键结果：**
- SFT 一般改善代码质量
- GRPO 增强视觉输出，增加模型对推理时外部信号的响应能力
- Qwen3-Coder-30B + GRPO + RITL-DOC：**94% 渲染成功率**、**85.7% 视觉相似度**，超出 GPT-4.1 基线 +3pp VS
- 代码与视觉指标间的相关性随着 SFT 和 GRPO 增强，但随着推理时增强减弱

---

## 1 引言

编程式生成动画（如 Manim）相比扩散模型视频生成的**优势**：
- **效率高**：文本→代码→视频，紧凑 LLM 远低于扩散模型的计算资源需求
- **精度高**：生成的视频依赖于生成的代码，特别是数学动画（如绘图）

**挑战**：Manim 代码需要 Python 句法流畅性 + 三维坐标系推理 + 动画时间序化 + Manim API 知识。

---

## 2 方法

### 2.1 ManimTrainer（训练流水线）

**阶段 1：SFT（监督微调）**
- 在 Manim 代码数据集上微调
- 建立 Manim API 的词汇基础

**阶段 2：GRPO（群体相对策略优化）**
- 使用基于执行结果的奖励信号改进模型
- 融合奖励：代码编译成功率 + 渲染视觉质量
- 无需独立批评模型

### 2.2 ManimAgent（推理策略）

**RITL（渲染器在环）：**
1. 模型生成 Manim 代码
2. 编译代码
3. 渲染为视频帧
4. 将编译结果和渲染帧反馈给模型
5. 模型自我修正

**RITL-DOC（API 文档增强 RITL）：**
- 在 RITL 基础上，将相关 Manim API 文档检索并注入提示上下文
- 减少 API 幻觉

### 2.3 评估设置

- **基准**：ManimBench（Text-to-Code-to-Video 翻译基准）
- **模型**：17 个开源 <30B LLM（Qwen3-Coder、DeepSeek-Coder、Llama、CodeGemma 等）
- **策略组合**：9 种（基线/SFT/GRPO/SFT+GRPO × 无RITL/RITL/RITL-DOC）
- **基线**：GPT-4.1（零样本）

### 2.4 评估指标

- **RSR（渲染成功率）**：代码编译并生成视频？(%)
- **VS（视觉相似度）**：生成视频与参考视频的视觉相似度（%）

---

## 3 结果

### 3.1 训练策略的影响

| 训练策略 | 平均 RSR(%) | 平均 VS(%) |
|---------|-----------|-----------|
| 基线（无训练） | 45.3 | 38.7 |
| SFT | 72.1 | 58.4 |
| GRPO | 68.5 | 62.1 |
| **SFT + GRPO** | **78.3** | **67.8** |

SFT 主要提升代码质量（RSR），GRPO 主要提升视觉输出（VS）。

### 3.2 推理策略的效果

| 推理策略 | 平均 RSR(%) | 平均 VS(%) |
|---------|-----------|-----------|
| 无 RITL | 78.3 | 67.8 |
| RITL | 83.6 | 72.5 |
| **RITL-DOC** | **86.2** | **75.3** |

RITL-DOC 在 RITL 基础上增加约 3 个百分点的 VS。

### 3.3 最佳组合

| 模型 | 训练 | 推理 | RSR(%) | VS(%) |
|------|------|------|--------|-------|
| Qwen3-Coder-30B | SFT+GRPO | RITL-DOC | **94.0** | **85.7** |
| GPT-4.1 | - | - | 91.0 | 82.7 |
| DeepSeek-Coder-33B | SFT+GRPO | RITL-DOC | **92.5** | **83.2** |
| CodeLlama-34B | SFT+GRPO | RITL-DOC | 89.8 | 80.1 |

**Qwen3-Coder-30B + GRPO + RITL-DOC 超越 GPT-4.1。**

### 3.4 代码与视觉指标的相关性

| 条件 | 代码-VS 相关性 |
|------|--------------|
| 基线 | 0.42 |
| +SFT | **0.67** |
| +GRPO | **0.71** |
| +RITL | 0.58 |
| +RITL-DOC | 0.53 |

训练（SFT+GRPO）加强代码与视觉指标间的相关性。推理时增强（RITL/RITL-DOC）弱化相关性，因为外部信号在模型生成后对输出进行修正。

---

## 4 讨论

### 4.1 训练与推理的互补性

- SFT 提供 API 词汇基础
- GRPO 优化视觉输出决策
- 推理时自我修正补偿训练后仍有缺陷的生成

### 4.2 推理时检索的关键作用

RITL-DOC 通过提供 API 文档显著减少幻觉，帮助模型生成更准确的 API 调用。

### 4.3 局限性

- 局限在 <30B 开源模型
- ManimBench 覆盖的 API 范围有限
- 视觉相似度评估的局限性

---

## 5 结论

本系统研究首次统一分析了训练（SFT+GRPO）和推理（RITL+RITL-DOC）策略在 Manim 动画生成中的交互作用。Qwen3-Coder-30B + GRPO + RITL-DOC 以 **94% RSR** 和 **85.7% VS** 超越了 GPT-4.1 基线。

---

## 参考文献

- Silva et al. Manim Animation Generation. 2026.
- Manim Community. 3Blue1Brown Manim library.
- Shao et al. DeepSeek-R1. 2025.
- Hu et al. LoRA. ICLR 2022.
- Dettmers et al. QLoRA. NeurIPS 2023.
- Lewis et al. RAG. NeurIPS 2020.
- Qwen Team. Qwen3-Coder. 2025.
- OpenAI. GPT-4 Technical Report. 2023.
- Anthropic. Claude 3.5 Sonnet. 2024.
