# 配置Python环境准备

Windows安装准备 Powershell系统管理员身份执行 

Set-ExecutionPolicy RemoteSigned

1.指定版本初始化

uv init --python 3.13.13

2.添加安装包，自动加到dependencies中

uv add packages名称

3.自动同步

uv sync

4.配置国内源

pip config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple

5.安装工具包

uv pip install pyrit deepeval garak adversarial-robustness-toolbox counterfit trufflehog fickling 

uv pip install giskard

