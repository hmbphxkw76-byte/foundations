# Node.js 与 npm 使用指南

本指南汇总了 Node.js / npm 环境的常见配置与命令示例，并包含 Promptfoo 的安装与使用说明，适用于开发者快速上手与排错。

## 目录
- 概览
- 前置要求
- 安装（npm / npx / Homebrew）
- 验证安装
- 快速初始化（Promptfoo）
- 常见配置（nvm / 镜像源 / 缓存）
- 常见问题与排查
- 参考链接

## 概览

本文档包含：
- Node.js 版本管理（使用 `nvm`）的推荐做法
- 常用的 `npm` 镜像与缓存操作
- Promptfoo 的安装与初始化示例（全局 / 项目 / npx）

## 前置要求

- 已安装 Node.js（建议使用 `nvm` 管理多个版本）
- npm 可用且在 PATH 中

## 安装（Promptfoo）

可以通过多种方式安装 Promptfoo：

- 全局安装（适合在多处调用命令行工具的场景）：

```bash
npm install -g promptfoo
```

- 作为项目依赖（在项目中以库形式使用）：

```bash
npm install promptfoo --save
```

- 使用 npx（无需全局安装，适合临时执行或初始化）：

```bash
npx promptfoo@latest init
```

- macOS / Linux（如果可用，也可通过 Homebrew 安装）：

```bash
# (示例) brew install promptfoo
```

## 验证安装

安装完成后，验证命令行工具是否可用：

```bash
promptfoo --version
```

如果能正确打印版本号，则安装成功。

## 快速初始化（Promptfoo）

在项目根目录运行初始化命令以创建配置和示例：

```bash
promptfoo init
# 或（使用 npx 确保使用最新版）
 npx promptfoo@latest init
```

初始化后，按照生成的配置与示例使用 Promptfoo 进行提示测试与基准。

## 常见配置

### 使用 nvm 管理 Node.js

推荐使用 `nvm` 来安装和切换 Node.js 版本：

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
# 重新打开终端或 source ~/.nvm/nvm.sh，然后安装稳定版本：
nvm install stable
```

### 配置 npm 镜像源（中国大陆用户）

如果网络访问官方 registry 较慢，可以切换到镜像：

```bash
npm config set registry https://registry.npmmirror.com
npm config get registry
```

### 查看与清理缓存

```bash
npm config get cache
npm cache clean --force
```

## 常见问题与排查

- PATH 或权限问题：全局安装后若命令不可用，请确认 npm 全局目录在 `PATH` 中，或使用 `nvm`/`sudo`（慎用）重新安装。
- 版本不兼容：若项目依赖特定 Node 版本，请使用 `nvm use <version>` 切换。
- 初始化失败：尝试使用 `npx promptfoo@latest init` 以保证使用最新版的初始化脚本。

## 参考链接

- Promptfoo 官方仓库 / 文档（请根据实际地址替换）
- nvm: https://github.com/nvm-sh/nvm
- npm registry 镜像: https://registry.npmmirror.com

----

如需，我可以：
- 将 Promptfoo 的配置示例添加到仓库中（例如 `promptfoo.yml`）
- 为常见问题添加更多排查命令和示例输出

完成：整理并美化 `npm` / Promptfoo 相关文档。
