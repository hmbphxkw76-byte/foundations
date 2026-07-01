# OffSec AI-300 (OSAI) 红队备考武器库指南

本指南严格参考 OffSec AI-300 (OSAI) 官方大纲、MITRE ATLAS 与 OWASP Top 10 for LLM 威胁矩阵。

OSAI 是一场 24 小时的纯实战 AI 红队挑战，考核核心是：从大模型语义漏洞（Jailbreak / Injection）出发，横向移动并彻底接管底层 AI 基础设施（Cloud / Kubernetes / 模型服务器 / 向量数据库）。

---

## 🛠️ 第一阶段：AI 资产探测与指纹识别 (Reconnaissance)

### 目标
- 在不触发警报的情况下，识别内网暴露的 AI 组件、LLM/VLM 服务、向量数据库及 RAG 架构。

### 关键工具
- **Mantra / AI API Scanner**
  - 自动化扫描未授权、暴露的 AI 服务，如 Ollama、vLLM 服务端点或未加密的 OpenAI API 密钥。
- **Nmap + 自定义 AI 脚本 / Curl**
  - 扫描 11434 (Ollama)、8000 (vLLM)、5001 (Triton)、5000 (MLflow) 等默认端口。
  - 通过空白 Prompt 返回的 HTTP 响应头（Headers）进行模型指纹识别（Model Fingerprinting）。
- **DeepEval**
  - 通过少量探测探针测试目标 API 的上下文长度、嵌入模型（Embedding）类型等物理限制。

## 💥 第二阶段：模型层漏洞挖掘与护栏绕过 (LLM Attacks & Evasion)

### 目标
- 攻破前置安全防御，通过单轮或多轮对话实现“越狱”（Jailbreak）或提取系统提示词（System Prompt Injection）。

### 关键工具
- **garak (LLM 领域的 Nmap)**
  - 高并发、自动化的单轮（One-shot）漏洞扫描器。
  - 内置 120+ 探针，可暴破模型原生的政治、色情、偏见、代码执行等安全护栏漏洞。
- **PyRIT (微软 AI 红队工具箱)**
  - 自动化多轮对话（Multi-turn）编排核心。
  - 学会使用 Converters 将攻击载荷自动转为 Base64、多语言或 Leetspeak。
  - 利用 Crescendo（渐进式引诱）和 TAP（提示词自动演进）执行攻击。
- **promptfoo**
  - 构建确定性的红队测试集（Test Cases）。
  - 通过 YAML 配置对目标系统的输入/输出策略进行合规与红队对抗脆弱性评估。
  - 常用于模拟 CI/CD 阶段的自动化防御绕过。
- **NeMo Guardrails / Llama Guard**
  - 本地部署并逆向主流开源 AI 防御/护栏框架。
  - 寻找分词、过滤机制的逻辑漏洞，设计控制字符注入、多语言混淆等绕过方式。

## 💉 第三阶段：RAG 管道与知识库污染 (RAG & Vector DB Exploitation)

### 目标
- 通过污染大模型检索的数据源（网页、PDF、数据库），使模型在读取时触发“间接提示词注入”（Indirect Prompt Injection），控制模型或窃取、外发敏感数据。

### 关键工具
- **Interactsh (ProjectDiscovery) / Burp Suite Collaborator**
  - 出网协同与数据外发测试（Data Exfiltration）。
  - 在知识库中植入恶意 Payload，例如 `![Image: http://malicious.com]`，诱导模型将敏感信息通过 HTTP/DNS 外发。
- **VectorDB Admin Tools (如 Python chromadb / pymilvus 客户端)**
  - 在发现向量数据库未授权访问或凭证接管后，直接使用官方 SDK 接入。
  - 数据窃取：利用 `collection.query()` 遍历并拉取存储的敏感嵌入向量及 Metadata。
  - 知识库污染：向特定 Collection 注入恶意高权重向量，使其在用户提问时被优先检索出来。
- **VectorSec**
  - 针对 Pinecone、Milvus、ChromaDB、Qdrant、Weaviate 进行基线安全检查和漏洞探测。
  - 一键识别弱口令和配置缺陷。

## 🤖 第四阶段：多 Agent 系统与 MCP 工具链劫持 (Agent Tool Abuse)

### 目标
- 当 AI 被赋予调用外部工具的权限时，利用工具本身的漏洞或参数越权机制实现横向移动。

### 关键工具
- **LangChain / LlamaIndex**
  - 理解并监控 Agent 执行链。
  - 通过它们的 Debug 工具寻找 Agent 之间相互信任的协议漏洞（A2A Protocol）。
  - 查找未严格限制工具入参的缺陷。
- **MCP (Model Context Protocol)**
  - 针对新型大模型上下文协议暴露的 Tool 接口进行参数注入。
  - 通过大模型命令工具执行非预期的系统命令，触发 Command Injection。

## 📦 第五阶段：AI 供应链与反序列化攻击 (Supply Chain Attacks)

### 目标
- 利用企业在内网或云端加载开源模型/数据集时的供应链漏洞，直接获取服务器最高权限（RCE）。

### 关键工具
- **Safetensors-Converter / Custom Pickle Exploiter**
  - 利用 `.bin` / `.pkl` 模型文件的反序列化漏洞。
  - 通过 Python 的 `__reduce__` 方法在模型文件中植入恶意代码，加载时执行反弹 Shell。
- **Nightshade / Glaze**
  - 针对多模态（VLM）或图像模型的上游数据集投毒。
  - 通过像素级对抗扰动使目标 AI 在微调或训练后产生特定后门。

## 🏗️ 第六阶段：底层云与 AI 基础设施渗透 (Infrastructure & Post-Exploitation)

### 目标
- 当大模型本身无法攻破时，转向攻击托管模型的 Kubernetes 集群、分布式计算平台（Ray）或 MLOps 管理端。

### 关键工具
- **TruffleHog**
  - 在获取部分文件系统权限后进行横向移动与凭证提权。
  - 扫描本地文件系统和私有 Git 仓库，寻找硬编码凭证（OpenAI_API_Key、Hugging Face Token、AWS S3、Ray 凭证、向量数据库管理密钥）。
- **Ray-Exploiter**
  - 利用 Ray 中的 ShadowRay / CVE-2023-6021 漏洞提交恶意分布式 Python Job。
  - 直接获取多个 Worker 节点宿主机的反弹 Shell。
- **MLflow / ClearML 漏洞利用武器库**
  - 利用 MLflow 任意文件读取漏洞（如 CVE-2023-27524）。
  - 直接下载服务器本地模型文件，或修改训练 Pipeline 脚本植入持久化后门。
- **CDK (Container Detection King) / Peirates / Kube-hunter**
  - 针对 Kubernetes 环境进行基线检测与容器逃逸。
  - 从低权限 Pod 获取 Service Account Token，最终实现 Node 控制权。

## 💡 OSAI 备考四大金律

- **promptfoo**：开发优先、CI/CD 深度集成、基于 YAML 的合规防护评估工具。
- **garak**：LLM 领域的 Nmap，单轮（One-shot）高并发暴力漏洞扫描器。
- **PyRIT**：多轮对话攻击（Crescendo）与多模态复杂红队编排利器。
- **Counterfit**：针对传统机器学习（CV 图像扰动、表格数据投毒、分类器推断）的传统黑客风格渗透工具。

> 代码能力是硬通货。OSAI 绝对不是点点鼠标。
> 你必须熟练掌握 Python 脚本编写。

### 核心攻击链闭环演练
- 利用 garak 扫出漏洞
- 触发 AI 工具调用执行代码
- 拿到 K8s 内部低权限 Pod
- 使用 TruffleHog / CDK 收集凭证
- 发现未授权 Ray 集群
- 提交恶意 Job 拿下 GPU 宿主机最高权限（RCE）

> 不要遗忘传统安全：大模型只是入口。当模型允许执行代码，或模型服务器存在配置缺陷时，仍然需要 Linux 权限提升、K8s 逃逸、端口转发等 OSCP / OSEP 级别技能。

---

## 🎯 推荐最适合 AI-300 备考的 Vulnerable AI 开源靶场

在 OffSec AI-300 的 24 小时实战挑战中，必须通过具有完整拓扑、包含真实业务漏洞的“故意留白/存在漏洞”的开源 AI 靶场来培养肌肉记忆。

### 1. 🏆 最佳 OSAI 专项替代方案：OpenAIRT-300

- **项目地址**：[pax-k/OpenAIRT-300](https://github.com/pax-k/OpenAIRT-300)
- **靶场定位**：**备考绝对首选。** 这是开源安全社区专门针对 OffSec 官方价值 1749 美元的 AI-300 课程而完全开源的对标靶场与完整课程体系。
- **靶场特色**：
  - 包含超过 81 小时的实验练习，复刻一个名为 `MegacorpAI` 的企业级靶场。
  - 实验设计基于过去 18 个月内真实 AI 严重安全事件，如 Vercel × Context.ai 供应链泄露事件。
  - 覆盖 Agent 协作网络、复杂 RAG 管道、MCP 服务器漏洞，以及通过本地提示词注入逐步斩获底层基础设施 RCE 的完整链路。

### 2. 🏗️ AI 基础设施与云渗透：AIGoat

- **项目地址**：[orcasecurity-research/AIGoat](https://github.com/orcasecurity-research/AIGoat)
- **靶场定位**：**云原生 AI 基础设施渗透测试。** 由 Orca Security 团队开源，使用 Terraform 在云端或本地模拟环境一键部署。
- **靶场特色**：
  - 基于包含多种机器学习功能的电商系统，完美对应 OWASP Top 10 for ML/LLM 的风险矩阵。
  - 核心实验包含极为致命的 AI 供应链攻击，练习分析漏洞 Python ML 第三方依赖包和利用 `.pkl` 序列化文件执行恶意代码，最终在模型服务器上触发反弹 Shell。

### 3. 🎯 综合性全栈红队靶场：Red AI Range (RAR)

- **项目地址**：[ErdemOzgen/RedAiRange](https://github.com/ErdemOzgen/RedAiRange)
- **靶场定位**：**全功能 AI 红队靶场控制台。** 提供类似 Cyber Range 的 Web 仪表盘。
- **靶场特色**：
  - 利用 Docker-Compose 快速启动或销毁多种“故意留白”的 AI 业务容器，例如带注入点的聊天机器人、无认证模型发布端、未授权向量数据库。
  - 自带“兵工厂（Arsenal）”模块，方便在同一个控制台中直接调用 `garak` 等攻击工具攻击靶机。

### 4. 🧠 Agent 决策网络与动态对抗：AgentDojo / AgentFence

- **项目地址**：可在 GitHub 搜索 `AgentDojo` 或 `AgentFence`
- **靶场定位**：**自主 AI Agent 攻防对抗环境。**
- **靶场特色**：
  - AI-300 高级考点包括当 AI 拥有自主工具调用和记忆功能时，如何进行越权。
  - 这些靶场提供动态测试流，供红队演练如何通过工作流污染、内存操纵劫持 Agent 执行路线，使其执行非预期系统命令。

### 5. 📚 官方合规与基线练习：OWASP AI Vulnerabilities Playground

- **项目地址**：[OWASP/AI-Vulnerabilities-Playground](https://github.com/OWASP/AI-Vulnerabilities-Playground)
- **靶场定位**：**OWASP LLM Top 10 标准演练场。**
- **靶场特色**：
  - 将大模型风险分为多个阶段和安全沙盒（Phase 1 至 Phase 4）。
  - 适合练习直接/间接提示词注入、敏感数据泄露、以及针对持久化 secrets（如本地 SQLite/JSON 中硬编码凭证）的本地提权练习。

---

## 📌 建议复习路线（利用开源靶场）

为了最大化备考效率，不要盲目同时启动所有靶场，推荐以下顺序：

1. **第一周**：在本地跑之前配好的 Docker（Ollama + ChromaDB + Ray），用自定义 Python 脚本手动摸透 Ray 的 RCE 和 ChromaDB 的数据读取，掌握底层机理。
2. **第二周**：拉取 `OWASP AI-Vulnerabilities-Playground`，配合 `garak` 和 `PyRIT` 去自动、高并发地打穿靶场里的 4 个难度阶段。
3. **第三周至考前**：全力攻克 `OpenAIRT-300` 课程及其实验场景。这是目前最贴近 OSAI 24 小时考试深度和工程视角的免费环境。

> 如果你在拉取某个靶场（如 `AIGoat` 或 `OpenAIRT-300`）时遇到本地依赖冲突，或需要某种特定反弹 Shell（如不依赖 nc 的 Python 一句话 Shell）去突破靶场隔离，我可以帮你编写或调试代码。
