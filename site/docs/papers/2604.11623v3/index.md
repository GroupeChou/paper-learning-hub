# Context Kubernetes：面向Agentic AI系统的企业知识声明式编排

## Context Kubernetes: Declarative Orchestration of Enterprise Knowledge for Agentic AI Systems

Charafeddine Mouzouni

OPIT（开放理工学院）& Cohorte AI，法国巴黎

---

## 摘要

**每个计算时代都会产生一个主导原语和一个扩展危机。虚拟机需要VMware。容器需要Kubernetes。AI智能体需要一个尚不存在的东西：组织知识的编排层。**

我们提出 **Context Kubernetes**，一个在Agentic AI系统中编排企业知识的架构，包含原型实现和实验评估。核心观察：在**整个组织**中向正确的智能体、以正确的权限、在正确的新鲜度、在正确的成本范围内交付正确的知识——在结构上类似于Kubernetes十年前解决的容器编排问题。

我们将这一类比发展为：
- **6个核心抽象**
- **基于YAML的声明式清单**（知识架构即代码）
- **协调循环**
- **三层智能体权限模型**（智能体权限严格是人工权限的子集）

**实验：** 92个自动化测试，8个实验，TLA+模型检查覆盖**460万可达状态**零违规。

---

## 1 核心抽象

| 抽象 | 对应K8s概念 | 功能 |
|------|-----------|------|
| **ContextPod** | Pod | 最小知识交付单元 |
| **ContextDeployment** | Deployment | 知识部署的声明式规范 |
| **ContextService** | Service | 知识检索的服务发现 |
| **ContextNamespace** | Namespace | 组织/团队级知识隔离 |
| **ContextPolicy** | NetworkPolicy | 访问控制策略 |
| **ContextVolume** | Volume | 持久知识存储 |

### 声明式清单（YAML）

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

---

## 2 权限模型

| 模型 | 阻止攻击数(5种) |
|------|---------------|
| 平面权限（无控制） | 0/5 |
| 基本RBAC | 4/5 |
| **三层权限（本文）** | **5/5** ✅ |

**三层结构：**
1. **人工管理员**：最高权限，定义策略
2. **智能体角色**：严格子集权限，只能执行已授权的操作
3. **执行层**：执行时的最小权限原则

---

## 3 评估结果

| 实验 | 发现 |
|------|------|
| **治理对比实验**（200个基准查询） | 只有三层权限模型阻止所有5种攻击场景 |
| **新鲜度监控** | 协调循环在**<1ms**内检测到过期/已删除内容 |
| **攻击场景** | 平面权限：0/5, RBAC: 4/5, 三层: **5/5** |
| **正确性实验** (5个) | 零未授权上下文交付，零权限不变违规 |
| **TLA+模型检查** | 460万可达状态，**零违规** |

---

## 4 为什么上下文编排比容器编排更难

1. **异构性**：知识来源多样（wiki、数据库、文件、API）
2. **语义**：需要理解内容含义，不仅是包名
3. **敏感性**：知识有访问控制需求
4. **学习**：使用模式随时间演变

---

## 5 结论

Context Kubernetes 提出了一个完整的声明式架构，用于企业Agent系统的知识编排。**上下文工程（Context Engineering）将作为AI时代的基础设施学科出现。**

---

## 参考文献

- Mouzouni. Context Kubernetes. arXiv:2604.11623, 2026.
- Kubernetes. Borg, Omega, and Kubernetes. ACM Queue, 2016.
- TLA+. Lamport. Specifying Systems. 2002.
