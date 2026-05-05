# SWE-Edit: Rethinking Code Editing for Efficient SWE-Agent

<!-- 论文元数据卡片 -->
<div class="paper-meta">
  <div class="paper-meta-item">
    <span class="paper-meta-label">机构</span>
    <span class="paper-meta-value org-Microsoft">Microsoft</span>
  </div>
  <div class="paper-meta-item">
    <span class="paper-meta-label">方向</span>
    <span class="paper-meta-value">AI Agent</span>
  </div>
  <div class="paper-meta-item">
    <span class="paper-meta-label">日期</span>
    <span class="paper-meta-value">2026-04-28</span>
  </div>
</div>

!!! info ""
    <span class="paper-tag paper-tag-translated">✅ 已完成精读</span>

- **来源**：[Microsoft arXiv query](https://arxiv.org/abs/2604.26102v1)
- **论文链接**：[https://arxiv.org/pdf/2604.26102v1](https://arxiv.org/pdf/2604.26102v1)
- **状态**：已生成

## 摘要

Large language model agents have achieved remarkable progress on software engineering tasks, yet current approaches suffer from a fundamental context coupling problem: the standard code editing interface conflates code inspection, modifi...

## 图表资源
- ![](assets/page-009-img-01.png)

## Section 1

> 待复核：该片段的文本提取或翻译结果置信度偏低。

### 中文翻译
> 当前使用 `mock` 翻译器，已保留原始片段作为待精读材料。

[Page 1] SWE-Edit: Rethinking Code Editing for Efficient SWE-Agent Yikai Zhang 1 2 * Jiaxin Pei 3 Kenan Li 1 Maoquan Wang 1 Jin Pan 2 Yu Kang 1 Shengyu Fu 1 Elsie Nallipogu 1 Junjie Hu 2 Yufan Huang 1 Zijian Jin 1 Abstract Large language model agents have achieved re- markable progress on software engineering tasks, yet current approaches suffer from a fundamen- tal context coupling problem: the standard code editing interface conflates code inspection, modi- fication planning, and edit execu...

### 术语解释
- `待接入模型`：此处应该由真实大模型输出逐句翻译和术语解释。
- `当前建议`：优先配置 OpenAI 兼容接口，或将该 chunk 交给本地智能体平台执行。

### 图表/公式说明
- 当前 chunk 未进行真实多模态解释。
- 解析备注：无

### 关键 takeaway
- 先完成可跑流水线，确保原文、状态库、站点和后续人工复核链路全部就位。
- 当前片段需要在接入真实模型后重新生成。

## Section 2

> 待复核：该片段的文本提取或翻译结果置信度偏低。

### 中文翻译
> 当前使用 `mock` 翻译器，已保留原始片段作为待精读材料。

[Page 2] SWE-Edit: Rethinking Code Editing for Efficient SWE-Agent Main Agent Viewer Module Editor Module ----------------------------- Adaptive Modes: {Find-Replace vs. Whole-File Rewrite} RL Optimizer (Reward Computing & Gradient Update) Environment (Codebase) Edit Instruction Target Query Edit Interface (Decoupled Execution) Policy Update Execute Outcome Figure 1. Overview of the proposed SWE-Edit framework architecture. The figure illustrates the dual optimization mechanism, demonstrating...

### 术语解释
- `待接入模型`：此处应该由真实大模型输出逐句翻译和术语解释。
- `当前建议`：优先配置 OpenAI 兼容接口，或将该 chunk 交给本地智能体平台执行。

### 图表/公式说明
- 当前 chunk 未进行真实多模态解释。
- 解析备注：无

### 关键 takeaway
- 先完成可跑流水线，确保原文、状态库、站点和后续人工复核链路全部就位。
- 当前片段需要在接入真实模型后重新生成。

## Section 3

> 待复核：该片段的文本提取或翻译结果置信度偏低。

### 中文翻译
> 当前使用 `mock` 翻译器，已保留原始片段作为待精读材料。

[Page 3] SWE-Edit: Rethinking Code Editing for Efficient SWE-Agent Austin et al., 2021; Jain et al., 2024; Zhuo et al., 2024) to code editing (Gauthier, 2024b) and repository-level software engineering (Jimenez et al., 2023). Early ap- proaches to SWE tasks such as bug fixing employed fixed pipelines ( ¨Orwall, 2024; Xia et al., 2024), decomposing problems into localization, repair, and validation phases. Re- cent agentic systems (Yang et al., 2024; Wang et al., 2024) instead equip LLMs with...

### 术语解释
- `待接入模型`：此处应该由真实大模型输出逐句翻译和术语解释。
- `当前建议`：优先配置 OpenAI 兼容接口，或将该 chunk 交给本地智能体平台执行。

### 图表/公式说明
- 当前 chunk 未进行真实多模态解释。
- 解析备注：无

### 关键 takeaway
- 先完成可跑流水线，确保原文、状态库、站点和后续人工复核链路全部就位。
- 当前片段需要在接入真实模型后重新生成。

## Section 4

> 待复核：该片段的文本提取或翻译结果置信度偏低。

### 中文翻译
> 当前使用 `mock` 翻译器，已保留原始片段作为待精读材料。

[Page 4] SWE-Edit: Rethinking Code Editing for Efficient SWE-Agent ification. It executes the edit directly, without requiring the main agent to produce format-sensitive find-replace commands. This decouples high-level reasoning—deciding what to change—from low-level generation—producing correctly formatted edit syntax. Both subagents are implemented using a smaller, cost- efficient model, while the main agent focuses purely on problem-solving and orchestration. Full implementation details an...

### 术语解释
- `待接入模型`：此处应该由真实大模型输出逐句翻译和术语解释。
- `当前建议`：优先配置 OpenAI 兼容接口，或将该 chunk 交给本地智能体平台执行。

### 图表/公式说明
- 当前 chunk 未进行真实多模态解释。
- 解析备注：无

### 关键 takeaway
- 先完成可跑流水线，确保原文、状态库、站点和后续人工复核链路全部就位。
- 当前片段需要在接入真实模型后重新生成。

## Section 5

> 待复核：该片段的文本提取或翻译结果置信度偏低。

### 中文翻译
> 当前使用 `mock` 翻译器，已保留原始片段作为待精读材料。

[Page 5] SWE-Edit: Rethinking Code Editing for Efficient SWE-Agent Input Editing Task Code Snippet + Instruction Analyze Scope & Structural Complexity timeout = 5 ======= timeout = 10 >>>>>>> REPLACE <<<<<<< SEARCH def fetch_data(url):` # ... (entire function body rewritten)` try: response = requests.get(url, timeout=10) # ... Pros: Cost-efficient, Precise. Cons: Sensitive to context boundaries. Mode A: FInd-Replace (Precise, Localized) Mode B: Whole-File Rewrite (Structural, Multi-line) Adap...

### 术语解释
- `待接入模型`：此处应该由真实大模型输出逐句翻译和术语解释。
- `当前建议`：优先配置 OpenAI 兼容接口，或将该 chunk 交给本地智能体平台执行。

### 图表/公式说明
- 当前 chunk 未进行真实多模态解释。
- 解析备注：无

### 关键 takeaway
- 先完成可跑流水线，确保原文、状态库、站点和后续人工复核链路全部就位。
- 当前片段需要在接入真实模型后重新生成。

## Section 6

> 待复核：该片段的文本提取或翻译结果置信度偏低。

### 中文翻译
> 当前使用 `mock` 翻译器，已保留原始片段作为待精读材料。

[Page 6] SWE-Edit: Rethinking Code Editing for Efficient SWE-Agent Table 2. Viewer vs. retrieval baselines on 50 held-out PR-Edit instances. Ground-truth relevant lines are taken from the PR diff. The LLM viewer achieves the highest recall and F1 while substan- tially reducing context. “Ctx. Red.” is the percentage of the input file that is omitted from the returned snippets. Method Recall Prec. F1 Ctx. Red. LLM Viewer (GPT-5-mini) 0.938 0.179 0.272 60.3% Dense (text-embedding-3-small) 0.868...

### 术语解释
- `待接入模型`：此处应该由真实大模型输出逐句翻译和术语解释。
- `当前建议`：优先配置 OpenAI 兼容接口，或将该 chunk 交给本地智能体平台执行。

### 图表/公式说明
- 当前 chunk 未进行真实多模态解释。
- 解析备注：无

### 关键 takeaway
- 先完成可跑流水线，确保原文、状态库、站点和后续人工复核链路全部就位。
- 当前片段需要在接入真实模型后重新生成。

## Section 7

> 待复核：该片段的文本提取或翻译结果置信度偏低。

### 中文翻译
> 当前使用 `mock` 翻译器，已保留原始片段作为待精读材料。

[Page 7] SWE-Edit: Rethinking Code Editing for Efficient SWE-Agent Table 4. Results on PR-Edit Benchmark. GRPO training substantially improves Qwen3-8B, achieving performance comparable to GPT-5-nano. Model Format (%) GPT Grader (%) Norm. Match (%) Qwen3-8B 76.8 56.0 32.0 Qwen3-8B + GRPO 90.4 68.4 38.8 GPT-5-nano 89.8 66.4 38.8 GPT-5-mini 96.1 77.5 41.7 GPT-5 98.1 77.2 44.1 Table 5. Downstream performance on SWE-bench Verified with different editor models. Higher PR-Edit scores predict better...

### 术语解释
- `待接入模型`：此处应该由真实大模型输出逐句翻译和术语解释。
- `当前建议`：优先配置 OpenAI 兼容接口，或将该 chunk 交给本地智能体平台执行。

### 图表/公式说明
- 当前 chunk 未进行真实多模态解释。
- 解析备注：无

### 关键 takeaway
- 先完成可跑流水线，确保原文、状态库、站点和后续人工复核链路全部就位。
- 当前片段需要在接入真实模型后重新生成。

## Section 8

> 待复核：该片段的文本提取或翻译结果置信度偏低。

### 中文翻译
> 当前使用 `mock` 翻译器，已保留原始片段作为待精读材料。

[Page 8] SWE-Edit: Rethinking Code Editing for Efficient SWE-Agent Grader is used only for the PR-Edit intermediate bench- mark; our main SWE-bench Verified evaluation is fully execution-based (patches are applied and the full repository test suite is run). The validity of the GPT Grader as a proxy is supported by its strong correlation with this downstream test-based metric (Figure 4): models that score higher on the GPT Grader consistently achieve higher SWE-bench resolve rates. 4.3.2. EVAL...

### 术语解释
- `待接入模型`：此处应该由真实大模型输出逐句翻译和术语解释。
- `当前建议`：优先配置 OpenAI 兼容接口，或将该 chunk 交给本地智能体平台执行。

### 图表/公式说明
- 当前 chunk 未进行真实多模态解释。
- 解析备注：无

### 关键 takeaway
- 先完成可跑流水线，确保原文、状态库、站点和后续人工复核链路全部就位。
- 当前片段需要在接入真实模型后重新生成。

## Section 9

> 待复核：该片段的文本提取或翻译结果置信度偏低。

### 中文翻译
> 当前使用 `mock` 翻译器，已保留原始片段作为待精读材料。

[Page 9] SWE-Edit: Rethinking Code Editing for Efficient SWE-Agent Figure 5. Training dynamics for fixed vs. adaptive format selection. The y-axis is validation reward (normalized match) and the x-axis is the rollout step. While fixed find-replace starts higher (simpler format, easier to learn), adaptive training surpasses it by learning when to invoke whole-file rewrite. Table 7. Effect of editor model scale. Stronger models show diminishing returns: GPT-5 provides minimal accuracy gain at 5...

### 术语解释
- `待接入模型`：此处应该由真实大模型输出逐句翻译和术语解释。
- `当前建议`：优先配置 OpenAI 兼容接口，或将该 chunk 交给本地智能体平台执行。

### 图表/公式说明
- 当前 chunk 未进行真实多模态解释。
- 解析备注：无

### 关键 takeaway
- 先完成可跑流水线，确保原文、状态库、站点和后续人工复核链路全部就位。
- 当前片段需要在接入真实模型后重新生成。

## Section 10

> 待复核：该片段的文本提取或翻译结果置信度偏低。

### 中文翻译
> 当前使用 `mock` 翻译器，已保留原始片段作为待精读材料。

[Page 10] SWE-Edit: Rethinking Code Editing for Efficient SWE-Agent With PR-Edit in place, RL-based editor training becomes practical, and we show that GRPO with a normalized match reward yields a 12.5pp improvement in edit success on a small open-source backbone (Qwen3-8B), substantially ex- ceeding what model scaling alone provides. Together, these three pieces—scaffold, benchmark, and training—provide a deployable and cost-efficient recipe for code-editing sub- agents. One limitation of ou...

### 术语解释
- `待接入模型`：此处应该由真实大模型输出逐句翻译和术语解释。
- `当前建议`：优先配置 OpenAI 兼容接口，或将该 chunk 交给本地智能体平台执行。

### 图表/公式说明
- 当前 chunk 未进行真实多模态解释。
- 解析备注：无

### 关键 takeaway
- 先完成可跑流水线，确保原文、状态库、站点和后续人工复核链路全部就位。
- 当前片段需要在接入真实模型后重新生成。

## Section 11

> 待复核：该片段的文本提取或翻译结果置信度偏低。

### 中文翻译
> 当前使用 `mock` 翻译器，已保留原始片段作为待精读材料。

[Page 11] SWE-Edit: Rethinking Code Editing for Efficient SWE-Agent Sun, W., Lu, M., Ling, Z., Liu, K., Yao, X., Yang, Y., and Chen, J. Scaling long-horizon llm agent via context- folding. arXiv preprint arXiv:2510.11967, 2025. Wang, H., Hou, Z., Wei, Y., Tang, J., and Dong, Y. Swe- dev: Building software engineering agents with training and inference scaling. arXiv preprint arXiv:2506.07636, 2025. Wang, X., Li, B., Song, Y., Xu, F. F., Tang, X., Zhuge, M., Pan, J., Song, Y., Li, B., Singh, J...

### 术语解释
- `待接入模型`：此处应该由真实大模型输出逐句翻译和术语解释。
- `当前建议`：优先配置 OpenAI 兼容接口，或将该 chunk 交给本地智能体平台执行。

### 图表/公式说明
- 当前 chunk 未进行真实多模态解释。
- 解析备注：无

### 关键 takeaway
- 先完成可跑流水线，确保原文、状态库、站点和后续人工复核链路全部就位。
- 当前片段需要在接入真实模型后重新生成。

## Section 12

> 待复核：该片段的文本提取或翻译结果置信度偏低。

### 中文翻译
> 当前使用 `mock` 翻译器，已保留原始片段作为待精读材料。

[Page 12] SWE-Edit: Rethinking Code Editing for Efficient SWE-Agent A. Implementation Details This appendix provides full details of the agent scaffolding, tool definitions, and prompts used in our experiments. A.1. Baseline Agent Scaffolding We adopt the reference agent scaffolding from Anthropic (Schluntz, 2025), which equips the agent with two tools: execute bash for shell command execution and str replace editor for file operations. The editor tool provides sub-commands for viewing, creat...

### 术语解释
- `待接入模型`：此处应该由真实大模型输出逐句翻译和术语解释。
- `当前建议`：优先配置 OpenAI 兼容接口，或将该 chunk 交给本地智能体平台执行。

### 图表/公式说明
- 当前 chunk 未进行真实多模态解释。
- 解析备注：无

### 关键 takeaway
- 先完成可跑流水线，确保原文、状态库、站点和后续人工复核链路全部就位。
- 当前片段需要在接入真实模型后重新生成。

## Section 13

> 待复核：该片段的文本提取或翻译结果置信度偏低。

### 中文翻译
> 当前使用 `mock` 翻译器，已保留原始片段作为待精读材料。

[Page 13] SWE-Edit: Rethinking Code Editing for Efficient SWE-Agent directories up to 2 levels deep\n* If ‘path‘ is a file, ‘view‘ uses AI to find and display only the sections relevant to your ‘query‘\n* The ‘create‘ command cannot be used if the specified ‘path‘ already exists as a file\n\nNotes for using the ‘view‘ command:\n* Provide a ‘query‘ describing what you’re looking for (e.g., \" Where is user authentication handled?\", \"Show me the class definition for User\")\n* The tool reads...

### 术语解释
- `待接入模型`：此处应该由真实大模型输出逐句翻译和术语解释。
- `当前建议`：优先配置 OpenAI 兼容接口，或将该 chunk 交给本地智能体平台执行。

### 图表/公式说明
- 当前 chunk 未进行真实多模态解释。
- 解析备注：无

### 关键 takeaway
- 先完成可跑流水线，确保原文、状态库、站点和后续人工复核链路全部就位。
- 当前片段需要在接入真实模型后重新生成。

## Section 14

> 待复核：该片段的文本提取或翻译结果置信度偏低。

### 中文翻译
> 当前使用 `mock` 翻译器，已保留原始片段作为待精读材料。

[Page 14] SWE-Edit: Rethinking Code Editing for Efficient SWE-Agent 1-indexed). Example output: [[10, 25], [45, 60], [100, 115]] RULES: 1. Only output the JSON array, no additional explanation or comments 2. Line numbers are 1-indexed (first line is line 1) 3. Each range should include complete logical blocks (don’t cut functions/classes in the middle) 4. Include a few lines of context before and after each relevant section when appropriate 5. If nothing in the file is relevant to the query,...

### 术语解释
- `待接入模型`：此处应该由真实大模型输出逐句翻译和术语解释。
- `当前建议`：优先配置 OpenAI 兼容接口，或将该 chunk 交给本地智能体平台执行。

### 图表/公式说明
- 当前 chunk 未进行真实多模态解释。
- 解析备注：无

### 关键 takeaway
- 先完成可跑流水线，确保原文、状态库、站点和后续人工复核链路全部就位。
- 当前片段需要在接入真实模型后重新生成。

## Section 15

> 待复核：该片段的文本提取或翻译结果置信度偏低。

### 中文翻译
> 当前使用 `mock` 翻译器，已保留原始片段作为待精读材料。

[Page 16] SWE-Edit: Rethinking Code Editing for Efficient SWE-Agent {{ instance.problem_statement }} </issue_description> Can you help me implement the necessary changes to the repository so that the requirements specified in the <issue_description> are met? I’ve already taken care of all changes to any of the test files described in the <issue_description>. This means you DON’T have to modify the testing logic or any of the tests in any way! Also the development Python environment is already...

### 术语解释
- `待接入模型`：此处应该由真实大模型输出逐句翻译和术语解释。
- `当前建议`：优先配置 OpenAI 兼容接口，或将该 chunk 交给本地智能体平台执行。

### 图表/公式说明
- 当前 chunk 未进行真实多模态解释。
- 解析备注：无

### 关键 takeaway
- 先完成可跑流水线，确保原文、状态库、站点和后续人工复核链路全部就位。
- 当前片段需要在接入真实模型后重新生成。

## Section 16

> 待复核：该片段的文本提取或翻译结果置信度偏低。

### 中文翻译
> 当前使用 `mock` 翻译器，已保留原始片段作为待精读材料。

[Page 17] SWE-Edit: Rethinking Code Editing for Efficient SWE-Agent Table 9. Per-run mean±std on SWE-bench Verified (500 instances, 3 runs). Configuration Resolved (%) Cost ($) Edit Succ. (%) Baseline 69.9 ± 0.6 243.7 ± 6.5 93.4 ± 0.8 + Viewer 70.3 ± 1.6 225.0 ± 5.6 94.3 ± 0.3 + Editor 71.3 ± 0.2 268.3 ± 19.3 96.1 ± 0.2 SWE-Edit 72.0 ± 0.0 200.1 ± 16.8 96.9 ± 0.1 learned via reinforcement learning rather than via prompting. C. PR-Edit Benchmark This section provides implementation details for...

### 术语解释
- `待接入模型`：此处应该由真实大模型输出逐句翻译和术语解释。
- `当前建议`：优先配置 OpenAI 兼容接口，或将该 chunk 交给本地智能体平台执行。

### 图表/公式说明
- 当前 chunk 未进行真实多模态解释。
- 解析备注：无

### 关键 takeaway
- 先完成可跑流水线，确保原文、状态库、站点和后续人工复核链路全部就位。
- 当前片段需要在接入真实模型后重新生成。

## Section 17

> 待复核：该片段的文本提取或翻译结果置信度偏低。

### 中文翻译
> 当前使用 `mock` 翻译器，已保留原始片段作为待精读材料。

[Page 19] SWE-Edit: Rethinking Code Editing for Efficient SWE-Agent # for issue #4093 def test_odd_size(): data = BytesIO() width = 100 im = Image.new("F", (width, 64)) im.save(data, format="SPIDER") data.seek(0) with Image.open(data) as im2: assert_image_equal(im, im2) Ground Truth (excerpt) import tempfile from io import BytesIO import pytest from PIL import Image, ImageSequence, SpiderImagePlugin from .helper import assert_image_equal_tofile, hopper, is_pypy TEST_FILE = "Tests/images/hoppe...

### 术语解释
- `待接入模型`：此处应该由真实大模型输出逐句翻译和术语解释。
- `当前建议`：优先配置 OpenAI 兼容接口，或将该 chunk 交给本地智能体平台执行。

### 图表/公式说明
- 当前 chunk 未进行真实多模态解释。
- 解析备注：无

### 关键 takeaway
- 先完成可跑流水线，确保原文、状态库、站点和后续人工复核链路全部就位。
- 当前片段需要在接入真实模型后重新生成。

## 复核建议

- 对关键公式、表格和实验结论做抽样核对。
- 如已接入真实模型，可重新运行该论文以覆盖 mock 内容。
