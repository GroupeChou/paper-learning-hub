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

AI 智能体正越来越多地部署在复杂、领域特定的工作流上——它们需要导航需要数十次点击和表单填写的企业级 Web 应用、编排跨越搜索—提取—综合的多步骤研究管线、自动化对不熟悉代码仓库的代码审查，以及处理需要细致领域知识的客户升级请求。每一个新的任务领域都需要费力且依赖专家经验的 harness 工程：设计让基础模型有效运行的 prompt、工具、编排逻辑和评估标准。我们提出一个**双层框架**来自动化这一过程。

在第一层，**Harness 进化循环（Harness Evolution Loop）** 为单个任务优化 Worker Agent 的 harness H：Worker Agent W_H 执行任务，Evaluator Agent V 以对抗方式诊断失败并评分性能，Evolution Agent E 基于完整的历史尝试记录修改 harness。

在第二层，**元进化循环（Meta-Evolution Loop）** 跨不同的任务优化进化协议 Λ = (W_H, H^(0), V, E) 本身，学习一个最优协议 Λ^best，使得在任何新任务上都能快速收敛 harness——这样将智能体适配到新领域完全不需要人工 harness 工程。我们将该框架形式化为元学习的对应结构，并给出了两个算法。该框架将**人工 harness 工程**转变为**自动化 harness 工程**，并更进一步——**自动化了自动化本身的设计**。



## 图表资源

- ![](assets/assets)
- ![](assets/page-002-img-01.png)



---

## 中文翻译

我们提出了 **Harness 进化循环**，一种闭环架构，通过重复的任务执行、对抗性评估和代码修改，自动优化 AI Agent 的 harness H——即围绕基础模型的 prompt、工具、编排逻辑和基础设施。该系统将 Agent 形式化为 W_H，将评估（V）与进化（E）分离，并在跟踪完整收敛历史的同时迭代改进 H。

然后我们引入了 **元进化循环**，该循环跨不同的任务优化进化协议 Λ = (W_H, H^(0), V, E) 本身。通过在每个训练任务 tᵢ ∈ T_train 上运行内层的 harness 进化循环并衡量收敛，元进化 Agent E_meta 学习一个协议 Λ^best，使其能够快速适应未见过的任务。这个双层形式化镜像了元学习：内循环将 harness 适应到单个任务，而外循环则优化适应过程的泛化能力。

在传统上，harness 工程需要针对每个特定任务领域投入深入的**人类专家经验**。Harness 进化循环将此过程完全自动化——将**人工 harness 工程转变为自动化 harness 工程**。而元进化循环更进一步：它**自动化了自动化本身的设计**——学习如何进化 harness，而不是进化任何一个单一的 harness。

[扩展] 结论的升华非常漂亮：第一层自动化解决了"怎么做"的问题，第二层元自动化解决了"怎么自动地做"的问题，本质上是在学习"学习如何设计 Agent"。

我们计划在后续工作中提供跨多个多样化工作流的实证结果——这些工作流即使使用最先进的 Agent 和 harness 也难以轻易自动化——从复杂的定制化客户工作流到领域特定的企业流程。目的是证明该框架可以打开那些之前被认为对自主 Agent 来说过于脆弱或过于专业化的任务类别。最终，我们将发布一个基于学习到的进化协议 Λ^best 的产品：一个系统，任何用户都可以将一个通用 Agent 指向一个新的任务领域，它就会自动**进化成一个专门的、高性能的 Agent**——不需要任何 harness 工程专业知识。

[扩展] 最后一段为该框架描绘了一个宏大的愿景：一个"即插即用"的 Agent 产品。用户不需要理解任何 harness 工程，只需要告诉 Agent"去干这个"，它就能自动调优自己。这就像把"训练一个专家"的过程自动化了。

### 术语解释
- **自动化自动化（Automating the automation）**：元进化的本质——不仅自动化任务执行，还自动化任务自动化的设计过程
- **收敛历史（Convergence History）**：每次迭代的 (harness 版本, 评估报告, 得分, 判定) 的完整记录
- **通用 Agent vs. 专门 Agent**：通用 Agent 能处理广泛但表面的任务；专门 Agent 通过调优 harness 在特定领域达到高精度

### 图表/公式说明
本片段无图表/公式。

### 关键 takeaway
- 本文提出了**两个层次的自动化**：自动化 harness 工程（第一层）和自动化 harness 工程过程的设计（第二层）
- 核心贡献是一个**理论框架**（双层进化 + 元学习形式化）和**两个算法**（Algorithm 1 & 2）
- 实证结果尚未发表（TODO），但计划在多样化复杂工作流上验证
- 最终愿景是一个**零配置的 Agent 产品**——用户只需描述任务，系统自动进化出高性能的专门 Agent
- **对 Hermes/青青 的启示**：这篇论文的方法论可以直接应用于物流预测 Agent 的自动调优——对于每个新场地（如 755W、021WJ），自动进化出最优的预测 prompt 和工具配置，而无需人工为每个场地编写不同的 Skill

## 复核建议

- 当前未发现明显的解析降级信号，仍建议抽样检查图表和公式。

## 参考文献

- 特别关注 Algorithm 1 和 Algorithm 2 的伪代码在站点渲染中的可读性。
