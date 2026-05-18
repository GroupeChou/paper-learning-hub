---
name: paper-learning-hub
description: 论文每日导引系统 — 每日自动发现 Agent + 时序预测两条路线的 arXiv 新论文，追加到路线文件。不做翻译，不做站点，轻量运行。
---

# 论文每日导引系统

**核心定位**：论文导引，不是论文翻译。
每天自动发现两条路线（Agent + 时序预测）的最新论文，输出到路线文件供参考。

**不做以下事情**：
- ❌ 不翻译论文全文
- ❌ 不下载 PDF
- ❌ 不构建 MkDocs 站点
- ❌ 不推送 GitHub

## 什么时候使用

当用户要求你：
- 更新今日论文导引
- 跑每日论文发现任务
- 为某条路线补充论文
- 查看当前路线论文列表

## 流程

### Step 1. 论文发现

在项目根目录运行：

```bash
cd /Users/zhouqunchen/Desktop/study/paper-learning-hub && source .venv/bin/activate && ./run_daily.sh --prepare-workbuddy
```

这会：
- 从 arXiv 搜索两条路线的最新论文（按 config.yaml 中的 feeds 定义）
- 写入 `.workbuddy/daily-brief.md`
- 写入 `.workbuddy/jobs/<paper_id>/job.md`

### Step 2. 处理论文（对每条路线分别输出）

读取 `.workbuddy/daily-brief.md` 中的论文列表。

对于每条路线（时序预测 / AI Agent），分别执行：

**输出格式**（追加写入路线文件）：

每篇论文只写三行：

```
- **论文中文标题** (Paper English Title) | 机构 | YYYY-MM-DD
  [arXiv](链接) — 2-3句简短说明
```

**路线文件**：
- `guides/ts-roadmap.md` — 时序预测路线
- `guides/agent-roadmap.md` — AI Agent 路线

**追加规则**：
1. 检查该论文是否已在路线文件中（通过 arXiv ID 去重）
2. 如果新论文已存在，跳过
3. 如果不存在，追加到对应路线文件**顶部**（最新优先）
4. 每条路线每天最多追加 5 篇

### Step 3. 完成

无需任何后续操作。路线文件会自动保留最新论文列表，供随时翻阅。

## 处理原则

1. **标题中英对照**：英文标题 + 中文翻译标题
2. **简短说明**：2-3 句中文，说清楚这篇论文做了什么、为什么值得看
3. **不做翻译**：不翻译正文、不写 detailed summary、不写表格
4. **链接导向**：每篇必须提供 arXiv 链接，用户有兴趣自己深入看
5. **去重**：同一篇论文不会重复追加
6. **并发**：每条路线独立处理，互不干扰
