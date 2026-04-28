# 第五章：多智能体协作篇

> **学习目标**：掌握多 Agent 系统的协作机制与通信模式。

---

## 📋 本章大纲

### 5.1 协作框架

| 论文 | 机构 | 年份 | 主题 | 状态 |
|------|------|------|------|------|
| **CAMEL** | Cambridge | 2023 | 通信Agent"角色扮演"协作 | 🔄 待收录 |
| **AutoGen** | Microsoft | 2023 | 多Agent对话框架 | 🔄 待收录 |
| **ChatDev** | USTC | 2023 | 虚拟软件公司 | 🔄 待收录 |
| **MetaGPT** | DeepWisdom | 2023 | 元编程多Agent | 🔄 待收录 |

### 5.2 本库已收录相关论文

| 论文 | 机构 | 日期 | 核心内容 | 入口 |
|------|------|------|---------|------|
| **Agentic Aggregation for Parallel Scaling of Long-Horizon Agentic Tasks** | 智谱 | 2026-04-13 | 并行Agent任务的聚合缩放 | [原文](https://arxiv.org/pdf/2604.11753v1) |
| **Learning to Evolve via Textual Parameter Graph Optimization** | Meta FAIR | 2026-04-22 | 多Agent自进化框架 | [原文](https://arxiv.org/pdf/2604.20714v1) |
| **Strategic Heterogeneous Multi-Agent Architecture** | DeepSeek | 2026-04-23 | 异构多Agent代码漏洞检测 | [原文](https://arxiv.org/pdf/2604.21282v1) |
| **FairQE: Multi-Agent Gender Bias Mitigation** | Meta FAIR | 2026-04-23 | 多Agent翻译质量评估 | [原文](https://arxiv.org/pdf/2604.21420v1) |
| **M2-PALE: Explaining Multi-Agent MCTS-Minimax Hybrids** | MiniMax | 2026-04-16 | 多Agent博弈论解释 | [原文](https://arxiv.org/pdf/2604.14687v1) |

---

## 💡 多Agent核心问题

1. **通信协议**：Agent之间如何交换信息？
2. **任务分配**：如何把大任务拆分给不同专长的Agent？
3. **冲突解决**：多个Agent意见不一致怎么办？
4. **资源调度**：多个并发Agent如何共享有限资源？（→ 参考第七章 **HiveMind**）
