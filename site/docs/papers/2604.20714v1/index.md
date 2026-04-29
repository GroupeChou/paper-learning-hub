# Learning to Evolve：通过文本参数图优化的多智能体系统自改进框架

**Learning to Evolve: A Self-Improving Framework for Multi-Agent Systems via Textual Parameter Graph Optimization**

---

| 元信息 | 内容 |
|--------|------|
| **作者** | Shan He*, Runze Wang*, Zhuoyun Du, Huiyu Bai, Zouying Cao, Yu Cheng, Bo Zheng†（阿里巴巴 未来生活实验室） |
| **发表时间** | 2026年4月 |
| **arXiv ID** | 2604.20714v1 |
| **领域** | 多智能体系统(MAS) · 自动优化 · 自演化 · 元学习 |
| **关键词** | Multi-Agent Systems, Self-Evolution, TPGO, Meta-Learning, Auto-Optimization |

---

## 摘要（Abstract）

设计和优化多智能体系统（MAS）是一个复杂、劳动密集的**"Agent工程"**过程。现有自动优化方法主要聚焦于**扁平化提示调优**，缺乏调试MAS中复杂交互网络的**结构性感知能力**。

更关键的是，这些优化器是**静态的**——它们不从经验中学习来改进自身的优化策略。

### 我们的方案：TPGO (Textual Parameter Graph Optimization)

提出 **文本参数图优化(TPGO)**框架，使MAS能够**学会演化**：

1. **将MAS建模为文本参数图(TPG)**：Agent、工具和工作流都是模块化可优化的节点
2. **导出"文本梯度"**：来自执行轨迹的结构化自然语言反馈，精确定位失败点并建议细粒度修改
3. **核心算法GRAO**：Group Relational Agent Optimization —— 从历史优化经验中学习的**元学习策略**

### 主要结果
- 在GAIA和MCP-Universe等复杂基准上**显著增强SOTA Agent框架性能**
- 通过自动化、自改进的优化实现更高的成功率
- MAS不仅完成任务，还学会了**如何优化自身**

---

## 1 引言（Introduction）

### 1.1 MAS优化的挑战

LLM推动了从被动问答接口向**自主Agent**的范式转变——最终发展为**多智能体系统(MAS)**：
- 多样化的Agent协作解决复杂的多步问题
- 从软件工程到开放式推理

但MAS效能**极其依赖其文本组件的精确配置**：

**"Agent工程师"必须精心制作：**
- 各个Agent的系统提示词
- 工具描述
- Agent间通信协议
- 总体工作流编排

这是一个**高维非结构化优化挑战**——MAS交互的不透明和非确定性使手动调优成为劳动密集的试错过程。

### 1.2 传统Agent工程 vs TPGO

```
传统 Agent 工程:
  人工设计提示词/工具/协议/工作流
       ↓
  手动试错调优 ( labor-intensive )
       ↓
  可能收敛到次优状态
  
TPGO (本文):
  将MAS建模为文本参数图 (TPG)
       ↓
  执行 → 收集轨迹 → 计算"文本梯度"
       ↓
  GRAO: 从历史优化经验学习如何更好地提议修改
       ↓
  自适应迭代 → 更好的配置
       ↓
  MAS 学会优化自身
```

### 1.3 两类优化设定

| 类型 | 说明 | 场景 |
|------|------|------|
| **探索性优化** | 无"金答案"，依赖自纠错反馈 | 新领域快速适配 |
| **模仿性优化** | 向期望结果对齐 | 有专家演示/理想方案可用 |

---

## 2 方法论（Methodology）

### 2.1 文本参数图（Textual Parameter Graph, TPG）

$$\text{TPG} = (\mathcal{N}, \mathcal{E}, \Theta)$$

- $\mathcal{N}$: 节点集 = {Agent节点, Tool节点, Workflow节点}
- $\mathcal{E}$: 边集 = {调用关系, 数据流, 通信协议}
- $\Theta$: 文本参数 = {每个节点的prompt, config, description}

**关键特性**：所有组件都是**模块化和可独立优化的**。

### 2.2 文本梯度（Textual Gradients）

不同于数值梯度（需要可微分），TPGO使用**结构化自然语言反馈**作为"梯度"：
- 来自执行轨迹的失败诊断
- 定位具体失败的节点和边
- 建议具体的文本修改（而非抽象方向）

### 2.3 GRAO（Group Relational Agent Optimization）

**元学习策略**：通过分析过去的成功和失败，逐步提升提出有效修改的能力。

```
GRAO 的学习循环:

  优化历史 H = {(TPG_i, trace_i, score_i)}^n_{i=1}
       │
       ▼
  分析模式:
  - 哪些类型的修改倾向于成功？
  - 哪些Agent组合容易出问题？
  - 工作流瓶颈通常在哪里？
       │
       ▼
  生成更好的修改提议策略 π_update
       │
       ▼
  应用于新任务 → 更快的收敛 → 更高的最终分数
```

---

## 3 实验（Experiments）

### 3.1 基准
- **GAIA**: 通用Agent能力基准
- **MCP-Universe**: MCP工具使用基准

### 3.2 主要结果

| 维度 | TPGO效果 |
|------|----------|
| vs SOTA Agent框架 | 显著增强性能 |
| vs 手工工程 | 更高成功率 |
| vs 静态自动优化(APO) | 更快收敛+更高上限 |
| 跨任务迁移 | 学习到的优化策略有效泛化 |

---

## 4 结论（Conclusion）

TPGO的核心洞察：
> **MAS不应只被优化——它应学会如何优化自身。**

通过将优化过程本身也纳入学习范畴，TPGO为MAS自动化开辟了新方向。
