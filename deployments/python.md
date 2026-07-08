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

## 6. 安装常用工具包

```bash
uv pip install pyrit deepeval garak adversarial-robustness-toolbox counterfit trufflehog fickling
```

```bash
uv pip install giskard
```


#支持GPU的包
pip install --pre --upgrade ipex-llm[xpu] -i https://pypi.org/simple --extra-index-url https://pytorch-extension.intel.com/release-whl/stable/xpu/us/

#模型加载时的设备指定
from ipex_llm import optimize_model
model = optimize_model(model, device="xpu")  # 自动识别 Iris Xe 为 xpu:0

#Iris Xe 加速收益有限，启用 AMX 指令集的 CPU 推理可能更快
model = optimize_model(model, device="cpu", dtype="bfloat16")  # 利用酷睿 Ultra AMX

#为何设置 device="xpu" 后 GPU 利用率仍为 0%？ 可能原因：
未设置 BIGDL_LLM_XMX_DISABLED=1（Iris Xe 必须关闭 XMX）。
模型过大触发显存溢出，自动切回 CPU。
驱动版本过旧（需 ≥ 31.0.101.5821）