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
- 图片数量超过上限，仅保留前 20 张。
- 图片数量超过上限，仅保留前 20 张。
- 图片数量超过上限，仅保留前 20 张。
- 图片数量超过上限，仅保留前 20 张。
- 图片数量超过上限，仅保留前 20 张。

## 图表资源
- ![](assets/page-001-img-01.jpeg)
- ![](assets/page-001-img-02.png)
- ![](assets/page-001-img-03.jpeg)
- ![](assets/page-001-img-04.png)
- ![](assets/page-001-img-05.jpeg)
- ![](assets/page-001-img-06.jpeg)
- ![](assets/page-001-img-07.png)
- ![](assets/page-001-img-08.png)
- ![](assets/page-001-img-09.jpeg)
- ![](assets/page-001-img-10.jpeg)
- ![](assets/page-001-img-11.png)
- ![](assets/page-001-img-12.png)
- ![](assets/page-001-img-13.jpeg)
- ![](assets/page-001-img-14.png)
- ![](assets/page-001-img-15.png)
- ![](assets/page-001-img-16.jpeg)
- ![](assets/page-003-img-01.png)
- ![](assets/page-003-img-02.jpeg)
- ![](assets/page-003-img-03.jpeg)
- ![](assets/page-008-img-01.png)



---

---

## 摘要

幻灯片生成的模态差距：生成以文本为中心，但质量由视觉美学决定。**AeSlides** 引入可验证美学指标的 GRPO 强化学习框架。

**6个可计算美学指标：** 宽高比一致性、空间利用率、元素间距均匀性、对齐度、视觉权重平衡、元素碰撞

---

## 结果

| 方法 | GPT-4o评估 | 用户研究 |
|------|-----------|---------|
| GLM-4.7-Flash（基线） | 100 | 100 |
| + 视觉反思 | +2.31% | +1.82% |
| + 完整微调 | +5.12% | +8.43% |
| **AeSlides（5K训练）** | **+6.24%** | **+10.86%** |

**消融：** 空间利用率（+3.42%）和元素碰撞（+2.87%）最具影响力。5K提示=最优性价比。

---

## 参考文献

- Pan et al. AeSlides. 2026.
- Shao et al. GRPO. 2025.
