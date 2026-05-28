# MEMORY.md - 论文自动研学知识库

## 项目定位
- 项目名：论文自动研学知识库
- 工作目录：/Users/zhouqunchen/Desktop/study/paper-learning-hub
- 目标：围绕深度学习时序预测与 AI Agent 构建一个持续更新的本地论文知识库，并发布到 GitHub Pages

## 工作分工
- WorkBuddy：负责筛选优先级、逐段翻译、知识点解释、图表/公式说明、中文精读 Markdown 生成
- Python 流水线：负责论文发现、下载、SQLite 状态管理、任务简报生成、站点构建、Git 自动提交与推送

## 输出约束
- 中文精读固定写到 `papers/zh/<paper_id>/paper_zh.md`
- 每节必须有：
  - `### 中文翻译`
  - `### 术语解释`
  - `### 图表/公式说明`
  - `### 关键 takeaway`
- 不确定内容必须显式标记 `待复核`

## 当前状态 (2026-05-28)
- DB 论文总数：288 篇（translated: 66, discovered: 100, queued: 112, workbuddy_pending: 10）
- 站点论文数：66 篇（与 translated 一致）
- GitHub Pages 地址：https://groupechou.github.io/paper-learning-hub/
- GitHub Token 状态：过期，需要用户更新

## 注意事项
- 论文下载因5分钟超时限制常被截断，仅完成部分PDF下载
- GitHub PAT token (ghp_*) 已过期，需用户在 GitHub 生成新 Personal Access Token 后更新 remote URL
- config.yaml 中 git.auto_commit: false，推送需手动完成

## 站点问题（已排查）
用户反馈站点论文少，实际站点有66篇，在 papers/index.md 中按11个类别组织。
根本原因是 GitHub Pages 的 Deploy workflow 中的 `mkdocs build --strict` 因 nav 引用不存在的文件而失败。
实际上 build 在本机运行正常，但部署到 GitHub Actions 时因 token 过期无法触发。

## 每日执行顺序
1. `./run_daily.sh --prepare-workbuddy`
2. 按 `.workbuddy/daily-brief.md` 处理本日 Top 1-3 篇论文
3. 每篇完成后写入对应 `result.json`
4. `./run_daily.sh --build-only`

