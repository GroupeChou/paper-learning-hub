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



## 图表资源
- ![](assets/page-004-img-01.png)
- ![](assets/page-005-img-01.png)
- ![](assets/page-017-img-01.png)



---

---

## 摘要

本文开发基于逻辑的方法从带时间戳数据和背景知识推断高层时间扩展事件。使用**逻辑规则**捕获存在条件和终止条件，组合为**元事件**。

**四种时间线：** 朴素、一致（满足约束）、偏好（最大置信度）、谨慎（所有偏好交集）

**形式化规范：** Σ = (Π_SE, Π_ME, Υ_temp, Υ_dom)

---

## 复杂度

| 任务 | 朴素 | 一致 | 偏好 | 谨慎 |
|------|------|------|------|------|
| 识别 | P | coNP-complete | coNP-complete | coNP-complete |
| 生成 | P | NP-hard | NP-hard | 更难 |

**可处理片段：** 分层规则集 + 非重叠约束 → 唯一偏好时间线 → 多项式时间

---

## 医学应用

肺癌用例（激素疗法TKI推理）：
```
exists(TKITh(p,d), t, 1) ← Adm(p,d,t) ∧ TKI(d)
ends(TKITh(p,d), t, 1) ← Adm(p,d',t') ∧ TKI(d') ∧ d' ≠ d
```

**结果：** 计算可行，与医学专家意见一致。

---

## 参考文献

- Awuklu et al. 2026.
- Brewka et al. Answer Set Programming. CACM 2011.
