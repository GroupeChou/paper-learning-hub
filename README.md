<p align="center">
  <h1 align="center">📚 论文自动研学知识库</h1>
  <p align="center">
    <strong>深度学习时序预测 · AI Agent</strong>
  </p>
  <p align="center">
    <a href="https://groupechou.github.io/paper-learning-hub/">
      <img src="https://img.shields.io/badge/📖-在线阅读站点-blue?style=for-the-badge" alt="在线阅读站点">
    </a>
    <a href="https://github.com/GroupeChou/paper-learning-hub/stargazers">
      <img src="https://img.shields.io/github/stars/GroupeChou/paper-learning-hub?style=for-the-badge" alt="Stars">
    </a>
    <a href="https://github.com/GroupeChou/paper-learning-hub/pulse">
      <img src="https://img.shields.io/github/last-commit/GroupeChou/paper-learning-hub?style=for-the-badge" alt="Last Commit">
    </a>
  </p>
  <p align="center">
    <b><a href="https://groupechou.github.io/paper-learning-hub/">🚀 立即进入知识库 →</a></b>
  </p>
</p>

---

## 📖 站点一览

| 维度 | 内容 |
|------|------|
| **已收录论文** | 40篇（持续更新） |
| **研究方向** | 🤖 AI Agent 主线 · 📈 时序预测主线 · 🔗 交叉领域 |
| **图片/表格** | 28篇含原版图表，全部正确嵌入 |
| **阅读方式** | 按主题/机构/时间线浏览，Markdown 沉浸式阅读 |

## 🚀 快速入口

👉 **[在线阅读站点](https://groupechou.github.io/paper-learning-hub/)**

站点支持：
- **AI Agent 主线**：Agent 基础架构 → 规划推理 → 工具使用 → 记忆检索 → 多智能体协作
- **时序预测主线**：基础理论 → 经典方法 → Transformer → Foundation Model → 长序列预测
- **机构专题**：OpenAI、DeepMind、Anthropic、Meta、Microsoft 及国内大厂
- **按论文浏览**：全部已精读论文列表，状态一目了然

---

## 🔧 项目架构

```text
paper-learning-hub/
├── site/            ← GitHub Pages 站点（MkDocs）
│   └── docs/papers/ ← 每篇论文独立目录（index.md + assets/）
├── papers/
│   ├── raw/         ← PDF 原文
│   └── zh/          ← 中文精读 + 提取图片
├── scripts/         ← 修复/构建工具
├── src/             ← Python 管线（解析→翻译→构建→发布）
├── config.yaml      ← 配置文件
└── .github/workflows/deploy.yml ← CI/CD 自动部署
```

## 🤖 智能流程

1. **每日发现** → arXiv 白名单机构论文检索
2. **PDF 解析** → PyMuPDF 提取文本 + 图片 → 分块
3. **逐句精译** → 逐 chunk 翻译（表格/公式/图片完整保留）
4. **站点构建** → MkDocs 生成 → GitHub Pages 自动发布

## 📋 状态

- [x] 40 篇论文精读完成
- [x] 图片完整嵌入（333 张）
- [x] 表格/公式还原
- [x] GitHub Pages 自动部署
- [x] 论文精读（✅ 已精读标记）+ 待精读队列
