# paper

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

## 解析备注

- 图片数量超过上限，仅保留前 20 张。
- 图片数量超过上限，仅保留前 20 张。
- 图片数量超过上限，仅保留前 20 张。
- 图片数量超过上限，仅保留前 20 张。
- 图片数量超过上限，仅保留前 20 张。
- 图片数量超过上限，仅保留前 20 张。
- 图片数量超过上限，仅保留前 20 张。



## 图表资源

- ![](assets/page-001-img-01.png)
- ![](assets/page-001-img-02.png)
- ![](assets/page-001-img-03.jpeg)
- ![](assets/page-001-img-04.jpeg)
- ![](assets/page-001-img-05.jpeg)
- ![](assets/page-001-img-06.png)
- ![](assets/page-001-img-07.png)
- ![](assets/page-001-img-08.png)
- ![](assets/page-001-img-09.png)
- ![](assets/page-001-img-10.png)
- ![](assets/page-001-img-11.png)
- ![](assets/page-001-img-12.png)
- ![](assets/page-001-img-13.jpeg)
- ![](assets/page-001-img-14.png)
- ![](assets/page-001-img-15.png)
- ![](assets/page-001-img-16.png)
- ![](assets/page-001-img-17.png)
- ![](assets/page-001-img-18.png)
- ![](assets/page-001-img-19.png)
- ![](assets/page-001-img-20.png)
- ![](assets/page-001-img-21.jpeg)
- ![](assets/page-001-img-22.png)
- ![](assets/page-001-img-23.jpeg)
- ![](assets/page-004-img-01.png)
- ![](assets/page-004-img-02.png)
- ![](assets/page-004-img-03.png)
- ![](assets/page-004-img-04.png)
- ![](assets/page-004-img-05.png)
- ![](assets/page-004-img-06.png)
- ![](assets/page-004-img-07.png)
- ![](assets/page-005-img-01.png)
- ![](assets/page-023-img-01.png)
- ![](assets/page-025-img-01.jpeg)
- ![](assets/page-025-img-02.png)
- ![](assets/page-025-img-03.png)
- ![](assets/page-025-img-04.png)
- ![](assets/page-026-img-01.png)
- ![](assets/page-026-img-02.png)
- ![](assets/page-026-img-03.png)
- ![](assets/page-027-img-01.jpeg)
- ![](assets/page-027-img-02.jpeg)
- ![](assets/page-027-img-03.jpeg)
- ![](assets/page-027-img-04.jpeg)
- ![](assets/page-027-img-05.jpeg)
- ![](assets/page-027-img-06.jpeg)
- ![](assets/page-027-img-07.jpeg)
- ![](assets/page-027-img-08.jpeg)
- ![](assets/page-027-img-09.png)



---

---

## 2 MathNet 数据构建

### 2.1 收集过程

| 步骤 | 细节 |
|------|------|
| 来源 | 47 个国家的数学竞赛题、奥赛题 |
| 时间跨度 | 4 个十年（从 1980 年代至今） |
| 语言 | 17 种语言，包含多语言平行版本 |
| 问题类型 | 68 种（代数、几何、数论、组合、三角、微积分、概率统计等） |

### 2.2 解答

每个问题附带：
- 人类专家编写的详细逐步解答
- 多模态内容（公式、图表、几何图）
- 多语言版本

### 2.3 问题类型本体

68 种问题类型，分为 7 大类别：

| 类别 | 子类型示例 |
|------|-----------|
| **代数（Algebra）** | 方程、不等式、多项式、函数方程、序列 |
| **几何（Geometry）** | 平面几何、立体几何、解析几何、三角几何 |
| **数论（Number Theory）** | 整除性、同余、质数、丢番图方程 |
| **组合数学（Combinatorics）** | 排列组合、图论、博弈论、计数 |
| **三角学（Trigonometry）** | 三角恒等式、三角方程 |
| **微积分（Calculus）** | 极限、导数、积分、级数 |
| **概率与统计（Probability & Stats）** | 概率计算、期望、组合概率 |

---

## 3 评估任务

### 任务 1：数学理解

标准数学问题求解。评估从 GPT-4o 到 DeepSeek-R1 的一系列前沿模型。

| 模型 | 准确率(%) |
|------|----------|
| DeepSeek-R1 | **54.1** |
| GPT-4o | 52.3 |
| Gemini 1.5 Pro | 48.7 |
| Claude 3.5 Sonnet | 46.2 |
| Qwen2.5-Math | 43.5 |
| LLaMA-3.1-70B | 38.9 |
| Gemma 2 27B | 34.2 |

**关键发现：** 即使在最先进的模型上，奥赛级数学推理的准确率仅约 50%，表明**巨大改进空间**。

### 任务 2：问题检索

**首个数学问题检索基准。**

给定查询问题，系统必须从题库中检索语义相似的问题。

| 方法 | Recall@10(%) | Recall@50(%) |
|------|-------------|-------------|
| BM25（词法） | 32.1 | 48.3 |
| Sentence-BERT | 45.7 | 62.1 |
| OpenAI Ada-002 | 51.2 | 68.5 |
| **BGE-M3** | **58.9** | **74.2** |
| **Math-specific embedding** | **67.3** | **81.5** |

**关键发现：** 通用嵌入模型在数学问题上表现不佳。BM25（词法匹配）对数学公式（涉及符号和结构）表现特别差。数学特定嵌入显著优于通用方法。

### 任务 3：数学 RAG

给定目标问题和检索到的相关问题的解答，模型必须预测目标答案。

| 方法 | 准确率(%) |
|------|----------|
| 无检索（仅模型） | 43.2 |
| BM25 检索 + RAG | 47.8 |
| BGE-M3 检索 + RAG | 52.6 |
| **Math embedding + RAG** | **56.1** |

数学 RAG 在数学推理中具有显著增值——检索到的相关问题解答为模型提供了重要的参考。

---

## 4 多语言分析

### 跨语言性能

| 语言 | GPT-4o | DeepSeek-R1 | Qwen2.5-Math |
|------|--------|-------------|-------------|
| 英文 | 58.3% | **62.1%** | 46.2% |
| 中文 | 52.7% | 56.3% | **48.5%** |
| 西班牙语 | 48.1% | 50.2% | 41.3% |
| 法语 | 47.5% | 49.8% | 40.8% |
| 阿拉伯语 | 42.3% | 45.1% | 36.2% |
| 韩语 | 41.8% | 43.7% | 35.1% |
| 俄语 | 40.5% | 42.3% | 34.8% |

**关键发现：** 所有模型在非英语语言上的性能均下降。DeepSeek-R1 在多语言设置下表现最一致。

---

## 5 结论

MathNet 是一个大规模（30K+）、多语言（17种语言）、多模态的数学基准，支持**三个评估任务**：理解、检索和 RAG。

**主要贡献：**
1. 最大规模的奥赛级多语言数学数据集（30,676 题）
2. **首个数学检索基准**
3. 覆盖 47 个国家、143 个竞赛、4 个十年的数据多样性
4. 最全面的人类编写多模态解答

**公开可用：** 数据、基准和排行榜在 mathnet.mit.edu 提供。

---

## 参考文献

- Alshammari et al. MathNet. ICLR 2026.
- Hendrycks et al. MATH. 2021.
- Shao et al. Omni-Math. 2024.
- He et al. OlympiadBench. 2024.
- Clark et al. OlympicArena. 2024.
- Azerbayev et al. LeanDojo. 2023.
- Cobbe et al. GSM8K. 2021.
- Xiao et al. BGE-M3. 2024.
- Reimers & Gurevych. Sentence-BERT. EMNLP 2019.
- OpenAI. Ada-002 embedding model.
- DeepSeek-AI. DeepSeek-R1. 2025.
- Qwen Team. Qwen2.5-Math. 2024.
- Gemini Team. Gemini 1.5. 2024.
- Anthropic. Claude 3.5 Sonnet. 2024.
