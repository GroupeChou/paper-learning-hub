# 长上下文感知的Upcycling：混合LLM缩放的新前沿

**Long-Context Aware Upcycling: A New Frontier for Hybrid LLM Scaling**

Parsa Ashrafi Fashi\*, Utkarsh Saxena\*, Mehdi Rezagholizadeh, Aref Jafari, Akash Haridas, Mingyu Yang, Vansh Bhatia, Guihong Li, Vikram Appia, Emad Barsoum

AMD

\*共同第一作者（随机顺序）

{parsa.fashi, utkarsh.saxena, mehdi.rezagholizadeh, aref.jafari}@amd.com

---

## 摘要（Abstract）

混合序列模型将高效 Transformer 组件与线性序列建模块相结合，是纯 Transformer 的有前途替代方案。然而大多数仍从零预训练，因此无法重用现有 Transformer 检查点。我们研究 **upcycling** 作为将预训练 Transformer LLM 转换为混合架构的实用路径，同时保持短上下文质量并改进长上下文能力。

我们称解决方案为 **HyLo（HYbrid LOng-context）**：一种长上下文 upcycling 配方，结合了架构适配（高效 Transformer 块、多头潜在注意力 MLA 和线性块 Mamba2/Gated DeltaNet），以及分阶段长上下文训练和教师引导蒸馏以稳定优化。

**关键成果：**
- 将可用上下文长度扩展 **32×**（通过高效后训练）
- KV缓存内存减少 **>90%**
- 支持 **2M 令牌**的预填充和解码（vLLM推理栈），而 Llama 基线在 64K 上下文外即 OOM
- 在 1B 和 3B 规模（Llama 和 Qwen 变体）上，HyLo 在短/长上下文性能上表现一致
- **HyLo-Qwen-1.7B** 仅训练 10B 令牌就显著优于训练 400B 令牌的 **JetNemotron**（在 GSM8K、Lm-Harness 常识推理和 RULER-64K 上）

---

## 1 引言（Introduction）

基于 Transformer 的大语言模型在多种任务上取得了显著成功。然而训练新模型成本日益高昂，促使研究走向更高效的架构和训练范式。

近期，混合架构（结合注意力机制与更高效的序列建模组件如状态空间模型或线性注意力）成为有前景的方向。代表包括 **Jamba**、**Samba**、**Qwen3-Next**、**Kimi-Linear** 等，它们在提升效率的同时保持竞争力。然而这些方法主要依赖**从零训练**，复制了开发 Transformer 的高昂成本。

**模型 Upcycling** 作为替代路线：将现有预训练 Transformer 转换为混合架构，而不丢弃已学知识。通过重用预训练 Transformer 的参数并转换其架构，随后继续训练，从而减少训练成本。

现有 upcycling 方法主要关注**保持短上下文性能**，忽视了现代 LLM 日益重要的**长上下文能力**。

**本文贡献：**
1. **长上下文感知的模型 upcycling**：基于 Zebra-Llama 改进的 upcycling 配方，在保持短上下文性能的同时实现优越的长上下文性能
2. **扩展的长上下文训练机制**：从 8K 到 **64K** 令牌的分阶段训练，系统分析训练序列长度对长上下文泛化的影响
3. **教师引导的长上下文蒸馏**：引入块级 KL 监督的教师引导长上下文训练
4. **高吞吐量推理服务**：将 HyLo 集成到 vLLM，支持张量并行，在 8 个 AMD MI300X GPU 上实现高达 **2M 令牌**的上下文服务（比 Llama-3.2-3B 扩展 30×）

---

## 2 相关工作（Related Work）

### 2.1 从零训练的混合长上下文模型

近期工作探索了从零训练混合架构：**S4**、**Mamba**、**RetNet**、**Hyena** 等。大规模混合模型如 **Jamba**（Transformer+Mamba+MoE）、**Zamba**、**Samba**、**MiniMax-01**（Lightning Attention）、**Kimi Linear**（Kimi Delta Attention + MLA）、**Qwen3-Next/Qwen3.5**（softmax attention + Gated DeltaNet）。关键设计原则：跨注意力和 SSM 组件的统一位置编码对稳定性至关重要。

### 2.2 后训练 Upcycling 和混合化

**MambaInLlama** 首次展示预训练注意力层可以初始化 SSM 块。后续有 **Llamba**、**X-EcoMLA**（转换为 MLA）、**Zebra-Llama**（Mamba2 + MLA + 改进初始化）、**L2A**（转换到滑动窗口+动态全注意力）、**RAD**（检测冗余注意力层）、**KL 引导层选择** 等。

---

## 3 方法论（Methodology）

### 3.1 架构设计

HyLo 采用混合架构，结合 **多头潜在注意力（MLA）** 与 **线性循环块**（Mamba-2 或 Gated DeltaNet）。MLA 与线性块的比例定义质量-效率权衡：更多 MLA 层增加注意力容量但也增加 KV 缓存使用，Mamba-2 和 GDN 无 KV 缓存开销。

不同于先前只聚焦一个基模型和一种线性模块的研究，我们评估两种 Transformer 家族（**Llama** 和 **Qwen**）和两种线性块类型（**Mamba-2** 和 **GDN**），证明配方跨架构和规模均有效。

### 3.2 初始化

核心挑战：如何从预训练注意力模型初始化替换的混合块。

**GDN 初始化流程：**
1. 从预训练模型出发，每个指定的 GDN 层进行就地模块替换
2. MLP 权重和 RMSNorm 参数从对应 Transformer 层直接复制
3. 注意力到 GDN 的权重转移：
   - **GQA 扩展**：当教师使用 H_kv < H_q 个 KV 头时，KV 权重矩阵通过重复每个 KV 头 H_q/H_kv 次来扩展
   - **维度截断**：由于 GDN 的键维度 d_k < d 而值维度 d_v > d，转移重叠子矩阵
4. GDN 特定参数（门投影 W_G、衰减参数 A_log/Δ_bias、beta 投影 W_β、短卷积核）保持默认随机初始化

### 3.3 两阶段轻量微调

**阶段 I：增强的中间层蒸馏（Enhanced-ILD）**——在仅 20% 数据上训练。在 Zebra-Llama 基础上，增加对 token-mixer 输出（Transformer 注意力输出与对应的 MLA/Mamba2/GDN 输出）的对齐：

$$L_{ILD} = \sum_{\ell=1}^L \left[ \|h_\ell^{(s)} - h_\ell^{(t)}\|^2 + \|a_\ell^{(s)} - a_\ell^{(t)}\|^2 \right]$$

其中 h_ℓ 是隐藏状态，a_ℓ 是注意力/token-mixer 输出。阶段 I 上下文长度固定为 2K。

**阶段 II：长上下文 SFT 训练**——加载阶段 I 分别蒸馏的 MLA/Mamba2/GDN 检查点组装为混合模型。扩展训练上下文长度从 2K 到 8K 和 64K。使用输出级 KL 散度知识蒸馏：

$$L_{SFT} = D_{KL}(\text{softmax}(z^{(s)}) \parallel \text{softmax}(z^{(t)}))$$

### 3.4 内存高效的长上下文蒸馏

从 2K 扩展到 64K 上下文长度引入严重内存压力，瓶颈在于 logit 张量：(T, V) 形状，T=65,536, V=128,256 时每个 logit 张量消耗约 **16 GB**（bfloat16）。

**表 1：upcycling Llama-1B 模型（4MLA+12Mamba2，64K 上下文）的训练内存**

| 配置 | 内存 (GiB) |
|------|-----------|
| 无教师 | OOM |
| 无教师 + FusedLinearCE + Act checkpoint | 29.6 |
| 8B 教师 + Fused KL Hidden | 158.8 |
| 8B 教师 + Fused KL + Act checkpointing | 144.8 |
| **8B 教师 + Fused KL Hidden + Act checkpointing** | **54.2** |

渐进式内存优化（依上下文长度部署）：
- **Fused Linear Cross-Entropy**：避免完整 logit 矩阵物化
- **分块 KL 散度**：沿序列维度分块（C=4,096）
- **Triton 融合 KL 散度**：单融合核 + 在线 softmax
- **融合隐藏状态 KL（无 logit 蒸馏）**：跳过 LM 头，直接从隐藏状态计算 KL

### 3.5 vLLM 运行时集成

将 HyLo 集成到 vLLM [22]，解决三个系统级挑战：
1. 异构层类型（Mamba SSM、GDN 线性注意力和 MLA 注意力）的统一执行
2. MLA 特定的 KV 压缩和头扩展机制
3. 核限制（HyLo 的压缩潜维度）

---

## 4 实验与结果（Experiments and Results）

### 4.1 实验设置

**模型配置**：从三个基模型出发——Llama-3.2-1B、Llama-3.2-3B、Qwen3-1.7B。

**评估任务**：短上下文常识推理（ARC-Challenge/Easy、HellaSwag、OpenBookQA、PIQA、RACE、WinoGrande）、长上下文（RULER 全部 13 个任务）、数学推理（GSM8K）。

**基线**：MambaInLlama、Llamba、Zebra-Llama、M1、HypeNet、Jet-Nemotron-2B。

### 4.2 主要结果

**表 2：Llama-3.2-1B 基线的对比结果**

| 模型/设置 | KV缓存 | 常识推理(平均) | RULER-8K→16K→32K→64K | GSM8K |
|-----------|--------|---------------|----------------------|-------|
| MambaInLlama-1B-50% | 50% | 59.3 | 18.9 / 3.0 / 1.0 / 0.0 | 16.2 |
| Zebra-Llama-1B (4MLA12M2) | 4% | 51.8 | 12.3 / 6.8 / 3.7 / 0.1 | 37.2 |
| **HyLo-1B-4MLA12M2** (8K训练) | **3.9%** | 52.1 | **53.1** / **10.6** / 2.0 / 0.5 | **49.2** |
| **HyLo-1B-4MLA12GDN** (8K训练) | **3.9%** | 53.1 | **55.1** / **11.9** / 2.4 / 0.8 | **51.9** |
| **HyLo-1B-4MLA12M2** (64K训练) | **3.9%** | 50.3 | **53.3** / **46.7** / **40.4** / **37.9** | 33.0 |
| **HyLo-1B-4MLA12GDN** (64K训练) | **3.9%** | 51.2 | **52.5** / **48.3** / **44.5** / **40.8** | 37.5 |

**表 3：Llama-3.2-3B 基线的对比结果（节选关键项）**

| 模型/设置 | KV缓存 | Avg | RULER-64K | GSM8K |
|-----------|--------|-----|-----------|-------|
| M1 | 21.4% | 56.2 | 17.4 | 62.5 |
| Zebra-Llama-3B (14MLA14M2) | 4.7% | 58.0 | 4.2 | 66.2 |
| **HyLo-3B-6MLA22M2** (64K训练) | **2.0%** | 56.7 | **42.3** | 51.6 |
| **HyLo-3B-14MLA14M2** (64K训练) | **4.7%** | 57.4 | **46.6** | 40.9 |
| **HyLo-3B-14MLA14GDN** (64K训练) | **4.7%** | 57.9 | **52.0** | 58.9 |

**表 4：Qwen 基线的对比结果**

| 模型/设置 | KV缓存 | Avg | RULER-64K | GSM8K |
|-----------|--------|-----|-----------|-------|
| Jet-Nemotron-2B (200B tokens) | 2.1% | 52.7 | 14.1 | 19.4 |
| HypeNet (7FA21LA) | 25% | 53.2 | 16.4 | 1.1 |
| **HyLo-Qwen-7MLA21M2** (8K训练) | **3.9%** | 55.2 | 14.6 | **72.3** |
| **HyLo-Qwen-7MLA21GDN** (8K训练) | **3.9%** | 56.1 | 17.4 | **76.0** |
| **HyLo-Qwen-14MLA14M2** (8K训练) | **7.8%** | 56.1 | 10.7 | **75.8** |
| **HyLo-Qwen-14MLA14GDN** (8K训练) | **7.8%** | 56.5 | 0.2 | **76.1** |

关键发现：HyLo-Qwen-1.7B仅训练10B令牌，在GSM8K（76.1）和RULER-64K（17.4）上显著超越JetNemotron-2B（训练400B令牌，GSM8K 19.4, RULER-64K 14.1）。

### 4.3 消融研究

**序列长度与位置插值（YaRN）**：YaRN略微降低短上下文精度但显著改善长上下文性能。1B-4MLA-12M2模型在8K训练后，YaRN扩展使RULER-64K从0.5%提升至31.3%。直接64K训练获得最佳长上下文性能。

**知识蒸馏的影响**：64K训练下，8B教师改善短上下文推理6%，RULER-64K改善22%。更大的教师模型带来更大增益。

**架构设计选择**：NoPE和Gated Attention在混合upcycling设置中不提供改进。

**Enhanced-ILD的影响**：Enhanced-ILD在GSM8K上提供显著提升（+6.3/+5.4/+6.1分），同时保持或略微改善常识推理。

### 4.4 推理延迟评估

使用vLLM（TP=8, batch size=1, 8 AMD MI300X GPU），测试8K到2M上下文。

- **预填充延迟**：8K-64K三种模型可比。64K以上Llama 3B OOM（28层注意力KV缓存超显存）。HyLo支持完整2M扫描。HyLo-6MLA22M2比14MLA14M2约**2.2×快**
- **解码延迟**：短上下文(8K-32K) Llama更低，但128K后OOM。HyLo-6MLA22M2在8K-64K维持平坦TPOT（Mamba层使用固定大小隐藏状态）。2M时比14MLA14M2**2×更快**

---

## 5 结论（Conclusion）

本文提出 **HyLo** 系列混合 LLM，从预训练 Transformer 检查点 upcycled，明确强调保持长上下文能力。我们引入了长上下文感知的 upcycling 策略，结合基于 MLA 的 Transformer 注意力块与 Mamba2/GDN 线性块、分阶段上下文长度扩展和教师引导蒸馏。在 1B- 和 3B- 规模上（包括 Llama 和 Qwen 骨干），HyLo 在保持短上下文质量的同时实现优越的长上下文泛化。KV 缓存减少 **>90%**，支持高达 **2M 令牌** 的预填充和/or 解码。

**未来工作**：进一步缩小长上下文长度下的剩余差距，改进蒸馏效率，扩展框架到更多下游场景。

---

## 附录 A

### A.1 模型配置详情

**表 7：模型配置与超参数**

| 模型 | 基础模型 | MLA层索引 | 活跃参数量 | 头数 | 层数 | 隐藏维 | lr | batch(8k/64k) |
|------|---------|-----------|-----------|------|------|--------|-----|--------------|
| HyLo-Llama-4MLA12M2 | Llama-3.2-1B | [1,5,10,14] | 1.5B | 32 | 16 | 2048 | 6e-5 | 32/8 |
| HyLo-Llama-4MLA12GDN | Llama-3.2-1B | [1,5,10,14] | 1.7B | 32 | 16 | 2048 | 6e-5 | 32/8 |
| HyLo-Llama-8MLA8M2 | Llama-3.2-1B | [0,2,4,6,8,10,12,14] | 1.5B | 32 | 16 | 2048 | 6e-5 | 32/8 |
| HyLo-Llama-8MLA8GDN | Llama-3.2-1B | [0,2,4,6,8,10,12,14] | 1.6B | 32 | 16 | 2048 | 6e-5 | 32/8 |
| HyLo-Llama-6MLA22M2 | Llama-3.2-3B | [0,5,10,16,21,26] | 3.8B | 24 | 28 | 3072 | 4e-5 | 16/8 |
| HyLo-Llama-14MLA14M2 | Llama-3.2-3B | [0,2,4,6,8,10,12,14,16,18,20,22,24,26] | 3.7B | 24 | 28 | 3072 | 4e-5 | 16/8 |
| HyLo-Qwen-7MLA21M2 | Qwen3-1.7B | [1,5,9,13,17,21,25] | 2.1B | 16 | 28 | 2048 | 6e-5 | 32/8 |

### A.2 MLA 层架构与 SVD 初始化

MLA 遵循 DeepSeek-V3 设计，通过低秩潜投影压缩 KV 缓存。

**查询路径:** cQ → q_nope + q_rope (带 RoPE)
**KV路径:** cKV → k_rope + k_nope + v，KV缓存仅存储压缩潜变量 cKV ∈ R^{r_kv} 和 k_rope ∈ R^{d_rope}
**注意力:** q_t = [q_nope; RoPE(q_rope)], k_t = [k_nope; RoPE(k_rope)]

SVD 初始化：将教师的全秩注意力权重通过截断 SVD 分解来初始化低秩 MLA 投影。

### A.3 GDN 层架构

GDN 混合器参数化：每个非注意力解码层使用 Gated DeltaNet (GDN) 替换标准注意力。

**GDN 参数量（Llama-3.2-1B, d=2048）：** 约 25.2M 参数

**门控 Delta 规则循环：**
- 状态更新：S_t = exp(g_t) · S_{t-1} + k_t · (β_t · (v_t - S_{t-1}^T k_t))^T
- 读取：o_t = (1/√d_k) · S_t^T · q_t
- 输出：y_t = W_O · RMSNorm([q_t S_t, W_G x_t])

### A.4 内存高效的长上下文知识蒸馏

**表 9：内存优化技术及其在不同上下文长度下的部署**

| 技术 | 节省的内存 | 使用于 |
|------|-----------|--------|
| Liger Fused Linear CE | 学生 logits (T×V) | 8K–32K |
| Chunked KL Divergence | Softmax 张量 2(T×V) | 64K |
| Triton Fused KL | Softmax + grad 3(T×V) | 128K |
| Fused Hidden-State KL | 两个 logit 矩阵 2(T×V) | 64K |
| FSDP Full Sharding | 模型参数 ÷ N_GPU | 全部 |
| Frozen teacher (no grad) | 教师梯度 + 优化器 | 全部 |
| bf16 mixed precision | 2× vs fp32 | 全部 |

---

## 参考文献

[1] Bick et al. Transformers to SSMs: Distilling quadratic knowledge to subquadratic models. arXiv:2408.10189, 2024.
[2] Bick et al. Llamba: Scaling distilled recurrent models for efficient language processing. arXiv:2502.14458, 2025.
[3] Bick et al. Retrieval-aware distillation for transformer-SSM hybrids. arXiv:2602.11374, 2026.
[4] Bisk et al. PIQA. AAAI, 2020.
[5] Brown et al. Language models are few-shot learners. NeurIPS, 2020.
[6] Chen et al. Hybrid linear attention done right. arXiv:2601.22156, 2026.
[7] Choudhary et al. Learning when to attend. arXiv:2603.17484, 2026.
[8] Chowdhery et al. PaLM. 2022.
[9] Clark et al. ARC. arXiv:1803.05457, 2018.
[10] Cobbe et al. Training verifiers to solve math word problems. arXiv:2110.14168, 2021.
[11] Dao & Gu. Transformers are SSMs. arXiv:2405.21060, 2024.
[12] Gao et al. A framework for few-shot language model evaluation. 2023.
[13] Gao et al. How to train long-context language models (effectively). ACL 2025.
[14] Gelberg et al. Extending the context of pretrained LLMs by dropping their positional embeddings. 2025.
[15] Glorioso et al. Zamba. arXiv:2405.16712, 2024.
[16] Gu & Dao. Mamba. COLM, 2024.
[17] Gu et al. S4. arXiv:2111.00396, 2021.
[18] Gu et al. Jet-Nemotron. arXiv:2508.15884, 2025.
[19] Hoshino et al. RAD. arXiv:2505.22135, 2025.
[20] Hsieh et al. RULER. arXiv:2404.06654, 2024.
[21] Katharopoulos et al. Transformers are RNNs. ICML, 2020.
[22] Kwon et al. Efficient memory management for LLM serving with PagedAttention. 2023.
[23] Lai et al. RACE. arXiv:1704.04683, 2017.
[24] Li et al. MiniMax-01. arXiv:2501.08313, 2025.
[25] Li et al. X-EcoMLA. arXiv:2503.11132, 2025.
[26] Li et al. X-EcoMLA. arXiv:2503.11132, 2025.
[27] Li et al. Distilling to hybrid attention models via KL-guided layer selection. arXiv:2512.20569, 2025.
[28-29] Lieber et al. Jamba. arXiv:2403.19887, 2024.
[30] DeepSeek-V2. arXiv:2405.04434, 2024.
[31] Mihaylov et al. OpenBookQA. arXiv:1809.02789, 2018.
[32] Milakov & Gimelshein. Online normalizer calculation for softmax. arXiv:1805.02867, 2018.
[33] Peng et al. YaRN. arXiv:2309.00071, 2023.
[34] Poli et al. Hyena. ICML, 2023.
[35] Qin et al. Lightning Attention-2. arXiv:2401.04658, 2024.
[36] Qiu et al. Gated Attention for LLMs. arXiv:2505.06708, 2025.
[37] Qwen Team. Qwen3-Next. 2025.
[38] Qwen Team. Qwen3.5. 2026.
[39-40] Ren et al. Samba. arXiv:2406.07522, 2024.
[41] Sakaguchi et al. WinoGrande. CACM, 2021.
[42] Sun et al. RetNet. arXiv:2307.08621, 2023.
[43] Kimi Team. Kimi Linear. arXiv:2510.26692, 2025.
[44] Vaswani et al. Attention is all you need. NeurIPS, 2017.
[45] Wang et al. A systematic analysis of hybrid linear attention. arXiv:2507.06457, 2025.
[46] Wang et al. The Mamba in the Llama. NeurIPS, 2024.
[47] Wang et al. M1: Towards scalable test-time compute with Mamba reasoning models. arXiv:2504.10449, 2025.
[48] Wu et al. TransXSSM. arXiv:2506.09507, 2025.
[49] Yang et al. RoPE to NoPE and back again. arXiv:2501.18795, 2025.
[50] Yang et al. Zebra-Llama. arXiv:2505.17272, 2025.
[51] Yang & Zhang. FLA library. GitHub, 2024.
[52] Yang et al. Gated Delta Networks. arXiv:2412.06464, 2024.
[53] Zellers et al. HellaSwag. arXiv:1905.07830, 2019.
