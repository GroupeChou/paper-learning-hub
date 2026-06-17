# 前沿 AI 技术日报系统 v2.2

**核心定位**：每日自动聚合 5 大机构官方博客 → 中英双语摘要 → 精美 HTML 日报 → Git 自动推送 GitHub Pages。

## v2.2 vs v2.1 变化

| 维度 | v2.1 | v2.2 |
|------|------|------|
| **数据源分层** | 全部直连抓取 | 直连层(RSS/arXiv) + 搜索缓存层(WorkBuddy WebSearch 预填) |
| **Anthropic** | 0 篇 | 使用 WebSearch 预填缓存，6 篇 |
| **OpenAI** | 403 失败 | 使用 WebSearch 预填缓存，6 篇 |
| **Meta** | 400 失败 | 使用 WebSearch 预填缓存，6 篇 |
| **DeepSeek** | old releases | arXiv API 搜索最新论文 |

## 数据源 5 层架构

```
┌─────────────────────────────────────────────┐
│  直连层 (Direct)                              │
│  Google DeepMind → RSS    ✅ 稳定             │
│  DeepSeek → arXiv API    ✅ 稳定              │
├─────────────────────────────────────────────┤
│  搜索缓存层 (WebSearch Cache)                  │
│  Anthropic → .websearch-cache.json           │
│  OpenAI    → .websearch-cache.json           │
│  Meta      → .websearch-cache.json           │
│  ↑ 由 WorkBuddy WebFetch 预填                 │
└─────────────────────────────────────────────┘
```

## 5 个订阅源

| 机构 | 抓取方式 | 代表方向 |
|------|---------|---------|
| **Anthropic** | WorkBuddy WebFetch → 缓存 | Agent 设计原则、安全对齐、可解释性 |
| **OpenAI** | WorkBuddy WebFetch → 缓存 | GPT 系列、推理能力、多模态 |
| **Google DeepMind** | RSS Feed | Gemini、Agent、世界模型、科学 AI |
| **Meta AI** | WorkBuddy WebFetch → 缓存 | Llama 开源、多模态、CV 基础模型 |
| **DeepSeek** | arXiv API 搜索 | MoE 架构、推理优化、高效训练 |

## 快速使用

### A. 完整运行（含搜索预填）

```bash
# Step 1: 预填搜索缓存（WorkBuddy WebFetch 获取 Anthropic/OpenAI/Meta 文章）
# 在 WorkBuddy 中执行 WebFetch:
#   - https://www.anthropic.com/research
#   - https://openai.com/research
#   - https://ai.meta.com/blog/
#   提取文章标题+URL → 保存到 daily-reports/.websearch-cache.json

# Step 2: 运行每日流水线
cd /Users/zhouqunchen/Desktop/study/paper-learning-hub
source .venv/bin/activate

python -m paper_learning_hub.daily_runner \
  --output ./daily-reports \
  --github-pages ./docs \
  --max 6 \
  -v
```

### B. 仅使用直连源（跳过搜索层）

无需缓存文件，仅运行 RSS + arXiv：

```bash
cd /Users/zhouqunchen/Desktop/study/paper-learning-hub
source .venv/bin/activate

python -m paper_learning_hub.daily_runner \
  --output ./daily-reports \
  --github-pages ./docs \
  --max 6 \
  --skip-search-layer
```

### C. 每日自动运行（WorkBuddy Automation）

**必读：两阶段流程**

```
Phase 1 — WebFetch 预填缓存
  1. 使用 WebFetch 爬取 anthropic.com/research
  2. 使用 WebFetch 爬取 openai.com/research
  3. 使用 WebFetch 爬取 ai.meta.com/blog
  4. 提取文章标题+URL+日期 → 保存为 daily-reports/.websearch-cache.json

Phase 2 — 运行流水线
  python -m paper_learning_hub.daily_runner \
    --output ./daily-reports \
    --github-pages ./docs \
    --max 6 -v --sync-ima
  → 自动 Git 推送 → 保存运行日志
```

### D. 对话触发

当用户说"更新今日报告"或"paper-hub"时：
1. 先执行 Phase 1（WebFetch 预填缓存）
2. 再执行 Phase 2（运行流水线）
3. 报告结果并给出访问链接

## 报告格式

### HTML 日报

精美响应式设计：
- 顶部统计卡片（总文章数、机构数、翻译数）
- 按机构分组展示
- 每篇文章：标题（可点击跳转原文）+ 中英双语并排摘要
- 支持移动端适配

### Markdown 降级版

同时生成纯 Markdown 版本作为降级方案。

## 部署位置

| 产出 | 路径 |
|------|------|
| HTML 日报 | `daily-reports/report-YYYY-MM-DD.html` |
| 最新版首页 | `daily-reports/index.html` |
| JSON 数据 | `daily-reports/daily-YYYY-MM-DD.json` |
| Markdown 降级 | `daily-reports/report-YYYY-MM-DD.md` |
| **搜索缓存** | `daily-reports/.websearch-cache.json` |
| 运行结果日志 | `daily-reports/.run-result-latest.json` |
| GitHub Pages | `docs/index.html` (GitHub Pages 根) |
| ima 同步 | `daily-reports/ima-sync-YYYY-MM-DD.json` |

## .websearch-cache.json 格式

```json
{
  "Anthropic": [
    {"title": "...", "url": "https://www.anthropic.com/research/...", "published": "2026-06-16", "snippet": "..."}
  ],
  "OpenAI": [...],
  "Meta": [...]
}
```

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `PAPERHUB_API_KEY` | LLM API Key（用于翻译） | — |
| `PAPERHUB_MODEL` | LLM 模型 | `gpt-4.1-mini` |
| `PAPERHUB_API_BASE` | LLM API 地址 | `https://api.openai.com/v1` |

## Git 自动推送配置

推送行为由 `config.yaml` 控制：

```yaml
git:
  auto_commit: true    # 自动 git add + commit
  auto_push: true      # 自动 git push
  branch: main
  remote_name: origin
  commit_prefix: "auto: paper hub"
```

CLI 参数 `--no-auto-push` 可临时禁用推送。

## 依赖

- Python 3.12+, `feedparser`, `requests`, `pyyaml`
- 可选：`OPENAI_API_KEY` 或兼容 API Key（用于翻译）
- Git（用于自动推送）
