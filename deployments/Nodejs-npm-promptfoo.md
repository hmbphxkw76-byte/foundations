# Node.js / npm 与 Promptfoo 使用与排查指南（中文）

本文档将 Node.js / npm 的常用配置与 Promptfoo 的安装、初始化、示例配置、运行与排查方法整合为一份便捷参考指南，适用于开发者本地开发与 CI 环境。

## 目录
- 概览
- 前置要求
- Node.js 与 nvm
- npm 常用配置与镜像
- Promptfoo 安装方式
- Promptfoo 快速初始化与示例配置
- 运行示例与输出
- 常见问题与排查
- CI 集成建议
- 参考链接

## 概览

本文档包含：Node 版本管理建议、npm 镜像与缓存操作、Promptfoo 的安装/初始化/示例配置（含 `promptfoo.yml`）、以及常见故障的定位与解决步骤。

## 前置要求

- 已安装 Git 与基本 shell（PowerShell / Bash）
- 已安装 Node.js（建议使用 `nvm` 管理多个版本）
- npm 可用且在 `PATH` 中

## Node.js 与 nvm

推荐使用 `nvm` 安装与切换 Node 版本：

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
# 重启 shell 或运行 source ~/.nvm/nvm.sh
nvm install stable
nvm use stable
```

## npm 常用配置与镜像

- 切换 registry（中国大陆建议）：

```bash
npm config set registry https://registry.npmmirror.com
npm config get registry
```

- 查看与清理缓存：

```bash
npm config get cache
npm cache clean --force
```

## Promptfoo 安装方式

- 全局安装（命令行工具）：

```bash
npm install -g promptfoo
```

- 作为项目依赖（库形式）：

```bash
npm install promptfoo --save
```

- 使用 npx（临时执行或初始化）：

```bash
npx promptfoo@latest init
```

- macOS / Linux（可选 Homebrew）：

```bash
# brew install promptfoo  # 若 Homebrew 有包
```

## Promptfoo 快速初始化与示例配置

初始化命令会在当前目录生成 `promptfoo.yml`（或示例配置）和 benchmarks 目录：

```bash
promptfoo init
# 或使用 npx 强制最新版初始化：
npx promptfoo@latest init
```

示例输出：

```
Initialized Promptfoo configuration: ./promptfoo.yml
Created example benchmark: benchmarks/example.json
```

下面是仓库中的示例配置（完整 YAML 已保存为 `foundations/deployment/promptfoo.yml`）：

```yaml
version: 1
models:
  - name: local-openai
    provider: openai
    api_key: ENV:OPENAI_API_KEY

benchmarks:
  - name: hello-translate
    description: 简单的英文翻译为中文示例
    inputs:
      - id: sample1
        content: "Translate to Chinese: Hello world"
    tasks:
      - id: translate
        prompt: "{{ input.content }}"
        model: local-openai
        max_tokens: 60

reports:
  output: promptfoo-report
```

使用前请设置环境变量 `OPENAI_API_KEY`（或根据 provider 修改配置）：

```bash
export OPENAI_API_KEY=...   # Unix
setx OPENAI_API_KEY "..."  # Windows (需重启 shell)
```

运行 benchmark：

```bash
promptfoo run --config promptfoo.yml
```

## 运行示例与典型输出

- 检查版本：

```bash
promptfoo --version
```

示例输出：

```
promptfoo 1.2.3
```

- 使用 npx 初始化示例输出：

```
Using promptfoo@latest from npx
Initialized Promptfoo configuration: ./promptfoo.yml
```

## 常见问题与排查步骤

- 命令不可用：检查全局安装路径是否在 `PATH`（Windows）：

```powershell
where.exe promptfoo
```

示例输出：

```
C:\Users\you\AppData\Roaming\npm\promptfoo
```

- 检查全局 npm 根目录：

```bash
npm root -g
```

- registry 与网络问题：

```bash
npm config get registry
```

- 权限问题（Unix）：避免用 `sudo` 安装全局包，推荐修复 npm 全局目录权限或使用 `nvm`。

- API 调用失败：
  - 确认环境变量：`echo $OPENAI_API_KEY` 或 `echo %OPENAI_API_KEY%`。
  - 确认 `promptfoo.yml` 中 `provider` 与 `api_key` 字段正确。

## CI 集成建议

- 将 `promptfoo run` 放入 CI 步骤做回归测试（GitHub Actions 示例）：

```yaml
name: Promptfoo benchmarks
on: [push, pull_request]
jobs:
  promptfoo:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: 'lts/*'
      - name: Install dependencies
        run: npm ci
      - name: Run promptfoo benchmarks
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: npx promptfoo@latest run --config foundations/deployment/promptfoo.yml
```

## 参考链接

- nvm: https://github.com/nvm-sh/nvm
- npm 镜像（国内）: https://registry.npmmirror.com

----

文件已生成：
- [foundations/deployment/Nodejs-npm-promptfoo.md](foundations/deployment/Nodejs-npm-promptfoo.md)
- 示例配置： [foundations/deployment/promptfoo.yml](foundations/deployment/promptfoo.yml)

如需我把旧文件合并后的内容覆盖原有 `npm.md` 或 `Promptfoo.md`，或把 CI 示例加入仓库的 `.github/workflows`，告诉我即可。