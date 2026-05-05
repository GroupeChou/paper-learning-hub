# 

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


## 图表资源
- ![](assets/page-001-img-01.png)
- ![](assets/page-001-img-02.png)
- ![](assets/page-002-img-01.png)



---

---



## 1 引言

并行测试时扩展在推理任务中有效——在数学、编程等任务中生成多条独立的推理路径并聚合。但智能体任务与推理任务的根本区别在于：

| 维度 | 推理任务 | 智能体任务 |
|------|---------|-----------|
| 轨迹长度 | 短（<1K tokens） | 长（10K+ tokens，含工具调用） |
| 输出类型 | 确定性的（数值、答案） | 开放式的（文本、代码、操作） |
| 轨迹信息量 | 仅最终答案 | 中间推理+工具使用+环境反馈 |

**核心问题：** 如何从小型、有用的信息子集中提取最相关的信号？

---

## 2 AggAgent 方法

### 2.1 将轨迹视为环境

AggAgent 将并行生成的一组轨迹视为一个**环境**，并配备三个工具：

| 工具 | 功能 |
|------|------|
| `get_solution(trajectory_id)` | 从指定轨迹获取最终解决方案 |
| `search_trajectory(query)` | 在所有轨迹中搜索与查询相关的内容 |
| `get_segment(trajectory_id, segment_id)` | 获取轨迹的特定部分 |

### 2.2 与传统聚合方法对比

| 方法 | 信息利用 | 上下文限制 | 扩展性 |
|------|---------|-----------|-------|
| Majority Voting | 仅最终答案 | 无 | 低 |
| Weighted Majority | 仅最终答案+权重 | 无 | 中 |
| Best-of-N | 仅最终分数 | 无 | 中 |
| 轨迹拼接（Concat） | 全部轨迹 | **严重超出上下文** | 差 |
| **AggAgent（本文）** | **按需搜索** | **无** | **高** |

---

## 3 实验

### 3.1 设置

- **6 个基准**：智能体搜索、深度研究、知识密集型问答等
- **3 个模型家族**：GLM-4.7、Qwen3.5、MiniMax-M2.5
- **对比方法**：Majority Voting、Best-of-N、Weighted Voting、Concat

### 3.2 主要结果

**表 1：GLM-4.7-Flash 上的平均性能**

| 方法 | 6基准平均(%) | 深度研究任务原(%) | 深度研究任务新(%) |
|------|------------|----------------|----------------|
| Majority Voting | 基线 | 基线 | 基线 |
| Best-of-N | +1.8 | +2.5 | +3.2 |
| 轨迹拼接 | 超出上下文 | 超出上下文 | 超出上下文 |
| **AggAgent** | **+5.3** | **+8.7** | **+10.3** |

**表 2：跨模型家族的结果**

| 模型 | Majority | Best-of-N | Weighted | **AggAgent** |
|------|---------|----------|---------|------------|
| GLM-4.7-Flash | 基线 | +1.8 | +2.1 | **+5.3** |
| Qwen3.5-32B | 基线 | +1.5 | +1.8 | **+4.8** |
| MiniMax-M2.5 | 基线 | +1.9 | +2.2 | **+5.7** |

AggAgent 在所有三个模型家族上一致优于其他方法。

### 3.3 聚合成本分析

| 方法 | 聚合额外成本 |
|------|------------|
| Majority Voting | 极低（计数） |
| Best-of-N | 低（评分一次） |
| 轨迹拼接 | **极高**（全部轨迹送入LLM） |
| **AggAgent** | **1× 单次智能体展开** |

---

## 4 结论

AggAgent 将智能体式聚合确立为并行测试时扩展的有效且经济的方法。通过将并行轨迹视为环境，使聚合智能体按需搜索和综合信息，AggAgent 在 6 个基准和 3 个模型家族上一致优于现有方法。

---

## 参考文献

