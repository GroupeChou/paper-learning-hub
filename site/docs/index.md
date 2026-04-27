---
hide:
  - navigation
  - footer
description: 物流预测 + AI Agent 论文研学知识库，结构化学习路线，配套中文精读笔记
---

<!-- 首页全幅封面 -->
<div style="text-align:center; padding: 60px 20px 40px; background: linear-gradient(135deg, #f3e5f5 0%, #e8eaf6 100%); border-radius: 16px; margin-bottom: 40px;">

# 📖 论文研学知识库

### 物流预测 · AI Agent · 时序建模

---

*面向顺丰科技预测分析场景的结构化论文学习体系*

</div>

---

## 🎯 这个知识库在做什么？

将 arXiv 论文流 → 结构化中文精读 → 形成可指导实践的知识体系。

不是论文列表展示，**而是一本持续更新的学习书籍**。

---

## 🗺️ 双学习路线

选择一条路线开始，按顺序阅读效果最佳。

!!! abstract "路线一：AI Agent 智能体"
    **为什么学**：智能体是顺丰预测底盘的核心架构——17个场景、7类Skills、Tools工具集，都依赖 Agent 的规划/推理/协作能力。

    **学什么**：Agent 基础（CoT/ReAct/Tool Use）→ 多Agent协作 → Agent 安全/评测 → 前沿进展

    **当前进度**：3/32 篇已完成精读

    [:fontawesome-solid-book: 开始 Agent 路线 :fontawesome-solid-arrow-right:](tracks/agent/index.md){.md-button .md-button--primary}

!!! abstract "路线二：时序预测深度学习"
    **为什么学**：业务量预测是核心——大网/业务区/网点/中转/航空枢纽，误差标准 ±8%~±25%。

    **学什么**：Transformer 基础 → Informer/Autoformer → PatchTST/iTransformer → 时空图/异构图

    **当前进度**：0/32 篇已完成精读

    [:fontawesome-solid-book: 开始时序路线 :fontawesome-solid-arrow-right:](tracks/forecasting/index.md){.md-button .md-button--primary}

---

## 📊 学习数据

| 指标 | 数值 |
|------|------|
| 已发现论文 | 32 篇 |
| 已完成精读 | 3 篇 |
| 待处理 | 29 篇 |
| 精读路线 | AI Agent / 时序预测 |

---

## 🏆 精选精读

> 已完成中文精读的论文，可以直接开始学习：

<div class="grid cards" markdown>

-   ### 🐝 HiveMind
    **OS 启发的 LLM Agent 并发调度**

    - 机构：OpenAI（Sperix Labs）
    - 方向：多 Agent 资源调度
    - 亮点：5 个 OS 调度原语，失败率从 72-100% 降至 0-18%

    [开始阅读 :fontawesome-solid-arrow-right:](papers/2604.17111v1/index.md){.md-button}

-   ### 🪞 When Agents Look the Same
    **蒸馏诱导的行为同质化问题**

    - 机构：Anthropic
    - 方向：Agent 评测/蒸馏
    - 亮点：RPS + AGS 双指标量化同质化，Kimi-K2 超越 Anthropic Opus 4.1

    [开始阅读 :fontawesome-solid-arrow-right:](papers/2604.21255v1/index.md){.md-button}

-   ### 🗺️ Spatial Atlas
    **空间感知研究 Agent 的评测范式**

    - 机构：OpenAI
    - 方向：Agent 评测/空间推理
    - 亮点：CGR 范式（计算引导推理），确定性计算优先 + LLM 验证

    [开始阅读 :fontawesome-solid-arrow-right:](papers/2604.12102v2/index.md){.md-button}

</div>

---

## 📚 书籍结构

| 章节 | 内容 |
|------|------|
| 📖 学习指南 | 本页面：路线概览与快速入口 |
| 🧠 AI Agent | Agent 架构/协作/安全/评测完整路线 |
| 📈 时序预测 | 时序预测深度学习模型完整路线 |
| 📚 经典必读 | 不追新，只追根基的经典论文 |
| 🗂 论文总索引 | 全部论文按状态分类索引 |
| 📅 每日更新 | 每日新增论文日志 |

---

## ⚙️ 使用说明

**每篇论文页面结构**：

1. **元数据卡片** — 机构/方向/日期/阅读难度
2. **摘要** — 论文核心要解决什么问题
3. **学习路线位置** — 这篇在前沿/入门/进阶中的位置
4. **逐节精读** — 每节：中文翻译 → 术语解释 → 图表说明 → 关键 Takeaway
5. **与物流预测的关联** — 这篇论文在顺丰业务场景的落地思考
6. **导航链** — 上一篇 / 下一篇

**导航方式**：
- 左侧栏：按路线章节展开
- 顶部：全站点搜索
- 每篇论文底部：顺序导航

---

*本知识库每日自动更新，通过 GitHub Pages 托管：[:fontawesome-brands-github: GroupeChou/paper-learning-hub](https://github.com/GroupeChou/paper-learning-hub)*
