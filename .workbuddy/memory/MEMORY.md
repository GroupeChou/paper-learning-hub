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

## 每日执行顺序
1. `./run_daily.sh --prepare-workbuddy`
2. 按 `.workbuddy/daily-brief.md` 处理本日 Top 1-3 篇论文
3. 每篇完成后写入对应 `result.json`
4. `./run_daily.sh --build-only`

