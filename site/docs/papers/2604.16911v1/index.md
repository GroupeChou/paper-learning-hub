# Skilldex：具有分层作用域分布的智能体技能包管理器与注册中心

## Skilldex: A Package Manager and Registry for Agent Skill Packages with Hierarchical Scope-Based Distribution

Sampriti Saha, Pranav Hemanth

Pandemonium Research

---

## 摘要

大语言模型（LLM）智能体越来越多地通过**技能包**（结构化自然语言指令包）在运行时进行扩展。社区安装工具和注册中心存在，但两个关键差距持续存在：

1. **无符合性信号**：没有公开工具根据 Anthropic 发布的格式规范对技能包进行评分
2. **无技能集一致性机制**：没有机制将相关技能与其所需的共享上下文捆绑以保持互一致性

我们提出 **Skilldex**，一个智能体技能包的包管理器与注册中心，解决了上述两个差距。

**两个新颖贡献：**
1. **编译器风格格式符合性评分**：针对 Anthropic 技能规范，产生 0-100 分评分，含行级诊断（描述特异性、前置元数据有效性、结构遵守性）
2. **技能集（Skillset）抽象**：相关技能的捆绑集合，附共享资产（词汇文件、模板、参考文档），强制跨技能行为一致性

**支持性基础设施：**
- **三层分层作用域系统**：全局/共享/项目
- **人在环路建议循环**：Agent 开始工作前展示建议技能清单供审查
- **仅元数据社区注册中心**：含符合性评分、全文搜索、信任层级
- **MCP 服务器**：将所有操作原生暴露给智能体

系统使用 TypeScript CLI（skillpm/spm）实现，后端为 Hono/Supabase 注册中心，开源发布。

---

## I. 引言

LLM 驱动的智能体越来越多地通过技能进行扩展——结构化自然语言文档，指导智能体采用特定行为。由 Anthropic 的 Claude Code 平台推广，技能形式化为 **SKILL.md 文件**（带 YAML frontmatter 的 Markdown）。

技能包类似于软件库：封装可复用功能、有作者和版本、质量参差不齐、在可发现和可共享时价值最大。安装工具和社区注册中心已经存在，但：

**两个关键差距的详细说明：**
1. **无符合性评分**：现有工具展示安装计数和发布者徽章，但没有一个工具根据 Anthropic 格式规范给技能评分。描述过短无法可靠触发，或 frontmatter 格式错误的技能，与格式正确的技能被同样对待
2. **无技能集机制**：技能作为平面单元单独安装。没有抽象用于捆绑相关技能及其所需的共享约定文件和参考文档——独立安装相关技能使每个技能使用自己的隐式词汇，可能逐步偏离

---

## II. 背景与相关工作

### A. Agent 技能包

SKILL.md 格式由 Anthropic 的 Claude Code 平台引入。技能是一个目录，包含标准化的 YAML frontmatter 区块后接 Markdown 内容：

```yaml
---
name: forensics-memory-analysis
description: "Guides Claude through systematic memory dump analysis..."
version: "1.0.0"
tags: [forensics, memory, volatility, incident-response]
author: "skilly"
spec_version: "1.0"
---
```

技能目录可选包含：scripts/（可执行辅助脚本）、references/（补充文档）、assets/（图像和数据文件）。

### B. 与相关系统的对比

| 系统 | 定位 | 与 Skilldex 的差异 |
|------|------|-------------------|
| **Smithery.ai / Glama.ai** | MCP 服务器注册中心 | 不同抽象层（MCP 暴露工具 vs 技能扩展行为） |
| **LangChain Hub** | LangChain 提示和链注册中心 | 不同生态系统和抽象层 |
| **Anthropic 技能目录** | 官方技能仓库 | 无 CLI 安装工具、无作用域模型 |
| **vercel-labs/skills** | 开放 Agent 技能 CLI | 无分层作用域安装、无符合性评分 |
| **CCPM / ClawdHub** | 技能安装工具 | 无评分规则或无技能集抽象 |

---

## III. 系统架构

Skilldex 由三个独立组件构成：

1. **Skilldex CLI**（skilldex-cli）：Node.js 20+ npm 包，提供 `skillpm` 和 `spm` 命令。TypeScript + Commander + simple-git + Zod
2. **Skilldex 注册中心**（skilldex-registry）：Hono Web 应用部署在 Vercel，后端 Supabase（PostgreSQL）。存储技能和技能集元数据；处理认证、搜索和安装计数
3. **Skilldex Web**：Next.js 应用，提供注册中心浏览器 UI 和文档站点

CLI 和 MCP 服务器共享相同的核心模块，两个接口调用相同的安装、验证、解析和清单函数。

---

## IV. 分层作用域系统

### A. 三层层级

| 层级 | 存储路径 | 用途 |
|------|---------|------|
| **global** | ~/.skilldex/global/ | 所有项目可用：风格指南、通用调试方法 |
| **shared** | ~/.skilldex/shared/ | 多个显式选择加入的项目可用：团队约定 |
| **project** | <project-root>/.skilldex/ | 单个项目限定：项目特定配置 |

### B. 解析规则

**本地优先优先规则**：较低作用域始终覆盖较高作用域的相同技能名。项目作用域的 `forensics-memory-analysis` 隐藏全局作用域的同一名称安装。

### C. 安装源

安装命令接受三种源形式：
1. **注册中心名称**：`skillpm install forensics-memory-analysis`
2. **Git URL**：`skillpm install git+https://github.com/user/repo/tree/main/skills/my-skill`
3. **本地路径**：`skillpm install ./my-skill`

---

## V. 格式符合性评分

### A. 动机

**触发不足**——智能体在应调用时未能调用技能——是记录的已知失败模式。主要原因：描述质量。格式符合性评分为发布者提供可测量的、客观的信号。

### B. 评分检查（8 项，满分 100）

| 检查项 | 分值 | 说明 |
|--------|------|------|
| YAML frontmatter 可解析 | 25 | 缺失时致命，不执行后续检查 |
| name 字段存在 | 10 | 注册中心和清单所需 |
| description 存在 | 10 | 主要触发机制 |
| 描述 ≥30 词 | 10 | 特异性阈值 |
| SKILL.md ≤500 行 | 15 | 令牌预算约束 |
| 仅允许的子目录 | 10 | 强制执行 scripts/, references/, assets/ |
| 引用的资源存在 | 15 | 无损坏的相对链接 |
| 资源在正确的子目录中 | 5 | 脚本在 scripts/，文档在 references/ |

### C. 诊断输出

编译器风格格式，包含严重级别（pass/error/warning）、可选行号和人类可读消息：

```
pass    YAML frontmatter valid
pass    name field present
error   line 4: description too short (12 words, recommended: 30+)
pass    SKILL.md line count OK (87 lines)
warning Unknown subdirectory "helpers"
pass    All referenced resources exist
Format conformance score: 45/100
```

---

## VI. Agent 建议循环

**动机**：大多数 Agent 框架在没有任务前能力审查的情况下执行。Skilldex 插入了显式的人在环路检查点。

**三阶段工作流：**

**阶段 1：上下文收集** — 读取 README.md、package.json、现有 Agent 配置和已安装技能清单。

**阶段 2：提议生成** — LLM（通过 Anthropic SDK）生成技能提议清单，含技能名、理由和建议作用域。

**阶段 3：人类批准** — CLI 交互式显示每个提议，用户批准/拒绝并可选覆盖作用域。

```
Proposed skills for this project:
forensics-memory-analysis [community] [project scope]
  Reason: project contains Volatility scripts
  Approve? (Y/n/scope): y
log-triage [verified] [project scope]
  Reason: multiple log directories detected
  Approve? (Y/n/scope): y
```

---

## VII. 社区注册中心

**元数据优先**：技能文件不上传到注册中心。`source_url` 指向 GitHub 仓库，安装直接从 GitHub 拉取。

**信任层级模型：**
- **verified（已验证）**：保留给 Anthropic 官方发布的技能，手动分配
- **community（社区）**：所有提交的默认等级，任何 GitHub 用户可发布

**重要：信任层级从不阻止安装。** 注册中心提供信息，不设门禁。

**API 端点（REST，版本化）：** 搜索、安装、发布、更新等核心操作。

---

## VIII. 技能集捆绑

### A. 动机

Agent 用例很少由单个技能定义。独立安装相关技能产生行为漂移——如 Conventional Commits 和 changelog-gen 两个技能使用不同的提交类型词汇，工作流因此断裂。

**技能集**：可发布、可安装的单元，将相关技能与共享资产打包（约定文件、模板、参考文档），保证输出互一致性。

### B. 开发者技能集示例

```
developer/
  SKILLSET.md
  assets/commit-conventions.md          ← 2个技能共享
  conventional-commit/SKILL.md          ← 引用 ../assets/
  changelog-gen/SKILL.md                ← 引用 ../assets/
  pr-description/SKILL.md
  test-writer/SKILL.md
```

**关键保证**：由 conventional-commit 写的提交消息保证被 changelog-gen 正确解析，因为两者在安装时绑定到相同的词汇文件。

### C. 技能集验证评分（7 项）

YAML 可解析(25)、name 字段(10)、description(10)、描述≥30词(10)、≥1个技能(20)、无未知顶级目录(10)、远程 URL 为 GitHub URL(15)。

---

## IX. MCP 集成

Skilldex 暴露完整 MCP 服务器（`skillpm mcp`），以长生命周期 stdio 进程运行，可在任何 MCP 兼容 Agent 中注册。

**MCP 工具**：skilldex_install、skilldex_uninstall、skilldex_validate、skilldex_list、skilldex_search、skilldex_suggest、skilldex_skillset_install 等。

---

## X. 设计理念

1. **警告而非阻止**：验证、信任层级检查信息告知但不阻止——12/100 分技能也可安装
2. **规范所有权归属 Anthropic**：Skilldex 跟踪和验证但不扩展或不解释规范
3. **两个接口，一个核心**：CLI 面向人类（丰富终端输出、交互提示）；MCP 面向 Agent（JSON 入/出，无提示）

---

## XI. 局限与未来工作

1. 规范版本化：Anthropic 目前不发布显式版本化的技能格式
2. 语义描述质量：客观可评分格式符合性，但语义描述质量无法客观评分
3. 清单并发：并发调用下清单写入不是原子的
4. 层级深度：三级可能不够，复杂多项目结构可能需要任意嵌套
5. 团队治理：当前模型没有团队身份或基于角色的访问概念
6. 社区贡献冷启动
7. 建议循环不自动安装

---

## XII. 结论

Skilldex 填补了现有工具留下的两个空白：编译器风格格式符合性评分使发布者获得基于规范的反馈而非社交代理；技能集抽象使相关技能共享公共资产，保证行为一致性。完整开发者或研究 Agent 配置成为一流的可发布工件。

开源地址：https://github.com/Pandemonium-Research/Skilldex

---

## 参考文献

- Anthropic. Claude Code: Skills and Skill Packages. 2024.
- Vercel. vercel-labs/skills: The open agent skills tool. 2025.
- LangChain. LangChain Hub. 2023.
- Anthropic. Model Context Protocol (MCP) Specification. 2024.
- Cappos et al. A look in the mirror: Attacks on package managers. CCS 2008.
- Seshia et al. Towards verified artificial intelligence. arXiv:1606.08514, 2016.
- npm, pip, cargo, Homebrew package management systems.
