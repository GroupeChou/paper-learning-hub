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

大型语言模型智能体在软件工程任务上取得了显著进展，然而当前方法存在一个根本性的上下文耦合问题（context coupling problem）：标准的代码编辑界面将代码检查、修改规划和编辑执行混在同一个上下文窗口中，迫使智能体将探索性查看与严格格式化的编辑生成交错进行。

这导致无关信息不断累积，损害了智能体的性能。

为了解决这一问题，我们提出了 SWE-Edit，它将代码编辑分解为两个专门的子智能体：一个 Viewer（查看器），按需提取与任务相关的代码；一个 Editor（编辑器），根据高层规划执行修改——从而让主智能体专注于推理，同时将上下文密集型操作委托给干净的上下文窗口。

我们进一步研究了什么构成一个有效的编辑模型：观察到当前主流的查找-替换格式容易出错，我们使用 GRPO 训练 Qwen3-8B，使其自适应地选择编辑模式，相比单一格式基线提升了编辑效率。

在 SWE-bench Verified 上，SWE-Edit 将解决率提升了 2.1%，同时将推理成本降低了 17.9%。

我们还额外提出了一个代码编辑基准，能够可靠地预测下游智能体性能，为编辑模型选择提供实用指导。

我们的代码已公开在 https://github.com/microsoft/SWE-Edit。

*Yikai Zhang 1 2 *，Jiaxin Pei 3，Kenan Li 1，Maoquan Wang 1，Jin Pan 2，Yu Kang 1，Shengyu Fu 1，Elsie Nallipogu 1，Junjie Hu 2，Yufan Huang 1，Zijian Jin 1*

*工作完成于微软实习期间。*
1 微软，美国华盛顿州雷德蒙德
2 威斯康星大学麦迪逊分校计算机科学系，美国威斯康星州麦迪逊
3 斯坦福大学以人为本人工智能研究所（HAI），美国加利福尼亚州斯坦福


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

大型语言模型智能体在软件工程任务上取得了显著进展，然而当前方法存在一个根本性的上下文耦合问题（context coupling problem）：标准的代码编辑界面将代码检查、修改规划和编辑执行混在同一个上下文窗口中，迫使智能体将探索性查看与严格格式化的编辑生成交错进行。

这导致无关信息不断累积，损害了智能体的性能。

为了解决这一问题，我们提出了 SWE-Edit，它将代码编辑分解为两个专门的子智能体：一个 Viewer（查看器），按需提取与任务相关的代码；一个 Editor（编辑器），根据高层规划执行修改——从而让主智能体专注于推理，同时将上下文密集型操作委托给干净的上下文窗口。

我们进一步研究了什么构成一个有效的编辑模型：观察到当前主流的查找-替换格式容易出错，我们使用 GRPO 训练 Qwen3-8B，使其自适应地选择编辑模式，相比单一格式基线提升了编辑效率。

在 SWE-bench Verified 上，SWE-Edit 将解决率提升了 2.1%，同时将推理成本降低了 17.9%。

我们还额外提出了一个代码编辑基准，能够可靠地预测下游智能体性能，为编辑模型选择提供实用指导。

我们的代码已公开在 https://github.com/microsoft/SWE-Edit。

*Yikai Zhang 1 2 *，Jiaxin Pei 3，Kenan Li 1，Maoquan Wang 1，Jin Pan 2，Yu Kang 1，Shengyu Fu 1，Elsie Nallipogu 1，Junjie Hu 2，Yufan Huang 1，Zijian Jin 1*

*工作完成于微软实习期间。*
1 微软，美国华盛顿州雷德蒙德
2 威斯康星大学麦迪逊分校计算机科学系，美国威斯康星州麦迪逊
3 斯坦福大学以人为本人工智能研究所（HAI），美国加利福尼亚州斯坦福


## 图表资源
- ![](assets/page-009-img-01.png)



---

