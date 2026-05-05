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
- **状态**：待复核

## 摘要



## 解析备注

- 图片数量超过上限，仅保留前 20 张。

## 图表资源
- ![](assets/page-002-img-01.jpeg)
- ![](assets/page-002-img-02.jpeg)
- ![](assets/page-002-img-03.jpeg)
- ![](assets/page-002-img-04.jpeg)
- ![](assets/page-002-img-05.jpeg)
- ![](assets/page-002-img-06.jpeg)
- ![](assets/page-002-img-07.jpeg)
- ![](assets/page-002-img-08.jpeg)
- ![](assets/page-002-img-09.png)
- ![](assets/page-002-img-10.jpeg)
- ![](assets/page-003-img-01.jpeg)
- ![](assets/page-003-img-02.jpeg)
- ![](assets/page-003-img-03.jpeg)
- ![](assets/page-003-img-04.jpeg)
- ![](assets/page-003-img-05.png)
- ![](assets/page-003-img-06.png)
- ![](assets/page-013-img-01.png)
- ![](assets/page-021-img-01.png)
- ![](assets/page-021-img-02.png)
- ![](assets/page-021-img-03.png)



---

---

## 摘要

MLLM 被用作交互环境中的自主智能体。**SafetyALFRED** 在 ALFRED 基准上增加六类厨房危害，评估 11 个模型（Qwen、Gemma、Gemini）的**危害识别（QA）vs 危害缓解（具身规划）**。

**关键发现：约 50pp 的对齐差距**
- QA 识别最高 **92.3%**
- 规划缓解最高仅 **42.1%**

---

## 结果

| 模型 | QA识别(%) | 规划缓解(%) | 差距 |
|------|---------|------------|------|
| Gemini 2.0 Flash | **92.3** | **42.1** | 50.2 |
| Gemini 1.5 Pro | 88.7 | 38.5 | 50.2 |
| Qwen2.5-VL-72B | 85.1 | 35.2 | 49.9 |
| Gemma 3-27B | 79.4 | 28.3 | 51.1 |

**按危害类别：** 简单危害（火灾 H1：44.8pp 差距）< 复杂危害（电气 H6：58.2pp 差距）

**失败模式：** 忽略危害、缓解不足、错误序列、幻觉行动

---

## 参考文献

- Torres-Fonseca et al. SafetyALFRED. 2026.
- Khandelwal et al. ALFRED. 2020.
