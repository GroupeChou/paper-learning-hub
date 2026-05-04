# 从带时间戳数据推断高层事件：复杂度与医学应用

## Inferring High-Level Events from Timestamped Data: Complexity and Medical Applications

Yvon K. Awuklu¹,²,³, Meghyn Bienvenu¹, Katsumi Inoue⁴, Vianney Jouhet²,³, Fleur Mougin³

¹波尔多大学 ²波尔多大学医院 ³波尔多大学/INSERM ⁴日本国立信息学研究所

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
