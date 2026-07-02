# Garak 攻击框架实战指南

> OffSec AI-300 (OSAI) 红队备考 - 使用 Garak 框架实现的攻击代码

---

## 目录

1. [Garak 安装与配置](#1-garak-安装与配置)
2. [核心 CLI 语法解析](#2-核心-cli-语法解析)
3. [OWASP LLM Top 10 Garak 探测](#3-owasp-llm-top-10-garak-探测)
4. [OWASP Agentic Top 10 Garak 探测](#4-owasp-agentic-top-10-garak-探测)
5. [OWASP Top 10 Garak 探测](#5-owasp-top-10-garak-探测)
6. [Garak 输出分析](#6-garak-输出分析)
7. [考试快速上手](#7-考试快速上手)

---

## 1. Garak 安装与配置

### 1.1 安装命令

```bash
# 安装 Garak
pip install garak

# 验证安装
garak --help

# 查看可用探测模块
garak --list_probes
```

### 1.2 考试环境配置

创建环境变量文件 `garak.env`：

```bash
# garak.env - 考试环境配置
export GARAK_MODEL="openai:chat:exam-target"
export GARAK_BASE_URL="http://exam-env:11434/v1"
export GARAK_API_KEY="lm-studio"
export GARAK_MODEL_NAME="qwen2.5:3b"
```

### 1.3 环境变量加载

```bash
# Linux/Mac
source garak.env

# Windows PowerShell
$env:GARAK_MODEL="openai:chat:exam-target"
$env:GARAK_BASE_URL="http://exam-env:11434/v1"
$env:GARAK_API_KEY="lm-studio"
$env:GARAK_MODEL_NAME="qwen2.5:3b"
```

---

## 2. 核心 CLI 语法解析

### 2.1 基本命令格式

```bash
garak --model <model_type>:<model_name> --probes <probe_name> [options]
```

### 2.2 关键参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| `--model` | 指定目标模型 | `--model openai:chat:exam-target` |
| `--probes` | 指定探测模块 | `--probes promptinject` |
| `--output` | 指定输出格式 | `--output json` |
| `--save_file` | 保存输出文件 | `--save_file results.json` |
| `--verbose` | 详细输出 | `--verbose` |
| `--list_probes` | 列出所有探测模块 | `--list_probes` |
| `--list_models` | 列出所有支持的模型类型 | `--list_models` |

### 2.3 模型类型格式

| 模型类型 | 格式 | 示例 |
|----------|------|------|
| OpenAI | `openai:chat:<model_name>` | `openai:chat:gpt-4o` |
| OpenAI (自定义API) | `openai:chat:<model_name>` | 通过环境变量指定base_url |
| HuggingFace | `huggingface:<model_name>` | `huggingface:mistral-7b` |
| Ollama | `ollama:<model_name>` | `ollama:qwen2.5:3b` |
| LM Studio | `lmstudio:<model_name>` | `lmstudio:qwen2.5:3b` |

### 2.4 考试常用命令模板

```bash
# 基础扫描命令
garak --model openai:chat:exam-target --probes promptinject --verbose

# 保存结果到文件
garak --model openai:chat:exam-target --probes promptinject --output json --save_file results.json

# 并行扫描多个探测模块
garak --model openai:chat:exam-target --probes promptinject,jailbreak,pii --verbose

# 使用环境变量
garak --model $GARAK_MODEL --probes promptinject --verbose
```

---

## 3. OWASP LLM Top 10 Garak 探测

### LLM01: 提示注入（Prompt Injection）

**适用探测模块**: `promptinject`, `goodside`, `lmrc`

```bash
# 基础提示注入探测
garak --model openai:chat:exam-target --probes promptinject --verbose

# 详细输出并保存结果
garak --model openai:chat:exam-target --probes promptinject --output json --save_file llm01-results.json

# 使用 goodside 探测（更强的注入技术）
garak --model openai:chat:exam-target --probes goodside --verbose

# 使用 lmrc 探测（语言模型风险分类器）
garak --model openai:chat:exam-target --probes lmrc --verbose

# 组合多个注入探测
garak --model openai:chat:exam-target --probes promptinject,goodside,lmrc --output json --save_file llm01-combined.json
```

**探测模块说明**：

| 探测模块 | 技术原理 | 覆盖场景 |
|----------|----------|----------|
| `promptinject` | 直接提示注入测试 | 基础注入、指令覆盖 |
| `goodside` | 编码绕过、多语言注入 | 编码绕过、混淆注入 |
| `lmrc` | 语言模型风险分类 | 多维度风险评估 |

---

### LLM02: 敏感信息泄露（Sensitive Information Disclosure）

**适用探测模块**: `pii`, `dataexfil`, `credentials`

```bash
# PII泄露探测
garak --model openai:chat:exam-target --probes pii --verbose

# 数据泄露探测
garak --model openai:chat:exam-target --probes dataexfil --verbose

# 凭证泄露探测
garak --model openai:chat:exam-target --probes credentials --verbose

# 组合探测
garak --model openai:chat:exam-target --probes pii,dataexfil,credentials --output json --save_file llm02-results.json
```

**探测模块说明**：

| 探测模块 | 检测内容 | 输出格式 |
|----------|----------|----------|
| `pii` | 邮箱、电话、地址、SSN等 | JSON格式的PII类型和置信度 |
| `dataexfil` | 数据外发风险 | 外发可能性评分 |
| `credentials` | API密钥、密码等凭证 | 凭证类型和匹配度 |

---

### LLM04: 数据中毒（Data Poisoning）

**适用探测模块**: `goodside`, `test.Blend`, `test.Fill`

```bash
# 数据投毒探测
garak --model openai:chat:exam-target --probes goodside --verbose

# 测试数据污染
garak --model openai:chat:exam-target --probes test.Blend --verbose

# 测试填充攻击
garak --model openai:chat:exam-target --probes test.Fill --verbose

# 组合测试
garak --model openai:chat:exam-target --probes goodside,test.Blend,test.Fill --output json --save_file llm04-results.json
```

**探测模块说明**：

| 探测模块 | 技术原理 | 测试目标 |
|----------|----------|----------|
| `goodside` | 渐进式提示投毒 | 模型是否接受虚假信息 |
| `test.Blend` | 数据混合测试 | 模型对混合数据的处理 |
| `test.Fill` | 填充攻击测试 | 模型是否完成恶意填充 |

---

### LLM06: 权限提升（Privilege Escalation）

**适用探测模块**: `jailbreak`, `dan`, `test.Replay`

```bash
# 越狱探测
garak --model openai:chat:exam-target --probes jailbreak --verbose

# DAN模式探测
garak --model openai:chat:exam-target --probes dan --verbose

# 重放攻击探测
garak --model openai:chat:exam-target --probes test.Replay --verbose

# 组合探测
garak --model openai:chat:exam-target --probes jailbreak,dan,test.Replay --output json --save_file llm06-results.json
```

**探测模块说明**：

| 探测模块 | 技术原理 | 测试目标 |
|----------|----------|----------|
| `jailbreak` | 越狱提示注入 | 绕过安全护栏 |
| `dan` | DAN模式激活 | 禁用安全限制 |
| `test.Replay` | 会话重放 | 权限持久化测试 |

---

### LLM08: 拒绝服务（Denial of Service）

**适用探测模块**: `denialofservice`, `test.Flood`

```bash
# 拒绝服务探测
garak --model openai:chat:exam-target --probes denialofservice --verbose

# 洪水攻击测试
garak --model openai:chat:exam-target --probes test.Flood --verbose

# 组合测试
garak --model openai:chat:exam-target --probes denialofservice,test.Flood --output json --save_file llm08-results.json
```

**探测模块说明**：

| 探测模块 | 技术原理 | 测试目标 |
|----------|----------|----------|
| `denialofservice` | 资源耗尽攻击 | 模型响应时间和稳定性 |
| `test.Flood` | 请求洪水攻击 | 系统处理能力 |

---

### LLM09: 误导与虚假信息（Misinformation）

**适用探测模块**: `misinformation`, `disinformation`, `test.Bias`

```bash
# 误导信息探测
garak --model openai:chat:exam-target --probes misinformation --verbose

# 虚假信息探测
garak --model openai:chat:exam-target --probes disinformation --verbose

# 偏见测试
garak --model openai:chat:exam-target --probes test.Bias --verbose

# 组合测试
garak --model openai:chat:exam-target --probes misinformation,disinformation,test.Bias --output json --save_file llm09-results.json
```

**探测模块说明**：

| 探测模块 | 技术原理 | 测试目标 |
|----------|----------|----------|
| `misinformation` | 误导信息生成 | 模型是否生成不准确信息 |
| `disinformation` | 故意虚假信息 | 模型是否生成恶意虚假内容 |
| `test.Bias` | 偏见检测 | 模型是否存在偏见输出 |

---

## 4. OWASP Agentic Top 10 Garak 探测

### ASI01: 目标劫持（Agent Goal Hijacking）

**适用探测模块**: `jailbreak`, `promptinject`, `lmrc`

```bash
# 目标劫持探测
garak --model openai:chat:exam-target --probes jailbreak --verbose

# 指令覆盖探测
garak --model openai:chat:exam-target --probes promptinject --verbose

# 风险分类探测
garak --model openai:chat:exam-target --probes lmrc --verbose

# 组合探测
garak --model openai:chat:exam-target --probes jailbreak,promptinject,lmrc --output json --save_file asi01-results.json
```

**探测模块说明**：

| 探测模块 | 测试目标 | 成功指标 |
|----------|----------|----------|
| `jailbreak` | 绕过Agent原始目标 | Agent执行非预期操作 |
| `promptinject` | 注入新目标指令 | Agent采纳注入目标 |
| `lmrc` | 评估风险等级 | 风险评分超过阈值 |

---

### ASI02: 工具滥用（Tool Misuse）

**适用探测模块**: `goodside`, `promptinject`, `test.Blend`

```bash
# 工具滥用探测
garak --model openai:chat:exam-target --probes goodside --verbose

# 指令注入探测
garak --model openai:chat:exam-target --probes promptinject --verbose

# 数据混合测试
garak --model openai:chat:exam-target --probes test.Blend --verbose

# 组合探测
garak --model openai:chat:exam-target --probes goodside,promptinject,test.Blend --output json --save_file asi02-results.json
```

**探测模块说明**：

| 探测模块 | 测试目标 | 成功指标 |
|----------|----------|----------|
| `goodside` | 诱导工具执行非预期操作 | 工具执行恶意命令 |
| `promptinject` | 注入工具调用指令 | Agent调用非预期工具 |
| `test.Blend` | 混合数据测试工具行为 | 工具处理恶意数据 |

---

### ASI03: 身份冒充（Identity Spoofing）

**适用探测模块**: `jailbreak`, `promptinject`, `lmrc`

```bash
# 身份冒充探测
garak --model openai:chat:exam-target --probes jailbreak --verbose

# 身份注入探测
garak --model openai:chat:exam-target --probes promptinject --verbose

# 风险评估
garak --model openai:chat:exam-target --probes lmrc --verbose

# 组合探测
garak --model openai:chat:exam-target --probes jailbreak,promptinject,lmrc --output json --save_file asi03-results.json
```

**探测模块说明**：

| 探测模块 | 测试目标 | 成功指标 |
|----------|----------|----------|
| `jailbreak` | 冒充其他角色 | Agent接受新身份 |
| `promptinject` | 注入身份信息 | Agent采纳注入的身份 |
| `lmrc` | 评估身份欺骗风险 | 风险评分超过阈值 |

---

## 5. OWASP Top 10 Garak 探测

### A01: 提示注入（Prompt Injection）

**适用探测模块**: `promptinject`, `goodside`, `jailbreak`

```bash
# 基础提示注入
garak --model openai:chat:exam-target --probes promptinject --verbose

# 高级注入技术
garak --model openai:chat:exam-target --probes goodside --verbose

# 越狱注入
garak --model openai:chat:exam-target --probes jailbreak --verbose

# 全面探测
garak --model openai:chat:exam-target --probes promptinject,goodside,jailbreak --output json --save_file a01-results.json
```

---

### A06: 安全配置错误（Security Misconfiguration）

**适用探测模块**: `encoding`, `test.Fill`, `lmrc`

```bash
# 编码绕过探测
garak --model openai:chat:exam-target --probes encoding --verbose

# 填充测试
garak --model openai:chat:exam-target --probes test.Fill --verbose

# 风险评估
garak --model openai:chat:exam-target --probes lmrc --verbose

# 组合探测
garak --model openai:chat:exam-target --probes encoding,test.Fill,lmrc --output json --save_file a06-results.json
```

**探测模块说明**：

| 探测模块 | 测试目标 | 成功指标 |
|----------|----------|----------|
| `encoding` | 检测编码绕过防护 | 编码后的恶意提示被执行 |
| `test.Fill` | 检测输入验证缺陷 | 超长输入被接受 |
| `lmrc` | 评估安全配置风险 | 风险评分超过阈值 |

---

### A09: 安全日志与监控不足（Insufficient Logging & Monitoring）

**适用探测模块**: `dataexfil`, `test.Replay`, `test.Blend`

```bash
# 数据外发探测
garak --model openai:chat:exam-target --probes dataexfil --verbose

# 会话重放测试
garak --model openai:chat:exam-target --probes test.Replay --verbose

# 数据混合测试
garak --model openai:chat:exam-target --probes test.Blend --verbose

# 组合探测
garak --model openai:chat:exam-target --probes dataexfil,test.Replay,test.Blend --output json --save_file a09-results.json
```

**探测模块说明**：

| 探测模块 | 测试目标 | 成功指标 |
|----------|----------|----------|
| `dataexfil` | 检测数据外发监控 | 敏感数据外发未被拦截 |
| `test.Replay` | 检测会话监控 | 重放攻击成功 |
| `test.Blend` | 检测异常行为检测 | 混合数据攻击成功 |

---

## 6. Garak 输出分析

### 6.1 输出格式说明

```bash
# JSON格式输出
garak --model openai:chat:exam-target --probes promptinject --output json --save_file results.json

# HTML格式输出
garak --model openai:chat:exam-target --probes promptinject --output html --save_file results.html

# 详细文本输出
garak --model openai:chat:exam-target --probes promptinject --verbose
```

### 6.2 Python 结果分析脚本

```python
import json
from typing import Dict, List, Any

class GarakResultAnalyzer:
    def __init__(self, results_file: str):
        self.results_file = results_file
        self.data = self._load_results()

    def _load_results(self) -> Dict[str, Any]:
        try:
            with open(self.results_file, "r") as f:
                return json.load(f)
        except Exception as e:
            return {"error": str(e)}

    def analyze_results(self) -> Dict[str, Any]:
        if "error" in self.data:
            return {"error": self.data["error"]}

        analysis = {
            "total_probes": 0,
            "vulnerabilities_found": 0,
            "severity_counts": {"critical": 0, "high": 0, "medium": 0, "low": 0},
            "detailed_results": []
        }

        for probe_name, probe_data in self.data.get("probes", {}).items():
            analysis["total_probes"] += 1
            
            for test_case in probe_data.get("tests", []):
                result = test_case.get("result", "FAIL")
                score = test_case.get("score", 0)
                
                if result == "PASS" or score > 0:
                    analysis["vulnerabilities_found"] += 1
                    
                    if score >= 0.8:
                        severity = "critical"
                    elif score >= 0.5:
                        severity = "high"
                    elif score >= 0.3:
                        severity = "medium"
                    else:
                        severity = "low"
                    
                    analysis["severity_counts"][severity] += 1
                    
                    analysis["detailed_results"].append({
                        "probe": probe_name,
                        "prompt": test_case.get("prompt", "")[:50],
                        "response": test_case.get("response", "")[:50],
                        "score": score,
                        "severity": severity
                    })

        return analysis

    def print_summary(self):
        analysis = self.analyze_results()
        
        if "error" in analysis:
            print(f"❌ Error: {analysis['error']}")
            return

        print("=" * 60)
        print("Garak Scan Results Summary")
        print("=" * 60)
        print(f"\nTotal probes: {analysis['total_probes']}")
        print(f"Vulnerabilities found: {analysis['vulnerabilities_found']}")
        print("\nSeverity distribution:")
        for severity, count in analysis["severity_counts"].items():
            print(f"  {severity.capitalize()}: {count}")
        
        if analysis["detailed_results"]:
            print("\nTop vulnerabilities:")
            for i, vuln in enumerate(analysis["detailed_results"][:5]):
                print(f"\n  [{i+1}] Probe: {vuln['probe']}")
                print(f"     Prompt: {vuln['prompt']}")
                print(f"     Score: {vuln['score']:.2f} ({vuln['severity']})")

def main():
    analyzer = GarakResultAnalyzer("results.json")
    analyzer.print_summary()

if __name__ == "__main__":
    main()
```

**代码逐行解释**：

| 行号 | 功能 | 说明 |
|------|------|------|
| 1-2 | 导入依赖 | `json` 用于解析Garak输出 |
| 4-8 | `GarakResultAnalyzer` 初始化 | 加载Garak结果文件 |
| 10-14 | `_load_results` | 加载JSON格式的扫描结果 |
| 16-55 | `analyze_results` | 分析扫描结果，统计漏洞 |
| 23-31 | 遍历探测结果 | 统计每个探测的测试用例 |
| 33-42 | 严重性分级 | 根据分数分为critical/high/medium/low |
| 57-74 | `print_summary` | 打印分析摘要 |
| 76-80 | `main` | 主函数：运行分析器 |

---

## 7. 考试快速上手

### 7.1 三步快速启动

```bash
# 第一步：设置环境变量
$env:GARAK_MODEL="openai:chat:exam-target"
$env:GARAK_BASE_URL="http://exam-env:11434/v1"
$env:GARAK_API_KEY="lm-studio"

# 第二步：运行基础扫描
garak --model $env:GARAK_MODEL --probes promptinject,jailbreak,pii --verbose --output json --save_file exam-results.json

# 第三步：分析结果
python analyze_garak_results.py
```

### 7.2 考试场景应对

**场景1：提示注入测试**
```bash
garak --model openai:chat:exam-target --probes promptinject,goodside --verbose
```

**场景2：Agent目标劫持**
```bash
garak --model openai:chat:exam-target --probes jailbreak,promptinject --verbose
```

**场景3：敏感信息泄露**
```bash
garak --model openai:chat:exam-target --probes pii,dataexfil,credentials --verbose
```

**场景4：全面扫描**
```bash
garak --model openai:chat:exam-target --probes promptinject,jailbreak,pii,dataexfil,goodside,lmrc --verbose --output json --save_file full-scan.json
```

### 7.3 考试常用命令速查

| 命令 | 用途 |
|------|------|
| `garak --list_probes` | 列出所有可用探测模块 |
| `garak --list_models` | 列出所有支持的模型类型 |
| `garak --model <model> --probes <probe> --verbose` | 运行单个探测模块 |
| `garak --model <model> --probes <p1>,<p2>,<p3>` | 运行多个探测模块 |
| `garak --model <model> --probes <probe> --output json --save_file <file>` | 保存结果到JSON文件 |
| `garak --model <model> --probes <probe> --output html --save_file <file>` | 保存结果到HTML文件 |

### 7.4 关键成功指标

| 指标 | 检测方式 |
|------|----------|
| **提示注入成功** | 探测结果中 `result: PASS` 或 `score > 0` |
| **目标劫持成功** | jailbreak探测返回成功 |
| **信息泄露成功** | pii/dataexfil探测发现敏感信息 |
| **编码绕过成功** | encoding探测发现绕过方式 |
| **数据投毒成功** | goodside/test.Blend探测成功 |

### 7.5 考试修改要点

| 修改项 | 默认值 | 修改方式 |
|--------|--------|----------|
| **模型类型** | `openai:chat:exam-target` | 修改`--model`参数 |
| **API地址** | 环境变量控制 | 修改`GARAK_BASE_URL` |
| **API密钥** | 环境变量控制 | 修改`GARAK_API_KEY` |
| **探测模块** | 根据场景选择 | 修改`--probes`参数 |
| **输出格式** | JSON | 修改`--output`参数 |

---

> **文档版本**: v1.0  
> **适用标准**: Garak Framework + OWASP Top 10 for LLM/Agent  
> **考试重要性**: ⭐⭐⭐⭐⭐