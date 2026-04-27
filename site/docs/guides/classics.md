---
description: 经典必读论文清单 — 不追新，只追根基，按难度分层
---

# 📚 经典必读

> 这些论文不追求"最新"，只追求"真的值得反复读"。是两条学习路线的根基。

!!! tip "使用规则"
    - 经典论文不追求"最新"，只追求"真的值得反复读"
    - 每读完一篇，在条目下追加：核心公式、关键图、工程启发、和当前项目的连接点
    - 如果某篇已被自动化流程抓取并做了精读，在此处补跳转链接

---

## 第一部分：AI Agent 智能体

### 🐣 入门级（必读基础）

<div class="classics-item" markdown>

#### 1. ReAct: Synergizing Reasoning and Acting in Language Models
- **机构**：Google Research / Princeton
- **发表**：ICLR 2023
- **方向**：Agent 推理框架
- **核心贡献**：Thought → Action → Observation 交替执行，解决 CoT 缺乏外部交互的问题
- **推荐理由**：顺丰 Agent 的执行逻辑本质是 ReAct 模式——理解需求 → 查询底盘 → 评估置信度
- **状态**：📖 待精读

</div>

<div class="classics-item" markdown>

#### 2. Toolformer: Language Models Can Teach Themselves to Use Tools
- **机构**：Meta AI
- **发表**：ICML 2023
- **方向**：工具调用
- **核心贡献**：用自监督让 LLM 学会调用外部工具（搜索/计算器/日历），不需要人工标注
- **推荐理由**：顺丰 7 类 Skills 体系的工具化思路，Toolformer 展示了如何让 Agent **自动发现**需要哪个工具
- **状态**：📖 待精读

</div>

<div class="classics-item" markdown>

#### 3. Generative Agents: Interactive Simulacra of Human Behavior
- **机构**：Stanford / Google
- **发表**：UMAP 2023
- **方向**：多轮 Agent 架构
- **核心贡献**：记忆流 → 反思 → 规划三段式架构，实现高度拟人的 Agent 行为
- **推荐理由**：顺丰 Agent 的长时记忆设计参考——预测结果 + 实际值偏差 = Experience，积累后自动改进 Skill
- **状态**：📖 待精读

</div>

### 🐥 进阶级（推荐阅读）

<div class="classics-item" markdown>

#### 4. LangChain / CrewAI / AutoGen 相关综述
- **机构**：社区
- **方向**：Agent 编排框架
- **核心贡献**：对比三大框架（LangChain / CrewAI / AutoGen）的调度能力差异
- **推荐理由**：顺丰 OpenClaw Agent 框架选型参考
- **状态**：📖 待补充

</div>

<div class="classics-item" markdown>

#### 5. RT-2 / RT-X: Vision-Language-Action Models
- **机构**：DeepMind / Google
- **发表**：CoRL 2023
- **方向**：Agent 视觉动作
- **核心贡献**：将 VLM 用于机器人控制，实现跨任务泛化
- **推荐理由**：物流场景中的视觉任务（违禁品识别/包型分类）的 VLA 思路
- **状态**：📖 待补充

</div>

---

## 第二部分：时序预测深度学习

### 🐣 入门级（必读基础）

<div class="classics-item" markdown>

#### 1. Attention Is All You Need
- **机构**：Google Brain
- **发表**：NeurIPS 2017
- **方向**：Transformer 基础
- **核心贡献**：提出 Transformer 架构——纯注意力机制替代 RNN，并行计算 + 长距离依赖
- **推荐理由**：Informer / Autoformer / PatchTST / iTransformer 都以此为基础，不懂这篇就不懂其他论文
- **状态**：📖 待精读

</div>

<div class="classics-item" markdown>

#### 2. Informer: Beyond Efficient Transformer for Long Sequence Time-Series Forecasting
- **机构**：Huawei Cloud
- **发表**：AAAI 2021 Best Paper
- **方向**：长序列预测
- **核心贡献**：ProbSparse Attention（$O(L^2) → O(L \log L)$）+ Distillation + Generative Decoder
- **推荐理由**：顺丰 72h+ 预测直接面临论文解决的三大问题；AAAI 2021 Best Paper，影响力最大
- **状态**：📖 待精读
- **精读链接**：→ Informer（路线建设中，参考 [时序预测入门](tracks/forecasting/getting-started.md)）

</div>

<div class="classics-item" markdown>

#### 3. Autoformer: Decomposition Transformers with Auto-Correlation for Long-Term Series Forecasting
- **机构**：清华/华为诺亚
- **发表**：NeurIPS 2021
- **方向**：季节性分解
- **核心贡献**：将时间序列分解（趋势/周期）嵌入 Transformer，提出自相关机制替代 Softmax Attention
- **推荐理由**：顺丰节假日高峰 vs 平日的季节性分解建模思路
- **状态**：📖 待精读

</div>

### 🐥 进阶级（推荐阅读）

<div class="classics-item" markdown>

#### 4. PatchTST: Transformer for Time Series Forecasting
- **机构**：IBM Research / 清华
- **发表**：ICLR 2023
- **方向**：高效长序列
- **核心贡献**：通道独立 Patch + Transformer，通道间参数共享，显著提升泛化能力
- **推荐理由**：顺丰多网点全局预测的最佳候选模型；论文验证了 Patch 策略的有效性
- **状态**：📖 待精读

</div>

<div class="classics-item" markdown>

#### 5. iTransformer: Inverted Transformer for Time Series Forecasting
- **机构**：KAIST / 字节
- **发表**：ICLR 2024
- **方向**：Transformer 逆向
- **核心贡献**：将 Transformer 的注意力从时间维度转向变量维度（Inverted），更符合时序预测任务
- **推荐理由**：物流多网点协同预测场景，直接对应变量间相关性建模
- **状态**：📖 待精读

</div>

---

## 第三部分：大模型基础（扩展阅读）

<div class="classics-item" markdown>

#### 6. LLM-as-a-Judge
- **机构**：DeepMind / Anthropic
- **方向**：LLM 评测
- **推荐理由**：Agent 评测如何用 LLM 打分，减少人工标注成本
- **状态**：📖 待补充

</div>

<div class="classics-item" markdown>

#### 7. Chain-of-Thought Prompting Elicits Reasoning in Large Language Models
- **机构**：Google Brain
- **方向**：CoT 推理
- **推荐理由**：CoT 是 Agent 推理的基础，所有 Agent 论文的前提
- **状态**：📖 待补充

</div>

---

## 已读笔记追加（请在此处追加）

---

*最后更新：2026-04-27 | 路线图：[阅读路线图](../roadmap.md)*
