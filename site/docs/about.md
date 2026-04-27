---
description: 关于论文研学知识库 — 项目背景、定位与维护说明
---

# 关于本知识库

## 项目背景

本知识库服务于**顺丰科技技术集团/大数据智能研发中心/策略数据分析组**的预测分析工作。

组内职责：
- 数据挖掘/识别异常场景，为营运管理提供抓手
- 预测底盘数据架构搭建、上线模型精度分析及业务应用跟进

研究方向：业务量预测（大网/业务区/网点/中转/航空枢纽）、流向预测、规划-预测双向联动。

## 定位

**不是**论文追踪工具（RSS 工具够了），**而是**系统化学习体系。

核心目标：
- 从"看了很多论文但串联不起来"到"形成自己的知识网络"
- 每篇精读都附带**与物流预测场景的关联思考**
- 建立可以指导实践的方法论体系

## 维护方式

| 动作 | 频率 | 方式 |
|------|------|------|
| 论文发现 | 每日 | 自动调用 arXiv API，按机构白名单过滤 |
| 论文下载 | 每日 | 下载 PDF 到本地 `papers/raw/` |
| 中文精读 | 每日（最多 3 篇） | AI 生成初稿 → 人工复核 |
| 站点构建 | 每日 | MkDocs 构建 → push 到 GitHub Pages |
| 知识更新 | 每周 | 回顾本周精读，更新路线关联 |

## 机构白名单

| 机构 | 优先级 | 说明 |
|------|--------|------|
| DeepMind | ⭐⭐⭐⭐⭐ | 时序 + Agent 双线 |
| OpenAI | ⭐⭐⭐⭐⭐ | Agent 安全/评测 |
| Anthropic | ⭐⭐⭐⭐⭐ | Agent 评测/MCP |
| Microsoft | ⭐⭐⭐⭐ | 企业 AI |
| Meta FAIR | ⭐⭐⭐⭐ | 多 Agent/开源 |
| DeepSeek | ⭐⭐⭐⭐ | 推理/安全 |
| MiniMax | ⭐⭐⭐ | 多模态/Agent |
| 智谱 GLM | ⭐⭐⭐ | 国产大模型 |
| 阿里通义 | ⭐⭐ | 国产开源 |
| 腾讯混元 | ⭐⭐ | 国产开源 |
| 百度文心 | ⭐ | 国产大模型 |
| 字节跳动 | ⭐ | Seed/豆包 |

## 技术栈

| 组件 | 技术 |
|------|------|
| 论文发现 | arXiv API + feedparser |
| PDF 解析 | PyMuPDF |
| 精读生成 | GPT-4o-mini |
| 站点构建 | MkDocs + material 主题 |
| 部署 | GitHub Pages |
| 大文件管理 | Git LFS |

## GitHub 仓库

[:fontawesome-brands-github: GroupeChou/paper-learning-hub](https://github.com/GroupeChou/paper-learning-hub)

---

*本知识库由 WorkBuddy 自动化任务驱动，每日定时运行，commit hash 即学习进度。*
