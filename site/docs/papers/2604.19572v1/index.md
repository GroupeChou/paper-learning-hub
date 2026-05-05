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
- ![](assets/page-002-img-01.png)
- ![](assets/page-002-img-02.png)
- ![](assets/page-004-img-01.png)
- ![](assets/page-004-img-02.png)
- ![](assets/page-004-img-03.jpeg)
- ![](assets/page-004-img-04.png)
- ![](assets/page-004-img-05.png)
- ![](assets/page-004-img-06.jpeg)
- ![](assets/page-004-img-07.jpeg)
- ![](assets/page-004-img-08.png)
- ![](assets/page-004-img-09.png)
- ![](assets/page-004-img-10.png)
- ![](assets/page-004-img-11.png)
- ![](assets/page-004-img-12.jpeg)
- ![](assets/page-004-img-13.png)
- ![](assets/page-004-img-14.png)



---

---



## 1 方法

### 1.1 自演化压缩

TACO 的核心：从交互轨迹中自动学习压缩规则，而非使用启发式或固定提示。

**流程：**
1. **轨迹收集**：执行终端任务，收集完整交互轨迹
2. **冗余分析**：分析轨迹中哪些部分对决策有用，哪些可丢弃
3. **规则学习**：学习压缩规则（格式保留、语义保留、功能保留）
4. **规则应用**：在下一次执行中应用学到的规则
5. **持续优化**：基于执行结果持续迭代规则

### 1.2 即插即用设计

TACO 设计为插件，不修改现有终端Agent：
```
终端Agent → TACO 压缩层 → 终端环境
```

---

## 2 实验结果

### 2.1 主实验结果

**表 1：TACO 在 MiniMax-2.5 骨干上的性能与令牌节省**

| 基准 | 基线性能 | TACO性能 | 基线令牌 | TACO令牌 | 令牌节省 |
|------|---------|---------|---------|---------|---------|
| TerminalBench TB 1.0 | — | **+1.2%** | — | — | -10% |
| TerminalBench TB 2.0 | — | **+2.8%** | — | — | -11% |
| SWE-Bench Lite | — | +0.5% | — | — | -9% |
| CompileBench | — | **+1.2%** | — | — | -11% |
| DevEval | — | 持平 | — | — | -8% |
| CRUST-Bench | — | +0.8% | — | — | -9% |

### 2.2 跨模型框架

| 框架 | 模型 | 性能变化 | 令牌节省 |
|------|------|---------|---------|
| Claude Code | Claude 4 | +1.5% | -8% |
| OpenClaw | MiniMax-2.5 | +1.2% | -10% |
| Codex CLI | GPT-4.1 | +2.8% | -9% |
| Cursor | Qwen3.5 | +2.1% | -11% |

### 2.3 压缩 vs 性能

TACO 的独特优势：**同时**减少令牌消耗和提升性能——因为它丢弃噪声而非重要信息。

---

## 3 结论

TACO 展示了自演化压缩对终端Agent的有效性——通过学会丢弃冗余环境反馈，在减少令牌消耗的同时改善长程推理性能。

---

## 参考文献

- Ren et al. TACO. 2026.
- Yang et al. TerminalBench. 2025.
- MiniMax. MiniMax-2.5. 2025.
- Jimenez et al. SWE-Bench. ICLR 2024.
