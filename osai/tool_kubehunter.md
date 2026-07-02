# kube-hunter Kubernetes漏洞扫描实战指南

> OffSec AI-300 (OSAI) 红队备考 - 使用 kube-hunter 进行 Kubernetes 安全扫描

---

## 目录

1. [kube-hunter 安装与配置](#1-kube-hunter-安装与配置)
2. [核心 CLI 语法解析](#2-核心-cli-语法解析)
3. [K8s 漏洞扫描](#3-k8s-漏洞扫描)
4. [扫描结果分析](#4-扫描结果分析)
5. [AI-300 特定场景扫描](#5-ai-300-特定场景扫描)
6. [考试快速上手](#6-考试快速上手)

---

## 1. kube-hunter 安装与配置

### 1.1 安装命令

```bash
# 通过 pip 安装
pip install kube-hunter

# 通过 git 克隆源码
git clone https://github.com/aquasecurity/kube-hunter.git
cd kube-hunter
pip install -e .

# 通过 Docker 运行
docker run -it --rm aquasec/kube-hunter

# 验证安装
kube-hunter --help
```

### 1.2 考试环境配置

创建环境变量文件 `kubehunter.env`：

```bash
# kubehunter.env - 考试环境配置
export KUBE_HUNTER_TARGET="10.0.0.1"
export KUBE_HUNTER_OUTPUT="kubehunter-results.json"
export KUBE_HUNTER_LOG_LEVEL="info"
```

### 1.3 环境变量加载

```bash
# Linux/Mac
source kubehunter.env

# Windows PowerShell
$env:KUBE_HUNTER_TARGET="10.0.0.1"
$env:KUBE_HUNTER_OUTPUT="kubehunter-results.json"
```

---

## 2. 核心 CLI 语法解析

### 2.1 基本命令格式

```bash
kube-hunter [options]
```

### 2.2 关键参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| `--remote` | 指定远程目标IP | `--remote 10.0.0.1` |
| `--pod` | 在Pod内运行扫描 | `--pod` |
| `--report` | 指定报告文件 | `--report results.json` |
| `--format` | 指定报告格式 | `--format json` |
| `--log` | 指定日志级别 | `--log debug` |
| `--list` | 列出所有检测模块 | `--list` |
| `--active` | 启用主动检测模式 | `--active` |
| `--quick` | 快速扫描模式 | `--quick` |
| `--cidr` | 指定CIDR范围扫描 | `--cidr 10.0.0.0/24` |

### 2.3 报告格式

| 格式 | 说明 | 使用方式 |
|------|------|----------|
| `json` | JSON格式报告 | `--format json` |
| `yaml` | YAML格式报告 | `--format yaml` |
| `text` | 文本格式报告 | `--format text` |
| `html` | HTML格式报告 | `--format html` |

### 2.4 考试常用命令模板

```bash
# 扫描本地集群
kube-hunter

# 扫描远程集群
kube-hunter --remote 10.0.0.1

# 扫描CIDR范围
kube-hunter --cidr 10.0.0.0/24

# 保存报告到文件
kube-hunter --remote 10.0.0.1 --report results.json --format json

# 使用环境变量
kube-hunter --remote $KUBE_HUNTER_TARGET --report $KUBE_HUNTER_OUTPUT --format json
```

---

## 3. K8s 漏洞扫描

### 3.1 基础扫描命令

```bash
# 扫描本地环境（在Pod内运行）
kube-hunter --pod

# 扫描远程集群
kube-hunter --remote 10.0.0.1

# 扫描多个目标
kube-hunter --remote 10.0.0.1 --remote 10.0.0.2

# 扫描CIDR范围
kube-hunter --cidr 10.0.0.0/24

# 快速扫描
kube-hunter --remote 10.0.0.1 --quick
```

### 3.2 主动检测模式

```bash
# 启用主动检测（更深入的漏洞探测）
kube-hunter --remote 10.0.0.1 --active

# 主动检测 + 详细日志
kube-hunter --remote 10.0.0.1 --active --log debug

# 主动检测 + 保存报告
kube-hunter --remote 10.0.0.1 --active --report results.json --format json
```

### 3.3 特定模块扫描

```bash
# 列出所有检测模块
kube-hunter --list

# 只检测特定模块
kube-hunter --remote 10.0.0.1 --include "apiserver"

# 排除特定模块
kube-hunter --remote 10.0.0.1 --exclude "dns"

# 检测多个模块
kube-hunter --remote 10.0.0.1 --include "apiserver,etcd,kubelet"
```

### 3.4 常用检测模块

| 模块 | 检测内容 | 风险等级 |
|------|----------|----------|
| `apiserver` | API Server配置缺陷 | 高 |
| `etcd` | etcd配置缺陷 | 高 |
| `kubelet` | Kubelet配置缺陷 | 高 |
| `dns` | DNS配置缺陷 | 中 |
| `dashboard` | Dashboard配置缺陷 | 高 |
| `rbac` | RBAC配置缺陷 | 高 |
| `privileged` | 特权Pod检测 | 高 |
| `mounts` | 挂载配置检测 | 中 |

---

## 4. 扫描结果分析

### 4.1 报告格式解读

```bash
# JSON格式报告示例
{
  "vulnerabilities": [
    {
      "severity": "HIGH",
      "category": "Access",
      "description": "Exposed Kubernetes API Server",
      "evidence": "Found API Server at https://10.0.0.1:6443",
      "location": "10.0.0.1:6443"
    },
    {
      "severity": "MEDIUM",
      "category": "Configuration",
      "description": "Weak RBAC configuration",
      "evidence": "Default Service Account has excessive permissions",
      "location": "default namespace"
    }
  ],
  "summary": {
    "total": 15,
    "high": 5,
    "medium": 8,
    "low": 2
  }
}
```

### 4.2 Python 结果分析脚本

```python
import json
from typing import Dict, List, Any

class KubeHunterAnalyzer:
    def __init__(self, report_file: str):
        self.report_file = report_file
        self.data = self._load_report()

    def _load_report(self) -> Dict[str, Any]:
        try:
            with open(self.report_file, "r") as f:
                return json.load(f)
        except Exception as e:
            return {"error": str(e)}

    def analyze_results(self) -> Dict[str, Any]:
        if "error" in self.data:
            return {"error": self.data["error"]}

        analysis = {
            "total_vulnerabilities": 0,
            "severity_counts": {"HIGH": 0, "MEDIUM": 0, "LOW": 0},
            "categories": {},
            "critical_vulnerabilities": []
        }

        for vuln in self.data.get("vulnerabilities", []):
            analysis["total_vulnerabilities"] += 1
            
            severity = vuln.get("severity", "UNKNOWN")
            if severity in analysis["severity_counts"]:
                analysis["severity_counts"][severity] += 1
            
            category = vuln.get("category", "UNKNOWN")
            if category not in analysis["categories"]:
                analysis["categories"][category] = 0
            analysis["categories"][category] += 1
            
            if severity == "HIGH":
                analysis["critical_vulnerabilities"].append({
                    "description": vuln.get("description", ""),
                    "evidence": vuln.get("evidence", ""),
                    "location": vuln.get("location", "")
                })

        return analysis

    def print_summary(self):
        analysis = self.analyze_results()
        
        if "error" in analysis:
            print(f"❌ Error: {analysis['error']}")
            return

        print("=" * 60)
        print("kube-hunter Scan Results Summary")
        print("=" * 60)
        print(f"\nTotal vulnerabilities: {analysis['total_vulnerabilities']}")
        print("\nSeverity distribution:")
        for severity, count in analysis["severity_counts"].items():
            print(f"  {severity}: {count}")
        
        print("\nCategory distribution:")
        for category, count in analysis["categories"].items():
            print(f"  {category}: {count}")
        
        if analysis["critical_vulnerabilities"]:
            print("\nCritical vulnerabilities:")
            for i, vuln in enumerate(analysis["critical_vulnerabilities"]):
                print(f"\n  [{i+1}] {vuln['description']}")
                print(f"     Evidence: {vuln['evidence']}")
                print(f"     Location: {vuln['location']}")

def main():
    analyzer = KubeHunterAnalyzer("kubehunter-results.json")
    analyzer.print_summary()

if __name__ == "__main__":
    main()
```

**代码逐行解释**：

| 行号 | 功能 | 说明 |
|------|------|------|
| 1-2 | 导入依赖 | `json` 用于解析报告 |
| 4-8 | `KubeHunterAnalyzer` 初始化 | 加载扫描报告 |
| 10-14 | `_load_report` | 加载JSON格式报告 |
| 16-42 | `analyze_results` | 分析报告，统计漏洞 |
| 22-26 | 统计严重性 | HIGH/MEDIUM/LOW |
| 28-32 | 统计类别 | Access/Configuration等 |
| 34-40 | 提取高危漏洞 | 保存详细信息 |
| 44-62 | `print_summary` | 打印分析摘要 |

---

## 5. AI-300 特定场景扫描

### 5.1 AI基础设施扫描

```bash
# 扫描AI集群
kube-hunter --remote 10.0.0.1 --report ai-cluster.json --format json

# 扫描多个AI节点
kube-hunter --cidr 10.0.0.0/24 --report ai-nodes.json --format json

# 主动扫描AI基础设施
kube-hunter --remote 10.0.0.1 --active --report ai-active.json --format json
```

### 5.2 模型服务安全检测

```bash
# 检测模型服务Pod
kube-hunter --remote 10.0.0.1 --include "privileged,mounts"

# 检测AI服务账户权限
kube-hunter --remote 10.0.0.1 --include "rbac"

# 检测模型服务器网络配置
kube-hunter --remote 10.0.0.1 --include "dns,network"
```

### 5.3 向量数据库安全检测

```bash
# 检测向量数据库Pod配置
kube-hunter --remote 10.0.0.1 --include "privileged,mounts"

# 检测向量数据库服务暴露
kube-hunter --remote 10.0.0.1 --include "apiserver,kubelet"

# 检测向量数据库凭证安全
kube-hunter --remote 10.0.0.1 --include "rbac"
```

### 5.4 Ray集群安全检测

```bash
# 检测Ray集群节点
kube-hunter --remote 10.0.0.1 --include "apiserver,kubelet"

# 检测Ray Dashboard暴露
kube-hunter --remote 10.0.0.1 --include "dashboard"

# 检测Ray工作节点配置
kube-hunter --remote 10.0.0.1 --include "privileged,mounts"
```

---

## 6. 考试快速上手

### 6.1 三步快速启动

```bash
# 第一步：设置环境变量
$env:KUBE_HUNTER_TARGET="10.0.0.1"

# 第二步：运行扫描
kube-hunter --remote $env:KUBE_HUNTER_TARGET --report kubehunter-results.json --format json

# 第三步：分析结果
python analyze_kubehunter.py
```

### 6.2 考试场景应对

**场景1：在Pod内扫描**
```bash
kube-hunter --pod --report pod-scan.json --format json
```

**场景2：扫描远程集群**
```bash
kube-hunter --remote 10.0.0.1 --report remote-scan.json --format json
```

**场景3：扫描整个网段**
```bash
kube-hunter --cidr 10.0.0.0/24 --report cidr-scan.json --format json
```

**场景4：主动扫描**
```bash
kube-hunter --remote 10.0.0.1 --active --report active-scan.json --format json
```

### 6.3 考试常用命令速查

| 命令 | 用途 |
|------|------|
| `kube-hunter` | 扫描本地环境 |
| `kube-hunter --remote <ip>` | 扫描远程集群 |
| `kube-hunter --pod` | 在Pod内扫描 |
| `kube-hunter --cidr <range>` | 扫描CIDR范围 |
| `kube-hunter --active` | 启用主动检测 |
| `kube-hunter --quick` | 快速扫描 |
| `kube-hunter --report <file> --format json` | 保存JSON报告 |
| `kube-hunter --list` | 列出检测模块 |

### 6.4 关键成功指标

| 指标 | 检测方式 |
|------|----------|
| **扫描成功** | 生成报告文件 |
| **发现高危漏洞** | 报告中包含HIGH级别漏洞 |
| **API Server暴露** | 检测到未授权的API Server访问 |
| **特权Pod** | 检测到特权运行的Pod |
| **RBAC缺陷** | 检测到过度权限配置 |

### 6.5 考试修改要点

| 修改项 | 默认值 | 修改方式 |
|--------|--------|----------|
| **目标IP** | 无 | 修改 `--remote` 参数 |
| **CIDR范围** | 无 | 修改 `--cidr` 参数 |
| **报告文件** | 控制台 | 修改 `--report` 参数 |
| **报告格式** | text | 修改 `--format` 参数 |
| **检测模式** | 被动 | 添加 `--active` 参数 |

### 6.6 AI-300攻击链中的kube-hunter使用

```
攻击链流程：
┌─────────────────────────────────────────────────────┐
│  Step 1: 获取Pod Shell                             │
│  └── 通过LLM漏洞利用获得容器内Shell                 │
├─────────────────────────────────────────────────────┤
│  Step 2: 运行kube-hunter                           │
│  └── kube-hunter --pod --report results.json       │
├─────────────────────────────────────────────────────┤
│  Step 3: 分析扫描结果                               │
│  └── python analyze_kubehunter.py                  │
├─────────────────────────────────────────────────────┤
│  Step 4: 利用高危漏洞                               │
│  ├── API Server暴露 → 未授权访问                    │
│  ├── 特权Pod → 容器逃逸                            │
│  └── RBAC缺陷 → 权限提升                           │
├─────────────────────────────────────────────────────┤
│  Step 5: 横向移动                                  │
│  ├── 访问其他节点                                  │
│  ├── 访问Ray集群                                   │
│  └── 访问向量数据库                                │
└─────────────────────────────────────────────────────┘
```

---

> **文档版本**: v1.0  
> **适用标准**: kube-hunter Kubernetes Vulnerability Scanner  
> **考试重要性**: ⭐⭐⭐⭐⭐