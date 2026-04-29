# AggAgent：长程Agentic任务的并行扩展聚合方法

**Agentic Aggregation for Parallel Scaling of Long-Horizon Agentic Tasks**

---

| 元信息 | 内容 |
|--------|------|
| **作者** | Yoonsang Lee, Howard Yen, Xi Ye, Danqi Chen（Princeton University, PLI） |
| **发表时间** | 2026年4月 |
| **arXiv ID** | 2604.11753v1 |
| **领域** | LLM Agent · 并行推理 · 测试时计算扩展 |
| **关键词** | Agentic Aggregation, Parallel Scaling, Test-time Compute, Long-Horizon Tasks |
| **代码** | https://github.com/princeton-pli/AggAgent |

---

## 摘要（Abstract）

我们研究**长程Agentic任务**（如Agent搜索和深度研究）的**并行测试时扩展（parallel test-time scaling）**，其中多个轨迹并行生成并聚合为最终响应。虽然这种扩展在思维链（CoT）推理中已被证明有效，但Agentic任务面临独特挑战：**轨迹长、多轮、工具增强，且输出往往是开放式的**。

**现有方法的困境：**
- 只聚合最终答案 → 丢弃轨迹中的丰富信息
- 连接所有轨迹 → 超出模型上下文窗口
- 总结压缩每条轨迹 → 信息损失且成本高昂

**我们的方案：AggAgent**
提出 **AggAgent**——一个将并行轨迹视为环境的**聚合Agent**。配备三个轻量工具使其能够按需导航和综合信息：
- `get_solution`：获取候选解决方案
- `search_trajectory`：跨轨迹搜索
- `get_segment`：读取特定步骤段

### 主要结果

| 模型 | 平均提升（vs 最强基线） | 深度研究任务提升 |
|------|------------------------|------------------|
| GLM-4.7-Flash | +2.7~5.3 pts | +10.3 pts |
| Qwen3.5-122B | +2.4~5.3 pts | 显著提升 |
| MiniMax-M2.5 | +2.9~5.3 pts | 显著提升 |

- 聚合成本保持在**单个Agent rollout**以内
- 甚至**超越Pass@8**——有效聚合能综合出任何单次rollout都无法实现的正确解

> 💡 **核心价值**：建立了agentic aggregation作为一种有效且高效的并行测试时扩展范式。

---

## 1 引言（Introduction）

### 1.1 背景

**测试时计算扩展（Test-time Compute Scaling）**已成为提升LLM性能的有前景的方向[Wei et al., 2022; Wang et al., 2023; Snell et al., 2025]。

成功主要展示在**标准CoT任务**如数学推理和编码中。然而，**长程Agentic任务**（深度研究、软件工程、网页导航）呈现根本不同的挑战：
- 轨迹是**多轮的**，跨越数百步，交织着工具调用和观察[Yao et al., 2022b]
- 输出通常是**开放式的**（长篇报告、多答案集合）

### 1.2 并行扩展的有效性证据

并行扩展允许同时生成多个独立轨迹，提供天然的计算优势[Zhao et al., 2025]：

**GLM-4.7-Flash 的扩展效果：**
| 任务 | Pass@1 | Pass@8 | 提升 |
|------|--------|--------|------|
| BrowseComp | 27% | 59% | **+32%** |
| HLE | 25% | 51% | **+26%** |

→ 正确解经常存在于并行rollouts中

### 1.3 核心问题：如何有效聚合？

现有方法在此场景下表现不佳：

| 方法 | 做法 | 局限 |
|------|------|------|
| 多数投票(MV) | 选最高频解 | 不适用于多答案/长文本任务 |
| Best-of-N(BoN) | 选最高置信度 | 模型校准差时失效 |
| 加权投票(WMV) | 置信度加权投票 | 同上 |
| 最少工具调用(FewTool) | 选工具调用最少的 | 不泛化 |
| 解聚合(SolAgg) | 拼接K个解让LLM综合 | **丢弃中间推理过程** |
| 总结聚合(SummAgg) | 压缩每条轨迹再聚合 | **信息损失 + K倍额外LLM调用** |
| **AggAgent（本文）** | **Agent式按需导航轨迹** | **全保真 + 单rollout成本** ✅ |

### 1.4 AggAgent核心思路

**将聚合本身框架化为一个Agentic任务**，将轨迹集合视为与之交互的环境：

```
用户问题 q
    ↓
生成 K 个并行轨迹 T = {T₁, T₂, ..., T_K}
    ↓
AggAgent（聚合Agent）
    ├── get_solution(traj_id)       → 获取各轨迹最终解
    ├── search_trajectory(id,q,k)   → 在轨迹内关键词搜索
    ├── get_segment(id,start,end)   → 读取特定步范围
    └── finish()                    → 提交最终综合解
    ↓
输出 ŷ
```

**关键设计决策：**
- 轨迹**不预加载到上下文**中，而是驻留在环境中**按需检索**
- 工具操作完全在内存中的轨迹数组上进行 → **零API成本和延迟**
- 聚合成本有界于单个Agent rollout

---

## 2 问题形式化（Problem Formulation）

### 2.1 任务定义

给定问题 $q$，目标是产生输出 $y$（短答案/答案集合/长篇报告）。Agent $A$ 与外部环境交互求解 $q$，生成轨迹：
$$T = (q, r_1, a_1, o_1, ..., r_m, a_m, o_m, y)$$

每步包含内部思考 $r_j$、工具调用 $a_j$ 和观测 $o_j$。

在**并行扩展**中，独立运行同一Agent $K$ 次，得到 $\mathcal{T} = \{T_1, T_2, ..., T_K\}$。

### 2.2 聚合形式化

聚合定义为函数 $f : (q, \mathcal{T}) \rightarrow \hat{y}$，其中 $\hat{y}$ 是聚合后的最终解。

- **Agent搜索**：$\hat{y}$ 与真实答案 $y^*$ 比较
- **深度研究**：$\hat{y}$ 按问题特定评分标准评估

---

## 3 方法：AggAgent（Our Approach: AggAgent）

### 3.1 工具设计（四件轻量工具）

| 工具 | 签名 | 功能 |
|------|------|------|
| **get_solution** | `(traj_id?) → solutions` | 获取一条或所有轨迹的最后一步最终解。默认返回全部K个 |
| **search_trajectory** | `(traj_id, query, role, k) → steps` | 在单条轨迹内搜索关键词，返回top-k匹配步（ROUGE-L排序） |
| **get_segment** | `(traj_id, start_step, end_step) → content` | 读取单条轨迹的连续步完整内容（含思考和观测） |
| **finish** | `(solution, reason) → final` | 提交最终解及聚合理由 |

### 3.2 工作流程（Workflow）

工具设计反映自然的**由粗到细调查工作流**：

```
Step 1: Survey（概览）
  ├── 获取元数据和所有K个解（get_solution）
  ├── 识别共识和分歧点
  └── 定位值得深入检查的轨迹
  
Step 2: Investigate（深入）
  ├── 用 search_trajectory 搜索关键主张
  └── 用 get_segment 验证思考块和工具观测
  
Step 3: Synthesize（综合）
  └── 跨轨迹验证后调用 finish() 提交最终解
```

### 3.3 成本分析

| 方法 | 额外LLM调用 | 成本特征 |
|------|------------|----------|
| MV/WMV/BoN/FewTool | 0 | 零额外开销 |
| SolAgg | 1次 | 合成K个候选解 |
| SummAgg | K次 | **最昂贵**（每条可能达最大上下文长度） |
| **AggAgent** | **≈1次** | **有界于单个上下文窗口，与K无关** ✅ |

---

## 4 实验设置（Experimental Setup）

### 4.1 评估基准（6个长程任务）

**类别一：Agent搜索（Agentic Search）**
| 基准 | 特点 |
|------|------|
| **BrowseComp** | 挑战性事实问答，需穷尽式多步网页浏览 |
| **BrowseComp-Plus** | BrowseComp的受控版（用本地KB替代网络搜索） |
| **HLE** | 跨学科专家级问题，强调严谨推理 |
| **DeepSearchQA** | 多答案查询，要求完整性 |

**类别二：深度研究（Deep Research）**
| 基准 | 特点 |
|------|------|
| **Healthbench-Hard** | 困难医学查询的长篇综合回答 |
| **ResearchRubrics** | 开放式研究任务，按详细多准则评分 |

### 4.2 模型

| 模型 | 规模 | 家族 |
|------|------|------|
| GLM-4.7-Flash | 30B | 智谱AI |
| Qwen3.5-122B-A10B | 122B | 通义千问 |
| MiniMax-M2.5 | 229B | MiniMax |

- Agent脚手架：**Tongyi DeepResearch**
- 最大上下文：128K tokens
- 最大工具调用：100次
- 并行轨迹数：K=8
- 聚合器使用**与rollout相同的模型**

### 4.3 评估方法

采用 **LLM-as-a-Judge**：
- ResearchRubrics → Qwen3.5-397B-A17B
- 其他数据集 → GPT-4.1
- 指标：Metric@K ∈ {1, 2, 4, 8}（bootstrap采样）

---

## 5 实验结果（Results）

### 5.1 主结果（K=8）

**平均分对比：**

| 方法 | GLM-4.7 | Qwen3.5 | MiniMax-M2.5 | 平均 |
|------|---------|---------|--------------|------|
| Pass@1 | 30.01 | 32.84 | 37.61 | **33.49** |
| MV | 27.42 | 25.00 | 32.42 | **28.28** |
| WMV | 32.67 | 26.45 | — | **29.56** |
| BoN | 50.67 | 27.74 | — | **39.21** |
| FewTool | 51.33 | 30.97 | 35.33 | **39.21** |
| SolAgg | 41.33 | 32.90 | 46.00 | **40.08** |
| SummAgg | 53.33 | 34.84 | 47.33 | **45.17** |
| **AggAgent** | **55.33** ✅ | **37.42** ✅ | **49.33** ✅ | **47.36** ✅ |

**AggAgent一致优于所有基线**，相对最强基线的平均提升：
- vs Pass@1: **+13.3 ~ +17.9 分**
- vs SolAgg: **+2.4 ~ +5.3 分**
- 深度研究任务（Healthbench-Hard, ResearchRubrics）：**+10.3 分**

### 5.2 不同K值的表现

AggAgent在所有K值（1/2/4/8）上一致领先，且随K增大优势扩大。

### 5.3 成本效率（Cost Efficiency）

| 方法 | 相对于8个rollout的开销 |
|------|-----------------------|
| MV/WMV/BoN/FewTool | **0%** |
| SolAgg | ~12.5% |
| **AggAgent** | **5.7%** ✅ |
| SummAgg | **41%** ❌ |

AggAgent通过选择性读取轨迹部分内容（而非整体加载）实现了**帕累托最优**的成本-性能权衡。

### 5.4 关键发现

1. **AggAgent超越Pass@8**：有效的聚合能综合出**任何单次rollout都无法达到的正确解**
2. **启发式方法的局限**：投票类方法不适用于多答案/长文本任务；置信度方法依赖模型校准质量
3. **LLM-based方法的局限**：SolAgg丢失中间推理；SummAgg成本过高且有损
4. **AggAgent的优势来源**：**全保真 + 按需访问 + 单rollout成本**

---

## 6 分析与讨论（Analysis and Discussion）

### 6.1 聚合方法特性对比矩阵

| 维度 | MV | WMV | BoN | FewTool | SolAgg | SummAgg | **AggAgent** |
|------|----|-----|-----|---------|--------|---------|-------------|
| 任务无关 | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | **✅** |
| 非启发式 | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | **✅** |
| 使用轨迹信息 | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | **✅** |
| 全保真 | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | **✅** |
| 聚合成本 | 0 | 0 | 0 | 0 | 低 | 高 | **低** ✅ |

### 6.2 失败案例分析

AggAgent仍有失败案例，主要源于：
1. **所有K条轨迹都缺乏关键证据** → 聚合无法凭空创造信息
2. **工具选择不当** → Agent未搜索到相关轨迹片段
3. **综合推理错误** → 即使获得了正确片段，最终判断仍出错

### 6.3 未来方向

- 训练专用的聚合Agent（而非复用通用LLM）
- 更丰富的工具集（如跨轨迹对比工具）
- 动态决定最优并行度K

---

## 7 结论（Conclusion）

AggAgent证明了 **agentic aggregation** 是长程任务测试时扩展的一种**可扩展且有效的范式**：

1. ✅ 一致超越所有现有聚合方法
2. ✅ 成本有界于单个rollout（帕累托最优）
3. ✅ 即使使用现成LLM也有效
4. ✅ 开启了训练专用聚合Agent的有前景方向

**核心启示：在并行测试时扩展中，"如何聚合"和"是否并行"同样重要。**

---

## 附录：方法对比图示

```
示例问题：CTBUH 1990年高楼列表第44-46位，
           哪个城市现任市长年龄最大？（截至2024.01.02）

K=3 并行轨迹:
  Traj 1 → 搜索1980-90 PDF → John Whitmire → Houston ❌
  Traj 2 → 搜索CTBUH 1990 → Eric Adams → New York City ✅
  Traj 3 → 搜索1980-90 PDF → Sylvester Turner → Houston ❌

=== 聚合方法对比 ===

Solution Aggregation:
  输入: [Houston, NYC, Houston] → LLM → Houston ❌

Summary Aggregation:
  Traj1 → LLM → Report1
  Traj2 → LLM → Report2
  Traj3 → LLM → Report3
  [R1,R2,R3] → LLM → Houston ❌

AggAgent (Ours):
  1. get_solution() → 发现Houston×2, NYC×1 → 存疑
  2. search_trajectory(Traj2, "Eric Adams") → 验证NYC路径
  3. get_segment(Traj2, 5, 15) → 确认完整推理链
  4. finish("New York City", "Traj2的证据最充分且逻辑链完整")
  → New York City ✅
```
