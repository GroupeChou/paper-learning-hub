---
name: paper-learning-hub
description: 论文每日导引系统 — 每日自动发现 Agent + 时序预测两条路线的 arXiv 新论文，生成中文摘要，更新路线图，构建站点，推送到 GitHub Pages。
---

# 论文每日研学系统

**核心定位**：每日自动发现大厂前沿论文 → 生成中文摘要 → 输出到路线图表 → 构建 MkDocs 站点 → 推送到 GitHub Pages。

## 能力概述

- **论文发现**：从 arXiv 按主题搜索最新论文（时序预测 + AI Agent）
- **大厂过滤**：只保留 16 家全球+国内大厂（OpenAI、Google、Anthropic、Meta、Microsoft、NVIDIA、阿里、智谱、百度、腾讯、华为、字节、DeepSeek、MiniMax 等）
- **摘要生成**：轻量中文摘要（标题翻译 + 摘要翻译 + 核心贡献要点），不逐段翻译
- **路线图更新**：按技术主题（智能体基础架构、多智能体系统、Transformer 时序预测等）以表格形式组织所有论文
- **站点构建**：MkDocs Material 站点，含论文详情页、路线图、专题索引
- **自动推送**：推送至 GitHub，触发 Pages 自动部署

## 技术栈

| 组件 | 说明 |
|------|------|
| 论文源 | arXiv API (`export.arxiv.org`) |
| 文本源 | `arxiv.org/html/{id}`（首选）→ `ar5iv.labs.arxiv.org/html/{id}`（降级） |
| 数据库 | SQLite (`papers.db`) |
| 站点 | MkDocs Material + GitHub Pages |
| 检索词 | 按主题关键词搜索（时序预测 / AI Agent 各方向） |
| 机构过滤 | 16 家全球+国内大厂，匹配作者单位或标题摘要关键词 |

## 配置

关键配置项（`config.yaml`）：

```yaml
raw:
  skip_download: true          # 不下载 PDF，从 arXiv HTML 远程读取
summary:
  enabled: true                # 摘要模式（替代全文翻译）
  chunk_chars: 8000
major_orgs: [...]              # 16 家机构的匹配关键词
daily_limit: 10                # 每次运行的论文处理上限
```

## 完整流程

### A. 每日自动运行（定时任务）

```bash
cd /Users/zhouqunchen/Desktop/study/paper-learning-hub
source .venv/bin/activate
./run_daily.sh
```

或分步：

```bash
# 1. 发现论文（含大厂过滤）
./run_daily.sh --prepare-workbuddy

# 2. 检查生成的每日简报
cat .workbuddy/daily-brief.md

# 3. 处理论文（摘要模式）
./run_daily.sh

# 4. 仅构建站点（论文已处理完时）
./run_daily.sh --build-only
```

**自动完成**：
1. 发现新论文（arXiv API）→ 大厂作者单位过滤
2. 跳过 PDF 下载（从 `arxiv.org/html` 远程读取）
3. 生成中文摘要 → 写入 `papers/zh/<id>/paper_zh.md`
4. 更新路线图（`guides/agent-roadmap.md` / `guides/ts-roadmap.md`）
5. 构建 MkDocs 站点
6. 推送到 GitHub（如 `git.auto_commit` 为 true）

### B. 对话触发学习论文

当用户说"学习论文 <arXiv链接>"时：
1. 从 arXiv 获取论文元数据（标题、摘要、作者）
2. 远程读取论文全文（HTML 或 PDF 临时下载）
3. 生成中文摘要（标题翻译 + 摘要 + 核心贡献）
4. 写入 `papers/zh/<id>/paper_zh.md`
5. 更新对应路线图的表格
6. 构建站点并推送

## 数据

- 论文按 `papers.db` (SQLite) 管理状态
- 中文摘要存储在 `papers/zh/<id>/paper_zh.md`
- 站点源文件在 `site/docs/`
- 每日简报在 `.workbuddy/daily-brief.md`

## 路线图表格式

路线图按技术主题分组，每个主题下的论文以表格展示：

```markdown
| 主题 | 英文标题 | 中文标题 | 发布日期 | 发布机构 |
|------|----------|----------|:--------:|:--------:|
| **智能体基础架构** (47) | [Paper Title](../papers/id/index.md) | *待补充* | 2026-05-29 | OpenAI |
```

## 注意事项

- PDF **不下载**到本地，从 arxiv.org/html 远程读取
- 不做全文逐段翻译，只做中文摘要
- 只保留全球+国内大厂的论文（个人/大学论文过滤）
- GitHub Pages 需要手动 `git push`（config 中 `auto_commit: false`）
- 构建时使用 `mkdocs build --strict`，确保 nav 只引用存在的文件
