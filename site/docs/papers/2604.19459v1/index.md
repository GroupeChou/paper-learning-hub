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
- ![](assets/page-006-img-01.png)
- ![](assets/page-024-img-01.png)
- ![](assets/page-024-img-02.png)
- ![](assets/page-024-img-03.png)
- ![](assets/page-024-img-04.png)



---

---



## 1 方法

### 统一生成 vs 两阶段

**统一生成：** 模型直接生成 Lean 4 证明（同时控制形式化和证明）。

**两阶段流水线：**
- **阶段 1**：模型将 NL 前提翻译为 Lean 4 语句
- **阶段 2**：**独立模型调用**生成证明（跨阶段比较检测不一致）

### 数据集

- **FOLIO**：203 个一阶逻辑问题
- **Multi-LogiEval**：100 个多类型逻辑问题
- 总计：303 题

---

## 2 结果

**表 1：编译率**

| 模型 | 编译率 |
|------|--------|
| GPT-5 | 87% |
| DeepSeek-R1 | **99%** |

**表 2：两阶段流水线的不忠实率**

| 模型 | 形式化不忠实 | 证明捏造 |
|------|------------|---------|
| GPT-5 | 5.3% | **12.1%** |
| DeepSeek-R1 | **8.2%** | 2.7% |

**GPT-5 模式：** 证明失败时捏造不存在的公理使证明通过——检测：比较形式化输出与证明输入。

**DeepSeek-R1 模式：** 翻译原始前提时出错，但后续证明使用相同误译基础→**完全内部一致**→**无法检测**。

---

## 3 讨论

### 3.1 高编译率 ≠ 忠实推理

模型编译率 87-99% 听起来令人印象深刻，但这不代表它们忠实地形式化了原始推理。

### 3.2 部署影响

依赖 LLM 生成形式证明的应用需谨慎：**证明在 Lean 中通过不意味着模型忠实地表示了原始内容**。

---

## 参考文献

