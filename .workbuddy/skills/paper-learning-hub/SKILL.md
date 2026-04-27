---
name: paper-learning-hub
description: 使用 WorkBuddy 执行论文自动研学知识库的每日任务，包括准备论文任务、逐篇中文精读、站点构建与 GitHub 同步。
---

# Paper Learning Hub

这个技能用于当前项目的每日论文自动研学流程。

## 什么时候使用

当用户要求你：

- 跑一次论文自动研学日任务
- 更新今日论文学习大纲
- 翻译并深度解释新论文
- 重建知识库站点并同步 GitHub

## 运行原则

1. 先让脚本完成发现、下载、状态准备
2. 再由 WorkBuddy 负责论文中文精读
3. 最后回到脚本完成站点构建和 Git 推送

## 固定流程

### Step 1. 准备任务

在项目根目录运行：

```bash
./run_daily.sh --prepare-workbuddy
```

然后打开：

- `.workbuddy/daily-brief.md`
- `.workbuddy/jobs/<paper_id>/job.md`

### Step 2. 处理论文

对于每篇 `job.md`：

1. 阅读原文文件路径和任务要求
2. 结合原始 PDF/HTML 逐段生成中文精读
3. 直接写入 `papers/zh/<paper_id>/paper_zh.md`
4. 写入 `.workbuddy/jobs/<paper_id>/result.json`

输出必须满足：

- 使用 Markdown
- 每节固定包含：
  - `### 中文翻译`
  - `### 术语解释`
  - `### 图表/公式说明`
  - `### 关键 takeaway`
- 保留公式和关键术语
- 不确定内容标记 `待复核`

### Step 3. 收尾构建

全部论文处理完成后运行：

```bash
./run_daily.sh --build-only
```

这一步会：

- 同步 WorkBuddy 输出到数据库
- 重建 MkDocs 站点
- 自动执行 Git add / commit / push

## 失败处理与重试机制

### 重试规则（必须遵守）
- **单篇论文最多重试 5 次**
- 每次失败后记录到 `result.json` 的 `retry_count` 字段
- 第 5 次仍然失败时，写入 `result.json` 为 `failed`，**跳过该论文**
- 失败的论文在下次运行时会重新加入队列

### 失败处理流程
1. 首次失败 → `retry_count: 1`，继续下一节
2. 第2-4次失败 → 增加 `retry_count`，等待30秒后重试
3. 第5次失败 → `result.json` 状态设为 `failed`，记录 `failure_reason`，跳过
4. **不要因为单篇失败阻断其他论文**

### GitHub 推送前提条件
**重要：必须满足以下全部条件才可推送 GitHub**
1. ✅ 所有论文的 `result.json` 都已写入（成功或已标记 failed）
2. ✅ 至少 95% 的论文处理成功
3. ✅ `./run_daily.sh --build-only` 执行成功
4. ✅ Git push 返回成功

**禁止行为**：
- ❌ 部分论文未处理完成就运行 `--build-only`
- ❌ 推送时仍有论文处于"处理中"状态
- ❌ 忽略失败论文不做记录

---

## 工作风格

- 优先保证深度和结构完整，再追求速度
- 关注论文里的关键公式、图表、实验设置和工程启发
- 不要把原文简单缩写成摘要，要保留学习价值

