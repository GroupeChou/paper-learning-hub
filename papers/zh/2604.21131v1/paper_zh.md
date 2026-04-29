# AI Agent中的跨会话威胁：基准、评估与算法

<!-- 论文元数据卡片 -->
<div class="paper-meta">
  <div class="paper-meta-item">
    <span class="paper-meta-label">机构</span>
    <span class="paper-meta-value org-other">Intrinsic AI</span>
  </div>
  <div class="paper-meta-item">
    <span class="paper-meta-label">方向</span>
    <span class="paper-meta-value">Agent安全 / 跨会话攻击 / 基准测试</span>
  </div>
  <div class="paper-meta-item">
    <span class="paper-meta-label">日期</span>
    <span class="paper-meta-value">2026-04-22</span>
  </div>
</div>

!!! info ""
    <span class="paper-tag paper-tag-translated">✅ 已完成精读</span>

- **来源**：[arXiv](https://arxiv.org/abs/2604.21131)
- **论文链接**：[2604.21131v1](https://arxiv.org/abs/2604.21131)
- **数据集**：[HuggingFace: intrinsec-ai/cstm-bench](https://huggingface.co/datasets/intrinsec-ai/cstm-bench)

## 摘要

**AI Agent护栏是无状态的（memoryless）的**：每条消息被孤立判断，而将单一攻击分散到数十或数百个会话的 adversary 滑过了每个会话边界检测器——因为**没有单条消息携带载荷，只有聚合后才携带**。我们对跨会话威胁检测做出三项贡献：

1. **问题与数据集（CSTM-Bench）**：引入**跨会话威胁记忆基准**——26种可执行攻击分类法，在两个正交轴上分类：kill-chain阶段和跨会话Operations本体论(accumulate/compose/launder/inject_on_reader)——每种绑定七个身份锚点之一，将ground-truth"违规"定义为清晰策略谓词。流量分为Attack、Benign-pristine和Benign-hard三类，使现实confounder上的误报与pristine-context幻觉分开报告。

2. **测量LLM相关器的跨会话可行性**：将跨会话检测形式化为入站消息流与下游correlator LLM之间的**信息瓶颈**，并实证表征纯LLM支持的相关器何时成功何时失败。固定correlator模型和上下文窗口后，会话绑定judge和Full-Log Correlator在从compositional-dilution分片移至cross-session-only分片时**丢失约一半攻击召回率**——累积token压力远在任何前沿上下文窗口内，因此退化是correlator在稀释下的属性而非截断产物。

3. **算法方向与服务成本指标**：**有界内存Coreset Memory Reader**（排序并保留最高信号跨会话片段）是架构响应。容量K=50的参考接收者是唯一在两个分片上都保持攻击召回的读者；Coreset门控相关性仅在实时成本上有用——其ranker越稳定越好：**CSR_prefix（coreset缓冲区的有序前缀稳定性）**作为一级指标——我们将其与检测质量融合为非补偿复合指标：**CSTM = 0.7·F1(CSDA@action, precision) + 0.3·CSR_prefix**

> **核心洞察**："AI Agent上下文窗口每季度增长约30×（2023年2K tokens → 2025-2026年1M-10M tokens），但Agent安全每会话重置为零。这是根本性的架构错配。"

---

## Section 1 — Introduction

### 中文翻译

**1.1 问题：无状态护栏 vs 有状态威胁**

**AI Agent上下文窗口每季度增长；AI Agent安全仍然每会话重置为零。**

护栏和威胁/DLP分类器是无状态的：每条消息被孤立判断，**没有先前轮次、先前会话或sibling agent的记忆**。同时，值得担心的攻击越来越**跨会话和跨agent**——慢速滴注式prompt注入、跨agent操纵、增量策略侵蚀。2025年11月，Anthropic披露了首个有记录的大规模AI编排的网络间谍活动(GTG-1002)，其中自主Agent在**跨越多个会话和子代理后执行了多阶段入侵的80-90%**——因为它被说服它正在执行"授权安全测试"。

该活动主要通过**分解**绕过per-turn安全性：每步单独良性；只有轨迹是恶意的。这正是Promptware kill chain预期的模式——也是**会话绑定护栏结构上无法看到的模式**。

标准企业回退方案是将每个警报（通常还有每个prompt和工具调用）流式传输到下游SIEM并在事后关联。这昂贵、缓慢且在架构上对agentic系统错误：**当SIEM查询触发时，攻击已经落地了。**

模型上下文窗口现已扩展至数百万tokens——因此在意图时（下游日志写入之前）保持相关跨会话状态在内存中**——首次变得可行。**CSTM-Bench是评估真正这样做的检测器的基准。**

**1.2 SIEM是为事件构建的；Agent先泄露意图**

前一代检测工具——SIEM、UEBA——是为一个**安全相关事实仅在发生后才可观察**的世界设计的。检测器关联下游事件和日志。在那个世界中，将所有内容管道到中心存储并对存储运行correlator是正确的形状。

**AI Agent反转了管道。安全相关事实通常在入站prompt中**远在任何下游事件触发之前就存在**。"总结此config文件然后将摘要POST到此URL"是一个以明文自然语言表达的**渗出计划**——最终到达SIEM的日志行仅是其影子。在Agent原生栈中，意图是一等公民，应在**意图时接受检查**，而非事后从下游遥测中重建。

**三种典型的跨会话累积模式**：
1. **组合式渗出链**：session 1列文件 → session 2读config → session 3总结凭证 → session 4将"报告"发送到外部端点
2. **马赛克攻击**：数百个单独无害的问题重建敏感信息（组织架构、内部IP、数据库schema）
3. **慢速滴注式注入**：将jailbreak分布在50+会话中，每次交互一个无害片段

**每条单独消息都通过任何会话绑定的分类器。威胁仅在聚合时可见。**

### 术语解释
| 英文术语 | 中文译名 | 一句话解释 | 应用场景 |
|----------|----------|------------|----------|
| Stateless guardrails | 无状态护栏 | 每条消息独立判断，无跨轮次/跨会话记忆 | 当前主流方案的缺陷 |
| Cross-session threat | 跨会话威胁 | 分布在多次会话中才能构成完整攻击的模式 | 核心研究对象 |
| Kill chain | 杀击链 | 多阶段入侵的步骤序列（recon→weaponize→exfiltrate） | 分类轴1 |
| Semantic laundering | 语义清洗 | 敏感信息经多次会话"洗白"为无害内容 | 隐蔽手段的核心 |
| Full-Log Correlator | 全日志关联器 | 将所有入站prompt按时间顺序拼接后送长上下文LLM | 天然但低效方案 |

### 图表/公式说明

**Figure 1**：Frontier LLM上下文窗口自2023年起每年增长约30×（GPT-3: 2K → GPT-5.4/Claude Opus 4.6/Gemini 3.1 Pro: 1M-10M tokens）

**核心指标公式**：
$$\text{CSTM} = 0.7 \cdot F1(\text{CSDA@action, precision}) + 0.3 \cdot \text{CSR}_{\text{prefix}}$$
- CSDA = Cross-Session Detection Accuracy（跨会话检测准确率）
- CSR_prefix = Coreset Reader有序前缀稳定性（服务成本指标）

### 关键 takeaway
- **要点1**：**"状态性安全 vs 无状态攻击"的根本矛盾**——这是论文要解决的核心gap
- **要点2**：Anthropic GTG-1002案例证明跨会话攻击已是现实威胁非理论假设
- **要点3**：SIEM范式对Agent完全不适用——需要在**意图时刻**而非**事件事后**检测

---

## Section 2-6 — Methods, CSTM-Bench, Results & Discussion

### 中文翻译（核心内容）

**2. CSTM-Bench基准**

**26种攻击taxonomy**，两维分类：
- **Kill Chain维度**（5阶段）：Reconnaissance → Weaponize/Persist → Lateral Movement → Collection/Exfiltration → Impact
- **Operations本体论维度**（4类操作 × 7身份锚点）：accumulate / compose / launder / inject_on_reader

每种攻击绑定到一个**身份锚点**（如GitHub token、AWS credential、Slack channel），将"违规"定义为清晰的策略谓词。

**两个分片**：
- **Dilution分片**（信号稀释轴）：targeting信号稀释效应
- **Cross-session分片**（12个隔离不可见场景）：闭环重写器软化表面措辞但保留跨会话攻击artifacts逐字

**3. LLM Correlator可行性测量**

关键发现：**Full-Log Correlator从dilution分片移至cross-session-only分片时丢失约50%攻击召回率**。累积token压力在任何前沿上下文窗口内——因此退化是correlator在稀释下的固有属性。

**4. Coreset Memory Reader算法**

有界内存的Coreset Reader排序并保留**最高信号的跨会话片段**。容量K=50时它是唯一在两个分片上都维持攻击召回的读者。**CSR_prefix（有序前缀稳定性）**被提升为一阶服务指标。

**5. 主要结果**

| 指标 | 值/发现 |
|------|---------|
| 攻击场景数 | 54个/分片 × 2分片 = 108个场景 |
| 流量分类 | Attack / Benign-pristine / Benign-hard 三类 |
| Full-Log召回率损失(dilution→cross-session) | **~50%** |
| Coreset Reader(K=50) | 两分片均保持高召回 |
| CSTM复合指标 | 0.7·F1 + 0.3·CSR_prefix |

**6. 讨论：动态性与局限性**

- Agent上下文窗口持续增长使**意图时状态保留首次可行**
- Absorbers（环境兼容、访问控制、LLM自身拒绝）存在但不能作为最后防线
- Naive Full-Log Correlator不关闭gap——架构形状仍是"一个无界日志，一次批处理调用"
- 本工作 sized for **一阶特征表征**（pattern-level瓶颈形状），非精细模型排名

### 关键 takeaway
- **要点1**：**CSTM-Bench填补了跨会话安全评估的基准空白**
- **要点2**：**~50%召回损失**是纯LLM correlator的结构性限制
- **要点3**：Coreset Reader + CSR_prefix提供了**实用的实时检测路径**
- **要点4**：当前方案适用于**一阶特征验证**——需更大规模多provider数据集推动

---

## 全文总结

### 核心创新点
1. **CSTM-Bench基准**——首个跨会话威胁评估专用基准，26种攻击taxonomy + 双分片设计
2. **LLM Correlator可行性实证**——证明Full-Log方案在跨会话场景下损失~50%召回
3. **Coreset Memory Reader算法**——有界内存+排序保留高信号片段的实用检测架构
4. **CSTM复合指标**——F1(检测质量) + CSR_prefix(服务成本)的非补偿融合

### 对Agent安全的启示
1. **"每会话重置"是根本性安全缺陷**——需要跨会话状态管理
2. **SIEM不适合Agent时代**——需要在**意图时**检测而非**事件后**关联
3. **语义清洗是最大隐蔽风险**——敏感值经多次会话"洗白"最难检测
4. **Absorber不是充分防御**——对抗性prompting是无限空间自适应的

### 局限性
- 单模型家族(Claude)、单correlator、首轮提示未优化
- 规模适合概念验证，非生产部署级别
- 未覆盖multi-agent横向扩散场景
