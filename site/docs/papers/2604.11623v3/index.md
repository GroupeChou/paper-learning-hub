# Context Kubernetes：面向智能体AI系统的企业知识声明式编排

**Context Kubernetes: Declarative Orchestration of Enterprise Knowledge for Agentic AI Systems**

---

| 元信息 | 内容 |
|--------|------|
| **作者** | Charafeddine Mouzouni（OPIT – Open Institute of Technology & Cohorte AI, Paris） |
| **发表时间** | 2026年4月 |
| **arXiv ID** | 2604.11623v3 |
| **领域** | Agent基础设施 · 企业知识管理 · AI治理 · 编排架构 |
| **关键词** | Context Orchestration, Agentic AI Infrastructure, Declarative Architecture, Enterprise Knowledge Management, Kubernetes |

---

## 摘要（Abstract）

每个计算时代都会产生一个主导原语和一个扩展危机。虚拟机需要VMware。容器需要Kubernetes。AI智能体需要一种尚不存在的东西：**面向组织知识的编排层（orchestration layer）**。

我们介绍 **Context Kubernetes**——一个用于在智能体AI系统中编排企业知识的架构，包含原型实现和实验评估。

**核心观察**：在整个组织中，将正确的知识、以正确的权限、在正确的新鲜度、在正确的成本范围内传递给正确的Agent——这一问题的结构与Kubernetes十年前解决的容器编排问题**结构类似**。

### 主要贡献

1. **六大核心抽象** + YAML声明式知识架构即代码清单 + 协调循环（Reconciliation Loop）
2. **三层Agent权限模型**：Agent权限始终是人类权限的严格子集
3. **原型实现**（92个自动化测试）+ 八项实验评估

### 关键实验发现

| 实验类型 | 核心结论 |
|----------|----------|
| **治理基线对比（200条查询）** | 从无治理RAG → ACL过滤检索 → RBAC感知路由 → 完整架构，每层贡献不同能力；仅三层模型能阻止全部5种攻击场景 |
| **新鲜度监控** | 无监控时静默提供过时/已删内容；有协调循环时过时检测 < 1ms |
| **攻击场景测试（5种）** | 平坦权限0/5；基础RBAC 4/5；**三层模型5/5全部拦截**——RBAC遗漏的恰好是三层模型专门设计的捕获目标 |

### 正确性验证
- 零未授权上下文交付
- 零权限不变量违反
- 架构层面强制执行带外审批隔离（**无任何被调查的企业平台能做到**）
- TLA+模型检验在**460万个可达状态**上验证安全属性，零违反

> 💡 **核心论点**：Context Engineering将成为AI时代定义性的基础设施学科。

---

## 1 引言（Introduction）

> *"最深刻的技术是那些消失的技术。它们编织进日常生活的织物中，直到与之无法区分。"* —— Mark Weiser, 1991

### 1.1 编排涌现论（The Orchestration Emergence Thesis）

**每代计算基础设施都遵循相同的弧线：**
1. 一个新原语出现（虚拟机 → 容器 → Serverless函数）
2. 先驱者在单机上展示非凡效果
3. 组织尝试大规模部署 → 同样的**五个问题**浮现：
   - **调度（Scheduling）**：什么到达哪里，从哪个源，以什么顺序？
   - **权限（Permissions）**：谁可以读写执行？
   - **健康监控（Health Monitoring）**：状态是否当前、完整、正确？
   - **状态管理（State Management）**：如何版本化、治理和迁移？
   - **可审计性（Auditability）**：谁在何时通过哪个Agent做了什么？

这些问题不是通过改进原语来解决的，而是通过在其之上构建**编排层**来解决的：
- **VMware**编排了虚拟机
- **Kubernetes**编排了容器
- **编排层本身成为持久的基础设施**，而非原语

### 1.2 AI智能体是新原语

配备本地Agent的知识工作者（Claude Code、Cursor、LangGraph应用），只需指向笔记本电脑上的一个组织良好的文件夹，就能用文件和对话替代其SaaS工具栈的大部分功能。

**市场数据：**
- Gartner预测到2026年底，40%的企业应用将包含任务特定AI Agent [2025a]
- 全球AI Agent市场在2026年初已超过90亿美元 [Grand View Research, 2025]

**但扩展危机已经开始：**
- 2026年1月至3月间，应用软件行业市值蒸发近3000亿美元（CNBC, 2026）
- 原因：企业认识到AI Agent使大多数SaaS接口变得可选
- 从一台笔记本上的1个Agent → 跨组织2000个Agent → 立即暴露同样的五个问题

**Gartner预测**：到2027年，超过40%的Agentic AI项目因治理不足而被取消 [2025b]。技术已经成熟。**编排层缺失**。

---

## 2 背景与动机（Background and Motivation）

### 2.1 容器编排先例

Docker (2013) 标准化了容器作为可移植计算单元。OCI定义了镜像规范，使容器与运行时无关。但**在组织规模部署容器**产生了编排危机：

- 异构机器调度、服务发现、负载均衡、滚动更新、密钥管理、访问控制

**Kubernetes通过两个创新解决此危机（可推广为通用设计模式）：**

#### 创新一：声明式期望状态管理
操作员指定他们想要什么（"该服务3个副本，512MB内存，443端口可访问"），而非如何实现。规范编码为YAML清单，版本控制于git中，通过API应用到集群。

#### 创新二：协调循环（Reconciliation Loop）
持续控制环监控实际集群状态，将其与声明的期望状态比较，计算增量并采取纠正行动。系统在无人干预下收敛至声明状态。

> 📌 **这两个模式并非容器特有**——它们是管理任何计算原语在组织规模下的通用解法。本文将其应用于**组织知识**。

### 2.2 企业Agentic格局（截至2026 Q1）

| 平台 | 架构 | 锁定程度 |
|------|------|----------|
| Microsoft Copilot Studio | Semantic Kernel + Power Platform治理 + M365集成 | 高 |
| Salesforce Agentforce | Atlas引擎 + "System 2"推理 + 协作Swarm | 高 |
| Google Vertex AI + Agentspace | 云原生 + Gemini模型 + A2A协议贡献者 | 中高 |
| AWS Bedrock Agents | 100+基础模型 + ReAct循环 + 6种护栏类型 | 中 |
| NVIDIA AI Agent Platform | NIM微服务 + NeMo Guardrails + 基础设施层 | 中 |
| LangGraph (LangChain) | 基于图的状态机 + 人在回路 | 低 |
| CrewAI | 基于角色的Agent（任务+团队） | 低 |
| AutoGen (Microsoft) | 对话式多Agent + 事件驱动 | 低 |
| OpenAI Agents SDK | 轻量多Agent + 移交原语 | 低 |

**关键观察**：所有平台都实现了某种四层架构：(1) 推理引擎 → (2) 工具/动作层 → (3) 记忆/上下文层 → (4) **治理层**

**协议栈正在Linux Foundation的Agentic AI Foundation下收敛**：
- MCP（Anthropic, 2025）：Agent-to-Tool通信
- A2A（Google, 2025）：Agent-to-Agent通信

### ⚠️ 关键问题：治理层普遍是最弱、最标准化程度最低、最厂商锁定的层

- Copilot Studio的治理无法管辖LangGraph Agent
- Salesforce的Einstein Trust Layer无法审计Bedrock Agent
- 开源框架提供编排但没有治理
- **治理差距不是一个缺失的功能——它是一个缺失的基础设施层**

### 2.3 上下文编排的七项需求（基于NIST AI RMF）

| # | 需求 | NIST对应类别 |
|---|------|-------------|
| R2.1 | **厂商中立性**：必须兼容任意LLM、Agent框架、云提供商和数据源 | Govern 1.2 |
| R2.2 | **声明式管理**：知识架构可表达为机器可读、版本控制的规范 | Govern 1.5 |
| R2.3 | **Agent权限分离**：Agent权限必须正式与用户权限分离；Agent能力是用户能力的可配置严格子集 | Govern 1.7 |
| R2.4 | **上下文新鲜度**：持续监控所有知识的新鲜度，超过TTL时采取纠正措施 | Measure 2.6 |
| R2.5 | **基于意图的访问**：Agent按意图请求知识，非按位置 | Map 1.5 |
| R2.6 | **完整可审计性**：每次知识访问、每个动作、每个审批都不可变记录（归因+时间戳+结果） | Manage 4.2 |
| R2.7 | **组织智能**：从聚合Agent活动中积累跨组织知识，不跨权限边界暴露个体数据 | Manage 4.1 |

---

## 3 Context Kubernetes 架构（Architecture）

### 3.1 七大设计原则

| # | 原则 | 对应需求 |
|---|------|----------|
| P1 | **声明式优于命令式**：组织声明期望的知识架构，系统协调现实去匹配 | R2.2 |
| P2 | **基于意图的访问优于基于位置的访问**：Agent按语义意图请求知识，系统解析为源/权限/排序 | R2.5 |
| P3 | **治理作为基础而非事后补充**：权限、新鲜度监控、护栏、审计是结构组件，非可选模块 | R2.3/2.4/2.6 |
| P4 | **Agent权限严格为人类权限子集**：架构不变量——不存在Agent超越用户范围的机制 | R2.3 |
| P5 | **编排层自身具备智能**：路由层使用LLM辅助语义解析；Context Operators积累组织智能 | R2.5/2.7 |
| P6 | **厂商中立性**：每个组件由接口定义，非实现 | R2.1 |
| P7 | **隐私设计**：系统监控组织边界（知识请求/动作/审批），不监控个体 | — |

### 3.2 六大核心抽象

#### 定义 3.1：上下文单元（Context Unit）
组织知识的**最小可寻址元素**。

$$u = (c, \tau, m, v, e, \pi)$$

| 字段 | 说明 |
|------|------|
| $c$ | 内容 |
| $\tau \in$ {unstructured, structured, hybrid} | 类型 |
| $m$ | 元数据集（作者、时间戳、域、敏感度、实体、来源） |
| $v \in V$ | 版本标识符 |
| $e \in \mathbb{R}^d$ | 嵌入向量 |
| $\pi \subseteq \mathbb{R}$ | 授权访问此单元的角色集合 |

#### 定义 3.2：上下文域（Context Domain）
组织知识的**隔离边界**。

$$D = (N, S, A, F, \rho, O, G)$$

- 域内查询对域外不可见，除非通过目标域Operator显式中转
- 类似Kubernetes中的Namespace隔离

#### 定义 3.3：上下文存储（Context Store）
持久化Context Unit的后端系统：$s = (\sigma, \iota, \phi)$
- Git仓库 / 关系数据库 / 外部系统连接器 / 文件系统
- 仅通过 **CxRI**（Context Runtime Interface）访问

#### 定义 3.4：上下文端点（Context Endpoint）
稳定的、**基于意图的**知识访问接口：
$$\varepsilon(q, \omega, \alpha) \rightarrow \{u_1, ..., u_k\} \subseteq U$$
- Agent**从不**指定知识在哪里——只说明需要什么
- 约束条件：权限检查、新鲜度检查、Token预算限制

#### 定义 3.5：上下文运行时接口（CxRI）
编排层与存储之间的标准适配器（类比Kubernetes的CRI）。六项操作：

```
connect(φ) → Connection        -- 连接
query(conn, q) → {u₁...uₙ}    -- 查询
read(conn, path) → u           -- 读取
write(conn, path, c) → Result  -- 写入
subscribe(conn, path) → Stream  -- 订阅
health(conn) → Status          -- 健康检查
```

#### 定义 3.6：上下文算子（Context Operator）
**领域特定的自治控制器**（类比Kubernetes Operators）：
$$O = (K, L, I, \Gamma)$$

| 组件 | 功能 |
|------|------|
| $K$ | 知识库（向量索引 + 全文索引） |
| $L$ | 推理引擎（LLM + 领域护栏） |
| $I$ | **组织智能模块**：从聚合Agent活动提取跨组织模式 |
| $\Gamma$ | 护栏集 |

**组织智能模块I的约束：**
- 最小信号阈值 θ ≥ 3（防止过早模式识别）
- 时间聚类窗口 Δtw
- 权限标签化（聚合洞察对域成员可用；归因洞察需记录级授权）
- 衰减机制（无支持信号则洞察退化）

### 3.3 系统架构总览

```
┌─────────────────────────────────────────────────────────────┐
│                        AGENTS                                │
│   Local Agent(Claude Code) │ LangGraph App │ Custom Agent    │
│                            │               │                  │
│                     Context API (10 endpoints)                │
│                   HTTPS + WSS + JWT                           │
├─────────────────────────────────────────────────────────────┤
│                    CONTEXT KUBERNETES                         │
│  ┌───────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐  │
│  │  Context  │ │  Context │ │Permission│ │ Freshness     │  │
│  │ Registry  │ │  Router  │ │ Engine   │ │ Manager      │  │
│  │(etcd类比) │ │(调度+入口)│ │(三层权限) │ │(fresh/stale/ │  │
│  └───────────┘ └──────────┘ └──────────┘ │expired/conf.)│  │
│  ┌──────────────────┐ ┌──────────────┐ ┌──────────────┐  │
│  │Trust Policy Engine│ │ Context      │ │ LLM Gateway  │  │
│  │(护栏/DLP/审计日志)│ │ Operators    │ │(提示检查/计费)│  │
│  └──────────────────┘ └──────────────┘ └──────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Reconciliation Loop                      │  │
│  │         ⟨desired state ⟷Δ⟷ actual state⟩              │  │
│  └──────────────────────────────────────────────────────┘  │
│  ══════════════ Context Runtime Interface (CxRI) ═════════  │
│                    — 6 ops per connector —                 │
├─────────────────────────────────────────────────────────────┤
│                    CONTEXT SOURCES                          │
│  Git Repos │ Databases │ Email/Calendar │ SaaS APIs │ ERP  │
└─────────────────────────────────────────────────────────────┘
```

### 3.4 三层Agent权限模型

#### 设计不变量 3.7：Agent权限子集
对于拥有权限集 $P_u$ 的用户 $u$ 及代表 $u$ 行事的Agent $a_u$：
$$P_{a_u} \subset P_u$$

**包含关系是严格的**：对于每个用户，存在至少一个用户可执行但Agent不可执行的操作。对于共享操作，所需的批准层级满足 $T(o, a_u) \geq T(o, u)$。

#### 三层批准模型

| 层级 | Agent角色 | 批准机制 | 示例 |
|------|-----------|----------|------|
| **T1: 自主** | 自由行动 | 无 | 读取上下文、起草文档 |
| **T2: 软批准** | 提议 | 用户在Agent UI中确认 | 发送内部消息 |
| **T3: 强批准** | 浮现任务 | **带外2FA/生物识别** | 签署合同、财务操作 |
| **排除** | 不能请求 | N/A（仅人工） | 终止员工 |

#### 设计不变量 3.8：强批准隔离（Strong Approval Isolation）

对于任何T3动作，批准通道C满足：
1. C 在Agent的**执行环境外部**
2. C 对Agent**既不可读也不可写**
3. C 需要**独立的认证因子**

**平台审批隔离调查结果（表3）**：调查了四大企业Agentic平台的安全架构，**没有一个平台在架构层面强制执行全部三个条件**。

| 平台 | HITL机制 | C1: 外部 | C2: 不可读写 | C3: 独立因子 |
|------|----------|----------|-------------|-------------|
| MS Copilot Studio | Outlook邮件请求信息 | 部分 | ❌ 否 | ❌ 否 |
| SF Agentforce | Einstein Trust Layer | ❌ 否 | ❌ 否 | ❌ 否 |
| Google Agentspace | Workspace通知 | 部分 | ❌ 否 | ❌ 否 |
| AWS Bedrock | SSO + Lambda触发 | ❌ 否 | ❌ 否 | ❌ 否 |

> 🔴 **关键发现**：所有平台都提供"人在回路"机制，但**没有一家**在架构上强制执行强批准隔离的三项条件。

---

## 4 声明式上下文管理（Declarative Context Management）

（略：YAML清单规范、协调循环详细设计）

**核心思想**：运维人员编写声明式YAML描述期望的知识拓扑（哪些域、哪些源、哪些权限规则、哪些新鲜度策略），系统通过协调循环持续将实际状态收敛至期望状态——完全类比Kubernetes的工作方式。

---

## 5 与Kubernetes的结构类比（Structural Analogy to Kubernetes）

| Kubernetes概念 | Context Kubernetes对应 | 映射紧密度 |
|----------------|----------------------|-----------|
| Pod（最小调度单元） | **Context Unit**（最小知识单元） | 紧 |
| Namespace（隔离边界） | **Context Domain**（域隔离） | 紧 |
| Container Runtime Interface | **CxRI**（运行时接口） | 紧 |
| Operator（领域控制器） | **Context Operator** | 紧 |
| etcd（元数据存储） | **Context Registry** | 中 |
| kube-scheduler（调度器） | **Context Router** | 松 |
| Service Account/RBAC | **三层Agent权限模型** | 松（新增维度） |
| Pod Disruption Budget | **Freshness Policy** | 新增概念 |

### 使上下文编排比容器编排更难的四大属性

| 属性 | 说明 | 为何增加价值 |
|------|------|-------------|
| **异质性（Heterogeneity）** | 知识类型远比容器类型多样（结构化/非结构化/混合/流式/实时） | 解决方案更具通用性 |
| **语义（Semantics）** | 知识具有内在含义，需要语义路由和理解 | 需要LLM辅助推理 |
| **敏感性（Sensitivity）** | 数据敏感度差异巨大（公开 vs 绝密） | 需要细粒度权限控制 |
| **学习（Learning）** | 知识使用方式会随时间演变，系统需自适应 | 需要组织智能模块 |

---

## 6 原型实现（Prototype Implementation）

- 92个自动化测试（含对抗性不变量违规测试）
- 核心组件：Context Router、Permission Engine、CxRI连接器、协调循环、审计日志、FastAPI HTTP服务
- 代码开源

---

## 7 实验评估（Experimental Evaluation）

### 7.1 五项正确性实验

| 实验 | 结果 |
|------|------|
| 未授权上下文交付 | **零次** |
| 权限不变量违反 | **零次** |
| 过时检测延迟 | **< 1ms** |
| 可接受延迟开销 | 符合生产要求 |
| 批准隔离架构执行 | 通过（无平台能做到） |
| TLA+模型检验 | **460万可达状态，零违反** ✅ |

### 7.2 三项价值实验

**实验一：治理基线对比（200条合成种子数据查询）**

| 治理层级 | 能力 | 攻击拦截数 |
|----------|------|-----------|
| 无治理RAG | 仅检索 | 0/5 |
| ACL过滤检索 | 基础权限过滤 | 2/5 |
| RBAC感知路由 | 角色感知路由 | 4/5 |
| **完整架构（三层模型）** | 全部能力 | **5/5** ✅ |

**实验二：无新鲜度监控 vs 有协调循环**
- 无监控：静默提供过时和已删除内容
- 有协调循环：**< 1ms** 内检测到过时

**实验三：五种真实攻击场景**

| 权限模型 | 拦截攻击数 | 备注 |
|----------|-----------|------|
| 平坦权限（无分层） | **0/5** | 完全无效 |
| 基础RBAC | **4/5** | 遗漏1种攻击 |
| **三层模型** | **5/5** ✅ | 全部拦截；RBAC遗漏的恰好是其专门设计的目标 |

---

## 8 相关工作（Related Work）

（略：涵盖企业AI平台、知识图谱、RAG治理、Agent安全等方向的相关工作综述）

---

## 9 局限性与开放问题（Limitations and Open Problems）

### 已知局限
1. 原型非生产级别
2. 尚无LLM辅助路由实现
3. 未在真实组织部署
4. 组织智能模块的治理含义需进一步研究
5. Alloy形式化验证待完成

### 开放问题
1. **编排层自身的推理风险**：如果编排层使用LLM进行语义解析，LLM本身的偏见/幻觉如何缓解？
2. **跨域知识流转**：如何在保证隔离的前提下允许受控的知识共享？
3. **性能规模化**：当Context Unit数量达到百万级时的性能优化策略
4. **动态权限调整**：如何根据Agent行为历史自动调整权限范围？

---

## 10 结论（Conclusion）

Context Kubernetes提出了AI时代的**编排层**愿景：

1. **VMware证明了虚拟机的编排价值 > 虚拟机自身**
2. **Kubernetes证明了容器的编排价值 > 容器自身**
3. **Context Engineering将成为AI Agent上下文的编排层，其价值将超越任何单一LLM、Agent框架或数据源**

LLM将被替换。框架会演进。**编排层持久存在。**

> 📌 **最终断言**：Context Engineering will emerge as the defining infrastructure discipline of the AI era.

---

## 附录：快速参考

### 架构速查卡

```
Context Kubernetes = 6大抽象 + 7大原则 + 3层权限 + 协调循环
                    ↓
         YAML声明式知识架构即代码
                    ↓
         TLA+验证的安全属性（460万状态零违反）
                    ↓
         解决Agent规模化的五大问题：
         调度 | 权限 | 健康 | 状态 | 审计
```

### 与现有方案的差异化优势

| 维度 | 现有方案 | Context Kubernetes |
|------|----------|--------------------|
| 治理深度 | 事后附加 | 架构内置（设计不变量） |
| 权限粒度 | 用户级RBAC | Agent三级权限（严格子集） |
| 强审批隔离 | ❌ 无平台做到 | ✅ 架构强制（C1+C2+C3） |
| 新鲜度保证 | 手动/无 | 自动协调循环 (<1ms) |
| 厂商中立性 | 各自锁定 | 接口标准化（CxRI） |
