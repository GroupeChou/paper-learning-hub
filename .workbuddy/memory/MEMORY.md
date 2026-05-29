# MEMORY.md - 论文自动研学知识库

## 项目定位
- 项目名：论文自动研学知识库
- 工作目录：/Users/zhouqunchen/Desktop/study/paper-learning-hub
- 目标：围绕深度学习时序预测与 AI Agent 构建一个持续更新的本地论文知识库，并发布到 GitHub Pages

## 工作分工
- WorkBuddy：负责筛选优先级、逐段翻译（或摘要模式）、知识点解释、中文精读 Markdown 生成
- Python 流水线：负责论文发现（大厂过滤）、下载（或跳过）、摘要生成、SQLite 状态管理、路线图更新、站点构建、Git 推送

## 输出约束
- 摘要模式下输出格式：中文标题 + 原始摘要 + 核心贡献 + 技术概要 + 实验结果 + 关键 takeaway
- 精读模式（完整翻译）每节必须有：
  - `### 中文翻译`
  - `### 术语解释`
  - `### 图表/公式说明`
  - `### 关键 takeaway`
- 不确定内容必须显式标记 `待复核`

## 当前状态 (2026-05-29)
- DB 论文总数：289 篇（全部 translated）
- 站点论文数：289 篇（AI Agent 197 篇 + 时序预测 84 篇 + 深度学习时序预测 8 篇）
- 已启用：大厂过滤 + 摘要模式 + skip_download
- GitHub Pages 地址：https://groupechou.github.io/paper-learning-hub/
- GitHub Token 状态：已更新，可正常使用

## 注意事项
- 论文下载因5分钟超时限制常被截断，仅完成部分PDF下载（已启用 skip_download 跳过）
- GitHub PAT token 已更新，git push 可正常使用
- config.yaml 中 git.auto_commit: false，推送需手动完成

## 站点问题（已排查）
用户反馈站点论文少，实际站点有66篇，在 papers/index.md 中按11个类别组织。
根本原因是 GitHub Pages 的 Deploy workflow 中的 `mkdocs build --strict` 因 nav 引用不存在的文件而失败。
实际上 build 在本机运行正常，但部署到 GitHub Actions 时因 token 过期无法触发（token 已修复）。

## 近期重要变更 (2026-05-29)
1. **大厂过滤**：新增 `major_orgs` 配置（16家全球+国内大厂），发现环节自动过滤作者单位
2. **摘要模式**：新增 `summary.enabled: true`，替换全文翻译为轻量摘要（中文标题+摘要翻译+核心贡献）
3. **路线图自动更新**：`update_roadmap()` 自动将新论文追加到 agent-roadmap.md / ts-roadmap.md
4. **skip_download**：默认跳过 PDF 下载，从 arxiv.org/html 远程读取

## 每日执行顺序
1. `./run_daily.sh --prepare-workbuddy`
2. 按 `.workbuddy/daily-brief.md` 处理本日 Top 1-3 篇论文
3. 每篇完成后写入对应 `result.json`
4. `./run_daily.sh --build-only`

