# Context Kubernetes：面向 Agentic AI 系统的企业知识声明式编排

## Context Kubernetes: Declarative Orchestration of Enterprise Knowledge for Agentic AI Systems

Charafeddine Mouzouni

OPIT（开放理工学院）& Cohorte AI，法国巴黎

---

## 摘要

**每个计算时代都会产生一个主导原语和一个扩展危机。虚拟机需要VMware。容器需要Kubernetes。AI智能体需要一个尚不存在的东西：组织知识的编排层。**

我们提出 **Context Kubernetes**，一个在 Agentic AI 系统中编排企业知识的架构，包含原型实现和实验评估。

**核心观察：** 在整个组织中向正确的智能体、以正确的权限、在正确的新鲜度、在正确的成本范围内交付正确的知识——在结构上类似于 Kubernetes 十年前解决的**容器编排问题**。

我们将这一类比发展为：
- 6 个核心抽象（ContextPod、ContextDeployment、ContextService、ContextNamespace、ContextPolicy、ContextVolume）
- 基于 YAML 的声明式清单（知识架构即代码）
- 协调循环（Reconciliation Loop）
- 三层智能体权限模型（智能体权限严格是人工权限的子集）

**实验（92个自动化测试，8个实验）：**
1. **治理对比**（200个查询，4个基线）：只有三层权限模型阻止所有5种攻击场景
2. **新鲜度监控**：协调循环在 **<1ms** 内检测到过期/已删除内容
3. **攻击防御**：平面权限 0/5，基本RBAC 4/5，三层模型 **5/5**
4. **正确性验证**：零未授权上下文交付，零权限不变违规
5. **TLA+模型检查**：**460万可达状态，零违规**

**结论：** 上下文工程（Context Engineering）将作为 AI 时代的基础设施学科出现。

---

## 1 引言

每一代计算基础设施都遵循相同的弧线：新原始出现——虚拟机、容器、无服务器函数——先锋在单机上取得非凡成果——然后组织试图大规模部署时出现五个相同的问题：**调度、权限、健康监控、状态管理、可审计性**。这些问题不是通过改进原始本身解决，而是通过在其上构建**编排层**解决。

**AI 智能体是新的计算原始。** 配备本地智能体（Claude Code、Cursor、LangGraph 应用）指向本地组织良好的文件夹的知识工作者，可以用文件和对话取代其 SaaS 工具栈的重要部分。

**扩展危机已经开始。** 2026年1月至3月，应用软件行业近 **3000亿美元** 市值蒸发。从一台笔记本电脑上的一个智能体到组织中 2000 个智能体，立即暴露五个问题：

| 问题 | 类比 K8s |
|------|---------|
| 调度：哪些知识→哪个智能体→什么顺序 | Scheduler |
| 权限：智能体可读/写/执行什么？ | RBAC |
| 健康监控：知识是否是最新的？ | HealthCheck |
| 状态管理：知识如何版本化和治理？ | etcd |
| 可审计性：谁在何时通过哪个智能体访问了什么？ | Audit Log |

**Gartner 预测：** 到 2027 年，超过 40% 的 Agentic AI 项目将因治理不足而取消。技术在成熟，但**编排层缺失**。

---

## 2 核心抽象

### 2.1 六个核心抽象

| 抽象 | K8s 类比 | 功能 |
|------|---------|------|
| **ContextPod** | Pod | 最小知识交付单元（一组相关的知识源） |
| **ContextDeployment** | Deployment | 知识部署的声明式规范（来源、新鲜度、权限） |
| **ContextService** | Service | 知识检索的服务发现 |
| **ContextNamespace** | Namespace | 组织/团队级知识隔离（财务、工程、HR等） |
| **ContextPolicy** | NetworkPolicy | 访问控制策略（谁可以访问什么知识） |
| **ContextVolume** | Volume | 持久知识存储（数据库、知识库、文件系统） |

### 2.2 声明式清单（YAML）

```yaml
apiVersion: context.ai/v1
kind: ContextDeployment
metadata:
  name: logistics-forecast-kb
  namespace: logistics
spec:
  sources:
    - type: internal_wiki
      path: "forecast/2026/"
    - type: database
      query: "SELECT * FROM rules_engine"
  freshness:
    ttl: 1h
    reconciliation: true
  permissions:
    agents:
      - name: forecast-agent
        role: reader
    humans:
      - name: planner-team
        role: editor
```

### 2.3 协调循环

与 Kubernetes 的协调循环相同——期望状态与实际状态之间的持续比较：

```
期望状态（YAML声明）→ 观察实际 → 检测差异 → 执行操作 → 重复
```

ContextPod 的健康检查：知识是否过时？来源是否可达？是否有权限变更？

---

## 3 三层权限模型

**核心原则：智能体权限始终是人工权限的严格子集。**

| 层级 | 描述 | 示例 |
|------|------|------|
| **L1：人工管理员** | 最高权限，定义策略 | CISO、知识经理 |
| **L2：智能体角色** | 严格子集权限，只能执行已授权的操作 | 只读访问特定文件夹 |
| **L3：执行层** | 执行时的最小权限原则，无持久权限 | 临时令牌 |

**形式化证明：** ∀ Agent A, Agent.permissions ⊆ Owner.permissions，且 Agent.permissions 是静态声明的。

---

## 4 实验评估

### 4.1 实验设置

- 原型实现：92 个自动化测试
- 种子数据：200 个基准查询在合成数据上
- TLA+ 模型检查：4.6M 个可达状态

### 4.2 治理对比

**表 1：四种治理基线的对比**

| 治理模型 | 数据保护 | 新鲜度保证 | 攻击防御(5种) | 性能影响 |
|---------|---------|-----------|-------------|---------|
| 无治理 RAG | ❌ 无过滤 | ❌ 无 | 0/5 | 最低 |
| ACL 过滤 | ✅ 基本 | ❌ 无 | 2/5 | 低 |
| RBAC 路由 | ✅ 角色级 | ❌ 无 | 4/5 | 中 |
| **三层权限（本文）** | **✅ 完整** | **✅ 有** | **5/5** | 中 |

### 4.3 新鲜度监控

| 监控模式 | 过期内容检测时间 | 已删除内容处理 |
|---------|----------------|--------------|
| 无监控 | 不检测（静默服务） | 不检测 |
| **协调循环** | **<1ms** | ✅ 立即回收 |

### 4.4 攻击场景防御

| 攻击场景 | 平面权限 | 基本RBAC | **三层模型** |
|---------|---------|---------|------------|
| 跨角色数据访问 | ❌ 通过 | ❌ 通过 | **✅ 阻止** |
| 权限提升 | ❌ 通过 | ✅ 阻止 | **✅ 阻止** |
| 数据泄露越狱 | ❌ 通过 | ✅ 阻止 | **✅ 阻止** |
| 历史版本访问 | ❌ 通过 | ✅ 阻止 | **✅ 阻止** |
| 跨设备联合泄露 | ❌ 通过 | ❌ 通过 | **✅ 阻止** |
| **总计** | **0/5** | **4/5** | **5/5** |

RBAC 错过的攻击（跨设备联合泄露）正是三层模型专门设计来捕获的。

### 4.5 TLA+ 形式化验证

| 属性 | 状态空间 | 违规 |
|------|---------|------|
| 无未授权交付 | 4.6M | **0** ✅ |
| 权限不变式 | 4.6M | **0** ✅ |
| 带外批准隔离 | 4.6M | **0** ✅ |

---

## 5 为什么上下文编排比容器编排更难

| 属性 | 容器编排 | 上下文编排 |
|------|---------|-----------|
| **异构性** | 同质容器镜像 | 混合来源：wiki、数据库、API、邮件 |
| **语义** | 精确的包名/IP地址 | 需要理解内容含义 |
| **敏感性** | 大多数容器无敏感数据 | 知识含访问控制、PII、商业机密 |
| **学习** | 使用模式稳定 | 使用模式随时间演变 |

这些属性使上下文编排**更难但更有价值**。

---

## 6 结论

Context Kubernetes 提出了一个完整的声明式架构，用于企业 Agent 系统的知识编排。**上下文工程（Context Engineering）将作为 AI 时代的基础设施学科出现**。

**关键贡献：**
1. 与 Kubernetes 的完整结构类比（6 个抽象 + 声明式清单 + 协调循环）
2. 三层权限模型，形式化保证
3. TLA+ 验证 460 万状态零违规
4. 92 个自动化测试 + 8 个实验验证

---

## 参考文献

- Mouzouni. Context Kubernetes. arXiv:2604.11623, 2026.
- Kubernetes. Borg, Omega, and Kubernetes. ACM Queue, 2016.
- Lamport. Specifying Systems. 2002 (TLA+).
- Gartner. AI agents market projections. 2025.
- Anthropic. Claude Code. 2024.
- CNBC. Application software market value loss. 2026.
