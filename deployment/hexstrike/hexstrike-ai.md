# HexStrike AI 安装与配置手册

## 1. 文档说明

本文档用于指导在 Kali Linux 环境下部署 HexStrike AI，并配置 Cherry Studio 等 MCP 客户端进行联调与使用。本文档适用于需要在虚拟机或服务器端运行 HexStrike 服务、并通过 Windows 客户端访问的场景。

---

## 2. 环境要求

在开始部署前，请确认以下条件已经满足：

- 操作系统：Kali Linux
- 权限要求：具备 sudo 权限
- 网络条件：可以访问外网，便于安装依赖和浏览器驱动
- 目标场景：需要使用 HexStrike 的 MCP Server 功能
- 可选组件：Chrome/Chromium 与 ChromeDriver（用于 Browser Agent）

---

## 3. 配置 APT 源（推荐）

为了提升下载速度并避免软件源异常，建议先配置国内镜像源。

### 3.1 备份原有源列表

```bash
sudo cp /etc/apt/sources.list /etc/apt/sources.list.bak
```

### 3.2 编辑源配置文件

```bash
sudo vim /etc/apt/sources.list
```

将官方源注释掉，并添加国内镜像源。推荐使用阿里云源：

```bash
deb https://mirrors.aliyun.com/kali kali-rolling main non-free contrib
deb-src https://mirrors.aliyun.com/kali kali-rolling main non-free contrib
```

也可以使用中科大源：

```bash
# deb https://mirrors.ustc.edu.cn/kali kali-rolling main non-free contrib
# deb-src https://mirrors.ustc.edu.cn/kali kali-rolling main non-free contrib
```

### 3.3 更新软件包索引

```bash
sudo apt update
```

---

## 4. 安装 HexStrike AI

### 4.1 安装软件包

```bash
sudo apt install hexstrike-ai
```

安装过程中可能需要输入当前用户密码，安装包大小约为数百 MB，具体时间取决于网络状况。

### 4.2 验证安装结果

执行以下命令检查是否安装成功：

```bash
hexstrike_server -h
```

若输出包含帮助信息，说明服务端已正确安装。

示例输出：

```text
usage: hexstrike_server [-h] [--port PORT] [--host HOST] [--debug] [--version]
```

---

## 5. 安装浏览器依赖（Browser Agent 需要）

HexStrike 的 Browser Agent 依赖 Chrome/Chromium 与 ChromeDriver。如果后续执行涉及浏览器交互的任务，缺少这些组件时可能会报错。

### 5.1 安装依赖工具

```bash
sudo apt install -y wget gnupg unzip
```

### 5.2 添加 Google Chrome 软件源

```bash
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/google-chrome.gpg > /dev/null
```

```bash
echo "deb [arch=amd64] https://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
```

### 5.3 更新软件源并安装 Chrome

```bash
sudo apt update
sudo apt install -y google-chrome-stable
```

### 5.4 查看 Chrome 版本

```bash
google-chrome --version
```

例如：

```text
Google Chrome 143.0.7499.146
```

### 5.5 下载并安装 ChromeDriver

根据 Chrome 的版本号，下载与之匹配的 ChromeDriver。

示例：

```bash
wget https://storage.googleapis.com/chrome-for-testing-public/143.0.7499.146/linux64/chromedriver-linux64.zip
```

解压并安装：

```bash
unzip chromedriver-linux64.zip
sudo mv chromedriver-linux64/chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver
```

验证安装：

```bash
chromedriver --version
```

---

## 6. 启动 HexStrike 服务

### 6.1 前台启动

```bash
hexstrike_server
```

默认监听端口为 8888。

### 6.2 后台运行（推荐）

使用 screen 或 tmux 可以让服务持续运行：

```bash
screen -S hexstrike
hexstrike_server --debug
```

退出会话：

```text
Ctrl + A，随后按 D
```

重新连接会话：

```bash
screen -r hexstrike
```

---

## 7. Cherry Studio 客户端配置

### 7.1 准备 MCP 脚本

HexStrike 的 MCP 相关脚本可从 GitHub 获取。请将脚本文件 `hexstrike_mcp.py` 放置在纯英文路径下，例如：

- `C:\hexstrike_mcp.py`
- `D:\tools\hexstrike_mcp.py`

> 说明：MCP 协议对非 ASCII 路径兼容性较弱，建议避免中文路径，以免出现调用异常。

### 7.2 在 Windows 环境中安装 Python 依赖

在 Windows 主机的 Python 环境中执行以下命令：

```bash
pip3 install --upgrade pip setuptools wheel -i https://mirrors.ustc.edu.cn/pypi/simple
pip3 install requests mcp -i https://mirrors.ustc.edu.cn/pypi/simple
```

### 7.3 在 Cherry Studio 中添加 MCP 服务

1. 打开 Cherry Studio。
2. 进入“设置” → “MCP”。
3. 点击“添加”按钮。
4. 配置以下参数：

- 命令：`C:\hexstrike_mcp.py`
- 参数 1：`--server`
- 参数 2：`http://<你的-Kali-虚拟机-IP>:8888`

例如：

```text
C:\hexstrike_mcp.py
--server
http://192.168.159.151:8888
```

### 7.4 验证连接

保存配置后，Cherry Studio 会尝试连接 HexStrike Server。如果连接成功，通常会显示“已连接”或绿色状态指示。

---

## 8. 常见问题排查

### 8.1 连接失败

请优先检查以下项：

- 确认 `hexstrike_server` 已正常启动
- 确认 8888 端口可访问
- 确认 Kali 防火墙未阻止连接
- 确认 Windows 主机能够 ping 通虚拟机 IP

开放端口示例：

```bash
sudo ufw allow 8888/tcp
```

### 8.2 浏览器相关错误

如果 Browser Agent 执行时出现浏览器错误，请检查：

- Chrome 是否已正确安装
- ChromeDriver 是否与 Chrome 版本匹配
- `chromedriver --version` 是否可正常输出

### 8.3 路径问题

若 Cherry Studio 不能正确调用 Python 脚本，请确保：

- 脚本路径为纯英文路径
- Python 环境已正确安装依赖
- 脚本文件本身可正常执行

---

## 9. 总结

完成上述步骤后，即可在 Kali Linux 上部署并运行 HexStrike AI 服务，并通过 Cherry Studio 等 MCP 客户端进行访问与测试。