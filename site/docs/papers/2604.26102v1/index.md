# paper

<!-- 论文元数据卡片 -->
<div class="paper-meta">
  <div class="paper-meta-item">
    <span class="paper-meta-label">机构</span>
    <span class="paper-meta-value org-"></span>
  </div>
  <div class="paper-meta-item">
    <span class="paper-meta-label">方向</span>
    <span class="paper-meta-value"></span>
  </div>
  <div class="paper-meta-item">
    <span class="paper-meta-label">日期</span>
    <span class="paper-meta-value"></span>
  </div>
</div>

!!! info ""
    <span class="paper-tag paper-tag-translated">✅ 已完成精读</span>

- **来源**：[]()
- **论文链接**：[]()
- **状态**：已生成

## 摘要

大型语言模型智能体在软件工程任务上取得了显著进展，然而当前方法存在一个根本性的上下文耦合问题（context coupling problem）：标准的代码编辑界面将代码检查、修改规划和编辑执行混在同一个上下文窗口中，迫使智能体将探索性查看与严格格式化的编辑生成交错进行。

这导致无关信息不断累积，损害了智能体的性能。

为了解决这一问题，我们提出了 SWE-Edit，它将代码编辑分解为两个专门的子智能体：一个 Viewer（查看器），按需提取与任务相关的代码；一个 Editor（编辑器），根据高层规划执行修改——从而让主智能体专注于推理，同时将上下文密集型操作委托给干净的上下文窗口。

我们进一步研究了什么构成一个有效的编辑模型：观察到当前主流的查找-替换格式容易出错，我们使用 GRPO 训练 Qwen3-8B，使其自适应地选择编辑模式，相比单一格式基线提升了编辑效率。

在 SWE-bench Verified 上，SWE-Edit 将解决率提升了 2.1%，同时将推理成本降低了 17.9%。

我们还额外提出了一个代码编辑基准，能够可靠地预测下游智能体性能，为编辑模型选择提供实用指导。

我们的代码已公开在 https://github.com/microsoft/SWE-Edit。

*Yikai Zhang 1 2 *，Jiaxin Pei 3，Kenan Li 1，Maoquan Wang 1，Jin Pan 2，Yu Kang 1，Shengyu Fu 1，Elsie Nallipogu 1，Junjie Hu 2，Yufan Huang 1，Zijian Jin 1*

*工作完成于微软实习期间。*
1 微软，美国华盛顿州雷德蒙德
2 威斯康星大学麦迪逊分校计算机科学系，美国威斯康星州麦迪逊
3 斯坦福大学以人为本人工智能研究所（HAI），美国加利福尼亚州斯坦福




## 图表资源

- ![](assets/assets)
- ![](assets/page-009-img-01.png)



---

---

## 附录

### A. 实现细节

本附录提供了实验中使用的智能体脚手架、工具定义和提示语的完整细节。

#### A.1. 基线智能体脚手架

我们采用来自 Anthropic 的参考智能体脚手架，该脚手架为智能体配备了两个工具：`execute_bash` 用于 shell 命令执行，`str_replace_editor` 用于文件操作。

编辑器工具提供了用于查看、创建和通过精确字符串替换编辑文件的子命令。

这反映了当前智能体软件工程的最佳实践。

**工具定义。** 基线智能体使用以下工具：

**Listing 1. Bash 工具架构。**
```json
{
  "type": "function",
  "name": "execute_bash",
  "description": "在 bash shell 中运行命令\n"
}
```

**Listing 2. 编辑器工具架构。**
```json
{
  "type": "function",
  "name": "str_replace_editor",
  "description": "用于查看、创建和编辑文件的自定义编辑器工具",
  "parameters": {
    "type": "object",
    "properties": {
      "command": {
        "type": "string",
        "enum": ["view", "create", "edit"],
        "description": "要运行的命令。可选值：'view', 'create', 'edit'。"
      },
      "path": {
        "type": "string",
        "description": "文件或目录的绝对路径"
      },
      "query": {
        "type": ["string", "null"],
        "description": "'view' 命令在 path 指向文件时必需。描述要查找内容的自然语言查询。"
      },
      "instruction": {
        "type": ["string", "null"],
        "description": "'edit' 命令必需。描述如何修改文件的详细指令。"
      }
    }
  }
}
```

Viewer 子智能体提示语：当调用 `view` 命令时，Viewer 子智能体接收文件内容和查询，返回相关行范围。

Editor 子智能体提示语：当调用 `edit` 命令时，Editor 子智能体接收文件内容和编辑指令，以搜索-替换格式或全文件重写输出修改。

### B. 完整实验结果

**表 8. SWE-bench Verified 上的详细性能指标。每个配置的结果为三次独立运行的平均值。"Succ." 表示编辑器工具调用的成功率。**

| 配置 | 解决率 (%) | 轮次 | 智能体成本 ($) | 编辑器成本 ($) | Viewer成本 ($) | 总成本 ($) | 输出 Tokens | 总输入 | 缓存输入 | 非缓存输入 | Viewer 调用 | Editor 调用 | 成功率 (%) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Baseline | 69.9 | 24.2 | 243.7 | — | — | 243.7 | 9632 | 369.8K | 276.7K | 5.78 | 2.86 | 93.4 |
| + Viewer | 70.3 | 23.0 | — | — | — | 225.0 | — | — | — | — | — | 94.3 |
| + Editor | 71.3 | — | — | — | — | 268.3 | — | — | — | — | — | 96.1 |
| SWE-Edit | 72.0 | — | — | — | — | 200.1 | — | — | — | — | — | 96.9 |

**表 9. SWE-bench Verified 上每次运行的均值±标准差（500 个实例，3 次运行）。**

| 配置 | 解决率 (%) | 成本 ($) | 编辑成功率 (%) |
|---|---|---|---|
| Baseline | 69.9 ± 0.6 | 243.7 ± 6.5 | 93.4 ± 0.8 |
| + Viewer | 70.3 ± 1.6 | 225.0 ± 5.6 | 94.3 ± 0.3 |
| + Editor | 71.3 ± 0.2 | 268.3 ± 19.3 | 96.1 ± 0.2 |
| SWE-Edit | 72.0 ± 0.0 | 200.1 ± 16.8 | 96.9 ± 0.1 |

### C. PR-Edit 基准

本节提供了 PR-Edit 基准的实现细节，包括用于计算归一化匹配奖励的归一化函数、用于 GPT-4.1 等价性评分的提示语以及数据集中的一个示例。

#### C.1. 代码归一化

归一化匹配奖励在规范化空白符和移除注释后将模型输出与真实值进行比较。

这为训练期间编辑正确性提供了一个可靠的、无需执行的代理指标。

**Listing 3. 用于计算归一化匹配奖励的代码归一化函数。**
```python
def normalize_code(code: str) -> str:
    \"\"\"
    通过移除注释和规范化空白符来归一化代码。
    允许容忍注释和空白符差异的比较。
    注意：这使用基于正则的启发式方法，可能错误处理字符串字面量中的类似注释的模式。
    对于大多数代码比较任务，这是一个可接受的权衡。
    \"\"\"
    # 首先移除多行注释
    code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)
    # Python 文档字符串 / 用作注释的多行字符串
    code = re.sub(r'""".*?"""', "", code, flags=re.DOTALL)
    code = re.sub(r"'''.*?'''", "", code, flags=re.DOTALL)
    # HTML/XML 注释
    code = re.sub(r"<!--.*?-->", "", code, flags=re.DOTALL)
    # 移除单行注释
    code = re.sub(r"//.*$", "", code, flags=re.MULTILINE)
    code = re.sub(r"#.*$", "", code, flags=re.MULTILINE)
    # 规范化空白符
    code = re.sub(r"\s+", " ", code)
    return code.strip()
```

### D. 开源模型评估细节

#### D.1. 模型选择

我们的主要实验使用 GPT-5，一个专有模型。

为验证 SWE-Edit 跨模型家族的泛化能力，我们在三个近期的开源推理模型上进行了评估：Kimi-K2-Thinking、MiniMax-M2.1 和 GLM-4.7。

选择这些模型有两个原因：（1）它们代表了最新一代具有强推理能力的开源模型；（2）它们经过了大量的智能体训练，使其成为挑战性软件工程任务的合适候选。

#### D.2. 推理配置

所有三个模型都配置了交错思考（Interleaved Thinking）和保留思考（Preserved Thinking）。

交错思考允许模型在每次响应和工具调用之前进行推理，改善指令遵循和生成质量。

保留思考自动在多轮对话中保留推理块，重用现有推理而非从头推导——减少信息损失并提高长程智能体任务的一致性。
