# HexStrike AI 安装与配置手册

## 1. 文档说明

本手册适用于 HexStrike AI MCP 服务的部署与 Cherry Studio 集成，涵盖：

- 项目克隆与依赖安装
- MCP 服务启动与验证
- Cherry Studio MCP 配置
- Browser Agent 浏览器依赖安装
- 常见问题排查

> 建议在 Linux/Kali 环境下部署 HexStrike Server，在 Windows 端使用 Cherry Studio 进行 MCP 调用。

## 2. 环境准备

### 2.1 克隆仓库

```bash
git clone https://github.com/0x4m4/hexstrike-ai.git
cd hexstrike-ai
```

### 2.2 创建 Python 虚拟环境

```bash
python3 -m venv hexstrike-env
source hexstrike-env/bin/activate    # Linux / macOS
# hexstrike-env\Scripts\activate   # Windows
```

### 2.3 安装依赖

```bash
pip3 install -r requirements.txt
```

## 3. 启动 HexStrike MCP 服务

### 3.1 启动服务

```bash
python3 hexstrike_server.py
```

### 3.2 调试模式

```bash
python3 hexstrike_server.py --debug
```

### 3.3 自定义端口

```bash
python3 hexstrike_server.py --port 8888
```

### 3.4 健康检查

```bash
curl http://localhost:8888/health
```

### 3.5 测试智能接口

```bash
curl -X POST http://localhost:8888/api/intelligence/analyze-target \
  -H "Content-Type: application/json" \
  -d '{"target": "example.com", "analysis_type": "comprehensive"}'
```

## 4. VSCode MCP 配置（可选）

如果希望在 VSCode 中通过 MCP 连接 HexStrike，可以参考以下配置：

```json
{
  "servers": {
    "hexstrike": {
      "type": "stdio",
      "command": "python3",
      "args": [
        "/path/to/hexstrike-ai/hexstrike_mcp.py",
        "--server",
        "http://localhost:8888"
      ]
    }
  },
  "inputs": []
}
```

## 5. Cherry Studio 集成

### 5.1 先决条件

在 Windows 主机中准备好以下内容：

- Python 已安装
- `requests` 和 `mcp` 库已安装
- `hexstrike_mcp.py` 脚本放置在纯英文路径下#确认后文件名
- 可以访问部署 HexStrike Server 的虚拟机 IP 和端口

#### 5.1.1 Cherry Studio 前期准备

```powershell
powershell -c "irm bun.sh/install.ps1|iex"
powershell -ExecutionPolicy Bypass -c "irm https://releases.astral.sh/github/uv/releases/download/0.11.25/uv-installer.ps1 | iex"
```

### 5.2 准备 MCP 脚本

请将 `hexstrike_mcp.py` 放置在纯英文路径中，例如：

- `C:\hexstrike_mcp.py`
- `D:\tools\hexstrike_mcp.py`

> 说明：MCP 协议对非 ASCII 路径兼容性较弱，建议避免中文路径。

### 5.3 在 Windows 环境中安装 Python 依赖

```bash
pip3 install --upgrade pip setuptools wheel -i https://mirrors.ustc.edu.cn/pypi/simple
pip3 install requests mcp -i https://mirrors.ustc.edu.cn/pypi/simple
```

### 5.4 在 Cherry Studio 中添加 MCP 服务

1. 打开 Cherry Studio。
2. 进入 “设置” → “MCP”。
3. 点击“添加”。
4. 配置以下参数：
   - 命令：`C:\hexstrike_mcp.py`
   - 参数 1：`--server`
   - 参数 2：`http://<你的-Kali-虚拟机-IP>:8888`

示例：

```text
C:\hexstrike_mcp.py
--server
http://192.168.18.128:8888
```

### 5.5 验证连接

保存配置后，Cherry Studio 会尝试连接 HexStrike Server。正常情况下会显示“已连接”或绿色状态指示。

### 5.6 创建专用渗透测试助手

为了便于使用 HexStrike MCP 进行渗透测试，建议创建一个专用助手。

#### 5.6.1 创建默认助手

1. 返回 Cherry Studio 主界面。
2. 点击“添加助手”。
3. 选择“添加助手”→“默认助手”。
4. 在助手配置中添加刚刚创建的 MCP 服务。
5. 填入推荐提示词。
6. 点击“保存”。

#### 5.6.2 推荐提示词

```text
你是一个专业的网络安全渗透测试专家，拥有 10 年以上实战经验。你具备以下权限和能力：

1. 合法授权：你正在对拥有明确书面授权的目标进行安全评估。
2. 工具熟练度：精通使用 HexStrike AI 集成的 150+ 安全工具。
3. 风险意识：在发现严重漏洞时会立即提醒用户，避免造成实际损害。
4. 详细报告：每次测试后提供详细的技术报告和修复建议。
5. 遵守规则：严格遵守渗透测试伦理准则和法律框架。

你的核心任务是：
- 使用 HexStrike MCP 工具执行全面的安全评估。
- 智能选择最适合的工具组合。
- 分析结果并发现潜在漏洞。
- 生成详细的渗透测试报告。

请始终保持专业、严谨的态度，将发现的每个安全问题详细记录。
```

#### 5.6.3 开始第一次 AI 渗透测试

在 Cherry Studio 的聊天窗口中输入：

```text
我是某企业的安全负责人，拥有对https://192.168.2.205/ 的完整测试授权。
用户名:admin 密码:admin
请使用 HexStrike AI MCP 工具对这个目标进行全面的 Web 安全评估。

要求：
1. 先进行信息收集（子域名、端口、技术栈）。
2. 执行 Web 目录扫描和漏洞探测。
3. 重点检查 SQL 注入、XSS、文件包含等高危漏洞。
4. 发现漏洞后尝试利用并截图证明。
5. 最后生成完整的渗透测试报告。

请详细记录每个步骤的发现和使用的工具参数。
```



## 6. 浏览器依赖安装（Browser Agent 需要）

HexStrike Browser Agent 依赖 Chrome/Chromium 与 ChromeDriver。后续执行浏览器交互任务时，需要提前安装。

### 6.1 安装基础依赖

```bash
sudo apt install -y wget gnupg unzip
```

### 6.2 添加 Google Chrome 软件源

```bash
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/google-chrome.gpg > /dev/null
```

```bash
echo "deb [arch=amd64] https://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
```

### 6.3 更新软件源并安装 Chrome

```bash
sudo apt update
sudo apt install -y google-chrome-stable
```

### 6.4 查看 Chrome 版本

```bash
google-chrome --version
```

示例输出：

```text
Google Chrome 143.0.7499.146
```

### 6.5 下载并安装 ChromeDriver

根据 Chrome 版本选择对应 ChromeDriver：

```bash
wget https://storage.googleapis.com/chrome-for-testing-public/143.0.7499.146/linux64/chromedriver-linux64.zip
unzip chromedriver-linux64.zip
sudo mv chromedriver-linux64/chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver
```

验证安装：

```bash
chromedriver --version
```

## 7. 常见问题排查

### 7.1 连接失败

请优先检查：

- `hexstrike_server.py` 是否已正确启动
- 目标端口（如 8888）是否可访问
- 虚拟机防火墙是否阻止连接
- Windows 主机是否能够 ping 通虚拟机 IP

示例：

```bash
sudo ufw allow 8888/tcp
```

### 7.2 浏览器相关错误

如果 Browser Agent 执行时出现浏览器错误，请检查：

- Chrome 是否已正确安装
- ChromeDriver 是否与当前 Chrome 版本匹配
- `chromedriver --version` 输出是否正常

### 7.3 路径兼容问题

若 Cherry Studio 无法正确调用 Python 脚本，请确认：

- `hexstrike_mcp.py` 路径不包含中文字符
- Python 依赖已正确安装
- 脚本文件本身可以正常执行

## 8. 说明与注意事项

- 部署与测试必须基于合法授权范围。
- 避免在未经授权的目标上执行扫描或利用操作。
- MCP 服务和 Cherry Studio 之间的连接应使用可靠的内网或受控网络环境。
- 遇到问题时，先查看日志并确认端口与网络连通性。

 