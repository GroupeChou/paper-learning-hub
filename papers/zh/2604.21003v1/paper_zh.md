# 你最后需要构建的 Harness

## The Last Harness You'll Ever Build

**技术报告**

Haebin Seong, Li Yin, Haoran Zhang

Sylph.AI

---

## 摘要

AI 智能体越来越多地部署在复杂、领域特定的工作流上——导航需要数十次点击和表单填写的企业 Web 应用、编排跨搜索/提取/合成的多步骤研究流水线、自动化不熟悉仓库的代码审查、以及处理需要细微领域知识的客户升级。

每个新任务域都需要**艰苦的、专家驱动的 Harness 工程**：设计提示、工具、编排逻辑和评估标准，使基础模型变得有效。我们提出一个**双层框架**自动化此过程：

**第一层：Harness 进化循环**——为单个任务优化工人智能体的 Harness H：
- **工人智能体 W_H**：执行任务并生成执行轨迹
- **评估智能体 V**：对抗性地验证、诊断失败模式并评分
- **进化智能体 E**：基于完整的进化历史修改 Harness（提示、工具、编排逻辑、观察）

**第二层：元进化循环**——跨不同任务优化进化协议 Λ = (W_H, H(0), V, E) 本身，学习协议 Λ(best)，使 Harness 在任何新任务上快速收敛。

该框架将**手动 Harness 工程**转变为**自动 Harness 工程**，并更进一步——**自动化自动化本身的设���**。

---

## 1 引言

近期 Harness 工程的工作表明，精心设计的脚手架（执行环境、反馈循环、评估标准和上下文管理）可以显著放大智能体的能力。Lopopolo (2026) 描述了构建自定义 linter、仓库级可观测性栈（日志、指标、追踪）、Chrome DevTools 集成和结构化文档层次——全部手工制作以使代码库对智能体可读。Rajasekaran (2026) 报告了多轮评估者提示校准的迭代。

在这两种情况下，Harness 需要深入的领域专业知识来构建和大量的迭代来调优。虽然自动提示优化方法（如 LLM-AutoDiff）可以调优单个组件，但它们不处理完整的 Harness——工具、编排逻辑、基础设施及它们的交互。

---

## 2 Harness 进化循环

### 2.1 定义 Agent Harness

**原始模型不是智能体。** 遵循 Trivedy (2026) 的公式：

```
Agent = Model + Harness
```

Harness 是除模型本身外的每段代码、配置和执行逻辑——它是使模型智能变得有用的系统。

**Harness 组件分类：**

| 组件 | 描述 | 示例 |
|------|------|------|
| **系统提示与任务提示** | 定义身份和约束的指令 | 系统级提示、目标描述、上下文示例 |
| **工具、技能及其描述** | 智能体调用以作用于环境的能力 | 文件编辑、Shell执行、UI交互、Web搜索、MCP服务器 |
| **捆绑基础设施** | 提供给智能体的执行环境 | 文件系统、沙箱、浏览器、可观测性栈 |
| **编排逻辑** | 结构化智能体交互循环的控制流 | 子智能体生成、交接、模型路由、反馈循环 |
| **Hook 与中间件** | 确定性执行保证 | 压缩、续写检查、验证循环 |
| **模型配置** | 底层模型选择与推理参数 | 温度、采样策略、令牌限制、路由规则 |

**生态系统中的 Harness：** AdaL、Claude Code、Codex 是通用软件工程的 Harness；OpAgent 是自主 Web 导航的 Harness。在每种情况下，Harness——而非模型——决定了智能体能感知什么、如何行动、以及工作如何编排和验证。

### 2.2 任务定义

任务 t = (I, S) 包含：
- **指令 I**：工人智能体的具体目标
- **成功标准 S = {s₁, ..., s_m}**：评估者用来判断完成度的可验证条件清单

### 2.3 工人智能体

工人智能体 W_H 是由 Harness H 参数化的被优化智能体。接口：W_H.execute(t)

基于 Harness 的智能体（AdaL、Claude Code、Codex、OpAgent）都可设置为工人智能体 W_H。

### 2.4 评估智能体

评估智能体 V 是一个独立的、对抗性审查者。接口：V.evaluate(τ, t) → (report, score)

四个功能：
1. **状态验证**：将工作���在 τ 中的观察与实际环境状态交叉引用
2. **标准检查**：对照每个成功标准 s_i 评估最终状态
3. **性能审计**：分解总执行时间为 LLM 时间（模型推理延迟） vs 工具时间（环境交互延迟）
4. **评分**：两级指标——先按通过/失败，再按执行时间作为平局决胜

### 2.5 进化智能体

进化智能体 E 是系统的进化驱动力。接口：E.evolve(history, H(best)) → H'

三种功能：
1. **聚合诊断**：读取完整进化历史，避免重复无效策略
2. **识别失败模式**：将失败分类为重复类别（工具使用错误、推理循环、环境误读、过度延迟）
3. **修改 Harness**：根据诊断编辑工人 Harness 的每段代码和配置

### 算法 1：Harness 进化循环

```
输入：任务 t, 工人智能体 WH, 初始 Harness H(0), 
      评估智能体 V, 进化智能体 E, 迭代次数 K
输出：最优 Harness H(best), 最优分数, 历史

H(best) ← H(0); best_score ← -∞
history ← []

for k = 1 to K do:
    trace ← WH(k-1).execute(t)          // 工人执行任务
    (report, score) ← V.evaluate(trace, t)  // 评估
    if score > best_score then
        verdict ← IMPROVED; H(best) ← H(k-1)
    else
        verdict ← REGRESSED
    history ← history ∪ {(H(k-1), report, score, verdict)}
    H(k) ← E.evolve(history, H(best))
return H(best), best_score, history
```

---

## 3 元进化：学会进化 Harness

### 3.1 Harness 进化循环本身也是一个 Harness

Harness 进化循环本身——评估者提示、进化智能体的诊断策略、评分函数、观察结构和编排逻辑——也是一个 Harness，记作 Λ：

Λ = (W_H, H(0), V, E)

Λ 具有与任何其他 Harness 相同的结构：提示、工具、观察和编排逻辑。优化 Λ 是在更高抽象层级上的 Harness 优化。

**Λ 的可修改组件：**
- 评估智能体提示
- 进化智能体提示
- 工人观察结构
- 评估者/进化者观察
- 评分函数设计
- 循环超参数

### 3.2 元学习形式化

| 元学习 | 元进化 |
|--------|--------|
| 参数: θ | Harness: H |
| 适应过程: (θ(0), optimizer, loss) | 进化协议: Λ = (WH, H(0), V, E) |
| 内循环: 在任务 t_i 上梯度更新 | 内循环: HARNESSEVOLUTIONLOOP(t_i, Λ, K) |
| 外循环: 元梯度更新 | 外循环: E_meta.evolve(meta history, Λ(best)) |
| 元训练任务 | 训练任务 T_train |
| 元测试任务 | 保留任务 T_test |

**外循环目标：**
$$\Lambda^{(best)} = \arg\max_\Lambda \mathbb{E}_{t_i \sim T_{train}}[\text{best\_score}(\text{HARNESSEVOLUTIONLOOP}(t_i, \Lambda, K))]$$

### 算法 2：元进化循环

```
输入：元训练任务 Ttrain, 元进化智能体 Emeta, 
      初始协议 Λ(0), 内循环预算 K
输出：最优协议 Λ(best)

Λ(best) ← Λ(0); best_meta_score ← -∞

for j = 0, 1, 2, ... do:
    for each task t_i in Ttrain do:
        H(best)_i, score_i ← HarnessEvolutionLoop(t_i, Λ(j), K)
    
    meta_score ← Aggregate({score_i})
    if meta_score > best_meta_score then:
        Λ(best) ← Λ(j)
    Λ(j+1) ← Emeta.evolve(meta_history, Λ(best))
return Λ(best)
```

### 3.3 评估协议

在新任务 T_test 上评估泛化能力。关键指标：
- **收敛速度**：达到目标性能阈值所需的内循环迭代次数
- **最终性能**：固定迭代次数后的任务通过率
- **鲁棒性**：不同元测试任务间收敛速度的方差

---

## 4 结论

我们提出了 **Harness 进化循环**，一个通过重复任务执行、对抗性评估和代码修改来自动优化 AI 智能体 Harness 的闭环架构。

然后引入**元进化循环**，优化进化协议 Λ 本身，使其学会如何进化 Harness 而非仅进化单个 Harness。

**关键意义：** 曾经需要深厚的领域专业知识（应用于每个特定任务域）的 Harness 工程，现在被完全自动化了。元进化循环更进一步——自动化了自动化本身的设计。

未来工作：在经典型难以自动化的复杂工作流上进行实证验证。最终将发布基于学习到的进化协议 Λ(best) 的产品——用户可以将通用智能体指向新任务域，它自动进化为专门的、高性能的智能体——**无需 Harness 工程专业知识**。

---

## 参考文献

- Anthropic. Claude code best practices. 2025.
- Guo et al. OpAgent for web navigation. arXiv:2602.13559, 2026.
- Lopopolo. Harness engineering. OpenAI Engineering Blog, 2026.
- OpenAI. Introducing Codex. 2025.
- Rajasekaran. Harness design for long-running app development. Anthropic Engineering Blog, 2026.
- SylphAI. AdaL: The self-evolving AI coding agent. 2026.
- Thrun & Pratt. Learning to Learn. Springer, 1998.
- Trivedy. The anatomy of an agent harness. LangChain Blog, 2026.
- Yin & Wang. LLM-AutoDiff. 2025.
- Zhou et al. WebArena. ICLR 2024.
