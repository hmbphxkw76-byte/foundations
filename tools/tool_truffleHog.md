# TruffleHog 凭证扫描实战指南

> OffSec AI-300 (OSAI) 红队备考 - 使用 TruffleHog 进行凭证收集与泄露检测

---

## 目录

1. [TruffleHog 安装与配置](#1-trufflehog-安装与配置)
2. [核心 CLI 语法解析](#2-核心-cli-语法解析)
3. [文件系统扫描](#3-文件系统扫描)
4. [Git 仓库扫描](#4-git-仓库扫描)
5. [Docker 镜像扫描](#5-docker-镜像扫描)
6. [凭证验证与过滤](#6-凭证验证与过滤)
7. [AI-300 特定场景扫描](#7-ai-300-特定场景扫描)
8. [考试快速上手](#8-考试快速上手)

---

## 1. TruffleHog 安装与配置

### 1.1 安装命令

```bash
# 通过 brew 安装（macOS）
brew install trufflehog

# 通过 apt 安装（Linux）
sudo apt install trufflehog

# 通过 scoop 安装（Windows）
scoop install trufflehog

# 通过 Docker 运行
docker run -v "$(pwd):/workspace" trufflesecurity/trufflehog:latest filesystem /workspace

# 验证安装
trufflehog --version
```

### 1.2 考试环境配置

创建环境变量文件 `trufflehog.env`：

```bash
# trufflehog.env - 考试环境配置
export TRUFFLEHOG_TARGET="/"
export TRUFFLEHOG_GIT_URL="https://github.com/target/repo.git"
export TRUFFLEHOG_OUTPUT="trufflehog-results.json"
export TRUFFLEHOG_LOG_LEVEL="debug"
```

### 1.3 环境变量加载

```bash
# Linux/Mac
source trufflehog.env

# Windows PowerShell
$env:TRUFFLEHOG_TARGET="/"
$env:TRUFFLEHOG_GIT_URL="https://github.com/target/repo.git"
$env:TRUFFLEHOG_OUTPUT="trufflehog-results.json"
```

---

## 2. 核心 CLI 语法解析

### 2.1 基本命令格式

```bash
trufflehog <source_type> <target> [options]
```

### 2.2 关键参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| `<source_type>` | 扫描源类型 | `filesystem`, `git`, `docker`, `github`, `gitlab` |
| `<target>` | 扫描目标 | 路径、URL、镜像名 |
| `--output` | 指定输出格式 | `--output results.json` |
| `--format` | 输出格式类型 | `json`, `csv`, `table`, `sarif` |
| `--only-verified` | 只显示已验证的凭证 | `--only-verified` |
| `--fail-on-find` | 发现凭证时返回非零退出码 | `--fail-on-find` |
| `--concurrency` | 并发扫描线程数 | `--concurrency 8` |
| `--exclude` | 排除路径/文件 | `--exclude "node_modules"` |
| `--include` | 包含特定模式 | `--include "*.env"` |
| `--log-level` | 日志级别 | `debug`, `info`, `warn`, `error` |

### 2.3 扫描源类型

| 源类型 | 说明 | 示例 |
|--------|------|------|
| `filesystem` | 扫描本地文件系统 | `trufflehog filesystem /` |
| `git` | 扫描Git仓库 | `trufflehog git https://github.com/target/repo` |
| `docker` | 扫描Docker镜像 | `trufflehog docker image:tag` |
| `github` | 扫描GitHub仓库 | `trufflehog github --repo https://github.com/target/repo` |
| `gitlab` | 扫描GitLab仓库 | `trufflehog gitlab --repo https://gitlab.com/target/repo` |

### 2.4 考试常用命令模板

```bash
# 基础文件系统扫描
trufflehog filesystem / --output results.json --format json

# 只显示已验证的凭证
trufflehog filesystem / --only-verified --output verified-results.json

# 扫描Git仓库（包含历史提交）
trufflehog git https://github.com/target/repo --output git-results.json

# 扫描Docker镜像
trufflehog docker my-image:latest --output docker-results.json

# 使用环境变量
trufflehog filesystem $TRUFFLEHOG_TARGET --output $TRUFFLEHOG_OUTPUT
```

---

## 3. 文件系统扫描

### 3.1 基础扫描命令

```bash
# 扫描整个文件系统
trufflehog filesystem / --output fs-results.json --format json

# 扫描特定目录
trufflehog filesystem /etc --output etc-results.json

# 扫描用户目录
trufflehog filesystem /home --output home-results.json

# 扫描根目录（递归）
trufflehog filesystem / --include "*.env" --output env-results.json
```

### 3.2 AI基础设施关键路径扫描

```bash
# 扫描环境变量文件
trufflehog filesystem / --include "*.env" --output env-secrets.json

# 扫描配置文件
trufflehog filesystem /etc --include "*.conf" --output etc-secrets.json

# 扫描 Kubernetes 配置
trufflehog filesystem /root/.kube --output kube-secrets.json

# 扫描 SSH 密钥
trufflehog filesystem /root/.ssh --output ssh-secrets.json

# 扫描 Python 虚拟环境
trufflehog filesystem /root/.virtualenvs --output venv-secrets.json

# 扫描 Ray 配置
trufflehog filesystem /etc/ray --output ray-secrets.json
```

### 3.3 快速扫描常用路径

```bash
# 考试常用路径扫描脚本
#!/bin/bash

PATHS=(
    "/etc"
    "/var/secrets"
    "/root"
    "/home"
    "/opt"
    "/tmp"
)

for path in "${PATHS[@]}"; do
    echo "[+] Scanning $path..."
    trufflehog filesystem "$path" --only-verified --output "results-${path//\//-}.json"
done
```

**脚本逐行解释**：

| 行号 | 功能 | 说明 |
|------|------|------|
| 1 | 脚本声明 | Bash脚本 |
| 3-11 | 路径数组 | 定义需要扫描的关键路径 |
| 13-17 | 循环扫描 | 遍历每个路径执行扫描 |
| 15 | 输出扫描路径 | 显示当前扫描的路径 |
| 16 | 执行扫描 | 使用TruffleHog扫描，只保留已验证凭证 |

---

## 4. Git 仓库扫描

### 4.1 基础扫描命令

```bash
# 扫描远程Git仓库
trufflehog git https://github.com/target/repo --output git-results.json

# 扫描本地Git仓库
trufflehog git /path/to/local/repo --output local-git-results.json

# 扫描指定分支
trufflehog git https://github.com/target/repo --branch main --output main-branch.json

# 扫描所有分支
trufflehog git https://github.com/target/repo --all-branches --output all-branches.json
```

### 4.2 历史提交扫描

```bash
# 扫描所有历史提交（深度扫描）
trufflehog git https://github.com/target/repo --history --output history-results.json

# 扫描最近N次提交
trufflehog git https://github.com/target/repo --max-depth 100 --output recent-results.json

# 扫描特定提交范围
trufflehog git https://github.com/target/repo --since "2024-01-01" --output year-results.json

# 扫描Git子模块
trufflehog git https://github.com/target/repo --include-submodules --output submodules-results.json
```

### 4.3 过滤与优化

```bash
# 排除特定路径
trufflehog git https://github.com/target/repo --exclude "node_modules" --exclude "*.log"

# 只扫描特定路径
trufflehog git https://github.com/target/repo --include "config/*" --include "*.env*"

# 并发扫描
trufflehog git https://github.com/target/repo --concurrency 16 --output fast-results.json
```

---

## 5. Docker 镜像扫描

### 5.1 基础扫描命令

```bash
# 扫描本地Docker镜像
trufflehog docker my-image:latest --output docker-results.json

# 扫描远程Docker镜像
trufflehog docker docker.io/library/nginx:latest --output remote-docker.json

# 扫描多个镜像
trufflehog docker image1:tag image2:tag --output multi-image.json

# 扫描镜像层
trufflehog docker my-image:latest --layers --output layers-results.json
```

### 5.2 AI容器镜像扫描

```bash
# 扫描AI模型服务镜像
trufflehog docker ollama/ollama:latest --output ollama-secrets.json
trufflehog docker vllm/vllm:latest --output vllm-secrets.json
trufflehog docker pytorch/pytorch:latest --output pytorch-secrets.json

# 扫描Kubernetes Pod中的镜像
kubectl get pods -o jsonpath='{.items[*].spec.containers[*].image}' | tr ' ' '\n' | while read img; do
    trufflehog docker "$img" --output "k8s-${img//\//-}.json"
done
```

**脚本逐行解释**：

| 行号 | 功能 | 说明 |
|------|------|------|
| 1 | 获取所有Pod的镜像 | 使用kubectl获取所有容器镜像 |
| 2 | 转换为每行一个镜像 | 将空格分隔的镜像名转为换行 |
| 3 | 循环扫描每个镜像 | 对每个镜像执行TruffleHog扫描 |

---

## 6. 凭证验证与过滤

### 6.1 只显示已验证的凭证

```bash
# 只显示已验证的凭证（排除误报）
trufflehog filesystem / --only-verified --output verified-results.json

# 扫描Git仓库，只保留已验证凭证
trufflehog git https://github.com/target/repo --only-verified --output verified-git.json

# 扫描Docker镜像，只保留已验证凭证
trufflehog docker my-image:latest --only-verified --output verified-docker.json
```

### 6.2 按类型过滤

```bash
# 只查找API密钥
trufflehog filesystem / --only-verified --filter-type "API Key" --output api-keys.json

# 只查找密码
trufflehog filesystem / --only-verified --filter-type "Password" --output passwords.json

# 只查找OAuth令牌
trufflehog filesystem / --only-verified --filter-type "OAuth Token" --output oauth.json

# 只查找数据库凭证
trufflehog filesystem / --only-verified --filter-type "Database" --output db-credentials.json
```

### 6.3 输出格式

```bash
# JSON格式输出（便于后续分析）
trufflehog filesystem / --format json --output results.json

# CSV格式输出（便于Excel分析）
trufflehog filesystem / --format csv --output results.csv

# 表格格式输出（便于终端查看）
trufflehog filesystem / --format table

# SARIF格式输出（便于CI/CD集成）
trufflehog filesystem / --format sarif --output results.sarif
```

---

## 7. AI-300 特定场景扫描

### 7.1 Kubernetes 环境扫描

```bash
# 扫描Kubernetes Secret文件
trufflehog filesystem /var/run/secrets/kubernetes.io/serviceaccount --output k8s-secrets.json

# 扫描Kubernetes配置目录
trufflehog filesystem /root/.kube --output kube-config.json

# 扫描Pod中的环境变量文件
trufflehog filesystem /proc/self/environ --output env-vars.json

# 扫描K8s ConfigMaps
kubectl get configmaps -o json | trufflehog filesystem - --output configmaps.json
```

### 7.2 Ray 集群扫描

```bash
# 扫描Ray配置文件
trufflehog filesystem /etc/ray --output ray-config.json

# 扫描Ray工作目录
trufflehog filesystem /tmp/ray --output ray-tmp.json

# 扫描Ray日志文件
trufflehog filesystem /var/log/ray --output ray-logs.json

# 扫描Ray环境变量
trufflehog filesystem /etc/profile.d/ray.sh --output ray-env.json
```

### 7.3 模型服务器扫描

```bash
# 扫描Ollama配置
trufflehog filesystem /root/.ollama --output ollama-secrets.json

# 扫描vLLM配置
trufflehog filesystem /etc/vllm --output vllm-secrets.json

# 扫描Triton配置
trufflehog filesystem /etc/triton --output triton-secrets.json

# 扫描MLflow配置
trufflehog filesystem /etc/mlflow --output mlflow-secrets.json

# 扫描模型权重文件（可能包含后门）
trufflehog filesystem /models --include "*.bin" --include "*.pkl" --output model-secrets.json
```

### 7.4 向量数据库扫描

```bash
# 扫描ChromaDB配置
trufflehog filesystem /chroma --output chroma-secrets.json

# 扫描Milvus配置
trufflehog filesystem /milvus --output milvus-secrets.json

# 扫描Pinecone配置（环境变量）
trufflehog filesystem /etc/environment --include "*pinecone*" --output pinecone-secrets.json

# 扫描Weaviate配置
trufflehog filesystem /weaviate --output weaviate-secrets.json
```

---

## 8. 考试快速上手

### 8.1 三步快速启动

```bash
# 第一步：设置环境变量
$env:TRUFFLEHOG_TARGET="/"

# 第二步：运行基础扫描（只保留已验证凭证）
trufflehog filesystem $env:TRUFFLEHOG_TARGET --only-verified --output trufflehog-results.json

# 第三步：查看结果
cat trufflehog-results.json | python -m json.tool | head -100
```

### 8.2 考试场景应对

**场景1：获取Shell后扫描文件系统**
```bash
trufflehog filesystem / --only-verified --output fs-results.json
trufflehog filesystem /etc --only-verified --output etc-results.json
trufflehog filesystem /root --only-verified --output root-results.json
```

**场景2：发现Git仓库**
```bash
trufflehog git /path/to/local/repo --history --only-verified --output git-results.json
```

**场景3：访问Kubernetes环境**
```bash
trufflehog filesystem /var/run/secrets/kubernetes.io/serviceaccount --output k8s-secrets.json
trufflehog filesystem /root/.kube --output kube-config.json
```

**场景4：发现Ray集群**
```bash
trufflehog filesystem /etc/ray --output ray-secrets.json
trufflehog filesystem /tmp/ray --output ray-tmp.json
```

### 8.3 考试常用命令速查

| 命令 | 用途 |
|------|------|
| `trufflehog filesystem / --only-verified` | 扫描根目录，只保留已验证凭证 |
| `trufflehog filesystem /etc --only-verified` | 扫描/etc目录 |
| `trufflehog filesystem /root --only-verified` | 扫描root目录 |
| `trufflehog git <repo-url> --history` | 扫描Git仓库历史提交 |
| `trufflehog docker <image>` | 扫描Docker镜像 |
| `trufflehog filesystem /var/run/secrets` | 扫描K8s Secret目录 |
| `trufflehog --only-verified --format json` | 只输出已验证凭证的JSON格式 |

### 8.4 关键成功指标

| 指标 | 检测方式 |
|------|----------|
| **发现API密钥** | 输出中包含 `API Key` 类型的凭证 |
| **发现密码** | 输出中包含 `Password` 类型的凭证 |
| **发现OAuth令牌** | 输出中包含 `OAuth Token` 类型的凭证 |
| **发现数据库凭证** | 输出中包含 `Database` 类型的凭证 |
| **凭证已验证** | 使用 `--only-verified` 参数过滤 |

### 8.5 考试修改要点

| 修改项 | 默认值 | 修改方式 |
|--------|--------|----------|
| **扫描目标** | `/` | 修改命令中的路径或URL |
| **输出文件** | `results.json` | 修改 `--output` 参数 |
| **扫描类型** | `filesystem` | 修改为 `git`, `docker` 等 |
| **验证模式** | 全部输出 | 添加 `--only-verified` 参数 |
| **过滤类型** | 所有类型 | 添加 `--filter-type` 参数 |

### 8.6 AI-300攻击链中的TruffleHog使用

```
攻击链流程：
┌─────────────────────────────────────────────────────┐
│  Step 1: LLM漏洞利用                               │
│  └── 获取初始访问权限                               │
├─────────────────────────────────────────────────────┤
│  Step 2: RCE获取Shell                              │
│  └── 在Pod/容器中获取命令执行权限                    │
├─────────────────────────────────────────────────────┤
│  Step 3: TruffleHog扫描                            │
│  ├── trufflehog filesystem / --only-verified       │
│  ├── trufflehog filesystem /etc --only-verified    │
│  ├── trufflehog filesystem /root --only-verified   │
│  └── trufflehog filesystem /var/run/secrets --only-verified │
├─────────────────────────────────────────────────────┤
│  Step 4: 获取凭证                                  │
│  ├── 发现API密钥、密码、令牌                        │
│  └── 验证凭证有效性                                │
├─────────────────────────────────────────────────────┤
│  Step 5: 横向移动                                  │
│  ├── 使用凭证访问Ray集群                            │
│  ├── 使用凭证访问GPU宿主机                          │
│  └── 使用凭证访问向量数据库                        │
└─────────────────────────────────────────────────────┘
```

---

> **文档版本**: v1.0  
> **适用标准**: TruffleHog Credential Scanner  
> **考试重要性**: ⭐⭐⭐⭐⭐