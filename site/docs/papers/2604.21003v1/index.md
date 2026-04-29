# The Last Harness You'll Ever Build：双层Harness自动演化框架

**The Last Harness You'll Ever Build**

---

| 元信息 | 内容 |
|--------|------|
| **作者** | Haebin Seong, Li Yin, Haoran Zhang（Sylph.AI） |
| **发表时间** | 2026年4月（技术报告） |
| **arXiv ID** | 2604.21003v1 |
| **领域** | Agent基础设施 · Harness工程 · 自动化 · 元学习 |
| **关键词** | Harness Engineering, Agent Automation, Meta-Learning, Self-Evolution |

---

## 摘要（Abstract）

AI Agent日益部署在复杂的特定工作流中——导航需要数十次点击和表单填写的企业Web应用、编排跨越搜索/提取/综合的多步研究管线、跨不熟悉仓库的代码审查自动化、处理需要细微领域知识的客户升级。

每个新任务域都需要痛苦的、专家驱动的**Harness工程**：设计提示词、工具、编排逻辑和评估标准。

### 我们的双层框架

**第一层：Harness Evolution Loop（内循环）**
针对单个任务优化Worker Agent的harness H：
- **Worker Agent WH**：由harness H参数化，执行任务并产生执行轨迹
- **Evaluator Agent V**：对抗性地验证任务结果，诊断故障模式并评分
- **Evolution Agent E**：分析完整演化历史并修改harness（提示词、工具、编排逻辑、观测、模型配置）

**第二层：Meta-Evolution Loop（外循环）**
跨多样化任务优化演化协议 Λ = (WH, H⁽, V, E) 本身，学习一个最佳协议 Λ(best)，使得在任何新任务上都能**快速收敛harness**——**完全无需人工Harness工程**。

> 🎯 **终极目标**: 不仅将Harness工程自动化，更进一步——将**自动化的设计本身也自动化**。

---

## 1 核心痛点：Harness工程的困境

### 1.1 什么是Harness Engineering？

Harness = 使基础模型在特定任务域有效的全部工程设施：
- **执行环境**（容器、沙箱、API连接器）
- **反馈循环**（测试、检查、重试逻辑）
- **评估标准**（成功/失败判定、评分函数）
- **上下文管理**（窗口管理、记忆组织）

### 1.2 现实案例的复杂度

| 案例 | 所需Harness组件 |
|------|----------------|
| Lopopolo [2026] | 自定义linter、仓库本地可观测性堆栈（日志/指标/trace）、Chrome DevTools集成、结构化文档层级 |
| Rajasekaran [2026] | 多轮evaluator prompt校准、四项评分标准设计、三Agent planner-generator-evaluator架构（含sprint contract协商） |

→ **共同特征**：需要深厚的领域专业知识 + 大量迭代调优

### 1.3 为什么现有方法不够

| 方法 | 局限 |
|------|------|
| **LLM-AutoDiff等自动Prompt优化** | 只能调优单个组件，无法处理完整的harness（工具+编排逻辑+基础设施+交互） |
| **手工工程** | 劳动密集、难以规模化、每次换领域几乎要从头开始 |

---

## 2 方法论：双层演化架构

### 2.1 整体架构

```
╔══ Meta-Evolution Loop (外层/绿色) ══════════════╝
│                                                      │
│   训练任务 t₁, t₂, ..., tₙ                         │
│     │         │         │                            │
│     ▼         ▼         ▼                            │
│  ╔═ Harness Evolution Loop (内层/蓝色) ═╗          │
│  ║                                       ║          │
│  ║  WH: 执行任务 → 产生轨迹              ║          │
│  ║       │                               ║          │
│  ║       ▼                               ║          │
│  ║  V: 对抗性验证 → 诊断+评分            ║ × N tasks  │
│  ║       │                               ║          │
│  ║       ▼                               ║          │
│  ║  E: 分析历史 → 修改H                 ║          │
│  ║       │                               ║          │
│  ║       └→ 迭代K步 → 返回H(best)        ║          │
│  ╚═══════════════════════════════════════╝          │
│                    │                                │
│                    ▼                                │
│   Meta-Agent: 聚合所有任务的得分                  │
│              → 修改演化协议 Λ                       │
│              → 输出 Λ(best)                        │
│                                              │
╔════════════════════════════════════════════╝
```

### 2.2 内循环详解

**初始化**：从通用、未调优的Agent脚手架 H⁽开始

**每轮迭代k**：
1. Worker Agent WH_k 用当前harness H_k 执行任务
2. Evaluator Agent V 对抗性地验证：
   - 任务是否成功完成？
   - 如果失败，**为什么**？（定位失败模式）
   - 量化评分（多维指标）
3. Evolution Agent E 分析**完整的历史**（所有之前的尝试），然后修改harness的所有组件：
   - **提示词**（system prompt, few-shot examples）
   - **工具定义**（schema, descriptions, examples）
   - **编排逻辑**（workflow, routing, error handling）
   - **观测管理**（what to capture, how to compress）
   - **模型配置**（temperature, top_p, model selection）
4. K步后返回最优harness H(best)

### 2.3 外循环详解

**目标**：学习一个好的演化协议Λ，使其适用于**任何新领域**

**Meta-Agent的操作**：
1. 在多个不同领域的训练任务上运行内循环
2. 聚合各任务的得分曲线和收敛速度
3. 分析哪些演化策略在哪些任务类型上最有效
4. 修改演化协议本身（如调整E的提示词、改变V的严格程度、修改迭代次数K等）
5. 输出 **Λ(best)** —— 一个在新任务上能**快速收敛**的最佳协议

---

## 3 与元学习的对应

| 传统元学习 | 本框架 |
|-----------|--------|
| 任务分布上的学习 | 任务域上的harness优化 |
| 支持/查询集划分 | 训练任务/新任务 |
| 快速适应 | 快速harness收敛 |
| 元优化器 | Meta-Evolution Agent |
| 内循环优化 | Harness Evolution Loop |

---

## 4 结论

**愿景**: 让任何新领域的Agent适配变成：
1. 给定任务描述
2. 运行 Λ(best)
3. 得到一个有效的harness
4. **零人工介入**

这不仅是自动化——这是**关于自动化的元自动化**。
