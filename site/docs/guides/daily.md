---
description: 每日新增论文更新日志
---

# 📅 每日更新日志

## 更新规则

- **每日自动发现**：从白名单机构（DeepMind/OpenAI/Anthropic/Meta/Microsoft/DeepSeek/MiniMax/智谱/阿里/腾讯/百度/字节）自动抓取最新论文
- **每日限额**：每天最多处理 3 篇论文
- **优先级排序**：按机构优先级 + 相关性评分排序

---

## 机构白名单

| 优先级 | 机构 | 备注 |
|--------|------|------|
| 95 | OpenAI | 最高优先级 |
| 94 | Google DeepMind | 最高优先级 |
| 93 | Anthropic | 最高优先级 |
| 92 | DeepSeek | 高优先级 |
| 90 | Microsoft | 高优先级 |
| 89 | Meta FAIR | 高优先级 |
| 88 | MiniMax / 智谱 | 中优先级 |
| 86 | 阿里通义 | 中优先级 |
| 85 | 腾讯混元 | 中优先级 |
| 84 | 百度文心 | 中优先级 |
| 83 | 字节跳动 | 中优先级 |

---

## 最近更新

### 2026-04-27

**新增论文**：

| 论文 ID | 机构 | 方向 | 状态 |
|---------|------|------|------|
| 2604.21255v1 | Anthropic | Agent评测 | ✅ 已精读 |
| 2604.17111v1 | OpenAI | 多Agent调度 | ✅ 已精读 |
| 2604.12102v2 | OpenAI | 空间推理 | ✅ 已精读 |

---

## 历史更新

> 更多历史记录请查看 [GitHub Commits](https://github.com/GroupeChou/paper-learning-hub/commits/main)

---

## 自动更新机制

本知识库通过 GitHub Actions 实现自动化更新：

1. **每日定时触发**：北京时间 15:00 自动运行
2. **论文发现**：从 arXiv API 抓取白名单机构新论文
3. **WorkBuddy 处理**：调用 paper-learning-hub 技能进行中文精读
4. **自动构建**：生成 MkDocs 站点并推送到 GitHub Pages

详细配置见 `run_daily.sh`（位于项目根目录）
