# Nuclei 模板化漏洞扫描实战指南

> OffSec AI-300 (OSAI) 红队备考 - 使用 Nuclei 进行多协议漏洞扫描

---

## 目录

1. [Nuclei 安装与配置](#1-nuclei-安装与配置)
2. [核心 CLI 语法解析](#2-核心-cli-语法解析)
3. [模板化漏洞扫描](#3-模板化漏洞扫描)
4. [自定义模板编写](#4-自定义模板编写)
5. [AI-300 特定场景扫描](#5-ai-300-特定场景扫描)
6. [考试快速上手](#6-考试快速上手)

---

## 1. Nuclei 安装与配置

### 1.1 安装命令

```bash
# 通过 apt 安装（Linux）
sudo apt install nuclei

# 通过 brew 安装（macOS）
brew install nuclei

# 通过 scoop 安装（Windows）
scoop install nuclei

# 通过 Docker 运行
docker run -it --rm projectdiscovery/nuclei

# 通过二进制安装
wget https://github.com/projectdiscovery/nuclei/releases/latest/download/nuclei_$(uname -s)_amd64.tar.gz
tar -xzvf nuclei_*.tar.gz
sudo mv nuclei /usr/local/bin/

# 验证安装
nuclei --help
```

### 1.2 更新模板

```bash
# 更新所有模板
nuclei -update-templates

# 更新特定模板
nuclei -update-templates -t cves/

# 查看已安装模板
ls ~/.local/share/nuclei/templates/
```

### 1.3 考试环境配置

创建环境变量文件 `nuclei.env`：

```bash
# nuclei.env - 考试环境配置
export NUCLEI_TARGET="http://10.0.0.1"
export NUCLEI_TEMPLATES="~/.local/share/nuclei/templates/"
export NUCLEI_OUTPUT="nuclei-results.json"
export NUCLEI_THREADS="10"
```

### 1.4 环境变量加载

```bash
# Linux/Mac
source nuclei.env

# Windows PowerShell
$env:NUCLEI_TARGET="http://10.0.0.1"
$env:NUCLEI_OUTPUT="nuclei-results.json"
```

---

## 2. 核心 CLI 语法解析

### 2.1 基本命令格式

```bash
nuclei -u <target> -t <templates> [options]
```

### 2.2 关键参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| `-u` | 指定目标URL | `-u http://10.0.0.1` |
| `-l` | 指定目标列表文件 | `-l targets.txt` |
| `-t` | 指定模板路径 | `-t templates/kubernetes/` |
| `-o` | 指定输出文件 | `-o results.json` |
| `-f` | 指定输出格式 | `-f json` |
| `-c` | 指定并发数 | `-c 10` |
| `-timeout` | 指定超时时间 | `-timeout 10` |
| `-retries` | 指定重试次数 | `-retries 3` |
| `-v` | 详细输出 | `-v` |
| `-silent` | 静默模式 | `-silent` |
| `-severity` | 指定严重级别 | `-severity critical,high` |
| `-tags` | 指定标签 | `-tags cve,misconfig` |

### 2.3 输出格式

| 格式 | 说明 | 使用方式 |
|------|------|----------|
| `json` | JSON格式输出 | `-f json` |
| `csv` | CSV格式输出 | `-f csv` |
| `table` | 表格格式输出 | `-f table` |
| `markdown` | Markdown格式输出 | `-f markdown` |
| `sarif` | SARIF格式输出 | `-f sarif` |

### 2.4 严重性级别

| 级别 | 说明 | 使用方式 |
|------|------|----------|
| `critical` | 关键漏洞 | `-severity critical` |
| `high` | 高危漏洞 | `-severity high` |
| `medium` | 中危漏洞 | `-severity medium` |
| `low` | 低危漏洞 | `-severity low` |
| `info` | 信息泄露 | `-severity info` |

### 2.5 考试常用命令模板

```bash
# 基础扫描
nuclei -u http://10.0.0.1 -t templates/

# 指定模板目录
nuclei -u http://10.0.0.1 -t templates/kubernetes/

# 只扫描高危漏洞
nuclei -u http://10.0.0.1 -t templates/ -severity critical,high

# 保存JSON格式输出
nuclei -u http://10.0.0.1 -t templates/ -o results.json -f json

# 使用环境变量
nuclei -u $NUCLEI_TARGET -t $NUCLEI_TEMPLATES -o $NUCLEI_OUTPUT -f json
```

---

## 3. 模板化漏洞扫描

### 3.1 基础扫描命令

```bash
# 扫描单个目标
nuclei -u http://10.0.0.1 -t templates/

# 扫描多个目标
nuclei -l targets.txt -t templates/

# 扫描CIDR范围
nuclei -u http://10.0.0.0/24 -t templates/

# 扫描子域名
nuclei -u "*.example.com" -t templates/
```

### 3.2 特定模板扫描

```bash
# K8s模板扫描
nuclei -u http://k8s-target -t templates/kubernetes/

# CVE模板扫描
nuclei -u http://target -t templates/cves/

# 云服务模板扫描
nuclei -u http://target -t templates/cloud/

# 网络服务模板扫描
nuclei -u http://target -t templates/network/

# 安全配置模板扫描
nuclei -u http://target -t templates/misconfiguration/
```

### 3.3 标签过滤扫描

```bash
# 按标签扫描
nuclei -u http://target -t templates/ -tags cve

# 多个标签
nuclei -u http://target -t templates/ -tags cve,misconfig

# 排除标签
nuclei -u http://target -t templates/ -tags-exclude ssl
```

### 3.4 常用模板目录

| 目录 | 内容 | 适用场景 |
|------|------|----------|
| `cves/` | CVE漏洞模板 | 已知漏洞检测 |
| `kubernetes/` | K8s漏洞模板 | K8s环境扫描 |
| `cloud/` | 云服务模板 | 云环境扫描 |
| `network/` | 网络服务模板 | 端口服务扫描 |
| `misconfiguration/` | 配置错误模板 | 安全配置检测 |
| `exposed-panels/` | 暴露面板模板 | 管理界面检测 |
| `fuzzing/` | Fuzzing模板 | 模糊测试 |

---

## 4. 自定义模板编写

### 4.1 模板结构

```yaml
id: template-id

info:
  name: Template Name
  author: Author Name
  severity: high
  description: Description of the vulnerability
  tags: cve,misconfig

http:
  - method: GET
    path:
      - "{{BaseURL}}/api/v1/health"
    
    matchers:
      - type: status
        status:
          - 200
      
      - type: word
        words:
          - "unauthorized"
        part: body
```

**模板逐行解释**：

| 字段 | 说明 |
|------|------|
| `id` | 模板唯一标识符 |
| `info.name` | 模板名称 |
| `info.author` | 作者名称 |
| `info.severity` | 严重级别 |
| `info.description` | 漏洞描述 |
| `info.tags` | 标签列表 |
| `http.method` | HTTP方法 |
| `http.path` | 请求路径 |
| `matchers.type` | 匹配器类型 |
| `matchers.status` | 状态码匹配 |
| `matchers.words` | 关键词匹配 |

### 4.2 自定义AI服务扫描模板

```yaml
id: ai-model-service-exposure

info:
  name: AI Model Service Exposure
  author: ai-red-team
  severity: high
  description: AI model service is exposed without authentication
  tags: ai,misconfig,exposure

http:
  - method: GET
    path:
      - "{{BaseURL}}/v1/models"
      - "{{BaseURL}}/api/models"
      - "{{BaseURL}}/models"
    
    headers:
      Content-Type: application/json
    
    matchers:
      - type: status
        status:
          - 200
      
      - type: word
        words:
          - "\"id\":"
          - "\"name\":"
          - "models"
        part: body
        condition: or
    
    extractors:
      - type: json
        json:
          - ".data[].id"
```

### 4.3 自定义向量数据库扫描模板

```yaml
id: vector-db-unauthorized-access

info:
  name: Vector Database Unauthorized Access
  author: ai-red-team
  severity: high
  description: Vector database is accessible without authentication
  tags: ai,vector-db,misconfig

http:
  - method: GET
    path:
      - "{{BaseURL}}/api/v1/collections"
      - "{{BaseURL}}/collections"
      - "{{BaseURL}}/v1/collections"
    
    matchers:
      - type: status
        status:
          - 200
      
      - type: word
        words:
          - "collections"
          - "embeddings"
          - "vectors"
        part: body
        condition: or
    
    extractors:
      - type: json
        json:
          - ".collections[].name"
```

### 4.4 自定义云元数据扫描模板

```yaml
id: cloud-metadata-exposure

info:
  name: Cloud Metadata Exposure
  author: ai-red-team
  severity: critical
  description: Cloud metadata service is accessible
  tags: cloud,metadata,misconfig

http:
  - method: GET
    path:
      - "http://169.254.169.254/latest/meta-data/"
      - "http://169.254.169.254/latest/user-data"
      - "http://169.254.169.254/latest/meta-data/iam/security-credentials/"
    
    matchers:
      - type: status
        status:
          - 200
      
      - type: word
        words:
          - "instance-id"
          - "iam"
          - "security-credentials"
        part: body
        condition: or
```

---

## 5. AI-300 特定场景扫描

### 5.1 AI服务扫描

```bash
# 扫描AI API服务
nuclei -u http://ai-target -t templates/exposed-panels/ -t templates/misconfiguration/

# 扫描模型服务
nuclei -u http://model-server -t templates/exposed-panels/ -severity critical,high

# 扫描向量数据库
nuclei -u http://vector-db -t templates/exposed-panels/ -severity critical,high
```

### 5.2 K8s环境扫描

```bash
# K8s API Server扫描
nuclei -u https://k8s-api:6443 -t templates/kubernetes/

# K8s Dashboard扫描
nuclei -u http://k8s-dashboard -t templates/kubernetes/

# K8s配置错误扫描
nuclei -u http://k8s-target -t templates/kubernetes/ -severity critical,high
```

### 5.3 云元数据扫描

```bash
# 扫描云元数据端点
nuclei -u http://169.254.169.254 -t templates/cloud/

# AWS元数据扫描
nuclei -u http://169.254.169.254/latest/meta-data/ -t templates/cloud/aws/

# GCP元数据扫描
nuclei -u http://metadata.google.internal -t templates/cloud/gcp/

# Azure元数据扫描
nuclei -u http://169.254.169.254/metadata/ -t templates/cloud/azure/
```

### 5.4 Ray集群扫描

```bash
# 扫描Ray Dashboard
nuclei -u http://ray-dashboard:8265 -t templates/exposed-panels/

# 扫描Ray API
nuclei -u http://ray-api:8265 -t templates/misconfiguration/

# 扫描Ray工作节点
nuclei -u http://ray-worker -t templates/network/
```

### 5.5 模型服务器扫描

```bash
# 扫描Ollama服务
nuclei -u http://ollama:11434 -t templates/exposed-panels/

# 扫描vLLM服务
nuclei -u http://vllm:8000 -t templates/exposed-panels/

# 扫描Triton服务
nuclei -u http://triton:8000 -t templates/exposed-panels/

# 扫描MLflow服务
nuclei -u http://mlflow:5000 -t templates/exposed-panels/
```

---

## 6. 考试快速上手

### 6.1 三步快速启动

```bash
# 第一步：设置环境变量
$env:NUCLEI_TARGET="http://10.0.0.1"

# 第二步：运行扫描
nuclei -u $env:NUCLEI_TARGET -t templates/ -o nuclei-results.json -f json -severity critical,high

# 第三步：查看结果
cat nuclei-results.json | python -m json.tool | head -100
```

### 6.2 考试场景应对

**场景1：扫描AI服务**
```bash
nuclei -u http://ai-target -t templates/exposed-panels/ -t templates/misconfiguration/ -o ai-scan.json -f json
```

**场景2：扫描K8s环境**
```bash
nuclei -u https://k8s-api -t templates/kubernetes/ -o k8s-scan.json -f json
```

**场景3：扫描云元数据**
```bash
nuclei -u http://169.254.169.254 -t templates/cloud/ -o cloud-scan.json -f json
```

**场景4：扫描多个目标**
```bash
nuclei -l targets.txt -t templates/ -o multi-scan.json -f json -c 20
```

### 6.3 考试常用命令速查

| 命令 | 用途 |
|------|------|
| `nuclei -u <target> -t templates/` | 基础扫描 |
| `nuclei -u <target> -t templates/kubernetes/` | K8s扫描 |
| `nuclei -u <target> -t templates/cloud/` | 云服务扫描 |
| `nuclei -u <target> -t templates/cves/` | CVE扫描 |
| `nuclei -u <target> -severity critical,high` | 只扫描高危漏洞 |
| `nuclei -u <target> -o results.json -f json` | 保存JSON报告 |
| `nuclei -update-templates` | 更新模板 |
| `nuclei -l targets.txt -t templates/` | 批量扫描 |

### 6.4 关键成功指标

| 指标 | 检测方式 |
|------|----------|
| **扫描成功** | 生成报告文件 |
| **发现高危漏洞** | 报告中包含critical/high级别漏洞 |
| **AI服务暴露** | 检测到未授权的AI API访问 |
| **云元数据暴露** | 检测到可访问的云元数据端点 |
| **K8s配置缺陷** | 检测到K8s安全配置错误 |

### 6.5 考试修改要点

| 修改项 | 默认值 | 修改方式 |
|--------|--------|----------|
| **目标URL** | 无 | 修改 `-u` 参数 |
| **模板路径** | `templates/` | 修改 `-t` 参数 |
| **输出文件** | 控制台 | 修改 `-o` 参数 |
| **输出格式** | text | 修改 `-f` 参数 |
| **严重级别** | 全部 | 修改 `-severity` 参数 |
| **并发数** | 5 | 修改 `-c` 参数 |

### 6.6 AI-300攻击链中的Nuclei使用

```
攻击链流程：
┌─────────────────────────────────────────────────────┐
│  Step 1: 初始访问                                   │
│  └── 通过LLM漏洞利用获得初始访问                    │
├─────────────────────────────────────────────────────┤
│  Step 2: 端口扫描                                   │
│  └── nmap -sV target                               │
├─────────────────────────────────────────────────────┤
│  Step 3: Nuclei扫描                                │
│  ├── nuclei -u http://target -t templates/         │
│  ├── nuclei -u http://k8s-target -t templates/kubernetes/ │
│  └── nuclei -u http://169.254.169.254 -t templates/cloud/ │
├─────────────────────────────────────────────────────┤
│  Step 4: 分析漏洞                                   │
│  └── 根据扫描结果选择可利用的漏洞                    │
├─────────────────────────────────────────────────────┤
│  Step 5: 漏洞利用                                   │
│  ├── 利用云元数据获取凭证                           │
│  ├── 利用K8s配置缺陷提升权限                        │
│  └── 利用AI服务暴露获取数据                         │
└─────────────────────────────────────────────────────┘
```

---

> **文档版本**: v1.0  
> **适用标准**: Nuclei Template-Based Vulnerability Scanner  
> **考试重要性**: ⭐⭐⭐⭐⭐