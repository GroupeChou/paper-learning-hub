# 论文自动研学知识库 V1

一个 `WorkBuddy-first` 的论文自动研学工程，用来持续追踪 `深度学习时序预测` 和 `AI Agent` 两条方向的权威大厂论文，并把原文、本地状态、中文精读、学习大纲、GitHub Pages 站点连成一条稳定流水线。

## 当前实现

- 每日发现并筛选来自白名单机构的论文候选
- 维护 `经典必读` 与 `每日前沿` 双轨内容
- 用 SQLite 跟踪论文状态、失败原因与更新时间
- 自动下载原文到本地 `papers/raw/`
- 由 WorkBuddy 负责深度翻译、术语解释、图表说明和知识拆解
- 生成中文精读 Markdown、学习大纲、专题索引和 MkDocs 站点
- 默认打开 Git 自动提交和自动推送

## 运行思路

这版不再把“大模型处理”放在 Python 脚本里硬调用，而是拆成两段：

1. **Python 准备阶段**
   - 抓新论文
   - 下载原文
   - 生成 WorkBuddy 任务简报
   - 写入 `.workbuddy/jobs/<paper_id>/job.md`

2. **WorkBuddy 执行阶段**
   - WorkBuddy 使用本项目自带技能 `paper-learning-hub`
   - 逐篇读取任务简报和原文
   - 直接把中文精读写入 `papers/zh/<paper_id>/paper_zh.md`
   - 写入 `result.json`

3. **Python 收尾阶段**
   - 同步 WorkBuddy 产出
   - 生成/更新学习大纲与站点
   - 自动 `git commit` 和 `git push`

这样做的好处是：调度和智能内容生成都更贴近 WorkBuddy 的使用方式，而确定性的下载、状态管理、站点构建和 Git 同步仍然由脚本稳定兜底。

## 目录结构

```text
paper-learning-hub/
├── .workbuddy/
│   ├── daily-task.md
│   ├── memory/
│   └── skills/paper-learning-hub/
├── config.yaml
├── guides/
├── logs/
├── papers/
│   ├── raw/
│   └── zh/
├── run_daily.sh
├── scripts/
├── site/
├── src/
└── tests/
```

## 快速开始

```bash
cd /Users/zhouqunchen/Desktop/study/paper-learning-hub
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
python3 scripts/run_daily.py --install-workbuddy-skill
```

如果你想把它作为一个独立 GitHub 项目使用，建议先在项目目录里初始化独立 Git 仓库，再配置远端：

```bash
cd /Users/zhouqunchen/Desktop/study/paper-learning-hub
git init -b main
git remote add origin <your-github-repo-url>
```

## 常用命令

```bash
# 发现新论文、下载原文、生成 WorkBuddy 任务
./run_daily.sh --prepare-workbuddy

# WorkBuddy 处理完内容后，收尾构建并自动提交/推送
./run_daily.sh --build-only

# 仅同步 WorkBuddy 已完成的结果到状态库
./run_daily.sh --sync-workbuddy

# 重新安装本项目的 WorkBuddy 技能
./run_daily.sh --install-workbuddy-skill

# 回归测试
pytest
```

## WorkBuddy 每日任务

WorkBuddy 的每日定时任务里，直接使用下面这条提示即可：

```text
请在 /Users/zhouqunchen/Desktop/study/paper-learning-hub 中使用 paper-learning-hub 技能执行每日论文自动研学任务。
先运行 ./run_daily.sh --prepare-workbuddy，再按 .workbuddy/daily-brief.md 逐篇处理论文，
处理完成后运行 ./run_daily.sh --build-only，并检查 git push 结果。
```

项目已经自带：

- WorkBuddy 技能源文件：[`/.workbuddy/skills/paper-learning-hub`](./.workbuddy/skills/paper-learning-hub)
- 每日任务提示：[`/.workbuddy/daily-task.md`](./.workbuddy/daily-task.md)
- 长期记忆：[`/.workbuddy/memory/MEMORY.md`](./.workbuddy/memory/MEMORY.md)

## GitHub 推送

`config.yaml` 现在默认：

- `git.auto_commit: true`
- `git.auto_push: true`

但要真正推送成功，还需要你在**项目自己的 Git 仓库**里配置好 `origin`。如果远端不存在，流水线会继续执行，只是在最后给出“已提交但未推送”或“未配置远端”的提示，不会把整条任务打断。

## 真实模型接入

默认运行模式已经改成 `translator.backend: workbuddy`。如果以后你想回退到脚本直连模型，也仍然可以把 `translator.backend` 改成：

- `openai_compatible`
- `mock`

但当前推荐路线就是：**WorkBuddy 做智能生成，脚本做状态和发布。**

