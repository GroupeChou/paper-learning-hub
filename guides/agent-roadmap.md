# AI Agent 路线 · 论文导引

> 每日自动更新。每篇论文仅记录标题（中英对照）+ 简短说明。
> 不做翻译，不做精读，仅作导引用。
> 最新论文在顶部。

---

## 经典基石（必读）

- **ReAct: Synergizing Reasoning and Acting in Language Models** (推理与行动的协同) | Yao et al. | Google / Princeton | 2023
  [arXiv](https://arxiv.org/abs/2210.03629) — Agent 推理+行动的经典起点，提出交错推理和行动的范式。

- **Toolformer: Language Models Can Teach Themselves to Use Tools** (语言模型自学习工具调用) | Schick et al. | Meta AI | 2023
  [arXiv](https://arxiv.org/abs/2302.04761) — 语言模型自主学习调用外部工具的经典工作。

- **Generative Agents: Interactive Simulacra of Human Behavior** (生成式智能体：人类行为的交互模拟) | Park et al. | Google / Stanford | 2023
  [arXiv](https://arxiv.org/abs/2304.03442) — 记忆、规划、反思三段式 Agent 架构的重要来源。

- **Chain-of-Thought Prompting Elicits Reasoning in Large Language Models** (思维链提示激发推理能力) | Wei et al. | Google | 2022
  [arXiv](https://arxiv.org/abs/2201.11903) — CoT 推理的奠基工作，影响所有 Agent 的推理设计。

- **Tree of Thoughts: Deliberate Problem Solving with Large Language Models** (思维树：有意识的 LLM 问题求解) | Yao et al. | Princeton / Google | 2023
  [arXiv](https://arxiv.org/abs/2305.10601) — 将 CoT 扩展为树搜索，支持多路径推理探索。

## 多智能体协作

- **AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation** (AutoGen：通过多智能体会话赋能下一代 LLM 应用) | Wu et al. | Microsoft | 2023
  [arXiv](https://arxiv.org/abs/2308.08155) — 微软的多智能体对话框架，支持多种角色分工协作。

- **ChatDev: Communicative Agents for Software Development** (ChatDev：用于软件开发的通讯智能体) | Qian et al. | 清华大学 | 2023
  [arXiv](https://arxiv.org/abs/2307.07924) — 多智能体协作开发的代表作，Agent 各自扮演不同角色协作完成软件工程。

---

> 每日自动更新于 2026-05-17

## 每日自动追加

_以下论文由系统在 2026-05-29 自动追加_

- [Agent Explorative Policy Optimization for Multimodal Agentic Reasoning](../papers/2605.28774v1/index.md) | AI Agent-核心 | 2026-05-27

- [VeriTrip: A Verifiable Benchmark for Travel Planning Agents over Unstructured Web Corpora](../papers/2605.28683v1/index.md) | AI Agent-核心 | 2026-05-27
- [Do Agents Need Semantic Metadata? A Comparative Study in Agentic Data Retrieval](../papers/2605.28787v1/index.md) | AI Agent-核心 | 2026-05-27
- [MOSS: Self-Evolution through Source-Level Rewriting in Autonomous Agent Systems](../papers/2605.22794v1/index.md) | AI Agent-核心 | 2026-05-21
- [Learn from Weaknesses: Automated Domain Specialization for Small Computer-Use Agents](../papers/2605.28775v1/index.md) | AI Agent-核心 | 2026-05-27
- [Self-Evolving Multi-Agent Systems via Decentralized Memory](../papers/2605.22721v1/index.md) | AI Agent-核心 | 2026-05-21
- [WorkstreamBench: Evaluating LLM Agents on End-to-End Spreadsheet Tasks in Finance](../papers/2605.22664v1/index.md) | AI Agent-核心 | 2026-05-21
- [EnvFactory: Scaling Tool-Use Agents via Executable Environments Synthesis and Robust RL](../papers/2605.18703v1/index.md) | AI Agent-核心 | 2026-05-18
- [SkillGenBench: Benchmarking Skill Generation Pipelines for LLM Agents](../papers/2605.18693v1/index.md) | AI Agent-核心 | 2026-05-18
- [Overeager Coding Agents: Measuring Out-of-Scope Actions on Benign Tasks](../papers/2605.18583v1/index.md) | AI Agent-核心 | 2026-05-18
- [HiveMind: OS-Inspired Scheduling for Concurrent LLM Agent Workloads](../papers/2604.17111v1/index.md) | OpenAI | 2026-04-18
- [Spatial Atlas: Compute-Grounded Reasoning for Spatial-Aware Research Agent Benchmarks](../papers/2604.12102v2/index.md) | OpenAI | 2026-04-13
- [When Agents Look the Same: Quantifying Distillation-Induced Similarity in Tool-Use Behaviors](../papers/2604.21255v1/index.md) | Anthropic | 2026-04-23
- [Reasoning-targeted Jailbreak Attacks on Large Reasoning Models via Semantic Triggers and Psychological Framing](../papers/2604.15725v1/index.md) | OpenAI | 2026-04-17
- [ArguAgent: AI-Supported Real-Time Grouping for Productive Argumentation in STEM Classrooms](../papers/2604.23449v1/index.md) | OpenAI | 2026-04-25
- [Benchmarks for Trajectory Safety Evaluation and Diagnosis in OpenClaw and Codex: ATBench-Claw and ATBench-CodeX](../papers/2604.14858v1/index.md) | OpenAI | 2026-04-16
- [Evaluating Multi-Hop Reasoning in RAG Systems: A Comparison of LLM-Based Retriever Evaluation Strategies](../papers/2604.18234v1/index.md) | OpenAI | 2026-04-20
- [Beyond the Attention Stability Boundary: Agentic Self-Synthesizing Reasoning Protocols](../papers/2604.24512v1/index.md) | DeepSeek | 2026-04-27
- [Local-Splitter: A Measurement Study of Seven Tactics for Reducing Cloud LLM Token Usage on Coding-Agent Workloads](../papers/2604.12301v1/index.md) | OpenAI | 2026-04-14
- [Narrative over Numbers: The Identifiable Victim Effect and its Amplification Under Alignment and Reasoning in Large Language Models](../papers/2604.12076v1/index.md) | OpenAI | 2026-04-13
- [Cross-Session Threats in AI Agents: Benchmark, Evaluation, and Algorithms](../papers/2604.21131v1/index.md) | Anthropic | 2026-04-22
- [Strategic Heterogeneous Multi-Agent Architecture for Cost-Effective Code Vulnerability Detection](../papers/2604.21282v1/index.md) | DeepSeek | 2026-04-23
- [Skilldex: A Package Manager and Registry for Agent Skill Packages with Hierarchical Scope-Based Distribution](../papers/2604.16911v1/index.md) | Anthropic | 2026-04-18
- [Less Languages, Less Tokens: An Efficient Unified Logic Cross-lingual Chain-of-Thought Reasoning Framework](../papers/2604.20090v1/index.md) | DeepSeek | 2026-04-22
- [First, Do No Harm (With LLMs): Mitigating Racial Bias via Agentic Workflows](../papers/2604.18038v1/index.md) | DeepSeek | 2026-04-20
- [Do LLMs Game Formalization? Evaluating Faithfulness in Logical Reasoning](../papers/2604.19459v1/index.md) | DeepSeek | 2026-04-21
- [ReflectMT: Internalizing Reflection for Efficient and High-Quality Machine Translation](../papers/2604.19144v1/index.md) | DeepSeek | 2026-04-21
- [MathNet: a Global Multimodal Benchmark for Mathematical Reasoning and Retrieval](../papers/2604.18584v1/index.md) | DeepSeek | 2026-04-20
- [Owner-Harm: A Missing Threat Model for AI Agent Safety](../papers/2604.18658v1/index.md) | Microsoft | 2026-04-20
- [Learning to Evolve: A Self-Improving Framework for Multi-Agent Systems via Textual Parameter Graph Optimization](../papers/2604.20714v1/index.md) | Meta FAIR | 2026-04-22
- [SWE-Edit: Rethinking Code Editing for Efficient SWE-Agent](../papers/2604.26102v1/index.md) | Microsoft | 2026-04-28
- [The Last Harness You'll Ever Build](../papers/2604.21003v1/index.md) | Meta FAIR | 2026-04-22
- [Context Kubernetes: Declarative Orchestration of Enterprise Knowledge for Agentic AI Systems](../papers/2604.11623v3/index.md) | Microsoft | 2026-04-13
- [FairQE: Multi-Agent Framework for Mitigating Gender Bias in Translation Quality Estimation](../papers/2604.21420v1/index.md) | Meta FAIR | 2026-04-23
- [A Self-Evolving Framework for Efficient Terminal Agents via Observational Context Compression](../papers/2604.19572v1/index.md) | MiniMax | 2026-04-21
- [Terminus-4B: Can a Smaller Model Replace Frontier LLMs at Agentic Execution Tasks?](../papers/2605.03195v1/index.md) | 阿里通义 | 2026-05-04
- [Agentic Aggregation for Parallel Scaling of Long-Horizon Agentic Tasks](../papers/2604.11753v1/index.md) | 智谱 | 2026-04-13
- [Nemobot Games: Crafting Strategic AI Gaming Agents for Interactive Learning with Large Language Models](../papers/2604.21896v1/index.md) | MiniMax | 2026-04-23
- [M2-PALE: A Framework for Explaining Multi-Agent MCTS--Minimax Hybrids via Process Mining and LLMs](../papers/2604.14687v1/index.md) | MiniMax | 2026-04-16
- [QuantClaw: Precision Where It Matters for OpenClaw](../papers/2604.22577v1/index.md) | 智谱 | 2026-04-24
- [AeSlides: Incentivizing Aesthetic Layout in LLM-Based Slide Generation via Verifiable Rewards](../papers/2604.22840v1/index.md) | 智谱 | 2026-04-21
- [What Happens Inside Agent Memory? Circuit Analysis from Emergence to Diagnosis](../papers/2605.03354v1/index.md) | 阿里通义 | 2026-05-05
- [SafetyALFRED: Evaluating Safety-Conscious Planning of Multimodal Large Language Models](../papers/2604.19638v1/index.md) | 阿里通义 | 2026-04-21
- [ComPASS: Towards Personalized Agentic Social Support via Tool-Augmented Companionship](../papers/2604.18356v1/index.md) | 阿里通义 | 2026-04-20
- [DataEvolver: Let Your Data Build and Improve Itself via Goal-Driven Loop Agents](../papers/2605.01789v1/index.md) | 阿里通义 | 2026-05-03
- [Quantum Knowledge Graph: Modeling Context-Dependent Triplet Validity](../papers/2604.23972v1/index.md) | 阿里通义 | 2026-04-27
- [Training and Agentic Inference Strategies for LLM-based Manim Animation Generation](../papers/2604.18364v1/index.md) | 阿里通义 | 2026-04-20
- [Agri-CPJ: A Training-Free Explainable Framework for Agricultural Pest Diagnosis Using Caption-Prompt-Judge and LLM-as-a-Judge](../papers/2604.23701v1/index.md) | 阿里通义 | 2026-04-26
- [Agent Explorative Policy Optimization for Multimodal Agentic Reasoning](../papers/2605.28774v1/index.md) | AI Agent-核心 | 2026-05-27
- [VeriTrip: A Verifiable Benchmark for Travel Planning Agents over Unstructured Web Corpora](../papers/2605.28683v1/index.md) | AI Agent-核心 | 2026-05-27
- [Do Agents Need Semantic Metadata? A Comparative Study in Agentic Data Retrieval](../papers/2605.28787v1/index.md) | AI Agent-核心 | 2026-05-27
- [MOSS: Self-Evolution through Source-Level Rewriting in Autonomous Agent Systems](../papers/2605.22794v1/index.md) | AI Agent-核心 | 2026-05-21
- [Learn from Weaknesses: Automated Domain Specialization for Small Computer-Use Agents](../papers/2605.28775v1/index.md) | AI Agent-核心 | 2026-05-27
- [Self-Evolving Multi-Agent Systems via Decentralized Memory](../papers/2605.22721v1/index.md) | AI Agent-核心 | 2026-05-21
- [WorkstreamBench: Evaluating LLM Agents on End-to-End Spreadsheet Tasks in Finance](../papers/2605.22664v1/index.md) | AI Agent-核心 | 2026-05-21
- [EnvFactory: Scaling Tool-Use Agents via Executable Environments Synthesis and Robust RL](../papers/2605.18703v1/index.md) | AI Agent-核心 | 2026-05-18
- [SkillGenBench: Benchmarking Skill Generation Pipelines for LLM Agents](../papers/2605.18693v1/index.md) | AI Agent-核心 | 2026-05-18
- [Overeager Coding Agents: Measuring Out-of-Scope Actions on Benign Tasks](../papers/2605.18583v1/index.md) | AI Agent-核心 | 2026-05-18
- [HiveMind: OS-Inspired Scheduling for Concurrent LLM Agent Workloads](../papers/2604.17111v1/index.md) | OpenAI | 2026-04-18
- [Spatial Atlas: Compute-Grounded Reasoning for Spatial-Aware Research Agent Benchmarks](../papers/2604.12102v2/index.md) | OpenAI | 2026-04-13
- [When Agents Look the Same: Quantifying Distillation-Induced Similarity in Tool-Use Behaviors](../papers/2604.21255v1/index.md) | Anthropic | 2026-04-23
- [Reasoning-targeted Jailbreak Attacks on Large Reasoning Models via Semantic Triggers and Psychological Framing](../papers/2604.15725v1/index.md) | OpenAI | 2026-04-17
- [ArguAgent: AI-Supported Real-Time Grouping for Productive Argumentation in STEM Classrooms](../papers/2604.23449v1/index.md) | OpenAI | 2026-04-25
- [Benchmarks for Trajectory Safety Evaluation and Diagnosis in OpenClaw and Codex: ATBench-Claw and ATBench-CodeX](../papers/2604.14858v1/index.md) | OpenAI | 2026-04-16
- [Evaluating Multi-Hop Reasoning in RAG Systems: A Comparison of LLM-Based Retriever Evaluation Strategies](../papers/2604.18234v1/index.md) | OpenAI | 2026-04-20
- [Beyond the Attention Stability Boundary: Agentic Self-Synthesizing Reasoning Protocols](../papers/2604.24512v1/index.md) | DeepSeek | 2026-04-27
- [Local-Splitter: A Measurement Study of Seven Tactics for Reducing Cloud LLM Token Usage on Coding-Agent Workloads](../papers/2604.12301v1/index.md) | OpenAI | 2026-04-14
- [Narrative over Numbers: The Identifiable Victim Effect and its Amplification Under Alignment and Reasoning in Large Language Models](../papers/2604.12076v1/index.md) | OpenAI | 2026-04-13
- [Cross-Session Threats in AI Agents: Benchmark, Evaluation, and Algorithms](../papers/2604.21131v1/index.md) | Anthropic | 2026-04-22
- [Strategic Heterogeneous Multi-Agent Architecture for Cost-Effective Code Vulnerability Detection](../papers/2604.21282v1/index.md) | DeepSeek | 2026-04-23
- [Skilldex: A Package Manager and Registry for Agent Skill Packages with Hierarchical Scope-Based Distribution](../papers/2604.16911v1/index.md) | Anthropic | 2026-04-18
- [Less Languages, Less Tokens: An Efficient Unified Logic Cross-lingual Chain-of-Thought Reasoning Framework](../papers/2604.20090v1/index.md) | DeepSeek | 2026-04-22
- [First, Do No Harm (With LLMs): Mitigating Racial Bias via Agentic Workflows](../papers/2604.18038v1/index.md) | DeepSeek | 2026-04-20
- [Do LLMs Game Formalization? Evaluating Faithfulness in Logical Reasoning](../papers/2604.19459v1/index.md) | DeepSeek | 2026-04-21
- [ReflectMT: Internalizing Reflection for Efficient and High-Quality Machine Translation](../papers/2604.19144v1/index.md) | DeepSeek | 2026-04-21
- [MathNet: a Global Multimodal Benchmark for Mathematical Reasoning and Retrieval](../papers/2604.18584v1/index.md) | DeepSeek | 2026-04-20
- [Owner-Harm: A Missing Threat Model for AI Agent Safety](../papers/2604.18658v1/index.md) | Microsoft | 2026-04-20
- [Learning to Evolve: A Self-Improving Framework for Multi-Agent Systems via Textual Parameter Graph Optimization](../papers/2604.20714v1/index.md) | Meta FAIR | 2026-04-22
- [SWE-Edit: Rethinking Code Editing for Efficient SWE-Agent](../papers/2604.26102v1/index.md) | Microsoft | 2026-04-28
- [The Last Harness You'll Ever Build](../papers/2604.21003v1/index.md) | Meta FAIR | 2026-04-22
- [Context Kubernetes: Declarative Orchestration of Enterprise Knowledge for Agentic AI Systems](../papers/2604.11623v3/index.md) | Microsoft | 2026-04-13
- [FairQE: Multi-Agent Framework for Mitigating Gender Bias in Translation Quality Estimation](../papers/2604.21420v1/index.md) | Meta FAIR | 2026-04-23
- [A Self-Evolving Framework for Efficient Terminal Agents via Observational Context Compression](../papers/2604.19572v1/index.md) | MiniMax | 2026-04-21
- [Terminus-4B: Can a Smaller Model Replace Frontier LLMs at Agentic Execution Tasks?](../papers/2605.03195v1/index.md) | 阿里通义 | 2026-05-04
- [Agentic Aggregation for Parallel Scaling of Long-Horizon Agentic Tasks](../papers/2604.11753v1/index.md) | 智谱 | 2026-04-13
- [Nemobot Games: Crafting Strategic AI Gaming Agents for Interactive Learning with Large Language Models](../papers/2604.21896v1/index.md) | MiniMax | 2026-04-23
- [M2-PALE: A Framework for Explaining Multi-Agent MCTS--Minimax Hybrids via Process Mining and LLMs](../papers/2604.14687v1/index.md) | MiniMax | 2026-04-16
- [QuantClaw: Precision Where It Matters for OpenClaw](../papers/2604.22577v1/index.md) | 智谱 | 2026-04-24
- [AeSlides: Incentivizing Aesthetic Layout in LLM-Based Slide Generation via Verifiable Rewards](../papers/2604.22840v1/index.md) | 智谱 | 2026-04-21
- [What Happens Inside Agent Memory? Circuit Analysis from Emergence to Diagnosis](../papers/2605.03354v1/index.md) | 阿里通义 | 2026-05-05
- [SafetyALFRED: Evaluating Safety-Conscious Planning of Multimodal Large Language Models](../papers/2604.19638v1/index.md) | 阿里通义 | 2026-04-21
- [ComPASS: Towards Personalized Agentic Social Support via Tool-Augmented Companionship](../papers/2604.18356v1/index.md) | 阿里通义 | 2026-04-20
- [DataEvolver: Let Your Data Build and Improve Itself via Goal-Driven Loop Agents](../papers/2605.01789v1/index.md) | 阿里通义 | 2026-05-03
- [Quantum Knowledge Graph: Modeling Context-Dependent Triplet Validity](../papers/2604.23972v1/index.md) | 阿里通义 | 2026-04-27
- [Training and Agentic Inference Strategies for LLM-based Manim Animation Generation](../papers/2604.18364v1/index.md) | 阿里通义 | 2026-04-20
- [Agri-CPJ: A Training-Free Explainable Framework for Agricultural Pest Diagnosis Using Caption-Prompt-Judge and LLM-as-a-Judge](../papers/2604.23701v1/index.md) | 阿里通义 | 2026-04-26
- [Agent Explorative Policy Optimization for Multimodal Agentic Reasoning](../papers/2605.28774v1/index.md) | AI Agent-核心 | 2026-05-27
- [VeriTrip: A Verifiable Benchmark for Travel Planning Agents over Unstructured Web Corpora](../papers/2605.28683v1/index.md) | AI Agent-核心 | 2026-05-27
- [Do Agents Need Semantic Metadata? A Comparative Study in Agentic Data Retrieval](../papers/2605.28787v1/index.md) | AI Agent-核心 | 2026-05-27
- [MOSS: Self-Evolution through Source-Level Rewriting in Autonomous Agent Systems](../papers/2605.22794v1/index.md) | AI Agent-核心 | 2026-05-21
- [Learn from Weaknesses: Automated Domain Specialization for Small Computer-Use Agents](../papers/2605.28775v1/index.md) | AI Agent-核心 | 2026-05-27
- [Self-Evolving Multi-Agent Systems via Decentralized Memory](../papers/2605.22721v1/index.md) | AI Agent-核心 | 2026-05-21
- [WorkstreamBench: Evaluating LLM Agents on End-to-End Spreadsheet Tasks in Finance](../papers/2605.22664v1/index.md) | AI Agent-核心 | 2026-05-21
- [EnvFactory: Scaling Tool-Use Agents via Executable Environments Synthesis and Robust RL](../papers/2605.18703v1/index.md) | AI Agent-核心 | 2026-05-18
- [SkillGenBench: Benchmarking Skill Generation Pipelines for LLM Agents](../papers/2605.18693v1/index.md) | AI Agent-核心 | 2026-05-18
- [Overeager Coding Agents: Measuring Out-of-Scope Actions on Benign Tasks](../papers/2605.18583v1/index.md) | AI Agent-核心 | 2026-05-18
- [HiveMind: OS-Inspired Scheduling for Concurrent LLM Agent Workloads](../papers/2604.17111v1/index.md) | OpenAI | 2026-04-18
- [Spatial Atlas: Compute-Grounded Reasoning for Spatial-Aware Research Agent Benchmarks](../papers/2604.12102v2/index.md) | OpenAI | 2026-04-13
- [When Agents Look the Same: Quantifying Distillation-Induced Similarity in Tool-Use Behaviors](../papers/2604.21255v1/index.md) | Anthropic | 2026-04-23
- [Reasoning-targeted Jailbreak Attacks on Large Reasoning Models via Semantic Triggers and Psychological Framing](../papers/2604.15725v1/index.md) | OpenAI | 2026-04-17
- [ArguAgent: AI-Supported Real-Time Grouping for Productive Argumentation in STEM Classrooms](../papers/2604.23449v1/index.md) | OpenAI | 2026-04-25
- [Benchmarks for Trajectory Safety Evaluation and Diagnosis in OpenClaw and Codex: ATBench-Claw and ATBench-CodeX](../papers/2604.14858v1/index.md) | OpenAI | 2026-04-16
- [Evaluating Multi-Hop Reasoning in RAG Systems: A Comparison of LLM-Based Retriever Evaluation Strategies](../papers/2604.18234v1/index.md) | OpenAI | 2026-04-20
- [Beyond the Attention Stability Boundary: Agentic Self-Synthesizing Reasoning Protocols](../papers/2604.24512v1/index.md) | DeepSeek | 2026-04-27
- [Local-Splitter: A Measurement Study of Seven Tactics for Reducing Cloud LLM Token Usage on Coding-Agent Workloads](../papers/2604.12301v1/index.md) | OpenAI | 2026-04-14
- [Narrative over Numbers: The Identifiable Victim Effect and its Amplification Under Alignment and Reasoning in Large Language Models](../papers/2604.12076v1/index.md) | OpenAI | 2026-04-13
- [Cross-Session Threats in AI Agents: Benchmark, Evaluation, and Algorithms](../papers/2604.21131v1/index.md) | Anthropic | 2026-04-22
- [Strategic Heterogeneous Multi-Agent Architecture for Cost-Effective Code Vulnerability Detection](../papers/2604.21282v1/index.md) | DeepSeek | 2026-04-23
- [Skilldex: A Package Manager and Registry for Agent Skill Packages with Hierarchical Scope-Based Distribution](../papers/2604.16911v1/index.md) | Anthropic | 2026-04-18
- [Less Languages, Less Tokens: An Efficient Unified Logic Cross-lingual Chain-of-Thought Reasoning Framework](../papers/2604.20090v1/index.md) | DeepSeek | 2026-04-22
- [First, Do No Harm (With LLMs): Mitigating Racial Bias via Agentic Workflows](../papers/2604.18038v1/index.md) | DeepSeek | 2026-04-20
- [Do LLMs Game Formalization? Evaluating Faithfulness in Logical Reasoning](../papers/2604.19459v1/index.md) | DeepSeek | 2026-04-21
- [ReflectMT: Internalizing Reflection for Efficient and High-Quality Machine Translation](../papers/2604.19144v1/index.md) | DeepSeek | 2026-04-21
- [MathNet: a Global Multimodal Benchmark for Mathematical Reasoning and Retrieval](../papers/2604.18584v1/index.md) | DeepSeek | 2026-04-20
- [Owner-Harm: A Missing Threat Model for AI Agent Safety](../papers/2604.18658v1/index.md) | Microsoft | 2026-04-20
- [Learning to Evolve: A Self-Improving Framework for Multi-Agent Systems via Textual Parameter Graph Optimization](../papers/2604.20714v1/index.md) | Meta FAIR | 2026-04-22
- [SWE-Edit: Rethinking Code Editing for Efficient SWE-Agent](../papers/2604.26102v1/index.md) | Microsoft | 2026-04-28
- [The Last Harness You'll Ever Build](../papers/2604.21003v1/index.md) | Meta FAIR | 2026-04-22
- [Context Kubernetes: Declarative Orchestration of Enterprise Knowledge for Agentic AI Systems](../papers/2604.11623v3/index.md) | Microsoft | 2026-04-13
- [FairQE: Multi-Agent Framework for Mitigating Gender Bias in Translation Quality Estimation](../papers/2604.21420v1/index.md) | Meta FAIR | 2026-04-23
- [A Self-Evolving Framework for Efficient Terminal Agents via Observational Context Compression](../papers/2604.19572v1/index.md) | MiniMax | 2026-04-21
- [Terminus-4B: Can a Smaller Model Replace Frontier LLMs at Agentic Execution Tasks?](../papers/2605.03195v1/index.md) | 阿里通义 | 2026-05-04
- [Agentic Aggregation for Parallel Scaling of Long-Horizon Agentic Tasks](../papers/2604.11753v1/index.md) | 智谱 | 2026-04-13
- [Nemobot Games: Crafting Strategic AI Gaming Agents for Interactive Learning with Large Language Models](../papers/2604.21896v1/index.md) | MiniMax | 2026-04-23
- [M2-PALE: A Framework for Explaining Multi-Agent MCTS--Minimax Hybrids via Process Mining and LLMs](../papers/2604.14687v1/index.md) | MiniMax | 2026-04-16
- [QuantClaw: Precision Where It Matters for OpenClaw](../papers/2604.22577v1/index.md) | 智谱 | 2026-04-24
- [AeSlides: Incentivizing Aesthetic Layout in LLM-Based Slide Generation via Verifiable Rewards](../papers/2604.22840v1/index.md) | 智谱 | 2026-04-21
- [What Happens Inside Agent Memory? Circuit Analysis from Emergence to Diagnosis](../papers/2605.03354v1/index.md) | 阿里通义 | 2026-05-05
- [SafetyALFRED: Evaluating Safety-Conscious Planning of Multimodal Large Language Models](../papers/2604.19638v1/index.md) | 阿里通义 | 2026-04-21
- [ComPASS: Towards Personalized Agentic Social Support via Tool-Augmented Companionship](../papers/2604.18356v1/index.md) | 阿里通义 | 2026-04-20
- [DataEvolver: Let Your Data Build and Improve Itself via Goal-Driven Loop Agents](../papers/2605.01789v1/index.md) | 阿里通义 | 2026-05-03
- [Quantum Knowledge Graph: Modeling Context-Dependent Triplet Validity](../papers/2604.23972v1/index.md) | 阿里通义 | 2026-04-27
- [Training and Agentic Inference Strategies for LLM-based Manim Animation Generation](../papers/2604.18364v1/index.md) | 阿里通义 | 2026-04-20
- [Agri-CPJ: A Training-Free Explainable Framework for Agricultural Pest Diagnosis Using Caption-Prompt-Judge and LLM-as-a-Judge](../papers/2604.23701v1/index.md) | 阿里通义 | 2026-04-26
