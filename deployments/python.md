# Python 环境准备说明

## 文档说明

本文件整合了原有的 Python 环境准备与依赖安装说明内容，适用于快速搭建开发环境。

## 1. Windows 下设置执行策略

```powershell
Set-ExecutionPolicy RemoteSigned

```

## 2. 初始化 Python 项目环境

```bash
uv init --python 3.13.13
```

## 3. 添加依赖

```bash
uv add <package-name>
```

## 4. 同步依赖

```bash
uv sync
```

## 5. 配置国内 PyPI 源

```bash
pip config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple
```

## 6. WSL安装PIP包

```bash
# 1. 先更新包列表
sudo apt update

# 2. 安装 pip（Python3 版）
sudo apt install python3-pip -y

# 3. 验证
pip3 --version

```



## 7. 安装常用工具包

```bash
uv pip install pyrit deepeval garak adversarial-robustness-toolbox counterfit trufflehog fickling
```

```bash
uv pip install giskard
```

 