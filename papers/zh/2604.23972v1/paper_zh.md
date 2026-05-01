# 量子知识图谱：建模上下文依赖的三元组有效性

**Quantum Knowledge Graph: Modeling Context-Dependent Triplet Validity**

王尧¹², 耿子旭³, 严俊¹\*

¹香港城市大学 HKAI-Sci  ²清华大学自动化系  ³杜克大学普拉特工程学院

{ywan75@cityu.edu.hk, zg73@duke.edu, yan.jun@cityu.hk}

\*通讯作者

2026年4月28日

**关键词**: 量子知识图谱、上下文依赖的三元组有效性、适用性条件、推理器-验证器流水线、患者上下文推理

---

> **图形摘要**：量子知识图谱中的上下文依赖三元组有效性。

---

## 摘要（Abstract）

知识图谱（KG）越来越多地用于支持大语言模型（LLM）推理，但标准的三元组式 KG 将每个关系视为全局有效。在许多场景中，一个关系是否应被视为证据取决于上下文。因此，我们将三元组有效性形式化为上下文的**三元组特定函数**，并将这一形式化称为**量子知识图谱（QKG）**。

我们在医学领域实例化 QKG，使用以糖尿病为中心的 PrimeKG 子图，其 **68,651 个上下文敏感关系**进一步标注了患者群体特定的约束。我们在一个推理器-验证器流水线中评估它，用于医学问答，使用 MedReason 中基于 KG 的子集（含 **2,788 个问题**）。以 Haiku-4.5 同时作为推理器和验证器时，基于 KG 的验证显著优于无验证器基线（**+0.61 pp**），而带上下文匹配的 QKG 取得了最大增益，优于无上下文匹配的 KG 验证（**+0.79 pp**）和无验证器基线（**+1.40 pp**；配对 McNemar 检验，所有 p < 0.05）。在更强的验证器（Qwen-3.6-Plus）下，QKG 在原始集上的增益从 +1.40 pp 增长到 **+5.96 pp**；上下文匹配差距在原始集上不显著（p = 0.73），但在调整知识泄露和可疑问题后变得**边界显著**（p = 0.05），这归因于基准金标准的天花板效应，而非 QKG 自身的局限。

综合来看，结果支持一个观点：KG 在基于 LLM 的临床推理中的价值不仅在于存储医学相关事实，更在于**表示这些事实是否适用于特定患者上下文**。为支持可复现性和进一步研究，我们发布了整理好的 QKG 数据集和源代码。

---

## 1 引言（Introduction）

大语言模型（LLM）和知识图谱（KG）正越来越多地作为互补组件而非竞争范式发展。最近的工作表明，KG 可以通过提供结构化、显式、可验证的知识来改进 LLM 系统的检索、推理和可信度，而 LLM 反过来也可以辅助 KG 的构建、丰富和操作使用（Sui et al., 2025; Wu et al., 2025b; Parović et al., 2025）。这种新兴的交互表明，在 LLM 时代，KG 的价值不仅在于作为标准 RAG 流水线中的检索资源，更在于作为**显式且可审查的验证基底**，确定模型生成的声明是否在给定上下文中适用。

这一性质在基于 LLM 的智能体系统中尤为重要——生成合理的输出不是唯一目标，可靠性能还需要验证输出背后的声明是否得到外部证据和上下文的支持（Dougrez-Lewis et al., 2025; Kolli et al., 2025）。

### 三元组有效性的形式化框架

传统 KG 通常将知识表示为包含头实体、关系和尾实体的三元组 τ = (h, r, t)。刻画三元组适用性的有效方式是通过上下文依赖的概率量 **P(τ | C)**，其中 C 表示观测上下文。不同的 KG 范式可视为该量的不同参数化形式：

```
P(τ | C) = {0, 1},     传统 KG（二值全局有效/无效）
P(τ | C) = μτ,          概率 KG（群体水平先验，μτ ∈ [0,1]）
P(τ | C) = Fτ(C),       三元组特定函数（本文提出的 QKG）
```

- **传统 KG**：将三元组视为全有或全无，无法建模上下文依赖的有效性
- **概率 KG**：编码群体水平的先验概率，但仍然不指定具体上下文
- **三元组特定函数 Fτ(C)**：允许有效性由上下文 C 决定，Fτ 可以是显式函数、经典统计模型（如逻辑回归、XGBoost）或 LLM

这一区分至关重要，因为在大多数现实场景中，三元组有效性取决于上下文：**P(τ | C) 在 C 上不是常数**。传统三元组式 KG 将这种依赖性坍缩为二值记录，限制了其作为验证基底的实用性。

这个问题在医学领域尤为突出，因为错误的验证可能导致有害结论。医学声明是否成立通常取决于患者特定上下文：合并症、实验室检查结果、疾病阶段、治疗史和禁忌症。

### 量子知识图谱（QKG）

为应对这一局限，我们转向**三元组特定函数**，并寻求一种实用的方式来实现和评估 Fτ(C)。我们将 Fτ(C) 操作化为对关系附加**自然语言有效性条件**。这种表示保持表达灵活性，同时与基于 LLM 的解读和下游评估兼容。我们称这种基于 Fτ(C) 的三元组有效性公式化为**量子知识图谱（QKG）**——这里的"量子"指上下文依赖的有效性，而非量子理论形式主义。

基于这一公式化，我们在医学领域实例化 QKG：
1. 从 PrimeKG（Chandak et al., 2023）中整理一个图
2. 构建一个验证器智能体，评估医学声明在患者上下文中是否得到支持
3. 将这个验证器集成到 LLM 推理的推理器-验证器流水线中
4. 在 MedReason（Wu et al., 2025a）的医学问答样本上评估

### 本文贡献

1. **形式化贡献**：引入三元组有效性框架，将知识声明的适用性建模为上下文依赖量 P(τ | C)，并将其三元组特定形式 Fτ(C) 操作化为 QKG
2. **实例化贡献**：在医学领域实例化，从 PrimeKG 衍生的 QKG 和基于 QKG 的验证器智能体
3. **实证贡献**：将基于 QKG 的验证集成到 LLM 推理器-验证器流水线中，改善了医学问答性能

---

## 2 背景（Background）

### 2.1 知识图谱中的上下文依赖有效性

传统 KG 将事实表示为三元组 (h, r, t)，通常视为全球有效。大量工作已表明这一假设过于严格。

**超关系 KG**：StarE（Galkin et al., 2020）等方法显式建模关系特定的限定符，表明许多事实最好理解为附带辅助条件的陈述，而非孤立的三元组。

**时序 KG**：时序 KG 问答和推理方法允许事实仅在特定时间间隔有效（Saxena et al., 2021; Chen et al., 2023; Ding et al., 2024），表明有效性可能依赖于时间而非普遍存在。

这些工作建立了一个重要的普遍观点：**三元组有效性通常是条件性的**。

然而，现有的上下文扩展通常通过有限且预定义的结构来操作化上下文。超关系 KG 假设相关上下文维度可以附加为显式限定符，时序 KG 主要关注时间。这些都未能充分应对适用性取决于更丰富、更组合性的条件且难以预先枚举的场景。

### 2.2 医学知识图谱中的上下文依赖有效性

这一局限在医学领域尤为明显。医学知识声明的有效性通常取决于患者特定细节：合并症、实验室发现、疾病阶段、用药史和禁忌症。

**PrimeKG**（Chandak et al., 2023）等生物医学 KG 为精准医学提供了广泛的关系覆盖，但其边主要记录"存在某个关联"，而非"在哪些条件下适用于特定患者"。

先前的研究已在两个方向上超越了朴素三元组公式：
- **Li et al.（2020b）** 提出具有四元组结构的真实医学 KG，表明临床事实需要比裸 (h, r, t) 更丰富的事实表示
- **Li et al.（2020a）** 进一步引入概率医学 KG 嵌入方法，在三元组层面建模不确定性，从二值有效性转向群体水平置信度

相关工作在临床时序 KG 中也强化了同样的观点。Diao et al.（2021）建模用于糖尿病并发症预测的时序临床 KG，表明医学知识的使用通常与不断演变的临床上下文密不可分。

**MedReason**（Wu et al., 2025a）等基准使基于 KG 的医学推理需求具体化：任务不仅是检索医学相关实体和关系，还要将它们组织成符合临床逻辑和循证医学的推理路径。这促使我们将三元组有效性本身视为**上下文依赖的**。

---

## 3 方法（Method）

### 3.1 知识来源

#### 3.1.1 从 PrimeKG 提取的疾病中心子图

PrimeKG（Chandak et al., 2023）为本工作提供源生物医学 KG。处理完整图计算成本极高，且会引入噪声。

我们构建一个以目标疾病实体为中心的聚焦子图——在我们的实验中，即**糖尿病（MONDO:5015）**。构建分两层进行：

- **直接层**：收集所有三元组 (h, r, t) ∈ PrimeKG，其中 h 或 t 为目标疾病实体，得到距离糖尿病一跳的中间实体集 **E1（735 个实体）**，包含 **1,470 个三元组**
- **间接层**：收集至少一个端点在 E1 中的所有三元组，捕获二阶关联（如作用于糖尿病相关通路中蛋白质的药物），不扩展到整个图，贡献额外 **861,070 个三元组**

去重后，Gsub 包含 **862,540 个三元组**，跨 **18,387 个唯一实体**，涵盖 10 种生物医学实体类型（基因/蛋白质、药物、疾病、生物过程、表型、通路、暴露、分子功能、细胞组分、解剖结构）和 **25 种关系类型**。

#### 3.1.2 聚焦关系标注

大多数 PrimeKG 关系类型编码的是在患者上下文中相对稳定的生物学或分子事实。因此，我们聚焦于适用性更可能随患者特定因素变化的关系类型：**indication（适应症）、contraindication（禁忌症）、off-label use（超说明书使用）和 drug_effect（药物效应）**。

对于这四个类型中的每个唯一三元组 (h, r, t)，我们使用 **Baichuan-M2-Plus API** 生成关于人群特定适用性的证据。输出存储为结构化的 **ConstraintItem** 记录，每条包含：
- patient_characteristics：关系成立的患者特征（如 "eGFR < 30"，"HbA1c > 9%"）
- applicability_level：五点序数量表（从 Definitely Applicable 到 Definitely NOT Applicable）
- supporting_evidence_text：支持证据文本

结果 **relation_with_facts** 集合包含 **68,651 个标注事实**，跨越 **2,591 个唯一实体**和 **4 种关系类型**。这些标注在推理时被检索，以支持患者上下文过滤。

### 3.2 推理流水线

我们实现一个**两智能体循环**（见图 1，面板 C），其中纯 LLM 推理器和基于 KG 的验证器迭代协作。

**算法 1：QKG 推理流水线**

```
输入：问题 Q，选项 C，知识图谱 Gsub
输出：最终答案 A*

1:  P ← ExtractPatientContext(Q)            ▷ 从问题中提取患者上下文
2:  (A, claims) ← Reasoner(Q, C)            ▷ 纯 LLM；为答案选项发出声明
3:  for each claim c ∈ claims do
4:    E ← SearchEntities(c)                  ▷ 搜索相关实体
5:    R ← GetRelationsWithContext(E, Gsub)    ▷ 获取带上下文的关系
6:    RP ← ApplyConstraintItems(R, P)        ▷ 应用约束项
7:    if RP supports c then
8:      status(c) ← SUPPORTED
9:    else if RP contradicts c then
10:     status(c) ← CONTRADICTED
11:   else
12:     status(c) ← NO_COVERAGE
13:   end if
14: end for
15: report ← {(c, status(c)) | c ∈ claims}
16: if any claim in report is CONTRADICTED then
17:   A* ← Reasoner(Q, C, report)            ▷ 重新考虑
18: else
19:   A* ← A
20: end if
21: return A*
```

**图 1：QKG 框架概览。** 面板 A 展示传统 KG 三元组的局限（上下文无关的二值有效性）。面板 B 展示 QKG 通过附加自然语言有效性条件实现 Fτ(C)。面板 C 展示推理器-验证器设置。面板 D 总结性能趋势。

**流程说明：**
1. **推理器**首先提出答案并发出结构化声明
2. **验证器**对照 QKG 和患者上下文检查每条声明
3. 患者上下文直接从临床问题中提取，包括人口统计学因素、合并症、实验室值和当前用药
4. 对于每个检索到的 KG 关系，验证器检查其关联的 ConstraintItem 记录，确定约束是否适用于当前患者
5. 不满足约束的关系在作为证据前被降权或排除
6. 验证器每轮最多允许 **20 次工具使用**（tool-use turns）
7. **推理器**根据验证报告重新考虑其答案

### 3.3 统计检验

为检验两个流水线设置之间的精度差异是否统计显著，我们对配对的每个样本正确性应用 **McNemar 检验**。对于在同一问题上评估的设置 A 和 B，令 b 和 c 分别表示在 A 下正确但在 B 下错误、以及在 A 下错误但在 B 下正确的样本计数。在零假设下（每个不一致翻转在任一方向等可能），我们报告精确的双侧二项式 p 值：

$p = \min\{1, 2 \sum_{k=\max(b,c)}^{b+c} \binom{b+c}{k} 2^{-(b+c)}\}$

对于与无验证器基线的比较，推理器单独的正确性被视为条件 A，验证后的最终正确性为条件 B（同一轮次）。对于 Qwen 验证器运行的泄露调整比较，如果在任一运行中样本的 W→C 修订被标记为 LIKELY_LEAKAGE，或 C→W 回归被标记为 LIKELY_KG_SUPPORTED 且决定性证据引用 QKG 适用性令牌，则在配对检验前移除该样本。

---

## 4 实验设置（Experimental Setup）

### 4.1 数据集

我们在来自 **MedReason**（Wu et al., 2025a）的医学问答样本上评估，该数据集约含 30,000 个问题，来自 7 个来源：**MedQA、MedMCQA、PubMedQA、MMLU、MedXpert、HuatuoGPT-o1** 和 **Humanity's Last Exam（HLE）的医学子集**。

为确保与 curated PrimeKG 子集对齐，我们通过以下流水线构建 KG 基础评估集：
1. **实体提取和 UMLS 对齐**：对每个问题和答案选项，LLM 基础智能体提取命名医学实体；通过近似最近邻搜索匹配到 UMLS CUI
2. **PrimeKG 对齐**：通过直接匹配和 UMLS 层次遍历将 UMLS CUI 映射到 PrimeKG 节点
3. **子图路径过滤**：枚举匹配 PrimeKG 节点间的 1 跳路径，排除无路径的样本
4. **患者特征标注**：从问题文本中提取结构化的 PatientCharacter 记录

结果评估集包含 **2,788 个样本**，覆盖一系列糖尿病相关的临床场景，具有经过验证的 KG 覆盖。

### 4.2 评估协议

- 每个样本，模型生成单个答案（A-J）及结构化推理
- 输出通过 **Pydantic 模式（QAResponse）** 约束确保一致的 JSON 格式
- 评估完全自动化：解析模型输出，计算与金标准的精确匹配精度
- 主要指标：**exact-match accuracy**
- 次要指标：验证后答案变化的数量与百分比，以及这些修订改进或降低最终正确性的频率

### 4.3 模型与比较设置

主实验使用两个 LLM：
- **Haiku-4.5**（Anthropic, 2025）：作为基线模型
- **Qwen-3.6-Plus**（Qwen Team, 2026）：作为更高能力模型

比较三种设置：
1. **无验证器基线**：仅推理器
2. **KG 验证（无上下文匹配）**：使用原始 KG 验证，不检查患者上下文
3. **QKG 验证（带上下文匹配）**：使用 QKG 验证，应用患者上下文匹配

---

## 5 结果（Results）

### 5.1 主要结果与患者上下文消融研究

**图 2 展示了 curated 评估集（N = 2,788）上的主要结果。** 在三种设置中，Haiku-4.5 被用作推理器；在两种验证设置中，Haiku-4.5 也被用作验证器。

**面板 (a) 最终精度：**
- 无验证器基线：**77.5%**
- KG 验证（无上下文）：**78.1%（+0.6 pp）**
- QKG 验证（带上下文）：**78.9%（+1.4 pp）**

**面板 (b) 验证修订数：**
- 无上下文设置：修订 2.19% 的答案（39 W→C，22 C→W），净改进 +17
- 带上下文设置：修订 2.55% 的答案（55 W→C，16 C→W），净改进 +39

**统计显著性（配对 McNemar 检验）：**
- 基线 vs KG 验证（无上下文）：**p = 0.04**
- 基线 vs QKG 验证（带上下文）：**p ≈ 3.8×10⁻⁶**
- KG（无上下文）vs QKG（带上下文）：**p = 0.014**

上下文消融表明，带上下文匹配的 QKG 产生了更高的 W→C 率和更低的 C→W 率。

### 5.2 上下文依赖修正的案例研究

**图 3 展示了两个上下文依赖修正的案例研究。**

**案例 1（顶部）：组合性患者上下文示例**——验证器结合多个患者特定因素（年龄、吸烟、饮酒、与环丙沙星暴露的时间接近度）来修正初始答案，识别出氟喹诺酮相关肌腱病。

**案例 2（底部）：基于阈值的示例**——验证器将患者特定的血小板计数（95,000/mm³）与 IV tPA 的资格阈值进行匹配。

### 5.3 Qwen-3.6-Plus 作为验证器

**图 4 展示了强验证器比较结果（N = 2,788），Haiku-4.5 作为推理器贯穿所有设置。** Qwen-3.6-Plus 在该集上显著强于 Haiku-4.5——其作为推理器的独立精度为 **89.1%**（vs Haiku-4.5 的 77.5%）。

**面板 (a) 最终精度：**
- 无验证器基线：**77.5%**
- KG 验证（无上下文）：**83.3%（+5.8 pp）**
- QKG 验证（带上下文）：**83.5%（+6.0 pp）**

**面板 (b) 验证修订数：**
- 无上下文设置：177 W→C，16 C→W，净改进 +161
- 带上下文设置：204 W→C，38 C→W，净改进 +166

#### 强验证器答案泄露的案例研究

两个 W→C 修订展示了泄露如何体现。在 qa_9542 中，KG 对任何选项都没有直接相关的调度边，验证器自行提供了季节性流感疫苗接种时机的论证。在 qa_6324（金标准：拔牙前抗生素预防）中，两项 CONTRADICTED 状态同样依赖于验证器在 KG 查找未返回直接相关边后的医学知识，分别引用 AHA 预防指南和关于一氧化二氮的通用药理学知识。

#### 定量泄露分类

**表 1：两个 Qwen-3.6-Plus 验证器运行的泄露调整精度核算（Haiku-4.5 作为推理器贯穿所有设置）。**

| 设置 | N | W→C | C→W | 估计调整数 | 原始最终精度(%) | 调整后最终精度(%) |
|------|---|------|-----|-----------|-----------------|-----------------|
| KG 无上下文 | 2,788 | 177 | 16 | 60 | 83.25 | **82.88** |
| QKG 带上下文 | 2,788 | 204 | 38 | 75 | 83.46 | **83.75** |

**表 2：两个 Qwen-3.6-Plus 验证器运行中 W→C 修订和 C→W 回归的类别级泄露分类。** 括号中为引用 QKG 特定适用性令牌的子集数量。

| 设置 | W→C: KG支持(上下文令牌) | W→C: 混合 | W→C: 泄露 | C→W: KG支持(上下文令牌) | C→W: 混合 | C→W: 泄露 |
|------|------------------------|-----------|----------|------------------------|-----------|----------|
| KG 无上下文 | 97 (0) | 20 | 60 | 12 (0) | 0 | 4 |
| QKG 带上下文 | **123 (27)** | 26 | 55 | **36 (20)** | 1 | 1 |

**关键发现：**
- 两个运行泄露程度相当（约 55-60 个 W→C 修订标记为可能泄露）
- 带上下文运行产生了明显更多的 KG 支持的 W→C 修订（123 vs 97），其中 27 个明确调用了 QKG 特定适用性令牌（vs 无上下文的 0 个）
- 泄露调整后最终精度：无上下文 82.88%，带上下文 **83.75%**——仍超过无验证器基线（77.5%）超过 5 个百分点
- C→W 回归中，带上下文运行的 38 个中有 36 个是 KG 支持的，仅 1 个为可能泄露——20 个引用了 QKG 适用性令牌

**统计检验结果：** 带上下文 vs 无上下文的配对 McNemar 检验：原始配对集（N=2,782）上 p = 0.73；泄露调整子集（N=2,665）上 **p = 0.05**——从强空假设变为边界显著效应。

---

## 6 讨论（Discussion）

### 6.1 不仅仅是事实，更是适用的知识

在临床推理中，关键问题不是 KG 事实是否与医学相关，而是该事实在患者的特定上下文中是否适用。

在第一个案例研究中，验证器仅在结合多个患者特定因素（年龄、吸烟、饮酒、环丙沙星暴露时间）后，才能确定药物诱导的肌腱病关系适用于该特定患者。在第二个案例中，验证器仅通过将具体的实验室值（血小板计数 95,000/mm³）与 tPA 资格阈值匹配才成功。

这正是建模上下文依赖的三元组有效性的动机。如果 KG 边一旦被检索就被视为"真"，验证器无法区分一般相关知识和当前患者实际有效的知识。

**聚合结果与此解释一致：**
- 仅仅是 KG 支持的验证已经有一定用处（KG 验证无上下文仍改善基线）
- 但更大的增益来自上下文感知验证：完整的 QKG 设置表现更好，因为它在检索到医学相关知识后还会判断该关系是否应为该患者计数
- 在更强验证器下顺序保持不变，尽管差距较小，这可以归因于强验证器自身的模型内部知识

### 6.2 为什么强验证器结果需要谨慎解读

Qwen-3.6-Plus 验证器结果比 Haiku 验证器消融更难进行因果解读。两个 Qwen 验证器运行中都包含答案泄露，因此原始增益不是基于图的验证的干净测量。

通过对 C→W 回归的逐案例泄露分类（表 2），带上下文下 C→W 的增加（38 vs 16）主要由 KG 支持的回归主导（+24），特别是 QKG 令牌驱动的回归（+20），而非验证器幻觉。

泄露调整后的配对检验结果（p 从 0.73 到 0.05）确认了这一解读——一旦移除基准金标准噪声案例，QKG 的上下文效应变得边界显著。

QKG 的上下文效应在真实临床推理中应该最为重要，因为答案通常依赖于上下文条件化的证据组合，而非单事实回忆。

### 6.3 局限性与未来工作

当前研究的主要局限性是，基准医学 QA 上的评估无法完全分离 QKG 的上下文验证和模型内部医学知识。这一问题在强验证器下尤为突出。

更干净的测试需要使用真实世界的患者级推理任务，但这类评估仍然困难，因为公开可用的临床数据集很少提供用于上下文推理的可扩展金标准标签。

**未来工作：**
- 构建真实的临床推理基准
- 测试 QKG 在更现实临床条件下的表现
- 诊断其失败模式
- 在更大规模上改进上下文依赖的 KG 验证

---

## 7 结论（Conclusion）

本文引入**量子知识图谱（QKG）**，一个将三元组有效性建模为上下文依赖而非上下文无关的框架。

我们在医学领域实例化 QKG，通过为 KG 关系附加自然语言适用性条件，并在医学问答的推理器-验证器流水线中使用它们。主要结果：
- **Haiku-4.5 配对设置**下，患者上下文匹配较无上下文的 KG 验证带来小而显著的增益（**+0.79 pp, p=0.014**），两种设置均超过无验证器基线
- **Qwen-3.6-Plus 强验证器**下，原始配对差距为 null（p=0.73），调整知识泄露后变为**边界显著**（p=0.05）——归因于 MCQ 医学 QA 的基准金标准天花板效应，而非 QKG 冗余

更广泛地说，研究结果支持一个观点：**知识图谱在 LLM 推理中的价值不仅在于存储相关事实，更在于表示这些事实在使用的特定上下文中是否适用。**

---

## 致谢

本研究由香港城市大学（项目编号 9610777）支持。我们感谢百川智能提供支持使用 Baichuan M2 Plus 模型的免费令牌额度。我们感谢李林峰博士的启发性讨论。我们感谢 HKAI-Sci 主任马维英教授鼓励我们探索这一研究前沿。

---

## 参考文献

（完整 20 篇参考文献，按文中出现顺序）

- Anthropic. Introducing Claude Haiku 4.5, 2025.
- Baichuan Intelligence. Baichuan-M2 Technical Blog, 2025.
- Chandak et al. PrimeKG: A knowledge graph for precision medicine. *Scientific Data*, 2023.
- Chen et al. Multi-granularity temporal question answering over knowledge graphs. *ACL 2023*.
- Diao et al. The research of clinical temporal knowledge graph based on deep learning. *JIFS*, 2021.
- Ding et al. Temporal fact reasoning over hyper-relational knowledge graphs. *EMNLP 2024 Findings*.
- Dougrez-Lewis et al. Assessing the reasoning capabilities of LLMs in the context of evidence-based claim verification. *ACL 2025 Findings*.
- Galkin et al. Message passing for hyper-relational knowledge graphs. *EMNLP 2020*.
- Johnson et al. MIMIC-IV. *Scientific Data*, 2023.
- Kolli et al. Hybrid fact-checking that integrates knowledge graphs, LLMs, and search-based retrieval agents. *Widening NLP Workshop*, 2025.
- Li et al. A method to learn embedding of a probabilistic medical knowledge graph. *JMIR Medical Informatics*, 2020a.
- Li et al. Real-world data medical knowledge graph: Construction and applications. *Artificial Intelligence in Medicine*, 2020b.
- Parović et al. Generating domain-specific knowledge graphs from large language models. *ACL 2025 Findings*.
- Qwen Team. Qwen3.6-Plus: Towards Real World Agents, 2026.
- Saxena et al. Question answering over temporal knowledge graphs. *ACL 2021*.
- Sui et al. Can knowledge graphs make large language models more trustworthy? *ACL 2025*.
- Wornow et al. EHRSHOT: An EHR benchmark for few-shot evaluation of foundation models. *NeurIPS 2023*.
- Wu et al. MedReason: Eliciting factual medical reasoning steps in LLMs via knowledge graphs. *arXiv:2504.00993*, 2025a.
- Wu et al. Medical Graph RAG. *ACL 2025*.
- Wu et al. Medical graph rag: Evidence-based medical large language model via graph retrieval-augmented generation. *ACL 2025*.

---

## 附录 A

### A.1 评估数据集构建

从 MedReason（Wu et al., 2025a）通过四阶段流水线推导评估集。

**表 3：完整 MedReason 数据集（N = 32,682）和 curated 评估集（N = 2,788）的 QA 来源分布。**

| 来源 | MedReason (完整) | curation 后 |
|------|-----------------|-------------|
| MedQA | 8,016 (24.5%) | **1,981 (71.0%)** |
| PubMedQA (人工) | 8,094 (24.8%) | 62 (2.3%) |
| HuatuoGPT-o1 | 6,475 (19.8%) | 313 (11.2%) |
| MedMCQA | 6,197 (19.0%) | 144 (5.2%) |
| PubMedQA (未标注) | 1,747 (5.3%) | 10 (0.4%) |
| MMLU | 827 (2.5%) | 58 (2.1%) |
| MedXpertQA | 666 (2.0%) | 208 (7.5%) |
| PubMedQA | 603 (1.8%) | 7 (0.3%) |
| HLE (医学) | 57 (0.2%) | 5 (0.2%) |

curation 集强烈偏向 MedQA（71.0%），反映 MedQA 问题往往包含丰富的临床场景和多个命名实体，产生更高的 PrimeKG 路径计数。

**阶段 1：实体提取与 UMLS 对齐** — LLM 基础智能体提取命名医学实体，通过近似最近邻搜索匹配到 UMLS CUI（Tencent VectorDB, google/gemini-embedding-001, 768维）。

**阶段 2：PrimeKG 对齐** — 通过直接匹配和 UMLS 层次遍历两种策略将 UMLS CUI 映射到 PrimeKG 节点。

**阶段 3：子图路径过滤** — 枚举匹配 PrimeKG 节点间的 1 跳路径；无路径的样本被排除。

**阶段 4：患者特征标注** — 从问题文本中提取结构化的 PatientCharacter 记录。

### A.2 QAResponse 模式

```python
class QAResponse(BaseModel):
    llm_answer_choice: str
    selected_option_text: str
    reasoning: str
```

### A.3 泄露分类启发式方法

**信号检测：** 对每个决定性的 CONTRADICTED 证据字符串 e，通过正则表达式测试四个信号：
- KG_SUPPORT(e)：e 引用 KG 实体、关系或边
- KG_GAP(e)：e 承认 KG 没有相关边
- PARAMETRIC(e)：e 断言外部临床或指南知识
- CONTEXT(e)：e 包含 QKG 特定适用性令牌（AVOID、RECOMMENDED、CAUTION、ConstraintItem、safety judgment）

**决定性证据：** 验证报告中的 CONTRADICTED 项是关键性的，如果其 supports 标志为真且其选项匹配推理器的原始答案，或其 supports 标志为假且其选项匹配金标准答案。

**泄露分类算法（算法 2）：**
```
LabelEvidence(e):
  若 Context(e) → EvContext
  否则若 KgGap(e) 且 Parametric(e) → EvLeakage
  否则若 Parametric(e) 且 ¬KgSupport(e) 且 ¬KgGap(e) → EvLeakage
  否则若 KgSupport(e) → EvKgGrounded
  否则 → EvUnclassified

ClassifyCase(record):
  收集决定性证据 D
  标签集 L ← {LabelEvidence(e.evidence) : e ∈ D}
  supp ← (EvContext ∈ L) ∨ (EvKgGrounded ∈ L)
  leak ← EvLeakage ∈ L
  若 supp ∧leak → Mixed
  否则若 supp → LikelyKgSupported
  否则若 leak → LikelyLeakage
  否则 → Unclassified
```

**调整后精度公式（公式 1）：**
$$adj\_final\_acc = \frac{\#final\_correct - n_{leak}^{W→C}}{N - n_{leak}^{W→C} - n_{ctx}^{C→W}}$$

其中 n_leak^W→C 表示标记为 LikelyLeakage 的 W→C 修订，n_ctx^C→W 表示决定性证据引用 QKG 适用性令牌的 C→W 回归。

**合理性检查：** 在 17 个手动标记的 W→C 案例上，ClassifyCase 在 9/9 个上下文驱动案例和 7/8 个泄露案例上一致。

**LLM 重新标记未分类案例：** 正则表达式留下 29 个（无上下文）和 27 个（带上下文）W→C 案例为 Unclassified。通过 Haiku-4.5 LLM 提示重新标记每个 Unclassified 案例。

### A.4 强验证器答案泄露案例研究

**案例 A（qa_9542）**：金标准 D（带状疱疹疫苗）。62 岁女性，常规体检。推理器初始回答 B（流感疫苗），认为流感疫苗年需且患者上次接种是 2 年前。验证器报告：选项 B 标记为 NO_COVERAGE（KG 缺乏疫苗接种时间表），选项 D 被 CONTRADICTED（6 月是流感淡季，带疱疫苗是优先级）。推理器接受论证，切换到 D。

**案例 B（qa_6324）**：金标准 A（拔牙前抗生素预防）。72 岁男性，主动脉瓣置换史。推理器初始回答 C（避免一氧化二氮）。验证器报告：C 被 CONTRADICTED（KG 查询一氧化二氮禁忌症返回空，医学上一氧化二氮在固态/金属假肢心脏瓣膜中不禁忌）；A 被 CONTRADICTED（AHA 指南明确推荐人工心脏瓣膜患者进行抗生素预防）。推理器接受，修正为 A。

### A.5 发布代码与数据

- **GitHub 仓库**：评估代码、分析脚本、论文材料、结果 CSV
- **Hugging Face 数据集**：qkg-primekg-entities-with-cui、qkg-relation-with-facts、qkg_qa_dataset
- **可复现性详情**：评估入口点 conditionKgTestAgentic.py，配对显著性检验 paper/data_result/significance_tests.py，泄露重标记脚本 classify_unclassified_with_llm.py
